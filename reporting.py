import database
import datetime

def sales_by_employee(cursor, employee_id):
    # Returns all sales for a selected employee
    try:
        query = """
            SELECT s.sale_id, s.sale_datetime, s.total, s.customer_id, c.name AS customer_name
            FROM Sales s
            JOIN Customers c ON s.customer_id = c.customer_id
            WHERE s.employee_id = %s
            ORDER BY s.sale_datetime DESC
        """
        cursor.execute(query, (employee_id,))
        results = cursor.fetchall()
        return [
            {
                "sale_id": row["sale_id"],
                "sale_datetime": row["sale_datetime"],
                "total": row["total"],
                "customer_id": row["customer_id"],
                "customer_name": row["customer_name"]
            }
            for row in results
        ] if results else []
    except Exception as e:
        raise ValueError(f"Error generating sales by employee report: {e}")

def supplier_purchase_report(cursor, supplier_id):
    # Returns all purchases for a selected supplier
    try:
        query = """
            SELECT p.purchase_id, p.purchase_datetime, pi.SKU, pr.name AS product_name, pi.quantity, pr.price, (pi.quantity * pr.price) AS line_total
            FROM Purchases p
            JOIN PurchaseItems pi ON p.purchase_id = pi.purchase_id
            JOIN Products pr ON pi.SKU = pr.SKU
            WHERE p.supplier_id = %s
            ORDER BY p.purchase_datetime DESC, p.purchase_id DESC
        """
        cursor.execute(query, (supplier_id,))
        results = cursor.fetchall()
        return [
            {
                "purchase_id": row["purchase_id"],
                "purchase_date": row["purchase_datetime"],
                "SKU": row["SKU"],
                "product_name": row["product_name"],
                "quantity": row["quantity"],
                "price": row["price"],
                "line_total": row["line_total"]
            }
            for row in results
        ] if results else []
    except Exception as e:
        raise ValueError(f"Error generating supplier purchase report: {e}")

def inventory_adjustment_history(cursor):
    # Returns all inventory adjustments
    try:
        query = """
            SELECT ia.adjustment_id, ia.adjustment_datetime, ia.SKU, ia.quantity_change, ia.reason, e.name AS employee_name
            FROM InventoryAdjustments ia
            JOIN Employees e ON ia.employee_id = e.employee_id
            ORDER BY ia.adjustment_datetime DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return [
            {
                "adjustment_id": row["adjustment_id"],
                "date": row["adjustment_datetime"],
                "SKU": row["SKU"],
                "quantity_change": row["quantity_change"],
                "employee_name": row["employee_name"],
                "reason": row["reason"]
            }
            for row in results
        ] if results else []
    except Exception as e:
        raise ValueError(f"Error generating inventory adjustment history: {e}")

def customer_purchase_history(cursor, customer_id):
    """
    Returns all purchases for a selected customer.
    Columns: Sale ID, Date/Time, SKU, Product Name, Quantity, Price, Total
    """
    try:
        print(f"Debug: customer_purchase_history called with customer_id: {customer_id}")
        query = '''
            SELECT s.sale_id, s.sale_datetime, si.SKU, p.name AS product_name, si.quantity, si.price, s.total
            FROM Sales s
            JOIN SaleItems si ON s.sale_id = si.sale_id
            JOIN Products p ON si.SKU = p.SKU
            WHERE s.customer_id = %s
            ORDER BY s.sale_datetime DESC, s.sale_id DESC
        '''
        cursor.execute(query, (customer_id,))
        results = cursor.fetchall()
        print(f"Debug: Query returned {len(results) if results else 0} results")
        return [
            {
                "sale_id": row["sale_id"],
                "sale_datetime": row["sale_datetime"],
                "SKU": row["SKU"],
                "product_name": row["product_name"],
                "quantity": row["quantity"],
                "price": row["price"],
                "total": row["total"]
            }
            for row in results
        ] if results else []
    except Exception as e:
        raise ValueError(f"Error generating customer purchase history report: {e}")