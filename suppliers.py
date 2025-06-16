from database import close_db


def handle_error(connection, cursor, e, message=""):
    # Handles an error, closes the connection if needed, and raises a ValueError
    if connection and cursor:
        close_db(connection, cursor)

    raise ValueError(f"{message}: {e}")


def add_supplier(connection, cursor, name, contact_info, address):
    # Adds a new supplier to the database
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
    # Updates an existing supplier's information in the database
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
    # Deletes a supplier from the database
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
    # Retrieves all suppliers from the database
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
    # Retrieves a supplier from the database by their ID
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
    # Searches for suppliers in the database by name
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