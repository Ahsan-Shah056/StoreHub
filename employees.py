from database import close_db


def handle_error(connection, cursor, error_message):
    """
    Handles errors by closing the database connection and raising a ValueError.
    """
    if connection and cursor:
        close_db(connection, cursor)
    raise ValueError(error_message)


def add_employee(connection, cursor, name, role):
    """
    Adds a new employee to the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        name (str): The name of the employee.
        role (str): The role of the employee.

    Returns:
        dict: A dictionary containing the details of the added employee.

    Raises:
        ValueError: If the role does not exist.
    """
    try:
        role_id = get_role_id(cursor, role)
        if role_id is None:
            raise ValueError(f"Role '{role}' not found.")

        query = "INSERT INTO Employees (name, role_id) VALUES (%s, %s)"
        cursor.execute(query, (name, role_id))
        connection.commit()

        employee_id = cursor.lastrowid
        return get_employee(cursor, employee_id)
    except Exception as e:
        handle_error(connection, cursor, f"Error adding employee: {e}")


def update_employee(connection, cursor, employee_id, name, role):
    """
    Updates an existing employee's information in the database.

    Args:
        connection: The database connection object.
        cursor: The database cursor object.
        employee_id (int): The ID of the employee to update.
        name (str): The new name of the employee.
        role (str): The new role of the employee.

    Returns:
        dict: A dictionary containing the updated employee's details.

    Raises:
        ValueError: If the role or the employee ID does not exist.
    """
    try:
        role_id = get_role_id(cursor, role)
        if role_id is None:
            raise ValueError(f"Role '{role}' not found.")

        query = "UPDATE Employees SET name = %s, role_id = %s WHERE employee_id = %s"
        cursor.execute(query, (name, role_id, employee_id))
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


def view_employees(cursor):
    """
    Retrieves all employees from the database.

    Args:
        cursor: The database cursor object.

    Returns:
        list: A list of dictionaries, where each dictionary represents an employee.
    """
    try:
        query = """
            SELECT e.employee_id, e.name, r.role_name, e.created_at
            FROM Employees e
            JOIN Roles r ON e.role_id = r.role_id
        """
        cursor.execute(query)
        result = cursor.fetchall()

        return [
            {
                "employee_id": row["employee_id"],
                "name": row["name"],
                "role": row["role_name"],
                "created_at": row["created_at"]
            }
            for row in result
        ]
    except Exception as e:
        handle_error(cursor.connection, cursor, f"Error viewing employees: {e}")


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
        query = """
            SELECT e.employee_id, e.name, r.role_name, e.created_at
            FROM Employees e
            JOIN Roles r ON e.role_id = r.role_id
            WHERE e.employee_id = %s
        """
        cursor.execute(query, (employee_id,))
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"Employee with ID '{employee_id}' not found.")

        return {
            "employee_id": result["employee_id"],
            "name": result["name"],
            "role": result["role_name"],
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
        query = """
            SELECT e.employee_id, e.name, r.role_name, e.created_at
            FROM Employees e
            JOIN Roles r ON e.role_id = r.role_id
            WHERE e.name LIKE %s
        """
        cursor.execute(query, (f"%{name}%",))
        result = cursor.fetchall()

        return [
            {
                "employee_id": row["employee_id"],
                "name": row["name"],
                "role": row["role_name"],
                "created_at": row["created_at"]
            }
            for row in result
        ]
    except Exception as e:
        handle_error(cursor.connection, cursor, f"Error searching employees: {e}")


def get_role_id(cursor, role_name):
    """
    Retrieves the ID of a role from the database.

    Args:
        cursor: The database cursor object.
        role_name (str): The name of the role.

    Returns:
        int or None: The role_id if found, otherwise None.
    """
    try:
        query = "SELECT role_id FROM Roles WHERE role_name = %s"
        cursor.execute(query, (role_name,))
        result = cursor.fetchone()
        return result["role_id"] if result else None
    except Exception as e:
        raise Exception(f"Error getting role ID: {e}")


def get_role_name(cursor, role_id):
    """
    Retrieves the name of a role from the database.

    Args:
        cursor: The database cursor object.
        role_id (int): The ID of the role.

    Returns:
        str or None: The role_name if found, otherwise None.
    """
    try:
        query = "SELECT role_name FROM Roles WHERE role_id = %s"
        cursor.execute(query, (role_id,))
        result = cursor.fetchone()
        return result["role_name"] if result else None
    except Exception as e:
        raise Exception(f"Error getting role name: {e}")