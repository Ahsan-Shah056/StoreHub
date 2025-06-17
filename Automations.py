import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
import tempfile

# Try to import PDF generation libraries
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib.colors import HexColor
    PDF_AVAILABLE = True
except ImportError:
    print("PDF libraries not available. Install with: pip install reportlab")
    PDF_AVAILABLE = False

# Note: Low stock threshold is now read from the Products table (low_stock_threshold column)
# instead of being hardcoded

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
Threshold: {product['low_stock_threshold']} units

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
        # Get the current stock and threshold of the updated product
        cursor.execute("SELECT SKU, name, stock, low_stock_threshold FROM Products WHERE SKU = %s", (updated_sku,))
        result = cursor.fetchone()
        
        if result and result['stock'] <= result['low_stock_threshold']:
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
        
        # 4. Low Stock Items (using individual product thresholds)
        cursor.execute("""
            SELECT SKU, name, stock, low_stock_threshold 
            FROM Products 
            WHERE stock <= low_stock_threshold
            ORDER BY stock ASC
        """)
        
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
    """Send enhanced end-of-day report email with PDF attachment"""
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
        
        # Create PDF report
        pdf_filename = None
        if PDF_AVAILABLE:
            try:
                # Create temporary PDF file
                temp_dir = tempfile.gettempdir()
                pdf_filename = os.path.join(temp_dir, f"Storecore_Daily_Report_{datetime.now().strftime('%Y%m%d')}.pdf")
                created_pdf = create_pdf_report(report_data, pdf_filename)
                if created_pdf:
                    print(f"PDF report created: {pdf_filename}")
                else:
                    pdf_filename = None
            except Exception as e:
                print(f"Failed to create PDF report: {e}")
                pdf_filename = None
        
        # Calculate performance changes for email summary
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
        
        # Enhanced subject line with key metrics
        if revenue_change >= 0:
            trend_emoji = "📈" if revenue_change_pct > 5 else "📊"
        else:
            trend_emoji = "📉"
        
        msg['Subject'] = f"{trend_emoji} Daily Report - {datetime.now().strftime('%Y-%m-%d')} | Revenue: ${today_revenue:,.0f} ({revenue_change_pct:+.1f}%)"
        
        # Create executive summary for email body
        email_body = f"""
{trend_emoji} DAILY BUSINESS REPORT - EXECUTIVE SUMMARY
{'=' * 60}
Date: {datetime.now().strftime('%A, %B %d, %Y')}

� KEY PERFORMANCE INDICATORS
{'─' * 40}
💰 Revenue Today: ${today_revenue:,.2f} ({revenue_change_pct:+.1f}% vs yesterday)
🛒 Transactions: {today_transactions:,} ({transaction_change:+,} vs yesterday)
💵 Average Sale: ${report_data['today_sales']['avg_transaction']:,.2f}
🎯 Largest Sale: ${report_data['today_sales']['max_transaction']:,.2f}

"""
        
        # Add top highlights
        if report_data['top_products']:
            top_product = report_data['top_products'][0]
            email_body += f"🏆 Best Seller: {top_product['name']} ({top_product['total_sold']} units, ${top_product['total_revenue']:,.2f})\n"
        
        if report_data['employees']:
            top_employee = max(report_data['employees'], key=lambda x: x.get('revenue', 0))
            email_body += f"⭐ Top Performer: {top_employee['name']} (${top_employee['revenue']:,.2f} in sales)\n"
        
        # Add alerts
        low_stock_count = len(report_data.get('low_stock', []))
        if low_stock_count > 0:
            email_body += f"⚠️  Inventory Alert: {low_stock_count} products need restocking\n"
        else:
            email_body += f"✅ Inventory: All products adequately stocked\n"
        
        adjustment_count = len(report_data.get('adjustments', []))
        if adjustment_count > 0:
            email_body += f"🔄 Inventory Adjustments: {adjustment_count} made today\n"
        
        # PDF attachment notice
        if pdf_filename and os.path.exists(pdf_filename):
            email_body += f"""
{'─' * 40}
📎 DETAILED REPORT
A comprehensive PDF report with detailed analytics, charts, and 
tables has been attached to this email for your review.

The PDF includes:
• Complete sales analysis and comparisons
• Top products performance ranking
• Employee performance breakdown  
• Inventory status and low stock alerts
• All inventory adjustments made today
• Professional charts and visualizations
"""
        else:
            email_body += f"\n{'─' * 40}\n⚠️  PDF report could not be generated. Please check system logs.\n"
        
        # Quick action items
        action_items = []
        if low_stock_count > 5:
            action_items.append(f"• Review and reorder {low_stock_count} low-stock items")
        if revenue_change_pct < -10:
            action_items.append("• Investigate significant revenue decline")
        if today_transactions < 10:
            action_items.append("• Low transaction volume - review marketing efforts")
        
        if action_items:
            email_body += f"\n🎯 RECOMMENDED ACTIONS\n{'─' * 40}\n"
            email_body += "\n".join(action_items)
        
        email_body += f"""

{'=' * 60}
Report generated automatically by Storecore POS System
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Have a great evening!
Storecore Management System
"""
        
        # Attach text body
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Attach PDF if created successfully
        if pdf_filename and os.path.exists(pdf_filename):
            try:
                with open(pdf_filename, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(pdf_filename)}'
                )
                msg.attach(part)
                print("PDF attachment added to email")
            except Exception as e:
                print(f"Failed to attach PDF: {e}")
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_config['email'], email_config['password'])
            server.sendmail(email_config['email'], [manager_email], msg.as_string())
        
        # Clean up temporary PDF file
        if pdf_filename and os.path.exists(pdf_filename):
            try:
                os.remove(pdf_filename)
                print("Temporary PDF file cleaned up")
            except:
                pass  # Don't fail if cleanup doesn't work
            
        print(f"Enhanced end-of-day report sent to {manager_email}")
        if pdf_filename:
            print("✅ Report included professional PDF attachment")
        return True
        
    except Exception as e:
        print(f"Error sending end-of-day report: {e}")
        return False

def create_pdf_report(report_data, filename):
    """Create a professional PDF report"""
    if not PDF_AVAILABLE:
        print("PDF libraries not available - using text report instead")
        return None
    
    try:
        # Create document
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2E86AB'),
            borderWidth=1,
            borderColor=colors.HexColor('#2E86AB'),
            borderPadding=5
        )
        
        # Header
        today = datetime.now()
        story.append(Paragraph("📊 STORECORE DAILY BUSINESS REPORT", title_style))
        story.append(Paragraph(f"Report Date: {today.strftime('%A, %B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Generated: {today.strftime('%H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2E86AB')))
        story.append(Spacer(1, 20))
        
        # Executive Summary Box
        exec_summary_style = ParagraphStyle(
            'ExecSummary',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=colors.HexColor('#2E86AB'),
            borderPadding=15,
            backColor=colors.HexColor('#F0F8FF')
        )
        
        today_sales = report_data.get('today_sales', {})
        yesterday_sales = report_data.get('yesterday_sales', {})
        revenue_change = today_sales.get('revenue', 0) - yesterday_sales.get('revenue', 0)
        revenue_change_pct = (revenue_change / yesterday_sales.get('revenue', 1) * 100) if yesterday_sales.get('revenue', 0) > 0 else 0
        
        summary_text = f"""
<b>📋 EXECUTIVE SUMMARY</b><br/>
<br/>
💰 Today's Revenue: <b>${today_sales.get('revenue', 0):,.2f}</b> ({revenue_change_pct:+.1f}% vs yesterday)<br/>
🛒 Total Transactions: <b>{today_sales.get('transactions', 0):,}</b><br/>
💵 Average Transaction: <b>${today_sales.get('avg_transaction', 0):,.2f}</b><br/>
"""
        
        if report_data.get('top_products'):
            top_product = report_data['top_products'][0]
            summary_text += f"🏆 Top Product: <b>{top_product['name']}</b> ({top_product['total_sold']} units)<br/>"
        
        low_stock_count = len(report_data.get('low_stock', []))
        if low_stock_count > 0:
            summary_text += f"⚠️ Stock Alerts: <b>{low_stock_count} items</b> need restocking<br/>"
        else:
            summary_text += f"✅ Inventory Status: <b>All products adequately stocked</b><br/>"
        
        story.append(Paragraph(summary_text, exec_summary_style))
        story.append(Spacer(1, 20))
        
        # Sales Summary Section
        story.append(Paragraph("📈 TODAY'S SALES PERFORMANCE", section_style))
        
        today_sales = report_data.get('today_sales', {})
        yesterday_sales = report_data.get('yesterday_sales', {})
        
        # Calculate changes
        revenue_change = today_sales.get('revenue', 0) - yesterday_sales.get('revenue', 0)
        revenue_change_pct = (revenue_change / yesterday_sales.get('revenue', 1) * 100) if yesterday_sales.get('revenue', 0) > 0 else 0
        transaction_change = today_sales.get('transactions', 0) - yesterday_sales.get('transactions', 0)
        
        sales_data = [
            ['Metric', 'Today', 'Yesterday', 'Change'],
            ['Total Transactions', f"{today_sales.get('transactions', 0):,}", 
             f"{yesterday_sales.get('transactions', 0):,}", f"{transaction_change:+,}"],
            ['Total Revenue', f"${today_sales.get('revenue', 0):,.2f}", 
             f"${yesterday_sales.get('revenue', 0):,.2f}", f"${revenue_change:+,.2f} ({revenue_change_pct:+.1f}%)"],
            ['Average Transaction', f"${today_sales.get('avg_transaction', 0):,.2f}", 
             f"${yesterday_sales.get('avg_transaction', 0):,.2f}", ""],
            ['Largest Sale', f"${today_sales.get('max_transaction', 0):,.2f}", "", ""],
            ['Smallest Sale', f"${today_sales.get('min_transaction', 0):,.2f}", "", ""]
        ]
        
        sales_table = Table(sales_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.8*inch])
        sales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(sales_table)
        story.append(Spacer(1, 20))
        
        # Add a simple performance chart
        if today_sales.get('revenue', 0) > 0 or yesterday_sales.get('revenue', 0) > 0:
            story.append(Paragraph("📈 REVENUE COMPARISON CHART", section_style))
            
            # Create a simple bar chart using table formatting
            max_revenue = max(today_sales.get('revenue', 0), yesterday_sales.get('revenue', 0))
            if max_revenue > 0:
                today_bar_width = (today_sales.get('revenue', 0) / max_revenue) * 4  # Max 4 inches
                yesterday_bar_width = (yesterday_sales.get('revenue', 0) / max_revenue) * 4
                
                chart_data = [
                    ['Period', 'Revenue', 'Visual Comparison'],
                    ['Today', f"${today_sales.get('revenue', 0):,.2f}", '█' * int(today_bar_width * 10)],
                    ['Yesterday', f"${yesterday_sales.get('revenue', 0):,.2f}", '█' * int(yesterday_bar_width * 10)]
                ]
                
                chart_table = Table(chart_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
                chart_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (1, -1), 'Helvetica'),
                    ('FONTNAME', (2, 1), (2, -1), 'Courier'),  # Monospace for bars
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                ]))
                
                story.append(chart_table)
                story.append(Spacer(1, 20))
        
        # Top Products Section
        story.append(Paragraph("🏆 TOP SELLING PRODUCTS", section_style))
        
        top_products = report_data.get('top_products', [])
        if top_products:
            products_data = [['Rank', 'Product Name', 'SKU', 'Units Sold', 'Revenue']]
            for i, product in enumerate(top_products[:10], 1):
                products_data.append([
                    str(i),
                    product.get('name', 'N/A')[:30],  # Truncate long names
                    product.get('SKU', 'N/A'),
                    f"{product.get('total_sold', 0):,}",
                    f"${product.get('total_revenue', 0):,.2f}"
                ])
            
            products_table = Table(products_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1*inch, 1.2*inch])
            products_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F18F01')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF8E1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(products_table)
        else:
            story.append(Paragraph("No sales recorded today.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Employee Performance Section
        story.append(Paragraph("👥 EMPLOYEE PERFORMANCE", section_style))
        
        employees = report_data.get('employees', [])
        if employees:
            emp_data = [['Employee Name', 'Transactions', 'Total Revenue', 'Avg per Sale']]
            for emp in employees:
                avg_sale = emp.get('revenue', 0) / emp.get('transactions', 1) if emp.get('transactions', 0) > 0 else 0
                emp_data.append([
                    emp.get('name', 'N/A'),
                    f"{emp.get('transactions', 0):,}",
                    f"${emp.get('revenue', 0):,.2f}",
                    f"${avg_sale:.2f}"
                ])
            
            emp_table = Table(emp_data, colWidths=[2*inch, 1.2*inch, 1.5*inch, 1.2*inch])
            emp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3E5F5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(emp_table)
        else:
            story.append(Paragraph("No employee sales recorded today.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Inventory Status Section
        story.append(Paragraph("📦 INVENTORY STATUS & ALERTS", section_style))
        
        low_stock = report_data.get('low_stock', [])
        if low_stock:
            story.append(Paragraph(f"⚠️ {len(low_stock)} items are running low on stock:", styles['Normal']))
            story.append(Spacer(1, 10))
            
            stock_data = [['Product Name', 'SKU', 'Current Stock', 'Status']]
            for item in low_stock[:15]:  # Show top 15
                # Dynamic status based on how far below threshold the item is
                threshold = item.get('low_stock_threshold', 5)
                current_stock = item.get('stock', 0)
                percentage_of_threshold = (current_stock / threshold * 100) if threshold > 0 else 0
                
                if percentage_of_threshold <= 50:  # Less than 50% of threshold
                    status = "🔴 Critical"
                elif percentage_of_threshold <= 100:  # Below threshold but above 50%
                    status = "🟡 Low"
                else:
                    status = "🟢 OK"  # This shouldn't happen in low stock report, but just in case
                
                stock_data.append([
                    item.get('name', 'N/A')[:25],
                    item.get('SKU', 'N/A'),
                    f"{current_stock} units (threshold: {threshold})",
                    status
                ])
            
            stock_table = Table(stock_data, colWidths=[2.2*inch, 1*inch, 1.2*inch, 1.5*inch])
            stock_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C73E1D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFEBEE')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(stock_table)
            
            if len(low_stock) > 15:
                story.append(Spacer(1, 5))
                story.append(Paragraph(f"... and {len(low_stock) - 15} more items need attention.", styles['Italic']))
        else:
            story.append(Paragraph("✅ All products are adequately stocked.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Inventory Adjustments Section
        story.append(Paragraph("🔄 INVENTORY ADJUSTMENTS", section_style))
        
        adjustments = report_data.get('adjustments', [])
        if adjustments:
            adj_data = [['Product', 'SKU', 'Change', 'Reason', 'Employee', 'Time']]
            for adj in adjustments[:10]:  # Show recent 10
                change_text = f"+{adj.get('quantity_change', 0)}" if adj.get('quantity_change', 0) > 0 else str(adj.get('quantity_change', 0))
                adj_data.append([
                    adj.get('name', 'N/A')[:20],
                    adj.get('SKU', 'N/A'),
                    change_text,
                    adj.get('reason', 'N/A')[:15],
                    adj.get('employee_name', 'N/A'),
                    adj.get('adjustment_time', 'N/A')
                ])
            
            adj_table = Table(adj_data, colWidths=[1.5*inch, 0.8*inch, 0.7*inch, 1.2*inch, 1*inch, 0.8*inch])
            adj_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3D5A80')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8F4FD')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
            ]))
            story.append(adj_table)
        else:
            story.append(Paragraph("No inventory adjustments were made today.", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
        story.append(Spacer(1, 10))
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.gray
        )
        
        story.append(Paragraph("Report generated automatically by Storecore POS System", footer_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}", footer_style))
        story.append(Paragraph("For questions about this report, please contact your system administrator.", footer_style))
        
        # Build PDF
        doc.build(story)
        return filename
        
    except Exception as e:
        print(f"Error creating PDF report: {e}")
        return None
