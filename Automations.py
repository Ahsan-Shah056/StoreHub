import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
import tempfile
import sys

# Import climate data functionality
climate_tab_path = os.path.join(os.path.dirname(__file__), 'Climate Tab')
sys.path.append(climate_tab_path)
try:
    from climate_data import ClimateDataManager
    CLIMATE_AVAILABLE = True
except ImportError:
    print("Climate data module not available")
    CLIMATE_AVAILABLE = False

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
LARGE_TRANSACTION_THRESHOLD = 4000

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

DigiClimate Store Hub Security System
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
        
        # 7. Climate Alerts and Raw Materials Status
        if CLIMATE_AVAILABLE:
            try:
                climate_manager = ClimateDataManager()
                climate_alerts = climate_manager.get_climate_alerts()
                
                # Organize alerts by type for better reporting
                current_alerts = []
                predictive_alerts = []
                stock_alerts = []
                
                for alert in climate_alerts:
                    alert_type = alert.get('alert_type', '')
                    if 'STOCK' in alert_type.upper() or 'DEPLETION' in alert_type.upper():
                        stock_alerts.append(alert)
                    elif 'CURRENT' in alert_type.upper() or alert.get('days_until_impact', 99) == 0:
                        current_alerts.append(alert)
                    else:
                        predictive_alerts.append(alert)
                
                report_data['climate_alerts'] = {
                    'current': current_alerts,
                    'predictive': predictive_alerts,
                    'stock': stock_alerts,
                    'total_count': len(climate_alerts)
                }
                
                # Get raw materials status summary
                materials_status = {}
                material_mapping = {1: "wheat", 2: "sugarcane", 3: "cotton", 4: "rice"}
                for material_id, material_name in material_mapping.items():
                    try:
                        status = climate_manager.get_material_status(material_id)
                        materials_status[material_name] = status
                    except Exception as e:
                        print(f"Error getting status for {material_name}: {e}")
                        materials_status[material_name] = None
                
                report_data['materials_status'] = materials_status
                
            except Exception as e:
                print(f"Error getting climate data for report: {e}")
                report_data['climate_alerts'] = {'current': [], 'predictive': [], 'stock': [], 'total_count': 0}
                report_data['materials_status'] = {}
        else:
            report_data['climate_alerts'] = {'current': [], 'predictive': [], 'stock': [], 'total_count': 0}
            report_data['materials_status'] = {}
        
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
                pdf_filename = os.path.join(temp_dir, f"DigiClimate_Store_Hub_Daily_Report_{datetime.now().strftime('%Y%m%d')}.pdf")
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
        email_body = f"""📊 DIGICLIMATE STORE HUB - DAILY EXECUTIVE SUMMARY
{'=' * 70}
Date: {datetime.now().strftime('%A, %B %d, %Y')}
Generated: {datetime.now().strftime('%H:%M:%S')}

🎯 BUSINESS PERFORMANCE OVERVIEW
{'─' * 50}
💰 Revenue Performance:
   • Today: ${today_revenue:,.2f} ({revenue_change_pct:+.1f}% vs yesterday)
   • Transactions: {today_transactions:,} ({transaction_change:+,} vs yesterday)  
   • Average Sale: ${report_data['today_sales']['avg_transaction']:,.2f}
   • Peak Sale: ${report_data['today_sales']['max_transaction']:,.2f}

"""
        
        # Add top highlights
        email_body += f"🏆 TOP PERFORMERS\n{'─' * 30}\n"
        if report_data['top_products']:
            top_product = report_data['top_products'][0]
            email_body += f"📦 Best Seller: {top_product['name']} ({top_product['total_sold']} units, ${top_product['total_revenue']:,.2f})\n"
        
        if report_data['employees']:
            top_employee = max(report_data['employees'], key=lambda x: x.get('revenue', 0))
            email_body += f"⭐ Top Staff: {top_employee['name']} (${top_employee['revenue']:,.2f} in sales)\n"
        
        email_body += f"\n🚨 CRITICAL ALERTS & STATUS\n{'─' * 40}\n"
        
        # Add inventory alerts first
        low_stock_count = len(report_data.get('low_stock', []))
        if low_stock_count > 0:
            email_body += f"📦 Inventory: {low_stock_count} products need restocking\n"
        else:
            email_body += f"✅ Inventory: All products adequately stocked\n"
        
        # Add detailed climate alerts with actual data
        climate_alerts = report_data.get('climate_alerts', {})
        total_climate_alerts = climate_alerts.get('total_count', 0)
        
        if total_climate_alerts > 0:
            current_alerts = climate_alerts.get('current', [])
            predictive_alerts = climate_alerts.get('predictive', [])
            stock_alerts = climate_alerts.get('stock', [])
            
            # Count high severity alerts
            high_severity_count = 0
            critical_materials = []
            
            for alert in (current_alerts + predictive_alerts + stock_alerts):
                severity = alert.get('severity', '').upper()
                if severity in ['HIGH', 'CRITICAL']:
                    high_severity_count += 1
                    material = alert.get('material_name', 'Unknown')
                    if material not in critical_materials:
                        critical_materials.append(material)
            
            email_body += f"🌡️ Climate & Supply Chain: {total_climate_alerts} alerts detected\n"
            if high_severity_count > 0:
                email_body += f"   ⚠️  HIGH PRIORITY: {high_severity_count} critical issues\n"
                email_body += f"   🏭 Affected Materials: {', '.join(critical_materials[:3])}"
                if len(critical_materials) > 3:
                    email_body += f" +{len(critical_materials)-3} more"
                email_body += f"\n"
            
            # Show most critical current alert
            if current_alerts:
                critical_current = [a for a in current_alerts if a.get('severity', '').upper() == 'CRITICAL']
                if critical_current:
                    alert = critical_current[0]
                    delay_val = alert.get('delay_percent', 0)
                    try:
                        delay_num = float(delay_val) if delay_val is not None else 0.0
                        email_body += f"   🔴 URGENT: {alert.get('material_name', 'Unknown')} - {delay_num:.1f}% delays\n"
                    except (ValueError, TypeError):
                        email_body += f"   🔴 URGENT: {alert.get('material_name', 'Unknown')} - experiencing delays\n"
            
            # Show most critical predictive alert
            if predictive_alerts:
                high_risk = [a for a in predictive_alerts if a.get('severity', '').upper() == 'HIGH']
                if high_risk:
                    alert = high_risk[0]
                    days = alert.get('days_until_impact', 0)
                    products = alert.get('affected_products_count', 0)
                    email_body += f"   ⏰ UPCOMING: {alert.get('material_name', 'Unknown')} risk in {days} days ({products} products affected)\n"
            
        else:
            email_body += f"🌱 Climate & Supply Chain: All systems normal\n"
        
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
        
        # Add comprehensive climate alerts section
        climate_alerts = report_data.get('climate_alerts', {})
        total_climate_alerts = climate_alerts.get('total_count', 0)
        
        if total_climate_alerts > 0:
            email_body += f"\n{'─' * 70}\n🌡️ CLIMATE & SUPPLY CHAIN DETAILED ANALYSIS\n{'─' * 70}\n"
            
            current_alerts = climate_alerts.get('current', [])
            predictive_alerts = climate_alerts.get('predictive', [])
            stock_alerts = climate_alerts.get('stock', [])
            
            # Current Critical Issues
            if current_alerts:
                email_body += f"\n⚠️ IMMEDIATE ATTENTION REQUIRED ({len(current_alerts)} alerts):\n"
                for i, alert in enumerate(current_alerts[:3], 1):
                    severity = alert.get('severity', 'UNKNOWN').upper()
                    material = alert.get('material_name', 'Unknown Material')
                    delay = alert.get('delay_percent', 0)
                    
                    # Convert delay to float to prevent format errors
                    try:
                        delay_num = float(delay) if delay is not None else 0.0
                    except (ValueError, TypeError):
                        delay_num = 0.0
                    
                    severity_icon = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟠"
                    
                    email_body += f"   {i}. {severity_icon} {material.upper()}\n"
                    email_body += f"      • Status: {severity} - {delay_num:.1f}% supply delays\n"
                    email_body += f"      • Action: {alert.get('recommendation', 'Review supply chain immediately')}\n\n"
                
                if len(current_alerts) > 3:
                    email_body += f"   ... plus {len(current_alerts) - 3} additional current alerts (see PDF)\n\n"
            
            # Predictive Risk Analysis  
            if predictive_alerts:
                email_body += f"🔮 PREDICTIVE RISK ANALYSIS ({len(predictive_alerts)} upcoming risks):\n"
                
                # Group by urgency
                high_risk = [a for a in predictive_alerts if a.get('severity', '').upper() == 'HIGH']
                medium_risk = [a for a in predictive_alerts if a.get('severity', '').upper() == 'MEDIUM']
                
                if high_risk:
                    email_body += f"\n   🟠 HIGH RISK PREDICTIONS:\n"
                    for alert in high_risk[:2]:  # Show top 2 high risk
                        material = alert.get('material_name', 'Unknown')
                        days = alert.get('days_until_impact', 0)
                        products = alert.get('affected_products_count', 0)
                        risk_days = alert.get('risk_days_count', 0)
                        avg_delay = alert.get('avg_delay', 0)
                        
                        # Convert avg_delay to float to prevent format errors
                        try:
                            avg_delay_num = float(avg_delay) if avg_delay is not None else 0.0
                        except (ValueError, TypeError):
                            avg_delay_num = 0.0
                        
                        email_body += f"      • {material}: Risk starts in {days} days\n"
                        email_body += f"        - {risk_days} problematic days expected\n"
                        email_body += f"        - {products} products at risk\n"
                        email_body += f"        - Average delays: {avg_delay_num:.1f}%\n"
                        email_body += f"        - Action: {alert.get('recommendation', 'Prepare contingency plans')}\n\n"
                
                if medium_risk:
                    medium_materials = [a.get('material_name', 'Unknown') for a in medium_risk]
                    email_body += f"   🟡 MEDIUM RISK: {len(medium_risk)} materials ({', '.join(medium_materials[:3])})\n\n"
            
            # Stock Depletion Warnings
            if stock_alerts:
                email_body += f"📦 STOCK DEPLETION WARNINGS ({len(stock_alerts)} alerts):\n"
                for alert in stock_alerts[:3]:
                    material = alert.get('material_name', 'Unknown')
                    # Extract days from message if available
                    message = alert.get('message', '')
                    email_body += f"   • {material}: {message}\n"
                    email_body += f"     Action: {alert.get('recommendation', 'Order immediately')}\n\n"
            
            # Summary and next steps
            total_materials_affected = len(set([
                alert.get('material_name', '') for alert in 
                current_alerts + predictive_alerts + stock_alerts
            ]))
            
            email_body += f"🟠 IMPACT SUMMARY:\n"
            email_body += f"   • {total_materials_affected} different raw materials affected\n"
            email_body += f"   • {len(current_alerts)} requiring immediate action\n"
            email_body += f"   • {len(predictive_alerts)} future risks to monitor\n"
            email_body += f"   • Detailed analysis and charts available in PDF attachment\n"
            
        else:
            email_body += f"\n{'─' * 70}\n🌱 CLIMATE & SUPPLY CHAIN STATUS: ALL CLEAR\n{'─' * 70}\n"
            email_body += f"✅ No climate alerts detected for any raw materials\n"
            email_body += f"✅ All supply chains operating normally\n"
            email_body += f"✅ No predictive risks identified\n"
        
        # Enhanced action items with specific climate recommendations
        action_items = []
        
        # Business performance actions
        if low_stock_count > 5:
            action_items.append(f"📦 INVENTORY: Review and reorder {low_stock_count} low-stock products")
        if revenue_change_pct < -10:
            action_items.append(f"📉 REVENUE: Investigate {revenue_change_pct:.1f}% revenue decline - implement recovery strategy")
        if today_transactions < 10:
            action_items.append("📱 MARKETING: Low transaction volume - boost promotional activities")
        
        # Climate-specific action items with priority levels
        climate_alerts = report_data.get('climate_alerts', {})
        current_alerts = climate_alerts.get('current', [])
        predictive_alerts = climate_alerts.get('predictive', [])
        stock_alerts = climate_alerts.get('stock', [])
        
        # Critical immediate actions
        critical_current = [a for a in current_alerts if a.get('severity', '').upper() == 'CRITICAL']
        if critical_current:
            materials = [a.get('material_name', 'Unknown') for a in critical_current]
            action_items.append(f"🚨 URGENT: Address critical supply issues for {', '.join(materials[:2])}")
        
        # High priority actions
        high_priority_current = [a for a in current_alerts if a.get('severity', '').upper() == 'HIGH']
        if high_priority_current:
            # Convert all delay values to float and calculate average
            delay_values = []
            for a in high_priority_current:
                try:
                    delay_val = float(a.get('delay_percent', 0))
                    delay_values.append(delay_val)
                except (ValueError, TypeError):
                    delay_values.append(0.0)
            
            avg_delay = sum(delay_values) / len(delay_values) if delay_values else 0.0
            action_items.append(f"⚠️  HIGH PRIORITY: Resolve {len(high_priority_current)} supply chain issues (avg {avg_delay:.1f}% delays)")
        
        # Predictive planning actions
        high_risk_predictive = [a for a in predictive_alerts if a.get('severity', '').upper() == 'HIGH']
        if high_risk_predictive:
            nearest_risk = min([a.get('days_until_impact', 999) for a in high_risk_predictive])
            total_products = sum([a.get('affected_products_count', 0) for a in high_risk_predictive])
            action_items.append(f"🔮 PLANNING: Prepare for supply risks starting in {nearest_risk} days ({total_products} products at risk)")
        
        # Stock management actions
        if stock_alerts:
            action_items.append(f"📦 PROCUREMENT: Urgent restocking needed for {len(stock_alerts)} raw materials")
        
        # Long-term strategic actions
        if len(predictive_alerts) > 2:
            affected_materials = len(set([a.get('material_name', '') for a in predictive_alerts]))
            action_items.append(f"🏭 STRATEGY: Diversify suppliers for {affected_materials} materials to reduce future risks")
        
        if action_items:
            email_body += f"\n{'─' * 70}\n🎯 PRIORITY ACTION ITEMS\n{'─' * 70}\n"
            for i, item in enumerate(action_items, 1):
                email_body += f"{i}. {item}\n"
        
        email_body += f"""

{'=' * 60}
Report generated automatically by DigiClimate Store Hub POS System
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Have a great evening!
DigiClimate Store Hub Management System
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
        story.append(Paragraph("📊 DIGICLIMATE STORE HUB DAILY BUSINESS REPORT", title_style))
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
        
        # Add climate alerts to summary
        climate_alerts = report_data.get('climate_alerts', {})
        total_climate_alerts = climate_alerts.get('total_count', 0)
        if total_climate_alerts > 0:
            current_count = len(climate_alerts.get('current', []))
            stock_count = len(climate_alerts.get('stock', []))
            predictive_count = len(climate_alerts.get('predictive', []))
            
            if current_count > 0:
                summary_text += f"🌡️ Climate Alerts: <b>{current_count} active</b> weather/supply issues<br/>"
            if stock_count > 0:
                summary_text += f"📦 Stock Depletion: <b>{stock_count} materials</b> running low<br/>"
            if predictive_count > 0:
                summary_text += f"🔮 Predictive Risks: <b>{predictive_count} potential</b> future issues<br/>"
        else:
            summary_text += f"🌱 Climate Status: <b>No active alerts</b> for raw materials<br/>"
        
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
        
        story.append(Spacer(1, 20))
        
        # Climate Alerts and Raw Materials Section
        story.append(Paragraph("🌡️ CLIMATE & RAW MATERIALS STATUS", section_style))
        
        climate_alerts = report_data.get('climate_alerts', {})
        materials_status = report_data.get('materials_status', {})
        total_climate_alerts = climate_alerts.get('total_count', 0)
        
        if total_climate_alerts > 0:
            # Current alerts
            current_alerts = climate_alerts.get('current', [])
            if current_alerts:
                story.append(Paragraph("⚠️ ACTIVE CLIMATE ALERTS", ParagraphStyle(
                    'SubSection',
                    parent=styles['Heading3'],
                    fontSize=12,
                    spaceAfter=8,
                    textColor=colors.red
                )))
                
                current_data = [['Material', 'Severity', 'Issue Description', 'Action Required']]
                for alert in current_alerts:
                    # Use correct field names from climate data
                    material = alert.get('material_name', 'Unknown')
                    severity = alert.get('severity', 'Unknown')
                    message = alert.get('message', 'No description available')
                    recommendation = alert.get('recommendation', 'No recommendation available')
                    
                    # More aggressive text truncation for narrow columns
                    material_short = material.title()[:12] + '..' if len(material) > 12 else material.title()
                    severity_short = severity.title()[:8] if len(severity) <= 8 else severity.title()[:7] + '.'
                    desc_text = message[:25] + '...' if len(message) > 25 else message
                    rec_text = recommendation[:30] + '...' if len(recommendation) > 30 else recommendation
                    
                    current_data.append([
                        material_short,
                        severity_short,
                        desc_text,
                        rec_text
                    ])
                
                current_table = Table(current_data, colWidths=[1*inch, 0.8*inch, 2*inch, 2.2*inch])
                current_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF5F5')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFF5F5'), colors.HexColor('#FFEBEE')]),
                ]))
                story.append(current_table)
                story.append(Spacer(1, 10))
            
            # Stock depletion alerts
            stock_alerts = climate_alerts.get('stock', [])
            if stock_alerts:
                story.append(Paragraph("📦 STOCK DEPLETION ALERTS", ParagraphStyle(
                    'SubSection',
                    parent=styles['Heading3'],
                    fontSize=12,
                    spaceAfter=8,
                    textColor=colors.orange
                )))
                
                stock_data = [['Material', 'Days Left', 'Status', 'Action Needed']]
                for alert in stock_alerts:
                    # Use correct field names for stock alerts
                    material = alert.get('material_name', 'Unknown')
                    message = alert.get('message', '')
                    recommendation = alert.get('recommendation', 'Order immediately')
                    
                    # Extract days from message if available
                    days_remaining = 'Unknown'
                    if 'days' in message.lower():
                        try:
                            # Try to extract number before 'days'
                            words = message.split()
                            for i, word in enumerate(words):
                                if 'day' in word.lower() and i > 0:
                                    days_remaining = words[i-1]
                                    break
                        except:
                            days_remaining = 'Unknown'
                    
                    # Determine status
                    try:
                        days_num = int(days_remaining) if days_remaining.isdigit() else 999
                        status = '🔴 Critical' if days_num < 30 else '🟡 Low'
                    except:
                        status = '⚠️ Unknown'
                    
                    # Better text truncation
                    material_short = material.title()[:15] + '..' if len(material) > 15 else material.title()
                    days_text = f"{days_remaining}d" if days_remaining != 'Unknown' else 'N/A'
                    rec_text = recommendation[:35] + '...' if len(recommendation) > 35 else recommendation
                    
                    stock_data.append([
                        material_short,
                        days_text,
                        status,
                        rec_text
                    ])
                
                stock_table = Table(stock_data, colWidths=[1.2*inch, 0.8*inch, 1*inch, 3*inch])
                stock_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF8E1')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                ]))
                story.append(stock_table)
                story.append(Spacer(1, 10))
            
            # Predictive alerts summary
            predictive_alerts = climate_alerts.get('predictive', [])
            if predictive_alerts:
                story.append(Paragraph("🔮 PREDICTIVE RISK ANALYSIS", ParagraphStyle(
                    'SubSection',
                    parent=styles['Heading3'],
                    fontSize=12,
                    spaceAfter=8,
                    textColor=colors.blue
                )))
                
                # Group predictive alerts by severity (not urgency)
                high_risk = [a for a in predictive_alerts if a.get('severity', '').upper() == 'HIGH']
                medium_risk = [a for a in predictive_alerts if a.get('severity', '').upper() == 'MEDIUM']
                low_risk = [a for a in predictive_alerts if a.get('severity', '').upper() == 'LOW']
                
                # Show detailed predictive alerts table
                pred_data = [['Material', 'Risk Level', 'Days', 'Products', 'Risk Description', 'Action Required']]
                
                # Add high risk alerts first
                for alert in high_risk:
                    material = alert.get('material_name', 'Unknown')
                    severity = alert.get('severity', 'Unknown')
                    days = alert.get('days_until_impact', 'N/A')
                    products = alert.get('affected_products_count', 'N/A')
                    message = alert.get('message', 'No description')
                    recommendation = alert.get('recommendation', 'Monitor closely')
                    
                    # Better text truncation for table readability
                    material_short = material.title()[:10] + '..' if len(material) > 10 else material.title()
                    severity_short = severity.title()[:6] if len(severity) <= 6 else severity.title()[:5] + '.'
                    desc_text = message[:30] + '...' if len(message) > 30 else message
                    rec_text = recommendation[:25] + '...' if len(recommendation) > 25 else recommendation
                    
                    pred_data.append([
                        material_short,
                        severity_short,
                        f"{days}d",
                        str(products),
                        desc_text,
                        rec_text
                    ])
                
                # Add medium and low risk alerts
                for alert in medium_risk + low_risk:
                    material = alert.get('material_name', 'Unknown')
                    severity = alert.get('severity', 'Unknown')
                    days = alert.get('days_until_impact', 'N/A')
                    products = alert.get('affected_products_count', 'N/A')
                    message = alert.get('message', 'No description')
                    recommendation = alert.get('recommendation', 'Monitor closely')
                    
                    # Better text truncation for table readability
                    material_short = material.title()[:10] + '..' if len(material) > 10 else material.title()
                    severity_short = severity.title()[:6] if len(severity) <= 6 else severity.title()[:5] + '.'
                    desc_text = message[:30] + '...' if len(message) > 30 else message
                    rec_text = recommendation[:25] + '...' if len(recommendation) > 25 else recommendation
                    
                    pred_data.append([
                        material_short,
                        severity_short,
                        f"{days}d",
                        str(products),
                        desc_text,
                        rec_text
                    ])
                
                # Create the predictive alerts table with better column widths
                pred_table = Table(pred_data, colWidths=[0.8*inch, 0.6*inch, 0.4*inch, 0.5*inch, 2*inch, 1.7*inch])
                pred_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0F8FF')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F0F8FF'), colors.HexColor('#E6F3FF')]),
                ]))
                story.append(pred_table)
                
                # Add summary paragraph after the table
                pred_summary = f"""
                <b>Summary:</b> {len(high_risk)} high-risk, {len(medium_risk)} medium-risk, and {len(low_risk)} low-risk predictions identified. 
                Priority focus should be on high-risk alerts requiring immediate planning and supplier diversification.
                """
                story.append(Spacer(1, 10))
                story.append(Paragraph(pred_summary, styles['Italic']))
                story.append(Spacer(1, 10))
        
        # Raw materials status summary
        if materials_status:
            story.append(Paragraph("🌱 RAW MATERIALS STATUS OVERVIEW", ParagraphStyle(
                'SubSection',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=8,
                textColor=colors.green
            )))
            
            materials_data = [['Material', 'Current Condition', 'Risk Level', 'Production Impact', 'Delay %']]
            for material, status in materials_status.items():
                if status:
                    # Use actual available fields from climate data
                    condition = status.get('current_condition', 'Unknown')
                    risk_level = status.get('risk_level', 'Unknown')
                    production_impact = status.get('production_impact', 0)
                    delay_percent = status.get('delay_percent', 0)
                    
                    # Format values appropriately
                    condition_text = condition[:25] + '...' if len(condition) > 25 else condition
                    impact_text = f"{production_impact:,.1f} tons" if isinstance(production_impact, (int, float)) else str(production_impact)
                    delay_text = f"{delay_percent:.1f}%" if isinstance(delay_percent, (int, float)) else str(delay_percent)
                    
                    materials_data.append([
                        material.title(),
                        condition_text,
                        risk_level.title(),
                        impact_text,
                        delay_text
                    ])
            
            if len(materials_data) > 1:  # Only create table if we have data
                materials_table = Table(materials_data, colWidths=[1.2*inch, 1.2*inch, 1*inch, 1.2*inch, 1.4*inch])
                materials_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F1F8E9')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                ]))
                story.append(materials_table)
        
        else:
            story.append(Paragraph("✅ No climate alerts detected. All raw materials are in good condition.", styles['Normal']))
        
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
        
        story.append(Paragraph("Report generated automatically by DigiClimate Store Hub POS System", footer_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}", footer_style))
        story.append(Paragraph("For questions about this report, please contact your system administrator.", footer_style))
        
        # Build PDF
        doc.build(story)
        return filename
        
    except Exception as e:
        print(f"Error creating PDF report: {e}")
        return None
