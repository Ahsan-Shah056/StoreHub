import mysql.connector
from mysql.connector.errors import Error

def get_db(host="localhost", user="root", password="Ahsan7424", database="store"):
    """
    Establishes a connection to the MySQL database and returns the connection and cursor.

    Args:
        host (str): The hostname of the MySQL server.
        user (str): The username for the MySQL server.
        password (str): The password for the MySQL server.
        database (str): The name of the database to connect to.

    Returns:
        tuple: A tuple containing the database connection and cursor.

    Raises:
        Exception: If the connection to the database fails.
    """
    connection = None
    cursor = None
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        if connection.is_connected():
            # Use dictionary=True to return results as dictionaries
            cursor = connection.cursor(dictionary=True)
            return connection, cursor
    except Error as e:
        raise Exception(f"Error connecting to the database: {e}")


def close_db(connection, cursor):
    """
    Closes a database connection and cursor.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The database connection object.
        cursor (mysql.connector.cursor.MySQLCursor): The database cursor object.
    """
    try:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("Connection closed successfully.")
    except Error as e:
        print(f"Error closing connection: {e}")
