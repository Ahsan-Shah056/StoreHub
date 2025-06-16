# Standard library imports
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import smtplib
import subprocess
import sys
from datetime import datetime

# Third-party imports
from PIL import Image, ImageTk
from ttkthemes import ThemedTk

# Email imports
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ReportLab imports for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus import Image as ReportLabImage  # Use alias to avoid conflict with PIL Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Local application imports
from database import get_db, close_db
import suppliers
import inventory
import sales
import customers
import employees
import reporting
from reporting import (
    sales_by_employee,
    supplier_purchase_report,
    inventory_adjustment_history,
    customer_purchase_history
)
from Ui import POSApp, alternate_treeview_rows
from Automations import (
    check_and_alert_low_stock,
    get_manager_email,
    send_low_stock_alert,
    LOW_STOCK_THRESHOLD,
    check_and_alert_large_transaction,
    send_large_transaction_alert,
    send_end_of_day_report
)


def handle_error(error_message):
    # Displays an error message in a message box
    messagebox.showerror("Error", error_message)

# Global variable to store last sale info for resend functionality
last_sale_info = {'sale_id': None, 'customer_id': None, 'receipt_text': None}

def load_email_config():
    # Load email configuration from credentials.json
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

def get_selected_customer_id():
    if 'selected_customer_id' not in get_selected_customer_id.__dict__:
        get_selected_customer_id.selected_customer_id = None
    return get_selected_customer_id.selected_customer_id



def set_selected_customer_id(customer_id):
    # Sets the ID or identifier of the currently selected customer
    get_selected_customer_id.selected_customer_id = customer_id

def _update_cart_display(cart, cart_tree, cursor):
    # Updates the cart display in the UI with the current items in the cart
    try:
        cart_tree.delete(*cart_tree.get_children())
        for item in cart:# for every item in the cart
            product = sales.get_product(cursor, item['SKU'])# gets the product
            if product:
                line_total = product['price'] * item['quantity']
                cart_tree.insert("", "end", values=(
                    item['SKU'], 
                    product['name'], 
                    item['quantity'], 
                    f"${product['price']:.2f}",
                    f"${line_total:.2f}"
                ))
        
        # Apply alternating row colors
        alternate_treeview_rows(cart_tree)
        
        # Update totals if UI elements are available
        try:
            # Try to get the UI reference from the global pos_app
            if 'pos_app' in globals() and hasattr(pos_app, 'sales_ui'):
                if hasattr(pos_app.sales_ui, 'subtotal_label'):
                    update_order_display(cart, cursor, 
                                       pos_app.sales_ui.subtotal_label,
                                       pos_app.sales_ui.taxes_label, 
                                       pos_app.sales_ui.total_label)
        except:
            pass  # Silently fail if UI elements not available
            
    except Exception as e:
        handle_error(f"An error occurred while updating the cart display: {e}")




def _display_product_details(product_listbox, cursor):
    # Display details for selected product
    try:
        selected_index = product_listbox.curselection()        
        if not selected_index:
            messagebox.showwarning("Selection Required", "Please select a product to view details.")
            return

        selected_product = product_listbox.get(selected_index[0])
        sku = selected_product.split(' (')[1][:-1]        
                
        product = sales.get_product(cursor, sku)
        if product:
            details = f"Name: {product['name']}\nCategory: {product['category']}\nPrice: ${product['price']:.2f}\nStock: {product['stock']}"
            messagebox.showinfo("Product Details", details)
    except Exception as e:
        handle_error(f"An error occurred while displaying product details: {e}")

    
# ----- Sales Management -----


def add_to_cart(sku, quantity, cart_tree, cart, cursor):
    # Adds a selected product to the cart with a specified quantity
    try:
        if not sku:
            raise ValueError("Please enter a product SKU.")
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be a positive number.")
        except ValueError:
            handle_error("Invalid quantity entered. Please enter a positive integer.")
            return
        sales.add_to_cart(cart, sku, quantity)
        _update_cart_display(cart, cart_tree, cursor)
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:
        handle_error(f"An error occurred while adding to cart: {e}")
            


def remove_from_cart(remove_from_cart_entry, cart_tree, cart, cursor):
    try:
        sku = remove_from_cart_entry.get()
        if not sku:
            raise ValueError("Please enter the SKU of the item to remove.")
        # use the sales function to remove the item from the cart
        sales.remove_from_cart(cart, sku)
        remove_from_cart_entry.delete(0, tk.END)
        _update_cart_display(cart, cart_tree, cursor)
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:
        handle_error(f"An error occurred while removing item from cart: {e}")

def update_cart_quantity(update_cart_sku_entry, update_cart_quantity_entry, cart_tree, cart, cursor):
    # Updates the quantity of an item in the cart
    try:
        sku = update_cart_sku_entry.get()
        new_quantity = int(update_cart_quantity_entry.get())
        if new_quantity <= 0:
            raise ValueError("Quantity must be a positive number.")
        sales.update_cart_quantity(cart, sku, new_quantity)
        _update_cart_display(cart, cart_tree, cursor)
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:
        handle_error(f"An error occurred while updating cart quantity: {e}")



# calculate the total
# the cart and the cursor are being received as parameters
def calculate_and_display_totals(subtotal_label, taxes_label, total_label, cart, cursor):
    # Calculates and displays totals for cart items
    try:

        totals = sales.calculate_totals(cart, cursor)
        subtotal_label.config(text=f"Subtotal: ${totals['subtotal']:.2f}")
        taxes_label.config(text=f"Taxes: ${totals['taxes']:.2f}")
        total_label.config(text=f"Total: ${totals['total']:.2f}")
    except Exception as e:        
        handle_error(f"An error occurred while calculating the totals: {e}")





        
# Sales Management function
def checkout(receipt_tree, cart_tree, cart, connection, cursor, employee_id):
    # Completes the checkout process for the current cart
    try:
        selected_customer_id = get_selected_customer_id()
        if not cart:
            raise ValueError("Cart is empty. Add items before checkout.")
        if not selected_customer_id:
            raise ValueError("Please select a customer")
            
        # Convert customer input to customer_id if it's an email or name
        customer_id = None
        customer_email = None
        try:
            # First try as direct customer_id (integer)
            customer_id = int(selected_customer_id)
        except ValueError:
            # If not integer, search by email or name
            cursor.execute("SELECT customer_id FROM Customers WHERE contact_info = %s OR name = %s", 
                         (selected_customer_id, selected_customer_id))
            result = cursor.fetchone()
            if result:
                customer_id = result['customer_id']
            else:
                raise ValueError(f"Customer not found: {selected_customer_id}")
        
        # Get customer email for receipt sending
        cursor.execute("SELECT contact_info FROM Customers WHERE customer_id = %s", (customer_id,))
        customer_result = cursor.fetchone()
        if customer_result:
            customer_email = customer_result['contact_info']
        
        # Calculate totals before clearing the cart
        totals = sales.calculate_totals(cart, cursor)
        sale_id = sales.log_sale(connection, cursor, cart, employee_id, customer_id)
        receipt_data = sales.generate_receipt_dict(cursor, sale_id)
        
        # Generate and display receipt
        receipt_text = generate_receipt_text(cursor, sale_id, customer_id, totals)
        show_receipt(receipt_text)
        
        # Store last sale info for potential resend
        global last_sale_info
        last_sale_info = {
            'sale_id': sale_id,
            'customer_id': customer_id,
            'receipt_text': receipt_text
        }
        
        # Send email receipt automatically if customer has email
        if customer_email and '@' in customer_email:
            send_email_receipt(customer_email, receipt_text, sale_id)
        else:
            messagebox.showinfo("Receipt Saved", "Receipt saved locally. Customer email not available for sending.")
        
        _display_receipt(receipt_data, receipt_tree, cursor)
        
        # Clear cart and update display
        cart.clear()
        _update_cart_display(cart, cart_tree, cursor)
        
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:
        handle_error(f"An error occurred while checking out: {e}")

def generate_receipt_text(cursor, sale_id, customer_id, totals):
    # Generate formatted receipt text
    
    # Get sale details
    cursor.execute("""
        SELECT s.sale_datetime, si.SKU, p.name, si.quantity, si.price,
               (si.quantity * si.price) as total_price
        FROM Sales s
        JOIN SaleItems si ON s.sale_id = si.sale_id
        JOIN Products p ON si.SKU = p.SKU
        WHERE s.sale_id = %s
        ORDER BY p.name
    """, (sale_id,))
    
    sale_items = cursor.fetchall()
    
    if not sale_items:
        return "Receipt generation failed - no items found"
    
    sale_datetime = sale_items[0]['sale_datetime']
    
    # Get customer info
    cursor.execute("SELECT name FROM Customers WHERE customer_id = %s", (customer_id,))
    customer_result = cursor.fetchone()
    customer_name = customer_result['name'] if customer_result else f"Customer #{customer_id}"
    
    receipt = f"""
        STORECORE ENTERPRISE SYSTEM
        {'='*45}
        Date: {sale_datetime.strftime('%Y-%m-%d %H:%M:%S')}
        Customer: {customer_name} (ID: {customer_id})
        Sale ID: {sale_id}
        {'-'*45}
        ITEM               QTY   PRICE   TOTAL
        {'-'*45}
        """
    
    for item in sale_items:
        item_name = item['name'][:18]  # Truncate long names
        receipt += f"{item_name:<18} {item['quantity']:^4} ${item['price']:>5.2f} ${item['total_price']:>6.2f}\n"
    
    receipt += f"{'-'*45}\n"
    receipt += f"{'SUBTOTAL:':>32} ${totals['subtotal']:>6.2f}\n"
    receipt += f"{'TAXES:':>32} ${totals['taxes']:>6.2f}\n"
    receipt += f"{'TOTAL:':>32} ${totals['total']:>6.2f}\n"
    receipt += f"{'='*45}\n"
    receipt += "Thank you for your purchase!\n"
    receipt += "       Storecore v1.0\n"
    
    return receipt

def show_receipt(receipt_text):
    # Display receipt in a message box and save to file
    messagebox.showinfo("Transaction Complete", receipt_text)
    print_receipt_to_file(receipt_text)
    print_receipt_to_pdf(receipt_text)

def print_receipt_to_file(receipt_text):
    # Save receipt to a text file
    try:
        
        # Create receipts directory if it doesn't exist
        receipts_dir = "receipts"
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{receipts_dir}/receipt_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(receipt_text)
            
        print(f"Receipt saved to: {filename}")
        
    except Exception as e:
        print(f"Could not save receipt to file: {e}")

def print_receipt_to_pdf(receipt_text):
    # Save receipt to a PDF file with company logo
    try:
        
        # Create receipts directory if it doesn't exist
        receipts_dir = "receipts"
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{receipts_dir}/receipt_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter, 
                              leftMargin=0.75*inch, rightMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.navy,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        center_style = ParagraphStyle(
            'Center',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12
        )
        
        right_style = ParagraphStyle(
            'Right',
            parent=styles['Normal'],
            alignment=TA_RIGHT,
            fontSize=10
        )
        
        # Build PDF content
        story = []
        
        # Add company logo (if exists)
        logo_path = "logo.jpeg"
        if os.path.exists(logo_path):
            try:
                logo = ReportLabImage(logo_path, width=2*inch, height=1.5*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 12))
            except Exception as e:
                print(f"Could not add logo: {e}")
        
        # Add company name and title
        story.append(Paragraph("STORECORE ENTERPRISE SYSTEM", title_style))
        story.append(Spacer(1, 20))
        
        # Parse receipt text to extract information
        lines = receipt_text.strip().split('\n')
        
        # Extract key information from receipt text
        date_line = next((line for line in lines if 'Date:' in line), '')
        customer_line = next((line for line in lines if 'Customer:' in line), '')
        sale_id_line = next((line for line in lines if 'Sale ID:' in line), '')
        
        # Add receipt header information
        if date_line:
            story.append(Paragraph(date_line.strip(), center_style))
        if customer_line:
            story.append(Paragraph(customer_line.strip(), center_style))
        if sale_id_line:
            story.append(Paragraph(sale_id_line.strip(), center_style))
        
        story.append(Spacer(1, 20))
        
        # Create table for items
        # Find the start and end of items section
        item_start = -1
        item_end = -1
        for i, line in enumerate(lines):
            if 'ITEM' in line and 'QTY' in line and 'PRICE' in line:
                item_start = i + 2  # Skip the header and separator line
            elif line.strip().startswith('SUBTOTAL:') or line.strip().startswith('TOTAL:'):
                item_end = i
                break
        
        if item_start > -1 and item_end > -1:
            # Create table data
            table_data = [['Item', 'Qty', 'Price', 'Total']]
            
            for i in range(item_start, item_end):
                line = lines[i].strip()
                if line and not line.startswith('-'):
                    # Parse item line - adjust based on your receipt format
                    parts = line.split()
                    if len(parts) >= 4:
                        item_name = ' '.join(parts[:-3])
                        qty = parts[-3]
                        price = parts[-2]
                        total = parts[-1]
                        table_data.append([item_name, qty, price, total])
            
            # Create and style the table
            table = Table(table_data, colWidths=[3*inch, 0.7*inch, 0.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Add totals section
        for line in lines:
            if any(keyword in line for keyword in ['SUBTOTAL:', 'TAXES:', 'TOTAL:']):
                if 'TOTAL:' in line and 'SUBTOTAL' not in line:
                    # Make final total bold and larger
                    style = ParagraphStyle(
                        'BoldTotal',
                        parent=styles['Normal'],
                        alignment=TA_RIGHT,
                        fontSize=14,
                        textColor=colors.darkgreen,
                        fontName='Helvetica-Bold'
                    )
                    story.append(Paragraph(line.strip(), style))
                else:
                    story.append(Paragraph(line.strip(), right_style))
                story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 30))
        
        # Add footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12,
            textColor=colors.navy
        )
        
        story.append(Paragraph("Thank you for your purchase!", footer_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Storecore v1.0 - Professional POS System", center_style))
        
        # Build PDF
        doc.build(story)
        
        print(f"PDF Receipt saved to: {filename}")
        
    except Exception as e:
        if not REPORTLAB_AVAILABLE:
            print("ReportLab library not installed. Installing now...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
                print("ReportLab installed successfully. Please restart the application.")
            except Exception as install_error:
                print(f"Could not install ReportLab: {install_error}")
                print("Please install manually: pip install reportlab")
        else:
            print(f"Could not save PDF receipt: {e}")

def generate_pdf_for_email(receipt_text, sale_id):
    # Generate a PDF receipt specifically for email attachment
    try:
        
        # Create receipts directory if it doesn't exist
        receipts_dir = "receipts"
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)
        
        # Generate filename for email attachment
        filename = f"{receipts_dir}/email_receipt_{sale_id}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter, 
                              leftMargin=0.75*inch, rightMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.navy,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        center_style = ParagraphStyle(
            'Center',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12
        )
        
        right_style = ParagraphStyle(
            'Right',
            parent=styles['Normal'],
            alignment=TA_RIGHT,
            fontSize=10
        )
        
        # Build PDF content
        story = []
        
        # Add company logo (if exists)
        logo_path = "logo.jpeg"
        if os.path.exists(logo_path):
            try:
                logo = ReportLabImage(logo_path, width=2*inch, height=1.5*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 12))
            except Exception as e:
                print(f"Could not add logo to email PDF: {e}")
        
        # Add company name and title
        story.append(Paragraph("STORECORE ENTERPRISE SYSTEM", title_style))
        story.append(Spacer(1, 20))
        
        # Parse receipt text to extract information
        lines = receipt_text.strip().split('\n')
        
        # Extract key information from receipt text
        date_line = next((line for line in lines if 'Date:' in line), '')
        customer_line = next((line for line in lines if 'Customer:' in line), '')
        sale_id_line = next((line for line in lines if 'Sale ID:' in line), '')
        
        # Add receipt header information
        if date_line:
            story.append(Paragraph(date_line.strip(), center_style))
        if customer_line:
            story.append(Paragraph(customer_line.strip(), center_style))
        if sale_id_line:
            story.append(Paragraph(sale_id_line.strip(), center_style))
        
        story.append(Spacer(1, 20))
        
        # Create table for items
        item_start = -1
        item_end = -1
        for i, line in enumerate(lines):
            if 'ITEM' in line and 'QTY' in line and 'PRICE' in line:
                item_start = i + 2
            elif line.strip().startswith('SUBTOTAL:') or line.strip().startswith('TOTAL:'):
                item_end = i
                break
        
        if item_start > -1 and item_end > -1:
            table_data = [['Item', 'Qty', 'Price', 'Total']]
            
            for i in range(item_start, item_end):
                line = lines[i].strip()
                if line and not line.startswith('-'):
                    parts = line.split()
                    if len(parts) >= 4:
                        item_name = ' '.join(parts[:-3])
                        qty = parts[-3]
                        price = parts[-2]
                        total = parts[-1]
                        table_data.append([item_name, qty, price, total])
            
            table = Table(table_data, colWidths=[3*inch, 0.7*inch, 0.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Add totals section
        for line in lines:
            if any(keyword in line for keyword in ['SUBTOTAL:', 'TAXES:', 'TOTAL:']):
                if 'TOTAL:' in line and 'SUBTOTAL' not in line:
                    # Make final total bold and larger
                    style = ParagraphStyle(
                        'BoldTotal',
                        parent=styles['Normal'],
                        alignment=TA_RIGHT,
                        fontSize=14,
                        textColor=colors.darkgreen,
                        fontName='Helvetica-Bold'
                    )
                    story.append(Paragraph(line.strip(), style))
                else:
                    story.append(Paragraph(line.strip(), right_style))
                story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 30))
        
        # Add footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12,
            textColor=colors.navy
        )
        
        story.append(Paragraph("Thank you for your purchase!", footer_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Storecore v1.0 - Professional POS System", center_style))
        
        # Build PDF
        doc.build(story)
        
        return filename
        
    except Exception as e:
        print(f"Could not generate PDF for email: {e}")
        return None

def send_email_receipt(customer_email, receipt_text, sale_id, show_success_popup=True):
    # Send receipt via email to customer with PDF attachment
    email_config = load_email_config()
    
    if not email_config.get("email") or not email_config.get("password"):
        messagebox.showwarning("Email Error", "Email configuration not set up properly in credentials.json")
        return False

    if not customer_email:
        messagebox.showwarning("Email Error", "Customer email address not available")
        return False

    try:
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_config['email']
        msg['To'] = customer_email
        msg['Subject'] = f"Your Purchase Receipt - Sale #{sale_id} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create email body
        email_body = f"""
Dear Valued Customer,

Thank you for your purchase! Please find your receipt details below and attached as a PDF.

{receipt_text}

We've also attached a professional PDF receipt for your records.

If you have any questions about your purchase, please don't hesitate to contact us.

Best regards,
Storecore Team

---
This is an automated message. Please do not reply to this email.
        """
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Generate PDF for email attachment
        try:
            pdf_filename = generate_pdf_for_email(receipt_text, sale_id)
            if pdf_filename and os.path.exists(pdf_filename):
                # Attach PDF to email
                with open(pdf_filename, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= receipt_{sale_id}.pdf',
                )
                msg.attach(part)
        except Exception as pdf_error:
            print(f"Could not attach PDF to email: {pdf_error}")
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_config['email'], email_config['password'])
            server.sendmail(email_config['email'], [customer_email], msg.as_string())
            
        if show_success_popup:
            messagebox.showinfo("Email Sent", f"Receipt has been sent to {customer_email} with PDF attachment")
        return True
        
    except Exception as e:
        messagebox.showerror("Email Error", f"Failed to send email: {str(e)}")
        return False

def resend_last_receipt(cursor):
    # Resend the last receipt to customer's email
    global last_sale_info
    
    if not last_sale_info['sale_id']:
        messagebox.showwarning("No Receipt", "No recent receipt available to resend")
        return
    
    try:
        # Get customer email
        cursor.execute("SELECT contact_info FROM Customers WHERE customer_id = %s", 
                      (last_sale_info['customer_id'],))
        customer_result = cursor.fetchone()
        
        if not customer_result:
            messagebox.showerror("Error", "Customer not found")
            return
            
        customer_email = customer_result['contact_info']
        
        if not customer_email or '@' not in customer_email:
            messagebox.showwarning("Email Error", "Customer email address not available")
            return
        
        # Send the stored receipt (suppress default success message)
        success = send_email_receipt(customer_email, last_sale_info['receipt_text'], last_sale_info['sale_id'], show_success_popup=False)
        
        if success:
            # Show specific confirmation for resend action
            messagebox.showinfo("Receipt Resent", 
                              f"Receipt for Sale #{last_sale_info['sale_id']} has been successfully resent to {customer_email}")
        else:
            messagebox.showerror("Email Error", "Failed to resend receipt")
            
    except Exception as e:
        handle_error(f"Error resending receipt: {e}")

# Low stock alert functions and large transaction alerts already imported at top

def update_order_display(cart, cursor, subtotal_label, taxes_label, total_label):
    """Update the order display with current cart contents and totals"""
    try:
        if not cart:
            # Clear totals if cart is empty
            subtotal_label.config(text="Subtotal: $0.00")
            taxes_label.config(text="Taxes: $0.00")
            total_label.config(text="Total: $0.00")
            return
            
        # Calculate and display totals
        totals = sales.calculate_totals(cart, cursor)
        subtotal_label.config(text=f"Subtotal: ${totals['subtotal']:.2f}")
        taxes_label.config(text=f"Taxes: ${totals['taxes']:.2f}")
        total_label.config(text=f"Total: ${totals['total']:.2f}")
        
    except Exception as e:
        handle_error(f"Error updating order display: {e}")

# Functions for Supplier Management
def add_supplier(connection, cursor, supplier_name_entry, supplier_contact_entry, supplier_address_entry): # function for adding a new supplier
    """Adds a new supplier to the database.
    the cursor is being received as parameter
    """
    try:
        name = supplier_name_entry.get()
        contact_info = supplier_contact_entry.get()
        address = supplier_address_entry.get()

        if not all([name, contact_info, address]):
            raise ValueError("All fields must be filled to add a supplier.")        
        if suppliers.add_supplier(connection, cursor, name, contact_info, address):
            messagebox.showinfo("Success", f"Supplier '{name}' has been successfully added.")
        else:
            raise ValueError("Failed to add supplier. Please try again.")
        supplier_name_entry.delete(0, tk.END)
        supplier_contact_entry.delete(0, tk.END)
        supplier_address_entry.delete(0, tk.END)
    except Exception as e: # exception handling
        handle_error(f"An error occurred while adding the supplier: {e}")        
        supplier_address_entry.delete(0, tk.END)

def search_suppliers(search_supplier_entry, cursor): # function for searching a supplier
    """Searches for suppliers by name.
    """
    try:        
        search_term = search_supplier_entry.get()
        if not search_term:# if the search term is empty

            raise ValueError("Search term cannot be empty.")
        
        results = suppliers.search_supplier_by_name(cursor, search_term) # now the function is receiving the cursor
        if results:
            results_text = "Search Results:\n"
            for supplier in results:
                results_text += f"ID: {supplier['supplier_id']}, Name: {supplier['name']}, Contact: {supplier['contact_info']}, Address: {supplier['address']}\n"
            messagebox.showinfo("Search Results", results_text)
        else:
            messagebox.showinfo("No Results", "No suppliers found matching the search criteria.")        
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:
        handle_error(f"An error occurred during the search: {e}")        
          
          
def update_supplier(connection, cursor, update_supplier_id_entry, update_supplier_name_entry, update_supplier_contact_entry, update_supplier_address_entry): # function for updating a supplier  
    """Updates an existing supplier's information.
    """
    
    try:
        supplier_id = int(update_supplier_id_entry.get())
        name = update_supplier_name_entry.get()
        contact_info = update_supplier_contact_entry.get()
        address = update_supplier_address_entry.get()

        if not all([supplier_id, name, contact_info, address]):
            raise ValueError("All fields must be filled to update a supplier.")        
        suppliers.update_supplier(connection, cursor, supplier_id, name, contact_info, address)
        messagebox.showinfo("Success", f"Supplier ID {supplier_id} has been successfully updated.") 
    except ValueError as ve:
        handle_error(str(ve))


def delete_supplier(connection, cursor, delete_supplier_id_entry): # function for delete a supplier    
    # Deletes a supplier from the database
    try:
        supplier_id = int(delete_supplier_id_entry.get())
        suppliers.delete_supplier(connection, cursor, supplier_id) # now the function is receiving the cursor
        messagebox.showinfo("Success", f"Supplier ID {supplier_id} has been successfully deleted.")        
    except ValueError as ve:        
        handle_error(str(ve))    
    except Exception as e:        
        handle_error(f"An error occurred while deleting the supplier: {e}")
    delete_supplier_id_entry.delete(0, tk.END)

    
def search_supplier(delete_supplier_name_entry, delete_supplier_id_entry): # function for deleting a supplier by name
    # Deletes suppliers from the database by name or id
    try:        
        name = delete_supplier_name_entry.get()
        if name:# if we want to delete by name
            results = suppliers.search_supplier_by_name(cursor, name)# search the supplier by name, we are correcting the function name here.
            if results: # if we find the supplier
                for supplier in results:# for every supplier found
                    suppliers.delete_supplier(cursor, supplier["supplier_id"])# delete the supplier by id
                messagebox.showinfo("Success", f"Suppliers named '{name}' deleted successfully.")
            else:# if we dont find any supplier
                raise ValueError(f"No suppliers found with the name: {name}")
    except Exception as e:
        handle_error(f"An error occurred while deleting the supplier: {e}")

# Customer Management


def add_customer(connection, cursor, customer_name_entry, customer_contact_entry, customer_address_entry):
    # Adds a customer to the database
    try:
        name = customer_name_entry.get()
        contact_info = customer_contact_entry.get()
        address = customer_address_entry.get()
        if not all([name, contact_info, address]):
            raise ValueError("All customer details are required.")
        customers.add_customer(connection, cursor, name, contact_info, address)
        customer_name_entry.delete(0, tk.END)
        customer_contact_entry.delete(0, tk.END)
        customer_address_entry.delete(0, tk.END)
    except Exception as e:
        handle_error(f"An error occurred while adding the customer: {e}")
           

def delete_customer(connection, cursor, delete_customer_id_entry):
    try:
        customer_id_str = delete_customer_id_entry.get()
        if customer_id_str:
            customer_id = int(customer_id_str)
            customers.delete_customer(connection, cursor, customer_id)
            messagebox.showinfo("Success", f"Customer with ID '{customer_id}' deleted successfully.")
        else:
            raise ValueError("Please enter a customer ID to delete.")
        delete_customer_id_entry.delete(0, tk.END)
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:
        handle_error(f"An error occurred while deleting the customer: {e}")
        
# check if the value is a number
def validate_numeric_input(value, field_name):
    if not value.replace('.', '', 1).isdigit():
        raise ValueError(f"{field_name} must be a numeric value.")
    return float(value) if '.' in value else int(value)

# Inventory Management
def is_valid_number(value):
    # Check if a value is a number
    try:
        float(value)
        return True
    except ValueError:
        return False

def validate_date_input(date_str):
    # Validate a date
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

def is_valid_date(date_str):
    try:# Check if a date is in the correct format
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def empty_cart(cart_tree, cart, cursor):
    # Empties the cart and updates the display
    cart.clear()
    _update_cart_display(cart_tree, cart, cursor)
def add_item(connection, cursor, sku_entry, item_name_entry, category_entry, price_entry, stock_entry, supplier_id_entry):
    try:
        sku = sku_entry.get()
        name = item_name_entry.get()
        category = category_entry.get()
        price_str = price_entry.get()
        stock_str = stock_entry.get()
        supplier_id_str = supplier_id_entry.get()
        if not all([sku, name, category, price_str, stock_str, supplier_id_str]):
            raise ValueError("All fields must be filled out to add an item.")
        if not is_valid_number(price_str) or not is_valid_number(stock_str):
            raise ValueError("Price and stock must be valid numbers.")
        price = float(price_str)
        stock = int(stock_str)
        supplier_id = int(supplier_id_str)
        inventory.add_item(connection, cursor, sku, name, category, price, stock, supplier_id)
        messagebox.showinfo("Success", f"Item '{name}' added successfully.")
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:
        handle_error(f"An error occurred while adding the item: {e}")

def delete_item(connection, cursor, delete_sku_entry):   # delete an Item
    try:
        sku = delete_sku_entry.get()
        inventory.delete_item(connection, cursor, sku)
        messagebox.showinfo("Success", f"Item with SKU '{sku}' deleted successfully.")
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:        
        handle_error(f"An error occurred while deleting the item: {e}")        

def view_inventory(connection, cursor, inventory_tree):
    """Fetches all inventory items from the database and returns them as a list of dictionaries."""
    try:
        inventory_list = inventory.view_inventory(connection, cursor)
        _populate_inventory_treeview(inventory_list, inventory_tree)
    except Exception as e:
        handle_error(f"An error occurred while viewing inventory: {e}")

def view_employees(cursor, employee_tree): # function to view all the employees
    # Displays a list of all employees
    try:
        employees_list = employees.view_employees(cursor)
        if not employees_list:
            raise ValueError("No employees found.")
        populate_employees_treeview(employees_list, employee_tree)
    except Exception as e:
        handle_error(f"An error occurred while viewing employees: {e}")

def _populate_suppliers_treeview(suppliers_list, suppliers_tree):
    suppliers_tree.delete(*suppliers_tree.get_children())
    for supplier in suppliers_list:
        suppliers_tree.insert("", "end", values=(supplier['supplier_id'], supplier['name'], supplier['contact_info'], supplier['address']))
    alternate_treeview_rows(suppliers_tree)

def _populate_inventory_treeview(inventory_list, inventory_tree):
    """Populates the inventory treeview with data."""
    inventory_tree.delete(*inventory_tree.get_children())
    for item in inventory_list:
        inventory_tree.insert("", "end", values=(item['SKU'], item['name'], item['category'], item['price'], item['stock'], item['supplier_id']))
    alternate_treeview_rows(inventory_tree)

def populate_employees_treeview(employees_list, employee_tree):    
    employee_tree.delete(*employee_tree.get_children())    
    for employee in employees_list:
        employee_tree.insert("", "end", values=(employee['employee_id'], employee['name'], employee['role']))
    alternate_treeview_rows(employee_tree)

def adjust_stock(connection, cursor, adjust_sku_entry, adjust_quantity_entry, employee_id, reason):
    """Adjusts the stock level of a specific item."""
    try:
        sku = adjust_sku_entry.get()
        quantity_change = int(adjust_quantity_entry.get())
        if quantity_change == 0:
            raise ValueError("Please enter a non-zero value to adjust stock.")
        if not reason:
            raise ValueError("Please provide a reason for the stock adjustment.")
        inventory.adjust_stock(connection, cursor, sku, quantity_change, reason=reason, employee_id=employee_id)
        messagebox.showinfo("Success", f"Stock for SKU '{sku}' adjusted successfully.")
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:
        handle_error(f"An error occurred while adjusting stock: {e}")

def view_suppliers(cursor, suppliers_tree): # function to view the suppliers
    """Displays a list of all suppliers.        
    """
    try:
        suppliers_list = suppliers.view_suppliers(cursor) # use the provided cursor        

        if not suppliers_list:
            raise ValueError("No suppliers found.")
        _populate_suppliers_treeview(suppliers_list, suppliers_tree)
    except Exception as e:
        handle_error(f"An error occurred while viewing suppliers: {e}")    

def display_receipt(receipt, receipt_tree):# function to display the receipt
    """Show a receipt in the receipt tree"""
    receipt_tree.delete(*receipt_tree.get_children())
    for item in receipt:# for every item in the receipt
        receipt_tree.insert("", "end", values=(item['SKU'], item['name'], item['quantity'], item['price']))
    alternate_treeview_rows(receipt_tree)


def generate_receipt(cursor, sale_id): # generate a receipt
    # Generates a receipt for the completed sale
    try:# generate a receipt
        return sales.generate_receipt_dict(cursor, sale_id)
    except Exception as e:
        handle_error(f"An error occurred while generating the receipt: {e}")
def _display_receipt(receipt_data, receipt_tree, cursor):
    # Displays the receipt data in the receipt Treeview

    
    try:
        receipt_tree.delete(*receipt_tree.get_children())
        for item in receipt_data:            
                product = sales.get_product(cursor, item['SKU'])
                if product:
                  receipt_tree.insert("", "end", values=(item['SKU'], product['name'], item['quantity'], item['price']))
                else:
                    receipt_tree.insert("", "end", values=(item['SKU'], "Product Name Not Found", item['quantity'], item['price']))
        
        # Apply alternating row colors
        alternate_treeview_rows(receipt_tree)
    except Exception as e:
        handle_error(f"An error occurred while displaying the receipt: {e}")
def low_stock_report(connection, cursor):
    try:
        low_stock_items = inventory.check_low_stock(connection, cursor)
        if not low_stock_items:
            raise ValueError("No items are currently low in stock.")
        columns = ("SKU", "Product Name", "Quantity")
        rows = [(
            str(item.get('SKU', '')),
            str(item.get('name', '')),
            str(item.get('stock', ''))
        ) for item in low_stock_items]
        pos_app.reports_ui.display_report(columns, rows, compact=True)
    except Exception as e:
        handle_error(f"An error occurred while generating the Low Stock Report: {e}")

def _populate_customers_treeview(customers_list, customer_tree):
    customer_tree.delete(*customer_tree.get_children())
    for c in customers_list:
        customer_tree.insert("", "end", values=(c['customer_id'], c['name'], c['contact_info'], c['address']))
    alternate_treeview_rows(customer_tree)

def sales_by_employee_callback(employee_id):
    try:
        sales_list = sales_by_employee(cursor, employee_id)
        columns = ("Sale ID", "Date/Time", "Total", "Customer ID", "Customer Name")
        rows = [
            (sale['sale_id'], sale['sale_datetime'], f"${sale['total']:.2f}", sale['customer_id'], sale['customer_name'])
            for sale in sales_list
        ]
        if not rows:
            rows = [("No sales found for this employee.", "", "", "", "")]
        pos_app.reports_ui.display_report(columns, rows)
    except Exception as e:
        handle_error(f"An error occurred while generating the sales by employee report: {e}")

def supplier_purchase_callback(supplier_id):
    try:
        purchases = supplier_purchase_report(cursor, supplier_id)
        columns = ("Purchase ID", "Date/Time", "SKU", "Product Name", "Quantity", "Price", "Line Total")
        rows = [
            (p['purchase_id'], p['purchase_date'], p['SKU'], p['product_name'], p['quantity'], f"${p['price']:.2f}", f"${p['line_total']:.2f}")
            for p in purchases
        ]
        if not rows:
            rows = [("No purchases found for this supplier.", "", "", "", "", "", "")]
        pos_app.reports_ui.display_report(columns, rows)
    except Exception as e:
        handle_error(f"An error occurred while generating the supplier purchase report: {e}")

def inventory_adjustment_history_callback():
    try:
        adjustments = inventory_adjustment_history(cursor)
        columns = ("Adjustment ID", "Date/Time", "SKU", "Quantity Change", "Employee Name", "Reason")
        rows = [
            (a['adjustment_id'], a['date'], a['SKU'], a['quantity_change'], a['employee_name'], a['reason'])
            for a in adjustments
        ]
        if not rows:
            rows = [("No adjustments found.", "", "", "", "")]
        pos_app.reports_ui.display_report(columns, rows)
    except Exception as e:
        handle_error(f"An error occurred while generating the inventory adjustment history: {e}")

def inventory_value_report(cursor):
    try:
        # Fetch all inventory items
        inventory_list = inventory.view_inventory(db_connection, cursor)
        if not inventory_list:
            raise ValueError("No items found in inventory.")
        columns = ("SKU", "Product Name", "Stock", "Price", "Total Value")
        rows = [
            (
                str(item.get('SKU', '')),
                str(item.get('name', '')),
                str(item.get('stock', '')),
                f"${item.get('price', 0):.2f}",
                f"${item.get('stock', 0) * item.get('price', 0):.2f}"
            )
            for item in inventory_list
        ]
        pos_app.reports_ui.display_report(columns, rows)
    except Exception as e:
        handle_error(f"An error occurred while generating the Inventory Value Report: {e}")

def customer_purchase_history_callback(customer_id):
    try:
        purchases = customer_purchase_history(cursor, customer_id)
        columns = ("Sale ID", "Date/Time", "SKU", "Product Name", "Quantity", "Price", "Total")
        rows = [
            (
                p['sale_id'],
                p['sale_datetime'],
                p['SKU'],
                p['product_name'],
                p['quantity'],
                f"${p['price']:.2f}",
                f"${p['total']:.2f}"
            )
            for p in purchases
        ]
        if not rows:
            rows = [("No purchases found for this customer.", "", "", "", "", "", "")]
        pos_app.reports_ui.display_report(columns, rows)
    except Exception as e:
        handle_error(f"An error occurred while generating the customer purchase history report: {e}")

def load_and_verify_credentials(username, password):
    """
    Load the credentials from the JSON file and verify if the entered credentials match.
    Returns the user role if credentials are valid, None otherwise.
    """
    try:
        credentials_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
        if not os.path.exists(credentials_file):
            # Create default credentials file if it doesn't exist
            default_credentials = {
                "users": [
                    {"username": "manager", "password": "manager123", "role": "manager"},
                    {"username": "sales", "password": "sales123", "role": "salesperson"}
                ]
            }
            with open(credentials_file, 'w') as f:
                json.dump(default_credentials, f, indent=4)
        
        with open(credentials_file, 'r') as f:
            credentials = json.load(f)
        
        for user in credentials["users"]:
            if user["username"] == username and user["password"] == password:
                return user["role"]
        
        return None
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def create_login_window(root):
    """
    Create a login window to authenticate users
    """
    # Hide the main root window until login is successful
    root.withdraw()
    
    # Create alternative red button using tk.Button (more reliable for color)
    login_window = tk.Toplevel(root)
    login_window.title("Login - Storecore")
    login_window.protocol("WM_DELETE_WINDOW", lambda: exit())  # Close app if login window is closed
    login_window.resizable(False, False)
    
    # Set the size first, then position it
    login_window.geometry("400x300")
    
    # Force update to ensure window has processed size
    login_window.update_idletasks()
    
    # Center the login window
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x = (screen_width - 400) // 2
    y = (screen_height - 300) // 2
    login_window.geometry(f"400x300+{x}+{y}")
    
    # Make sure window stays on top
    login_window.lift()
    
    # Create a frame for the login components
    login_frame = ttk.Frame(login_window, padding="20")
    login_frame.pack(fill=tk.BOTH, expand=True)
    
    # Add logo if it exists
    try:
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((100, 100), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(login_frame, image=logo_photo)
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(pady=(0, 20))
    except Exception as e:
        print(f"Error loading logo: {e}")
    
    # Title
    title_label = ttk.Label(login_frame, text="Storecore Login", font=("TkDefaultFont", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Username
    username_frame = ttk.Frame(login_frame)
    username_frame.pack(fill=tk.X, pady=5)
    username_label = ttk.Label(username_frame, text="Username:", width=10)
    username_label.pack(side=tk.LEFT, padx=5)
    username_entry = ttk.Entry(username_frame)
    username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    # Password
    password_frame = ttk.Frame(login_frame)
    password_frame.pack(fill=tk.X, pady=5)
    password_label = ttk.Label(password_frame, text="Password:", width=10)
    password_label.pack(side=tk.LEFT, padx=5)
    password_entry = ttk.Entry(password_frame, show="*")
    password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    # Error message label
    error_label = ttk.Label(login_frame, text="", foreground="red")
    error_label.pack(pady=5)
    
    # Login button
    login_button = ttk.Button(login_frame, text="Login", style="TButton")
    login_button.pack(pady=10)
    
    # Return data structure
    result = {"role": None}
    
    def on_login():
        username = username_entry.get()
        password = password_entry.get()
        
        if not username or not password:
            error_label.config(text="Please enter both username and password")
            return
        
        role = load_and_verify_credentials(username, password)
        if role:
            result["role"] = role
            result["username"] = username
            login_window.destroy()
        else:
            error_label.config(text="Invalid username or password")
    
    login_button.config(command=on_login)
    
    # Bind Enter key to login button
    login_window.bind("<Return>", lambda event: on_login())
    
    # Give focus to username entry
    username_entry.focus_set()
    
    # Wait for the login window to be destroyed
    login_window.wait_window()
    
    return result["role"], result.get("username", "")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    root.title("Storecore")
    
    # Function to handle logout and return to login screen
    def handle_logout():
        global pos_app
        
        # Send end-of-day report before logout
        try:
            print("Generating end-of-day report...")
            send_end_of_day_report(cursor)
        except Exception as e:
            print(f"Error sending end-of-day report: {e}")
        
        # Hide the main window
        root.withdraw()
        
        # Clear the cart
        cart.clear()
        
        # Reset the window to default size before showing login
        root.geometry("1200x800")
        
        # Make sure we have a correct style for the logout button
        style = ttk.Style()
        style.configure("Red.TButton", background="red", foreground="white")
        
        # Show login window again
        user_role, username = create_login_window(root)
        if not user_role:
            exit()  # Exit if login fails
            
        # Show the main window again with the new user's role
        root.deiconify()
        
        global pos_app
        pos_app = POSApp(
            root,
            add_to_cart_callback=lambda product_id_entry, quantity_entry, cart_tree, *_: add_to_cart(
                product_id_entry.get(),
                quantity_entry.get(),
                cart_tree,
                cart,
                cursor
            ),
            checkout_callback=lambda cart_tree, receipt_tree, employee_id, *_: checkout(
                receipt_tree, cart_tree, cart, db_connection, cursor, employee_id
            ),
            empty_cart_callback=lambda cart_tree, *_: empty_cart(cart_tree, cart, cursor),
            remove_from_cart_callback=lambda remove_from_cart_entry, cart_tree, *_: remove_from_cart(
                remove_from_cart_entry, cart_tree, cart, cursor
            ),
            update_cart_quantity_callback=lambda update_cart_sku_entry, update_cart_quantity_entry, cart_tree, *_: update_cart_quantity(
                update_cart_sku_entry, update_cart_quantity_entry, cart_tree, cart, cursor
            ),
            calculate_and_display_totals_callback=lambda subtotal_label, taxes_label, total_label, *_: calculate_and_display_totals(
                subtotal_label, taxes_label, total_label, cart, cursor
            ),
            select_customer_callback=lambda customer_id, *_: set_selected_customer_id(customer_id),
            resend_receipt_callback=lambda *_: resend_last_receipt(cursor),
            add_supplier_callback=lambda supplier_name_entry, supplier_contact_entry, supplier_address_entry, *_: add_supplier(
                db_connection, cursor, supplier_name_entry, supplier_contact_entry, supplier_address_entry
            ),
            search_suppliers_callback=lambda search_supplier_entry, *_: search_suppliers(search_supplier_entry, cursor),
            delete_supplier_callback=lambda delete_supplier_id_entry, *_: delete_supplier(
                db_connection, cursor, delete_supplier_id_entry
            ),
            add_customer_callback=lambda customer_name_entry, customer_contact_entry, customer_address_entry, *_: add_customer(
                db_connection, cursor, customer_name_entry, customer_contact_entry, customer_address_entry
            ),
            delete_customer_callback=lambda delete_customer_id_entry, *_: delete_customer(
                db_connection, cursor, delete_customer_id_entry
            ),
            add_item_callback=lambda sku_entry, item_name_entry, category_entry, price_entry, stock_entry, supplier_id_entry, *_: add_item(
                db_connection, cursor, sku_entry, item_name_entry, category_entry, price_entry, stock_entry, supplier_id_entry
            ),
            delete_item_callback=lambda delete_sku_entry, *_: delete_item(db_connection, cursor, delete_sku_entry),
            view_inventory_callback=lambda inventory_tree, *_: view_inventory(db_connection, cursor, inventory_tree),
            view_employees_callback=lambda employee_tree, *_: view_employees(cursor, employee_tree),
            view_suppliers_callback=lambda suppliers_tree, *_: view_suppliers(cursor, suppliers_tree),
            adjust_stock_callback=lambda adjust_sku_entry, adjust_quantity_entry, employee_id, reason, *_: adjust_stock(
                db_connection, cursor, adjust_sku_entry, adjust_quantity_entry, employee_id, reason
            ),
            low_stock_report_callback=lambda *_: low_stock_report(db_connection, cursor),
            _update_cart_display_callback=_update_cart_display,
            _display_receipt_callback=lambda receipt_tree, receipt_data: _display_receipt(receipt_data, receipt_tree, cursor),
            get_customers_callback=lambda: customers.view_customers(cursor),
            get_employees_callback=lambda: employees.view_employees(cursor),
            view_customers_callback=lambda customer_tree, *_: _populate_customers_treeview(customers.view_customers(cursor), customer_tree),
            sales_by_employee_callback=sales_by_employee_callback,
            get_suppliers_callback=lambda: suppliers.view_suppliers(cursor),
            supplier_purchase_callback=supplier_purchase_callback,
            adjustment_history_callback=inventory_adjustment_history_callback,
            inventory_value_report_callback=lambda *_: inventory_value_report(cursor),
            customer_purchase_history_callback=customer_purchase_history_callback,
            user_role=user_role,
            username=username
        )
        
        # Set the logout callback for the new instance
        pos_app.logout_callback = handle_logout
    
    # Show login window before initializing the main app
    user_role, username = create_login_window(root)
    if not user_role:
        exit()  # Exit if login fails
    
    # Now that login is successful, show the main window
    root.deiconify()
    
    # Configure main window appearance
    root.geometry("1200x800")  # Set appropriate size
    
    # Create style for red logout button
    style = ttk.Style()
    style.theme_use('clam')  # Use clam theme which supports custom button styling
    style.configure("Red.TButton", 
                   background="red", 
                   foreground="white",
                   borderwidth=1,
                   relief="raised")
    style.map("Red.TButton",
             background=[('active', '#cc0000'), ('pressed', '#990000')],
             foreground=[('active', 'white'), ('pressed', 'white')])
    
    # Force all widgets/dialogs to use the main root
    if hasattr(tk, '_default_root'):
        tk._default_root = root
    
    # Display the logo in the top-right corner
    try:
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((80, 80), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(root, image=logo_photo)
            logo_label.image = logo_photo  # Keep a reference
            logo_label.place(relx=1.0, y=0, anchor="ne")
    except Exception as e:
        print(f"Error loading logo for main window: {e}")
    
    print(f"Logged in as: {username} (Role: {user_role})")
    
    db_connection, cursor = get_db()
    cart = []

    global pos_app
    pos_app = POSApp(
        root,
        # --- SALES TAB CALLBACKS ---
        add_to_cart_callback=lambda product_id_entry, quantity_entry, cart_tree, *_: add_to_cart(
            product_id_entry.get(),
            quantity_entry.get(),
            cart_tree,
            cart,
            cursor
        ),
        checkout_callback=lambda cart_tree, receipt_tree, employee_id, *_: checkout(
            receipt_tree,
            cart_tree,
            cart,
            db_connection,
            cursor,
            employee_id
        ),
        empty_cart_callback=lambda cart_tree, *_: empty_cart(
            cart_tree,
            cart,
            cursor
        ),
        remove_from_cart_callback=lambda remove_from_cart_entry, cart_tree, *_: remove_from_cart(
            remove_from_cart_entry,
            cart_tree,
            cart,
            cursor
        ),
        update_cart_quantity_callback=lambda update_cart_sku_entry, update_cart_quantity_entry, cart_tree, *_: update_cart_quantity(
            update_cart_sku_entry,
            update_cart_quantity_entry,
            cart_tree,
            cart,
            cursor
        ),
        calculate_and_display_totals_callback=lambda subtotal_label, taxes_label, total_label, *_: calculate_and_display_totals(
            subtotal_label,
            taxes_label,
            total_label,
            cart,
            cursor
        ),
        select_customer_callback=lambda customer_id, *_: set_selected_customer_id(customer_id),
        resend_receipt_callback=lambda *_: resend_last_receipt(cursor),
        add_supplier_callback=lambda supplier_name_entry, supplier_contact_entry, supplier_address_entry, *_: add_supplier(
            db_connection,
            cursor,
            supplier_name_entry,
            supplier_contact_entry,
            supplier_address_entry
        ),
        search_suppliers_callback=lambda search_supplier_entry, *_: search_suppliers(
            search_supplier_entry,
            cursor
        ),
        delete_supplier_callback=lambda delete_supplier_id_entry, *_: delete_supplier(
            db_connection,
            cursor,
            delete_supplier_id_entry
        ),
        add_customer_callback=lambda customer_name_entry, customer_contact_entry, customer_address_entry, *_: add_customer(
            db_connection,
            cursor,
            customer_name_entry,
            customer_contact_entry,
            customer_address_entry
        ),
        delete_customer_callback=lambda delete_customer_id_entry, *_: delete_customer(
            db_connection,
            cursor,
            delete_customer_id_entry
        ),
        add_item_callback=lambda sku_entry, item_name_entry, category_entry, price_entry, stock_entry, supplier_id_entry, *_: add_item(
            db_connection,
            cursor,
            sku_entry,
            item_name_entry,
            category_entry,
            price_entry,
            stock_entry,
            supplier_id_entry
        ),
        delete_item_callback=lambda delete_sku_entry, *_: delete_item(
            db_connection,
            cursor,
            delete_sku_entry
        ),
        view_inventory_callback=lambda inventory_tree, *_: view_inventory(
            db_connection,
            cursor,
            inventory_tree
        ),
        view_employees_callback=lambda employee_tree, *_: view_employees(cursor, employee_tree),
        view_suppliers_callback=lambda suppliers_tree, *_: _populate_suppliers_treeview(suppliers.view_suppliers(cursor), suppliers_tree),
        adjust_stock_callback=lambda adjust_sku_entry, adjust_quantity_entry, employee_id, reason, *_: adjust_stock(
            db_connection,
            cursor,
            adjust_sku_entry,
            adjust_quantity_entry,
            employee_id,
            reason
        ),
        low_stock_report_callback=lambda *_: low_stock_report(db_connection, cursor),
        _update_cart_display_callback=_update_cart_display,
        _display_receipt_callback=lambda receipt_tree, receipt_data: _display_receipt(receipt_data, receipt_tree, cursor),
        get_customers_callback=lambda: customers.view_customers(cursor),
        get_employees_callback=lambda: employees.view_employees(cursor),
        view_customers_callback=lambda customer_tree, *_: _populate_customers_treeview(customers.view_customers(cursor), customer_tree),
        
        sales_by_employee_callback=sales_by_employee_callback,
        get_suppliers_callback=lambda: suppliers.view_suppliers(cursor),
        supplier_purchase_callback=supplier_purchase_callback,
        adjustment_history_callback=inventory_adjustment_history_callback,
        inventory_value_report_callback=lambda *_: inventory_value_report(cursor),
        customer_purchase_history_callback=customer_purchase_history_callback,
        user_role=user_role,  # Pass the user role to restrict access
        username=username  # Pass the username for display
    )

    # Set the logout callback for the POS app
    pos_app.logout_callback = handle_logout

    # Function to handle application closing (when X button is clicked)
    def on_closing():
        try:
            print("Generating end-of-day report...")
            send_end_of_day_report(cursor)
        except Exception as e:
            print(f"Error sending end-of-day report: {e}")
        finally:
            root.destroy()

    # Set the window close protocol
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
    close_db(db_connection, cursor)