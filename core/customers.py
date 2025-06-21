from .database import get_db, close_db


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
    # Delete customer if no related sales exist
    try:
        if customer_id == 0:
            raise ValueError("Cannot delete the anonymous customer.")
        customer = get_customer(cursor, customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        # Check for related sales
        cursor.execute("SELECT COUNT(*) AS sale_count FROM Sales WHERE customer_id = %s", (customer_id,))
        result = cursor.fetchone()
        if result and result['sale_count'] > 0:
            raise ValueError("Cannot delete customer: This customer has related sales records. Deletion is not allowed to preserve sales history.")
        # Delete customer
        query = "DELETE FROM Customers WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        connection.commit()
        return customer
    except Exception as e:
        raise ValueError(f"Error deleting customer: {e}")


def view_customers(cursor):
    # Get all customers from database
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
    # Get customer by ID
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
    # Search for customers by name
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

def update_customer(connection, cursor, customer_id, name, contact_info, address):
    """
    Updates an existing customer's information in the database.
    """
    try:
        # Check if customer exists
        customer = get_customer(cursor, customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        
        # Update customer information
        query = "UPDATE Customers SET name = %s, contact_info = %s, address = %s WHERE customer_id = %s"
        cursor.execute(query, (name, contact_info, address, customer_id))
        connection.commit()
        
        # Return updated customer
        updated_customer = get_customer(cursor, customer_id)
        return updated_customer
    except Exception as e:        
        raise ValueError(f"Error updating customer: {e}")
