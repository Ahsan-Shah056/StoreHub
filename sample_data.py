import mysql.connector
from datetime import datetime
import random

def create_tables(cursor):
    with open("schema.sql", "r") as file:
        sql_script = file.read()
    commands = sql_script.split(';')
    for command in commands:
        if command.strip():
            try:
                cursor.execute(command + ";")
            except mysql.connector.Error as err:
                print(f"Error executing command: {command}: {err}")

def insert_sample_data():
    """Inserts sample data into the Crockery Store POS database."""
    try:
        # Database connection
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ahsan7424",
            database="store"
        )
        cursor = mydb.cursor()

        # Drop and recreate tables
        create_tables(cursor)

        # Disable foreign key checks temporarily
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DELETE FROM Suppliers")
        cursor.execute("DELETE FROM Customers WHERE customer_id != 0")
        cursor.execute("DELETE FROM Products")
        cursor.execute("DELETE FROM Categories")
        cursor.execute("DELETE FROM Employees")
        cursor.execute("DELETE FROM Sales")
        cursor.execute("DELETE FROM SaleItems")
        cursor.execute("DELETE FROM Purchases")
        cursor.execute("DELETE FROM PurchaseItems")
        cursor.execute("DELETE FROM InventoryAdjustments")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Insert Employees (no roles)
        employees = [
            ("Ahmed Khan",),
            ("Ayesha Siddiqui",),
            ("Bilal Hassan",)
        ]
        for (name,) in employees:
            sql = "INSERT INTO Employees (name) VALUES (%s)"
            cursor.execute(sql, (name,))

        # Insert Suppliers
        suppliers_list = [
            ("Lahore Crockery House", "contact@lahorecrockery.pk", "Mall Road, Lahore"),
            ("Karachi Tableware Mart", "info@karachitableware.pk", "Tariq Road, Karachi"),
            ("Islamabad Ceramics", "sales@islamabadceramics.pk", "Blue Area, Islamabad"),
            ("Peshawar Pottery Palace", "info@potterypeshawar.pk", "Saddar, Peshawar"),
            ("Multan Clay Crafts", "contact@multanclay.pk", "Hussain Agahi, Multan"),
            ("Faisalabad Porcelain Center", "info@porcelainfaisalabad.pk", "D Ground, Faisalabad"),
            ("Rawalpindi Crockery Store", "sales@rawalcrockery.pk", "Commercial Market, Rawalpindi"),
            ("Sialkot Table Tops", "hello@sialkottops.pk", "Cantt Bazaar, Sialkot"),
            ("Quetta Dinnerware Depot", "info@quettadinnerware.pk", "Jinnah Road, Quetta"),
            ("Hyderabad Kitchenware Hub", "contact@hyderabadkitchenware.pk", "Auto Bhan Road, Hyderabad")
        ]
        for name, contact_info, address in suppliers_list:
            sql = "INSERT INTO Suppliers (name, contact_info, address) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, contact_info, address))

        # Fetch supplier IDs
        cursor.execute("SELECT supplier_id FROM Suppliers")
        supplier_ids = [row[0] for row in cursor.fetchall()]

        # Insert Categories
        categories = ["Plates", "Bowls", "Cups", "Cutlery", "Serving Dishes"]
        for category in categories:
            sql = "INSERT INTO Categories (name) VALUES (%s)"
            cursor.execute(sql, (category,))

        # Fetch category IDs
        cursor.execute("SELECT category_id, name FROM Categories")
        category_dict = {row[1]: row[0] for row in cursor.fetchall()}

        # Insert Products (with required fields only)
        base_products = [
            ("Dinner Plate", "Plates", 12.99, 100, supplier_ids[0]),
            ("Salad Plate", "Plates", 9.99, 150, supplier_ids[0]),
            ("Dessert Plate", "Plates", 11.99, 120, supplier_ids[0]),
            ("Soup Bowl", "Bowls", 8.99, 80, supplier_ids[1]),
            ("Cereal Bowl", "Bowls", 7.99, 110, supplier_ids[1]),
            ("Mixing Bowl", "Bowls", 15.99, 60, supplier_ids[2]),
            ("Coffee Mug", "Cups", 6.99, 200, supplier_ids[3]),
            ("Tea Cup", "Cups", 7.99, 180, supplier_ids[3]),
            ("Espresso Cup", "Cups", 5.99, 160, supplier_ids[4]),
            ("Fork", "Cutlery", 3.99, 300, supplier_ids[5]),
            ("Knife", "Cutlery", 4.99, 300, supplier_ids[5]),
            ("Spoon", "Cutlery", 3.49, 300, supplier_ids[5]),
            ("Serving Platter", "Serving Dishes", 24.99, 40, supplier_ids[6]),
            ("Serving Bowl", "Serving Dishes", 19.99, 50, supplier_ids[6]),
            ("Gravy Boat", "Serving Dishes", 14.99, 70, supplier_ids[7]),
        ]
        for name, category_name, price, stock, supplier_id in base_products:
            sku = name.upper().replace(" ", "_")
            category_id = category_dict[category_name]
            sql = "INSERT INTO Products (SKU, name, category_id, price, stock, supplier_id) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (sku, name, category_id, price, stock, supplier_id))

        # Insert Customers (do not touch customer_id=0)
        customers_list = [
            ("Alice Brown", "alice.brown@email.com", "12 Oak St, Anytown"),
            ("Bob Green", "bob.green@email.com", "34 Pine Ave, Springfield"),
            ("Carol White", "carol.white@email.com", "56 Maple Dr, Riverdale"),
            ("David Black", "david.black@email.com", "78 Cedar Ln, Hillside"),
            ("Eve Red", "eve.red@email.com", "90 Birch Rd, Valleyview")
        ]
        for name, contact_info, address in customers_list:
            sql = "INSERT INTO Customers (name, contact_info, address) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, contact_info, address))

        # Insert Purchases and PurchaseItems
        for supplier_id in supplier_ids:
            sql = "INSERT INTO Purchases (supplier_id, purchase_datetime, delivery_status) VALUES (%s, %s, %s)"
            cursor.execute(sql, (supplier_id, datetime.now(), "received"))
            purchase_id = cursor.lastrowid
            cursor.execute("SELECT SKU FROM Products")
            products_skus = [row[0] for row in cursor.fetchall()]
            for _ in range(2):
                sku = products_skus[_ % len(products_skus)]
                quantity = 10
                cursor.execute("SELECT price FROM Products WHERE SKU = %s", (sku,))
                unit_cost = cursor.fetchone()[0]
                sql = "INSERT INTO PurchaseItems (purchase_id, SKU, quantity, unit_cost) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (purchase_id, sku, quantity, unit_cost))

        # Insert Inventory Adjustments
        cursor.execute("SELECT SKU FROM Products")
        products_skus = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT employee_id FROM Employees")
        employee_ids = [row[0] for row in cursor.fetchall()]
        for _ in range(5):
            sku = products_skus[_ % len(products_skus)]
            quantity_change = 5
            employee_id = employee_ids[_ % len(employee_ids)]
            sql = "INSERT INTO InventoryAdjustments (SKU, adjustment_datetime, quantity_change, reason, employee_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (sku, datetime.now(), quantity_change, "Sample adjustment", employee_id))

        mydb.commit()
        print("Sample data inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if mydb.is_connected():
            cursor.close()
            mydb.close()