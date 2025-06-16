import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Low stock threshold
LOW_STOCK_THRESHOLD = 25

def get_manager_email():
    """Get the manager's email from credentials.json"""
    try:
        with open('credentials.json', 'r') as file:
            data = json.load(file)
            for user in data.get('users', []):
                if user.get('role') == 'manager':
                    return user.get('email', '')
        return ''
    except Exception as e:
        print(f"Error getting manager email: {e}")
        return ''

def load_email_config():
    """Load email configuration from credentials.json"""
    try:
        with open('credentials.json', 'r') as file:
            data = json.load(file)
            return {
                'email': data.get('email', ''),
                'password': data.get('password', '')
            }
    except Exception as e:
        print(f"Error loading email config: {e}")
        return {'email': '', 'password': ''}

def send_low_stock_alert(cursor, product):
    """Send low stock alert email to manager"""
    try:
        manager_email = get_manager_email()
        if not manager_email:
            print("Manager email not found in credentials.json")
            return
            
        email_config = load_email_config()
        if not email_config['email'] or not email_config['password']:
            print("Email configuration not available for low stock alerts")
            return
            
        # Create email
        msg = MIMEMultipart()
        msg['From'] = email_config['email']
        msg['To'] = manager_email
        msg['Subject'] = f"LOW STOCK ALERT - {product['name']}"
        
        # Email body
        email_body = f"""Dear Manager,

Product {product['name']} (SKU: {product['SKU']}) has fallen below the low stock threshold.

Current Stock: {product['stock']} units
Threshold: {LOW_STOCK_THRESHOLD} units

Please consider restocking this product.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_config['email'], email_config['password'])
            server.sendmail(email_config['email'], [manager_email], msg.as_string())
            
        print(f"Low stock alert sent for {product['name']} (SKU: {product['SKU']}) to {manager_email}")
        
    except Exception as e:
        print(f"Error sending low stock alert: {e}")

def check_and_alert_low_stock(cursor, updated_sku):
    """Check if a specific product is below threshold and send alert if needed"""
    try:
        # Get the current stock of the updated product
        cursor.execute("SELECT SKU, name, stock FROM Products WHERE SKU = %s", (updated_sku,))
        result = cursor.fetchone()
        
        if result and result['stock'] <= LOW_STOCK_THRESHOLD:
            send_low_stock_alert(cursor, result)
            
    except Exception as e:
        print(f"Error checking low stock for SKU {updated_sku}: {e}")

# Large Transaction Alert Automation
LARGE_TRANSACTION_THRESHOLD = 10000.0

def send_large_transaction_alert(cursor, sale_data):
    """Send large transaction alert email to manager"""
    try:
        manager_email = get_manager_email()
        if not manager_email:
            return
            
        email_config = load_email_config()
        if not email_config['email'] or not email_config['password']:
            return
        
        # Get employee and customer names
        employee_name = "Unknown Employee"
        customer_name = "Unknown Customer"
        
        if sale_data.get('employee_id'):
            cursor.execute("SELECT name FROM Employees WHERE employee_id = %s", (sale_data['employee_id'],))
            emp_result = cursor.fetchone()
            if emp_result:
                employee_name = emp_result['name']
        
        if sale_data.get('customer_id'):
            cursor.execute("SELECT name FROM Customers WHERE customer_id = %s", (sale_data['customer_id'],))
            cust_result = cursor.fetchone()
            if cust_result:
                customer_name = cust_result['name']
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = email_config['email']
        msg['To'] = manager_email
        msg['Subject'] = f"LARGE TRANSACTION ALERT - ${sale_data['total']:.2f}"
        
        email_body = f"""Dear Manager,

LARGE TRANSACTION ALERT

A transaction above ${LARGE_TRANSACTION_THRESHOLD:.2f} has been processed:

Sale ID: {sale_data['sale_id']}
Amount: ${sale_data['total']:.2f}
Employee: {employee_name}
Customer: {customer_name}
Date & Time: {sale_data.get('sale_datetime', 'Unknown')}

Please review this transaction.

Storecore Security System
"""
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_config['email'], email_config['password'])
            server.sendmail(email_config['email'], [manager_email], msg.as_string())
            
        print(f"Large transaction alert sent for Sale ID {sale_data['sale_id']} (${sale_data['total']:.2f})")
        
    except Exception as e:
        print(f"Error sending large transaction alert: {e}")

def check_and_alert_large_transaction(cursor, sale_id, total_amount, employee_id, customer_id):
    """Check if transaction is above threshold and send alert if needed"""
    try:
        if total_amount > LARGE_TRANSACTION_THRESHOLD:
            # Get the actual sale datetime from the database
            cursor.execute("SELECT sale_datetime FROM Sales WHERE sale_id = %s", (sale_id,))
            sale_result = cursor.fetchone()
            
            if sale_result:
                sale_datetime = sale_result['sale_datetime'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                sale_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            sale_data = {
                'sale_id': sale_id,
                'total': total_amount,
                'employee_id': employee_id,
                'customer_id': customer_id,
                'sale_datetime': sale_datetime
            }
            send_large_transaction_alert(cursor, sale_data)
    except Exception as e:
        print(f"Error checking large transaction: {e}")

# End-of-Day Report Automation
def generate_end_of_day_report(cursor):
    """Generate comprehensive end-of-day report data"""
    try:
        from datetime import date, timedelta
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        report_data = {}
        
        # 1. Today's Sales Summary
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(total) as total_revenue,
                AVG(total) as avg_transaction,
                MIN(total) as min_transaction,
                MAX(total) as max_transaction
            FROM Sales 
            WHERE DATE(sale_datetime) = %s
        """, (today,))
        
        today_summary = cursor.fetchone()
        if today_summary:
            report_data['today_sales'] = {
                'transactions': today_summary['total_transactions'] or 0,
                'revenue': float(today_summary['total_revenue'] or 0),
                'avg_transaction': float(today_summary['avg_transaction'] or 0),
                'min_transaction': float(today_summary['min_transaction'] or 0),
                'max_transaction': float(today_summary['max_transaction'] or 0)
            }
        else:
            report_data['today_sales'] = {
                'transactions': 0, 'revenue': 0, 'avg_transaction': 0,
                'min_transaction': 0, 'max_transaction': 0
            }
        
        # 2. Yesterday's Sales for Comparison
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(total) as total_revenue
            FROM Sales 
            WHERE DATE(sale_datetime) = %s
        """, (yesterday,))
        
        yesterday_summary = cursor.fetchone()
        if yesterday_summary:
            report_data['yesterday_sales'] = {
                'transactions': yesterday_summary['total_transactions'] or 0,
                'revenue': float(yesterday_summary['total_revenue'] or 0)
            }
        else:
            report_data['yesterday_sales'] = {'transactions': 0, 'revenue': 0}
        
        # 3. Top Selling Products Today
        cursor.execute("""
            SELECT 
                p.name,
                p.SKU,
                SUM(si.quantity) as total_sold,
                SUM(si.quantity * si.price) as total_revenue
            FROM SaleItems si
            JOIN Products p ON si.SKU = p.SKU
            JOIN Sales s ON si.sale_id = s.sale_id
            WHERE DATE(s.sale_datetime) = %s
            GROUP BY p.SKU, p.name
            ORDER BY total_sold DESC
            LIMIT 5
        """, (today,))
        
        top_products = cursor.fetchall()
        report_data['top_products'] = top_products or []
        
        # 4. Low Stock Items
        cursor.execute("""
            SELECT SKU, name, stock 
            FROM Products 
            WHERE stock <= %s
            ORDER BY stock ASC
        """, (LOW_STOCK_THRESHOLD,))
        
        low_stock_items = cursor.fetchall()
        report_data['low_stock'] = low_stock_items or []
        
        # 5. Employee Performance Today
        cursor.execute("""
            SELECT 
                e.name,
                COUNT(s.sale_id) as transactions,
                SUM(s.total) as revenue
            FROM Sales s
            JOIN Employees e ON s.employee_id = e.employee_id
            WHERE DATE(s.sale_datetime) = %s
            GROUP BY e.employee_id, e.name
            ORDER BY revenue DESC
        """, (today,))
        
        employee_performance = cursor.fetchall()
        report_data['employees'] = employee_performance or []
        
        # 6. Inventory Adjustments Today
        cursor.execute("""
            SELECT 
                p.name,
                p.SKU,
                ia.quantity_change,
                ia.reason,
                e.name as employee_name,
                TIME(ia.adjustment_datetime) as adjustment_time
            FROM InventoryAdjustments ia
            JOIN Products p ON ia.SKU = p.SKU
            JOIN Employees e ON ia.employee_id = e.employee_id
            WHERE DATE(ia.adjustment_datetime) = %s
            ORDER BY ia.adjustment_datetime DESC
        """, (today,))
        
        inventory_adjustments = cursor.fetchall()
        report_data['adjustments'] = inventory_adjustments or []
        
        return report_data
        
    except Exception as e:
        print(f"Error generating end-of-day report: {e}")
        return None

def send_end_of_day_report(cursor):
    """Send end-of-day report email to manager"""
    try:
        manager_email = get_manager_email()
        if not manager_email:
            print("Manager email not found - skipping end-of-day report")
            return
            
        email_config = load_email_config()
        if not email_config['email'] or not email_config['password']:
            print("Email configuration not available - skipping end-of-day report")
            return
        
        # Generate report data
        report_data = generate_end_of_day_report(cursor)
        if not report_data:
            print("Failed to generate report data")
            return
        
        # Calculate performance changes
        today_revenue = report_data['today_sales']['revenue']
        yesterday_revenue = report_data['yesterday_sales']['revenue']
        revenue_change = today_revenue - yesterday_revenue
        revenue_change_pct = (revenue_change / yesterday_revenue * 100) if yesterday_revenue > 0 else 0
        
        today_transactions = report_data['today_sales']['transactions']
        yesterday_transactions = report_data['yesterday_sales']['transactions']
        transaction_change = today_transactions - yesterday_transactions
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = email_config['email']
        msg['To'] = manager_email
        msg['Subject'] = f"📊 End-of-Day Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Build email body
        email_body = f"""END-OF-DAY BUSINESS REPORT
{'=' * 50}
Date: {datetime.now().strftime('%A, %B %d, %Y')}

📈 TODAY'S SALES SUMMARY
{'─' * 30}
• Total Transactions: {today_transactions:,}
• Total Revenue: ${today_revenue:,.2f}
• Average Transaction: ${report_data['today_sales']['avg_transaction']:,.2f}
• Largest Sale: ${report_data['today_sales']['max_transaction']:,.2f}
• Smallest Sale: ${report_data['today_sales']['min_transaction']:,.2f}

📊 PERFORMANCE vs YESTERDAY
{'─' * 30}
• Revenue Change: ${revenue_change:+,.2f} ({revenue_change_pct:+.1f}%)
• Transaction Change: {transaction_change:+,} transactions
"""

        # Add top products section
        if report_data['top_products']:
            email_body += f"\n🏆 TOP SELLING PRODUCTS\n{'─' * 30}\n"
            for i, product in enumerate(report_data['top_products'][:5], 1):
                email_body += f"{i}. {product['name']} (SKU: {product['SKU']})\n"
                email_body += f"   Sold: {product['total_sold']} units | Revenue: ${product['total_revenue']:,.2f}\n"
        else:
            email_body += f"\n🏆 TOP SELLING PRODUCTS\n{'─' * 30}\nNo sales recorded today.\n"

        # Add employee performance section
        if report_data['employees']:
            email_body += f"\n👥 EMPLOYEE PERFORMANCE\n{'─' * 30}\n"
            for employee in report_data['employees']:
                email_body += f"• {employee['name']}: {employee['transactions']} sales, ${employee['revenue']:,.2f}\n"
        else:
            email_body += f"\n👥 EMPLOYEE PERFORMANCE\n{'─' * 30}\nNo employee sales recorded today.\n"

        # Add low stock section
        if report_data['low_stock']:
            email_body += f"\n⚠️  LOW STOCK ALERTS ({len(report_data['low_stock'])} items)\n{'─' * 30}\n"
            for item in report_data['low_stock'][:10]:  # Show top 10
                email_body += f"• {item['name']} (SKU: {item['SKU']}): {item['stock']} units\n"
            if len(report_data['low_stock']) > 10:
                email_body += f"... and {len(report_data['low_stock']) - 10} more items\n"
        else:
            email_body += f"\n✅ INVENTORY STATUS\n{'─' * 30}\nAll products are above low stock threshold.\n"

        # Add inventory adjustments section
        if report_data['adjustments']:
            email_body += f"\n📦 INVENTORY ADJUSTMENTS ({len(report_data['adjustments'])} today)\n{'─' * 30}\n"
            for adj in report_data['adjustments']:
                change_type = "+" if adj['quantity_change'] > 0 else ""
                email_body += f"• {adj['name']} (SKU: {adj['SKU']})\n"
                email_body += f"  Change: {change_type}{adj['quantity_change']} units | Reason: {adj['reason']}\n"
                email_body += f"  By: {adj['employee_name']} at {adj['adjustment_time']}\n"
        else:
            email_body += f"\n📦 INVENTORY ADJUSTMENTS\n{'─' * 30}\nNo inventory adjustments made today.\n"

        email_body += f"""
{'=' * 50}
Report generated automatically by Storecore POS System
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Have a great evening!
Storecore Management System
"""
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_config['email'], email_config['password'])
            server.sendmail(email_config['email'], [manager_email], msg.as_string())
            
        print(f"End-of-day report sent to {manager_email}")
        return True
        
    except Exception as e:
        print(f"Error sending end-of-day report: {e}")
        return False
