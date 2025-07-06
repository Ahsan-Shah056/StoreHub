import mysql.connector
from mysql.connector.errors import Error
import logging

# Configure logging for database module
logger = logging.getLogger(__name__)

def get_db(host="localhost", user="root", password="Ahsan7424", database="store"):
    # Establishes a connection to the MySQL database and returns the connection and cursor
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
    # Closes a database connection and cursor
    try:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed successfully.")
    except Error as e:
        logger.error(f"Error closing connection: {e}")
