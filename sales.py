from database import get_db, close_db
from decimal import Decimal

class SalesError(Exception):
    """
    Represents an error that occurs during sales operations.
    """
    pass

def handle_error(connection, cursor, error):
    """
    Handles errors, closes the database connection if needed, and raises a SalesError.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        error: The exception that occurred.
    """
    if connection and cursor:
        close_db(connection, cursor)
    raise SalesError(str(error))



def get_product(cursor, sku):
    """
    Retrieves a product from the database based on its SKU.

    Args:
        cursor: The database cursor object.
        sku (str): The SKU of the product to retrieve.

    Returns:
        dict: A dictionary containing the product details.

    Raises:
        SalesError: If the product is not found or a database error occurs.
    """
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
    """
    Adds a product to the shopping cart or increases its quantity if already present.

    Args:
        cart (list): The shopping cart (a list of dictionaries).
        sku (str): The SKU of the product to add.
        quantity (int): The quantity of the product to add.

    Raises:
        SalesError: If quantity <= 0.
    """
    if quantity <= 0:
        raise SalesError("Quantity must be greater than 0.")
    for item in cart:
        if item['SKU'] == sku:
            item['quantity'] += quantity
            return
    cart.append({'SKU': sku, 'quantity': quantity})

def remove_from_cart(cart, sku):
    """
    Removes a product from the shopping cart.

    Args:
        cart (list): The shopping cart (a list of dictionaries).
        sku (str): The SKU of the product to remove.

    Raises:
        SalesError: If the SKU is not found in the cart.
    """
    for item in cart:
        if item['SKU'] == sku:
            cart.remove(item)
            return
    raise SalesError(f"SKU '{sku}' not found in cart.")

def update_cart_quantity(cart, sku, quantity):
    """
    Updates the quantity of a product in the shopping cart.

    Args:
        cart (list): The shopping cart (a list of dictionaries).
        sku (str): The SKU of the product to update.
        quantity (int): The new quantity of the product.

    Raises:
        SalesError: If quantity <= 0 or SKU is not found in cart.
    """
    if quantity <= 0:
        raise SalesError("Quantity must be greater than 0.")
    for item in cart:
        if item['SKU'] == sku:
            item['quantity'] = quantity
            return
    raise SalesError(f"SKU '{sku}' not found in cart.")

def get_cart_items(cart):
    """
    Retrieves all items in the shopping cart.

    Args:
        cart (list): The shopping cart (a list of dictionaries).

    Returns:
        list: The list of items in the cart.
    """
    return cart

def calculate_totals(cart, cursor):
    """
    Calculates the subtotal, taxes, and total of all items in the shopping cart.

    Args:
        cart (list): The shopping cart (a list of dictionaries).
        cursor: The database cursor object.

    Returns:
        dict: A dictionary containing the subtotal, taxes, and total.

    Raises:
        SalesError: If any item in the cart references a SKU not in the database, 
                    or any database error occurs.
    """
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
        taxes = subtotal * Decimal('0.10')  # 10% tax
        total = subtotal + taxes
        return {"subtotal": float(subtotal), "taxes": float(taxes), "total": float(total)}
    except Exception as e:
        raise SalesError(f"Error calculating totals: {e}")

def log_sale(connection, cursor, cart, employee_id, customer_id):
    """
    Logs a sale in the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        cart (list): The shopping cart (a list of dictionaries).
        employee_id (int): The ID of the employee who made the sale.
        customer_id (int): The ID of the customer who made the purchase.

    Returns:
        int: The ID of the newly created sale (transaction).

    Raises:
        SalesError: If the employee_id or customer_id doesn't exist, 
                    or any database error occurs.
    """
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
        connection.commit()
        return sale_id
    except Exception as e:
        raise SalesError(f"Error logging sale: {e}")

def generate_receipt(cursor, transaction_id):
    """
    Generates a receipt for a given transaction ID.

    Args:
        cursor: The database cursor object.
        transaction_id (int): The unique ID of the sale.

    Returns:
        str: The receipt text as a formatted string.

    Raises:
        SalesError: If the transaction_id is not found or a database error occurs.
    """
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
    """
    Generates a receipt for a given transaction ID as a list of dicts for UI display.
    Args:
        cursor: The database cursor object.
        transaction_id (int): The unique ID of the sale.
    Returns:
        list: List of dicts with keys: SKU, quantity, price
    Raises:
        SalesError: If the transaction_id is not found or a database error occurs.
    """
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


