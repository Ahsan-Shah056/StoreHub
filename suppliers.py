from database import close_db


def handle_error(connection, cursor, e, message=""):
    """
    Handles an error, closes the connection if needed, and raises a ValueError.
    """
    if connection and cursor:
        close_db(connection, cursor)

    raise ValueError(f"{message}: {e}")


def add_supplier(connection, cursor, name, contact_info, address):
    """
    Adds a new supplier to the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        name (str): The name of the supplier.
        contact_info (str): The contact information of the supplier.
        address (str): The address of the supplier.

    Returns:
        dict: The details of the newly added supplier.

    Raises:
        ValueError: If the supplier name already exists or if a database error occurs.
    """
    try:
        query = "SELECT * FROM Suppliers WHERE name = %s"
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        if result:
            raise ValueError(f"Supplier with name '{name}' already exists.")
        query = "INSERT INTO Suppliers (name, contact_info, address) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, contact_info, address))
        connection.commit()
        supplier = get_supplier(cursor, cursor.lastrowid)
        return supplier
    except ValueError as ve:
        raise ValueError(str(ve))
    except Exception as e:
        handle_error(connection, cursor, e, "Error adding supplier")


def update_supplier(connection, cursor, supplier_id, name, contact_info, address):
    """
    Updates an existing supplier's information in the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        supplier_id (int): The ID of the supplier to update.
        name (str): The new name of the supplier.
        contact_info (str): The new contact information of the supplier.
        address (str): The new address of the supplier.

    Returns:
        dict: The details of the updated supplier.

    Raises:
        ValueError: If the supplier ID is not found or if a database error occurs.
    """
    try:
        get_supplier(cursor, supplier_id)
        query = "UPDATE Suppliers SET name = %s, contact_info = %s, address = %s WHERE supplier_id = %s"
        cursor.execute(query, (name, contact_info, address, supplier_id))
        connection.commit()
        supplier = get_supplier(cursor, supplier_id)
        return supplier
    except ValueError as ve:
        raise ValueError(str(ve))
    except Exception as e:
        handle_error(connection, cursor, e, "Error updating supplier")


def delete_supplier(connection, cursor, supplier_id):
    """
    Deletes a supplier from the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        supplier_id (int): The ID of the supplier to delete.

    Returns:
        dict: The details of the deleted supplier.

    Raises:
        ValueError: If the supplier ID is not found or if a database error occurs.
    """
    try:
        supplier = get_supplier(cursor, supplier_id)
        query = "DELETE FROM Suppliers WHERE supplier_id = %s"
        cursor.execute(query, (supplier_id,))
        connection.commit()
        return supplier
    except ValueError as ve:
        raise ValueError(str(ve))
    except Exception as e:
        handle_error(connection, cursor, e, "Error deleting supplier")


def view_suppliers(cursor, connection=None):
    """
    Retrieves all suppliers from the database.

    Args:
        cursor: The database cursor object.
        connection: The database connection object (optional, for error handling).

    Returns:
        list: A list of dictionaries, where each dictionary contains the details of a supplier.

    Raises:
        Exception: If a database error occurs.
    """
    try:
        query = "SELECT * FROM Suppliers"
        cursor.execute(query)
        suppliers = cursor.fetchall()
        if not suppliers:
            return []
        suppliers_list = []
        for supplier in suppliers:
            if isinstance(supplier, dict):
                suppliers_list.append({
                    'supplier_id': supplier['supplier_id'],
                    'name': supplier['name'],
                    'contact_info': supplier['contact_info'],
                    'address': supplier['address']
                })
            else:
                suppliers_list.append({
                    'supplier_id': supplier[0],
                    'name': supplier[1],
                    'contact_info': supplier[2],
                    'address': supplier[3]
                })
        return suppliers_list
    except Exception as e:
        raise Exception(f"Error viewing suppliers: {e}")


def get_supplier(cursor, supplier_id):
    """
    Retrieves a supplier from the database by their ID.

    Args:
        cursor: The database cursor object.
        supplier_id (int): The ID of the supplier to retrieve.

    Returns:
        dict: The details of the supplier.

    Raises:
        ValueError: If the supplier ID is not found or if a database error occurs.
    """
    try:
        query = "SELECT * FROM Suppliers WHERE supplier_id = %s"
        cursor.execute(query, (supplier_id,))
        supplier = cursor.fetchone()
        if not supplier:
            raise ValueError(f"Supplier with ID '{supplier_id}' not found.")
        if isinstance(supplier, dict):
            return {
                'supplier_id': supplier['supplier_id'],
                'name': supplier['name'],
                'contact_info': supplier['contact_info'],
                'address': supplier['address']
            }
        else:
            return {
                'supplier_id': supplier[0],
                'name': supplier[1],
                'contact_info': supplier[2],
                'address': supplier[3]
            }
    except Exception as e:
        raise Exception(f"Error getting supplier: {e}")


def search_supplier_by_name(cursor, name):
    """
    Searches for suppliers in the database by name.

    Args:
        cursor: The database cursor object.
        name (str): The name (or part of the name) to search for.

    Returns:
        list: A list of dictionaries, where each dictionary contains the details of a matching supplier.

    Raises:
        Exception: If a database error occurs.
    """
    try:
        if not name:
            return []
        query = "SELECT * FROM Suppliers WHERE name LIKE %s"
        cursor.execute(query, (f"%{name}%",))
        suppliers = cursor.fetchall()
        suppliers_list = []
        for supplier in suppliers:
            if isinstance(supplier, dict):
                suppliers_list.append({
                    'supplier_id': supplier['supplier_id'],
                    'name': supplier['name'],
                    'contact_info': supplier['contact_info'],
                    'address': supplier['address']
                })
            else:
                suppliers_list.append({
                    'supplier_id': supplier[0],
                    'name': supplier[1],
                    'contact_info': supplier[2],
                    'address': supplier[3]
                })
        return suppliers_list
    except Exception as e:
        raise Exception(f"Error searching supplier: {e}")