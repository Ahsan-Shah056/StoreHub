from database import close_db


def handle_error(connection, cursor, error_message):
    """
    Handles errors by closing the database connection and raising a ValueError.
    """
    if connection and cursor:
        close_db(connection, cursor)
    raise ValueError(error_message)


def add_employee(connection, cursor, name):
    """
    Adds a new employee to the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        name (str): The name of the employee.

    Returns:
        dict: A dictionary containing the details of the added employee.
    """
    try:
        query = "INSERT INTO Employees (name) VALUES (%s)"
        cursor.execute(query, (name,))
        connection.commit()

        employee_id = cursor.lastrowid
        return get_employee(cursor, employee_id)
    except Exception as e:
        handle_error(connection, cursor, f"Error adding employee: {e}")


def update_employee(connection, cursor, employee_id, name):
    """
    Updates an existing employee's information in the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        employee_id (int): The ID of the employee to update.
        name (str): The new name of the employee.

    Returns:
        dict: A dictionary containing the updated employee's details.
    """
    try:
        query = "UPDATE Employees SET name = %s WHERE employee_id = %s"
        cursor.execute(query, (name, employee_id))
        connection.commit()

        return get_employee(cursor, employee_id)
    except Exception as e:
        handle_error(connection, cursor, f"Error updating employee: {e}")


def delete_employee(connection, cursor, employee_id):
    """
    Deletes an employee from the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        employee_id (int): The ID of the employee to delete.

    Returns:
        dict: A dictionary containing the details of the deleted employee.

    Raises:
        ValueError: If the employee with the given ID does not exist.
    """
    try:
        employee = get_employee(cursor, employee_id)
        query = "DELETE FROM Employees WHERE employee_id = %s"
        cursor.execute(query, (employee_id,))
        connection.commit()
        return employee
    except Exception as e:
        handle_error(connection, cursor, f"Error deleting employee: {e}")


def view_employees(cursor, connection=None):
    """
    Retrieves all employees from the database.

    Args:
        cursor: The database cursor object.
        connection: The database connection object (optional, for error handling).

    Returns:
        list: A list of dictionaries, where each dictionary represents an employee.
    """
    try:
        query = "SELECT employee_id, name, created_at FROM Employees"
        cursor.execute(query)
        result = cursor.fetchall()

        return [
            {
                "employee_id": row["employee_id"],
                "name": row["name"],
                "created_at": row["created_at"]
            }
            for row in result
        ]
    except Exception as e:
        handle_error(connection, cursor, f"Error viewing employees: {e}")


def get_employee(cursor, employee_id):
    """
    Retrieves an employee from the database by their ID.

    Args:
        cursor: The database cursor object.
        employee_id (int): The ID of the employee to retrieve.

    Returns:
        dict: A dictionary containing the employee's details.

    Raises:
        ValueError: If the employee with the given ID does not exist.
    """
    try:
        query = "SELECT employee_id, name, created_at FROM Employees WHERE employee_id = %s"
        cursor.execute(query, (employee_id,))
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"Employee with ID '{employee_id}' not found.")

        return {
            "employee_id": result["employee_id"],
            "name": result["name"],
            "created_at": result["created_at"]
        }
    except Exception as e:
        handle_error(cursor.connection, cursor, f"Error getting employee: {e}")


def search_employee_by_name(cursor, name):
    """
    Searches for employees in the database whose names contain the given search term.

    Args:
        cursor: The database cursor object.
        name (str): The name or part of the name to search for.

    Returns:
        list: A list of dictionaries, where each dictionary represents an employee.
    """
    try:
        query = "SELECT employee_id, name, created_at FROM Employees WHERE name LIKE %s"
        cursor.execute(query, (f"%{name}%",))
        result = cursor.fetchall()

        return [
            {
                "employee_id": row["employee_id"],
                "name": row["name"],
                "created_at": row["created_at"]
            }
            for row in result
        ]
    except Exception as e:
        handle_error(cursor.connection, cursor, f"Error searching employees: {e}")