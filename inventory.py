from database import close_db


def handle_error(connection, cursor, e):
    raise ValueError(str(e))


def add_item(connection, cursor, sku, name, category, price, stock, supplier_id):
    """Adds a new item to the inventory.

    Args:
        connection: The database connection.
        cursor: The database cursor.
        sku: The SKU of the item.
        name: The name of the item.
        category: The category of the item.
        price: The price of the item.
        stock: The stock of the item.
        supplier_id: The supplier ID of the item.

    Returns:
        A dictionary containing the details of the added item.

    Raises:
        ValueError: If the price or stock is negative, or if the category or supplier does not exist.
    """
    try:
        if price <= 0 or stock < 0:
            raise ValueError("Price must be greater than 0 and stock cannot be negative.")

        # Check if category exists
        cursor.execute("SELECT category_id FROM Categories WHERE name = %s", (category,))
        category_id_result = cursor.fetchone()
        if not category_id_result:
            raise ValueError(f"Category with name '{category}' does not exist.")
        category_id = category_id_result['category_id']

        # Check if supplier exists
        cursor.execute("SELECT supplier_id FROM Suppliers WHERE supplier_id = %s", (supplier_id,))
        if not cursor.fetchone():
            raise ValueError(f"Supplier with ID '{supplier_id}' does not exist.")

        # Insert the product
        cursor.execute(
            "INSERT INTO Products (SKU, name, category_id, price, stock, supplier_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (sku, name, category_id, price, stock, supplier_id)
        )
        connection.commit()
        return get_item(connection, cursor, sku)
    except Exception as e:
        handle_error(connection, cursor, f"Error adding item: {e}")




def delete_item(connection, cursor, sku):
    """Deletes an item from the inventory, including related inventory adjustments."""
    try:
        item = get_item(connection, cursor, sku)
        # First, delete related inventory adjustments
        cursor.execute("DELETE FROM InventoryAdjustments WHERE SKU = %s", (sku,))
        # Then, delete the product itself
        cursor.execute("DELETE FROM Products WHERE SKU = %s", (sku,))
        connection.commit()
        return item
    except Exception as e:
        handle_error(connection, cursor, f"Error deleting item: {e}")


def get_item(connection, cursor, sku):
    """Retrieves an item from the inventory.

    Args:
        connection: The database connection.
        cursor: The database cursor.
        sku: The SKU of the item to retrieve.

    Returns:
        A dictionary containing the item details.

    Raises:
        ValueError: If the SKU does not exist.
    """
    try:
        cursor.execute(
            "SELECT p.SKU, p.name, c.name AS category, p.price, p.stock, p.supplier_id "
            "FROM Products p JOIN Categories c ON c.category_id = p.category_id WHERE p.SKU = %s",
            (sku,)
        )
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Item with SKU '{sku}' does not exist.")
        return {
            "SKU": result["SKU"],
            "name": result["name"],
            "category": result["category"],
            "price": result["price"],
            "stock": result["stock"],
            "supplier_id": result["supplier_id"],
        }
    except Exception as e:
        handle_error(connection, cursor, f"Error getting item: {e}")


def view_inventory(connection, cursor):
    """Retrieves all items in the inventory.

    Args:
        connection: The database connection.
        cursor: The database cursor.

    Returns:
        list: A list of dictionaries, where each dictionary contains the details of an item.
    """
    try:
        cursor.execute(
            "SELECT p.SKU, p.name, c.name AS category, p.price, p.stock, p.supplier_id "
            "FROM Products p JOIN Categories c ON c.category_id = p.category_id"
        )
        results = cursor.fetchall()
        return [
            {
                "SKU": row["SKU"],
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "stock": row["stock"],
                "supplier_id": row["supplier_id"],
            }
            for row in results
        ]
    except Exception as e:
        handle_error(connection, cursor, f"Error viewing inventory: {e}")


def check_low_stock(connection, cursor, threshold=None):
    """Retrieves items with low stock from the inventory.

    
    """
    try:
        if threshold is None:
            query = "SELECT SKU, name, stock FROM Products WHERE stock < 25"
            cursor.execute(query)
        else:
            query = "SELECT SKU, name, stock FROM Products WHERE stock < %s"
            cursor.execute(query, (threshold,))
        results = cursor.fetchall()
        return [
            {"SKU": row["SKU"], "name": row["name"], "stock": row["stock"]}
            for row in results
        ]
    except Exception as e:
        handle_error(connection, cursor, f"Error checking low stock: {e}")


def adjust_stock(connection, cursor, sku, quantity_change, reason, employee_id):
    """Adjusts the stock of an item in the inventory, now requires employee_id."""
    try:
        item = get_item(connection, cursor, sku)
        new_stock = item["stock"] + quantity_change
        if new_stock < 0:
            raise ValueError("Stock cannot go below 0.")
        cursor.execute("UPDATE Products SET stock = %s WHERE SKU = %s", (new_stock, sku))
        cursor.execute(
            "INSERT INTO InventoryAdjustments (SKU, adjustment_datetime, quantity_change, reason, employee_id) VALUES (%s, NOW(), %s, %s, %s)",
            (sku, quantity_change, reason, employee_id)
        )
        connection.commit()
        return get_item(connection, cursor, sku)
    except Exception as e:
        handle_error(connection, cursor, f"Error adjusting stock: {e}")