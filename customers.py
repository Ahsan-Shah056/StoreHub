from database import get_db, close_db


def add_customer(connection, cursor, name, contact_info, address):
    try:
        query = "INSERT INTO Customers (name, contact_info, address) VALUES (%s, %s, %s)"
        params = (name, contact_info, address)
        cursor.execute(query, params)
        connection.commit()
        customer_id = cursor.lastrowid
        return get_customer(cursor, customer_id)
    except Exception as e:        
        raise ValueError(f"Error adding customer: {e}")

def get_all_customers(cursor):
    try:
        query = "SELECT * FROM Customers"
        cursor.execute(query)
        customers = cursor.fetchall()
        if not customers:
            return []
        return [
            {'customer_id': row['customer_id'], 'name': row['name'], 'contact_info': row['contact_info'], 'address': row['address']}
            for row in customers
        ]
    except Exception as e:        
        raise ValueError(f"Error getting all customers: {e}")




def delete_customer(connection, cursor, customer_id):
    """
    Deletes a customer from the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        customer_id (int): The ID of the customer to delete.

    Returns:
        list: A list of dictionaries containing the details of the deleted customer.
    """
    try:
        if customer_id == 0:
            raise ValueError("Cannot delete the anonymous customer.")
        customer = get_customer(cursor, customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")

        # Delete customer
        query = "DELETE FROM Customers WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        connection.commit()
        return customer
    except Exception as e:
        raise ValueError(f"Error deleting customer: {e}")


def view_customers(cursor):
    """
    Retrieves all customers from the database.

    Args:
        cursor: The database cursor object.

    Returns:
        list: A list of dictionaries containing the details of all customers.
    """
    try:
        query = "SELECT * FROM Customers"
        cursor.execute(query)
        customers = cursor.fetchall()
        return [
            {
                'customer_id': row['customer_id'],
                'name': row['name'],
                'contact_info': row['contact_info'],
                'address': row['address'],
                'is_anonymous': row['is_anonymous'],
                'created_at': row['created_at']
            }
            for row in customers
        ] if customers else []
    except Exception as e:
        raise ValueError(f"Error viewing customers: {e}")


def get_customer(cursor, customer_id):
    """
    Retrieves a customer from the database by their ID.

    Args:
        cursor: The database cursor object.
        customer_id (int): The ID of the customer to retrieve.

    Returns:
        dict: A dictionary containing the customer's details.
    """
    try:
        query = "SELECT * FROM Customers WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        return {
            'customer_id': customer['customer_id'],
            'name': customer['name'],
            'contact_info': customer['contact_info'],
            'address': customer['address'],
            'is_anonymous': customer['is_anonymous'],
            'created_at': customer['created_at']
        }
    except Exception as e:
        raise ValueError(f"Error getting customer: {e}")

def get_customer_by_id(cursor, customer_id):
    return get_customer(cursor, customer_id)


def search_customer_by_name(cursor, name):
    """
    Searches for customers in the database by name.

    Args:
        cursor: The database cursor object.
        name (str): The name or part of the name to search for.

    Returns:
        list: A list of dictionaries containing the details of matching customers.
    """
    try:
        query = "SELECT * FROM Customers WHERE name LIKE %s"
        cursor.execute(query, ('%' + name + '%',))
        customers = cursor.fetchall()
        return [
            {
                'customer_id': row['customer_id'],
                'name': row['name'],
                'contact_info': row['contact_info'],
                'address': row['address'],
                'is_anonymous': row['is_anonymous'],
                'created_at': row['created_at']
            }
            for row in customers
        ] if customers else []
    except Exception as e:
        raise ValueError(f"Error searching customer: {e}")
