from database import get_db, close_db
from decimal import Decimal

# Import for low stock alerts and large transaction alerts
try:
    from Automations import check_and_alert_low_stock, check_and_alert_large_transaction
except ImportError:
    check_and_alert_low_stock = None
    check_and_alert_large_transaction = None

class SalesError(Exception):
    """Sales operation error."""
    pass

def handle_error(connection, cursor, error):
    """Close DB connection and raise SalesError."""
    if connection and cursor:
        close_db(connection, cursor)
    raise SalesError(str(error))

def get_product(cursor, sku):
    """Get product by SKU."""
    try:
        query = "SELECT p.SKU, p.name, c.name AS category, p.price, p.stock, p.supplier_id FROM Products p JOIN Categories c ON p.category_id = c.category_id WHERE p.SKU = %s"
        cursor.execute(query, (sku,))
        result = cursor.fetchone()
        if not result:
            raise SalesError(f"Product with SKU '{sku}' not found.")
        return {
            "SKU": result["SKU"],
            "name": result["name"],
            "category": result["category"],
            "price": result["price"],
            "stock": result["stock"],
            "supplier_id": result["supplier_id"]
        }
    except Exception as e:
        raise SalesError(f"Error getting product: {e}")

def add_to_cart(cart, sku, quantity):
    # Add product to cart or increase quantity
    if quantity <= 0:
        raise SalesError("Quantity must be greater than 0.")
    for item in cart:
        if item['SKU'] == sku:
            item['quantity'] += quantity
            return
    cart.append({'SKU': sku, 'quantity': quantity})

def remove_from_cart(cart, sku):
    # Remove product from cart
    for item in cart:
        if item['SKU'] == sku:
            cart.remove(item)
            return
    raise SalesError(f"SKU '{sku}' not found in cart.")

def update_cart_quantity(cart, sku, quantity):
    # Update product quantity in cart
    if quantity <= 0:
        raise SalesError("Quantity must be greater than 0.")
    for item in cart:
        if item['SKU'] == sku:
            item['quantity'] = quantity
            return
    raise SalesError(f"SKU '{sku}' not found in cart.")

def get_cart_items(cart):
    # Get all cart items
    return cart

def calculate_totals(cart, cursor):
    # Calculate subtotal, taxes, and total
    try:
        subtotal = Decimal('0.00')
        for item in cart:
            query = "SELECT price FROM Products WHERE SKU = %s"
            cursor.execute(query, (item['SKU'],))
            result = cursor.fetchone()
            if not result:
                raise SalesError(f"Product with SKU '{item['SKU']}' not found.")
            price = result['price']
            quantity = Decimal(str(item['quantity']))
            subtotal += price * quantity
        taxes = subtotal * Decimal('0.175')  # 10% tax
        total = subtotal + taxes
        return {"subtotal": float(subtotal), "taxes": float(taxes), "total": float(total)}
    except Exception as e:
        raise SalesError(f"Error calculating totals: {e}")

def log_sale(connection, cursor, cart, employee_id, customer_id):
    # Log sale transaction to database
    try:
        # Check if customer_id exists (if provided)
        if customer_id is not None:
            cursor.execute("SELECT customer_id FROM Customers WHERE customer_id = %s", (customer_id,))
            if not cursor.fetchone():
                raise SalesError(f"Customer ID '{customer_id}' not found.")

        # Check if employee_id exists
        cursor.execute("SELECT employee_id FROM Employees WHERE employee_id = %s", (employee_id,))
        if not cursor.fetchone():
            raise SalesError(f"Employee ID '{employee_id}' not found.")

        # Check stock for each item in cart
        for item in cart:
            cursor.execute("SELECT stock FROM Products WHERE SKU = %s", (item['SKU'],))
            result = cursor.fetchone()
            if not result:
                raise SalesError(f"Product with SKU '{item['SKU']}' not found.")
            if result['stock'] < item['quantity']:
                raise SalesError(f"Not enough stock for SKU '{item['SKU']}'. Available: {result['stock']}, Requested: {item['quantity']}")

        # Calculate totals
        totals = calculate_totals(cart, cursor)

        # Insert into Sales table
        cursor.execute(
            "INSERT INTO Sales (sale_datetime, total, employee_id, customer_id) "
            "VALUES (NOW(), %s, %s, %s)",
            (totals['total'], employee_id, customer_id),
        )
        sale_id = cursor.lastrowid

        # Insert each cart item into SaleItems and decrement stock
        for item in cart:
            cursor.execute("SELECT price FROM Products WHERE SKU = %s", (item['SKU'],))
            price_row = cursor.fetchone()
            if price_row:
                price = price_row['price']
            else:
                raise SalesError(f"Product with SKU '{item['SKU']}' not found while logging sale.")

            cursor.execute(
                "INSERT INTO SaleItems (sale_id, SKU, quantity, price) VALUES (%s, %s, %s, %s)",
                (sale_id, item['SKU'], item['quantity'], price)
            )
            cursor.execute(
                "UPDATE Products SET stock = stock - %s WHERE SKU = %s",
                (item['quantity'], item['SKU'])
            )
            # Check for low stock and send alert if needed
            if check_and_alert_low_stock:
                check_and_alert_low_stock(cursor, item['SKU'])
        connection.commit()
        
        # Check for large transaction and send alert if needed
        if check_and_alert_large_transaction:
            check_and_alert_large_transaction(cursor, sale_id, totals['total'], employee_id, customer_id)
        
        return sale_id
    except Exception as e:
        raise SalesError(f"Error logging sale: {e}")

def generate_receipt(cursor, transaction_id):
    """Generate receipt text for transaction."""
    try:
        query = """
            SELECT s.sale_datetime, s.total, si.SKU, si.quantity, si.price
            FROM Sales s
            JOIN SaleItems si ON s.sale_id = si.sale_id
            WHERE s.sale_id = %s
        """
        cursor.execute(query, (transaction_id,))
        results = cursor.fetchall()
        if not results:
            raise SalesError(f"Transaction with ID {transaction_id} not found.")

        # Build a textual receipt
        sale_datetime = results[0]['sale_datetime']
        total = results[0]['total']
        receipt_lines = [
            f"Receipt for Transaction ID: {transaction_id}",
            f"Date: {sale_datetime}",
            "Items:"
        ]
        for row in results:
            sku = row['SKU']
            qty = row['quantity']
            price = row['price']
            receipt_lines.append(f"  SKU: {sku}, Quantity: {qty}, Price: {price}")
        receipt_lines.append(f"Total: {total}")

        return "\n".join(receipt_lines)
    except Exception as e:
        raise SalesError(f"Error generating receipt: {e}")

def generate_receipt_dict(cursor, transaction_id):
    """Generate receipt data as dictionary."""
    try:
        query = """
            SELECT si.SKU, si.quantity, si.price
            FROM Sales s
            JOIN SaleItems si ON s.sale_id = si.sale_id
            WHERE s.sale_id = %s
        """
        cursor.execute(query, (transaction_id,))
        results = cursor.fetchall()
        if not results:
            raise SalesError(f"Transaction with ID {transaction_id} not found.")
        return [
            {"SKU": row["SKU"], "quantity": row["quantity"], "price": row["price"]}
            for row in results
        ]
    except Exception as e:
        raise SalesError(f"Error generating receipt: {e}")


