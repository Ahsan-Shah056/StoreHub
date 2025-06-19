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

# Helper function for consistent TreeView text formatting
def format_treeview_text(value):
    """
    Formats text for consistent display in TreeViews.
    - Applies title case to string values
    - Preserves numeric values as-is
    - Handles None values gracefully
    """
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        # Apply title case but preserve certain patterns
        text = str(value).strip()
        if text.upper() in ['SKU', 'ID', 'N/A', 'USA', 'UK', 'CA']:  # Preserve common abbreviations
            return text.upper()
        # Check if it's an email address - keep lowercase
        if '@' in text and '.' in text:
            return text.lower()
        # Check if it's a phone number pattern - keep as-is
        if any(char in text for char in ['-', '(', ')', '+']) and any(char.isdigit() for char in text):
            return text
        # Apply title case for regular text
        return text.title()
    return str(value)

def format_treeview_values(values):
    """
    Formats a tuple/list of values for TreeView insertion.
    """
    return tuple(format_treeview_text(value) for value in values)
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
                formatted_values = format_treeview_values((
                    item['SKU'], 
                    product['name'], 
                    item['quantity'], 
                    f"${product['price']:.2f}",
                    f"${line_total:.2f}"
                ))
                cart_tree.insert("", "end", values=formatted_values)
        
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
        DIGICLIMATE STORE HUB ENTERPRISE SYSTEM
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
    receipt += "    DigiClimate Store Hub v2.0\n"
    
    return receipt

def show_receipt(receipt_text):
    # Display receipt in a message box and save to file
    messagebox.showinfo("Transaction Complete", receipt_text)
    generate_premium_pdf_receipt(receipt_text, for_email=False)



def generate_premium_pdf_receipt(receipt_text, sale_id=None, for_email=False):
    """Generate a premium, professional PDF receipt with advanced styling and layout
    
    Args:
        receipt_text: The receipt content to format
        sale_id: Optional sale ID for email filename
        for_email: If True, generates for email attachment; if False, for local storage
    
    Returns:
        str: The filename of the generated PDF
    """
    try:
        # Create receipts directory if it doesn't exist
        receipts_dir = "receipts"
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)
        
        # Generate appropriate filename
        if for_email and sale_id:
            filename = f"{receipts_dir}/email_receipt_{sale_id}.pdf"
            pdf_title = f"Receipt #{sale_id} - DigiClimate Store - Resilience meets innovation"
            pdf_subject = "Purchase Receipt - Email Copy"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{receipts_dir}/receipt_{timestamp}.pdf"
            pdf_title = "DigiClimate Store Receipt - Resilience meets innovation"
            pdf_subject = "Purchase Receipt"
        
        # Create PDF document with premium settings
        doc = SimpleDocTemplate(
            filename, 
            pagesize=letter,
            leftMargin=0.5*inch, 
            rightMargin=0.5*inch,
            topMargin=0.4*inch, 
            bottomMargin=0.5*inch,
            title=pdf_title,
            author="DigiClimate Store Hub - Resilience meets innovation",
            subject=pdf_subject
        )
        
        # Get base styles
        styles = getSampleStyleSheet()
        
        # Define premium color palette
        primary_blue = colors.Color(0.1, 0.2, 0.4)  # Dark professional blue
        accent_green = colors.Color(0.0, 0.5, 0.3)  # Professional green
        light_gray = colors.Color(0.95, 0.95, 0.95)  # Light background
        dark_gray = colors.Color(0.3, 0.3, 0.3)     # Dark text
        gold_accent = colors.Color(0.8, 0.6, 0.1)   # Gold highlight
        
        # Create sophisticated custom styles
        company_title_style = ParagraphStyle(
            'CompanyTitle',
            parent=styles['Heading1'],
            fontSize=28,
            fontName='Helvetica-Bold',
            textColor=primary_blue,
            alignment=TA_CENTER,
            spaceAfter=8,
            spaceBefore=0,
            leading=30,
            letterSpacing=1
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Oblique',
            textColor=accent_green,
            alignment=TA_CENTER,
            spaceAfter=25,
            leading=14
        )
        
        header_box_style = ParagraphStyle(
            'HeaderBox',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            textColor=dark_gray,
            alignment=TA_CENTER,
            spaceAfter=6,
            leading=13
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=primary_blue,
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=20,
            borderPadding=5,
            backColor=light_gray,
            borderColor=primary_blue,
            borderWidth=0.5,
            leading=16
        )
        
        total_style = ParagraphStyle(
            'GrandTotal',
            parent=styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=accent_green,
            alignment=TA_RIGHT,
            spaceAfter=8,
            leading=20,
            borderPadding=8,
            backColor=light_gray,
            borderColor=accent_green,
            borderWidth=1
        )
        
        footer_style = ParagraphStyle(
            'FooterText',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            textColor=dark_gray,
            alignment=TA_CENTER,
            spaceAfter=5,
            leading=12
        )
        
        # Build PDF content with premium layout
        story = []
        
        # === PREMIUM HEADER SECTION ===
        
        # Add company logo with professional styling
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            try:
                # Create a frame around the logo
                logo_table_data = [
                    [ReportLabImage(logo_path, width=2.5*inch, height=1.8*inch)]
                ]
                logo_table = Table(logo_table_data, colWidths=[7.5*inch])
                logo_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('BOX', (0, 0), (-1, -1), 1, light_gray),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 15),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ]))
                story.append(logo_table)
                story.append(Spacer(1, 15))
            except Exception as e:
                print(f"Could not add logo: {e}")
        
        # Add "EMAIL COPY" indicator for email receipts
        if for_email:
            email_indicator_data = [['📧 EMAIL COPY']]
            email_indicator_table = Table(email_indicator_data, colWidths=[7.5*inch])
            email_indicator_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), gold_accent),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(email_indicator_table)
            story.append(Spacer(1, 15))
        
        # Company name with elegant typography
        story.append(Paragraph("DIGICLIMATE STORE HUB", company_title_style))
        story.append(Paragraph("Enterprise Point of Sale System", subtitle_style))
        
        # Add company tagline with distinctive styling
        tagline_style = ParagraphStyle(
            'TaglineStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Oblique',
            textColor=gold_accent,
            alignment=TA_CENTER,
            spaceAfter=15,
            leading=12
        )
        story.append(Paragraph("Resilience meets innovation", tagline_style))
        
        # Decorative separator line
        line_table = Table([['']], colWidths=[7.5*inch], rowHeights=[3])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, gold_accent),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 20))
        
        # === RECEIPT INFORMATION EXTRACTION ===
        lines = receipt_text.strip().split('\n')
        
        # Extract information with better parsing
        date_info = ""
        customer_info = ""
        sale_id_info = ""
        
        for line in lines:
            if 'Date:' in line:
                date_info = line.replace('Date:', '').strip()
            elif 'Customer:' in line:
                customer_info = line.replace('Customer:', '').strip()
            elif 'Sale ID:' in line:
                sale_id_info = line.replace('Sale ID:', '').strip()
        
        # === PROFESSIONAL RECEIPT HEADER ===
        
        # Create information box with elegant styling
        if for_email:
            header_data = [
                ['Receipt Information', ''],
                ['Date & Time:', date_info],
                ['Customer:', customer_info],
                ['Transaction ID:', sale_id_info],
                ['Email Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
        else:
            header_data = [
                ['Receipt Information', ''],
                ['Date & Time:', date_info],
                ['Customer:', customer_info],
                ['Transaction ID:', sale_id_info],
                ['Processed by:', 'DigiClimate POS System v2.0']
            ]
        
        header_table = Table(header_data, colWidths=[2*inch, 5.5*inch])
        header_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Data rows styling
            ('BACKGROUND', (0, 1), (0, -1), light_gray),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, dark_gray),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 25))
        
        # === PREMIUM ITEMS TABLE ===
        
        story.append(Paragraph("Purchase Details", section_header_style))
        
        # Parse items from receipt text with improved algorithm
        item_start = -1
        item_end = -1
        for i, line in enumerate(lines):
            if 'ITEM' in line and 'QTY' in line and 'PRICE' in line:
                item_start = i + 2  # Skip header and separator
            elif line.strip().startswith('SUBTOTAL:'):
                item_end = i
                break
        
        if item_start > -1 and item_end > -1:
            # Create sophisticated table data
            table_data = [
                ['Item Description', 'Qty', 'Unit Price', 'Line Total']
            ]
            
            for i in range(item_start, item_end):
                line = lines[i].strip()
                if line and not line.startswith('-') and line:
                    parts = line.split()
                    if len(parts) >= 4:
                        item_name = ' '.join(parts[:-3])
                        qty = parts[-3]
                        price = parts[-2]
                        total = parts[-1]
                        table_data.append([item_name, qty, price, total])
            
            # Create premium items table
            items_table = Table(table_data, colWidths=[3.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])
            items_table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), primary_blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                # Data rows - alternating colors
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Item names left-aligned
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),   # Numbers centered
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # Professional grid
                ('GRID', (0, 0), (-1, -1), 0.5, dark_gray),
                ('LINEBELOW', (0, 0), (-1, 0), 2, primary_blue),
                # Padding for readability
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            # Add alternating row colors for better readability
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    items_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, i), (-1, i), light_gray)
                    ]))
            
            story.append(items_table)
            story.append(Spacer(1, 25))
        
        # === ELEGANT TOTALS SECTION ===
        
        # Extract and format totals
        subtotal_amount = ""
        tax_amount = ""
        total_amount = ""
        
        for line in lines:
            if 'SUBTOTAL:' in line:
                subtotal_amount = line.split('$')[-1].strip()
            elif 'TAXES:' in line:
                tax_amount = line.split('$')[-1].strip()
            elif 'TOTAL:' in line and 'SUBTOTAL' not in line:
                total_amount = line.split('$')[-1].strip()
        
        # Create elegant totals table
        totals_data = [
            ['', 'Subtotal:', f"${subtotal_amount}"],
            ['', 'Taxes:', f"${tax_amount}"],
            ['', '', ''],  # Spacer row
            ['', 'GRAND TOTAL:', f"${total_amount}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[4*inch, 1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            # Subtotal and tax rows
            ('FONTNAME', (1, 0), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (-1, 1), 11),
            ('ALIGN', (1, 0), (-1, 1), 'RIGHT'),
            ('TEXTCOLOR', (1, 0), (-1, 1), dark_gray),
            # Grand total row - make it stand out
            ('FONTNAME', (1, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 3), (-1, 3), 13),
            ('ALIGN', (1, 3), (-1, 3), 'RIGHT'),
            ('TEXTCOLOR', (1, 3), (-1, 3), accent_green),
            ('BACKGROUND', (1, 3), (-1, 3), light_gray),
            ('BOX', (1, 3), (-1, 3), 1.5, accent_green),
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 30))
        
        # === PROFESSIONAL FOOTER ===
        
        # Thank you message with style
        thank_you_data = [
            ['Thank you for choosing DigiClimate Store Hub!']
        ]
        thank_you_table = Table(thank_you_data, colWidths=[7.5*inch])
        thank_you_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(thank_you_table)
        story.append(Spacer(1, 20))
        
        # Contact information and system details
        if for_email:
            story.append(Paragraph("This receipt was emailed from DigiClimate Store Hub v2.0", footer_style))
            story.append(Paragraph("Enterprise Point of Sale & Inventory Management System", footer_style))
            story.append(Paragraph(f"Email generated on {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}", footer_style))
        else:
            story.append(Paragraph("This receipt was generated by DigiClimate Store Hub v2.0", footer_style))
            story.append(Paragraph("Enterprise Point of Sale & Inventory Management System", footer_style))
            story.append(Paragraph(f"Generated on {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}", footer_style))
        
        # Add a subtle footer line
        footer_line_table = Table([['']], colWidths=[7.5*inch], rowHeights=[2])
        footer_line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 1, gold_accent),
        ]))
        story.append(Spacer(1, 10))
        story.append(footer_line_table)
        
        # Build the premium PDF
        doc.build(story)
        
        print(f"✨ Premium PDF Receipt saved to: {filename}")
        return filename
        
    except Exception as e:
        if not REPORTLAB_AVAILABLE:
            print("ReportLab library not installed. Installing now...")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
                print("ReportLab installed successfully. Please restart the application.")
            except Exception as install_error:
                print(f"Could not install ReportLab: {install_error}")
                print("Please install manually: pip install reportlab")
        else:
            print(f"Could not save PDF receipt: {e}")
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
DigiClimate Store Hub Team

---
This is an automated message. Please do not reply to this email.
        """
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Generate PDF for email attachment
        try:
            pdf_filename = generate_premium_pdf_receipt(receipt_text, sale_id=sale_id, for_email=True)
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

def update_supplier(connection, cursor, supplier_id, supplier_name_entry, supplier_contact_entry, supplier_address_entry):
    # Updates a supplier in the database
    try:
        name = supplier_name_entry.get()
        contact_info = supplier_contact_entry.get()
        address = supplier_address_entry.get()
        
        if not all([name, contact_info, address]):
            raise ValueError("All supplier details are required.")
        
        supplier_id_int = int(supplier_id)
        suppliers.update_supplier(connection, cursor, supplier_id_int, name, contact_info, address)
        messagebox.showinfo("Success", f"Supplier with ID '{supplier_id}' updated successfully.")
        
        # Clear the form fields
        supplier_name_entry.delete(0, tk.END)
        supplier_contact_entry.delete(0, tk.END)
        supplier_address_entry.delete(0, tk.END)
        
    except ValueError as ve:
        handle_error(f"Invalid input: {ve}")
    except Exception as e:
        handle_error(f"An error occurred while updating the supplier: {e}")

def load_supplier(cursor, supplier_id):
    # Loads a supplier's data for updating
    try:
        supplier_id_int = int(supplier_id)
        supplier_data = suppliers.get_supplier(cursor, supplier_id_int)
        return supplier_data
    except ValueError:
        raise ValueError("Supplier ID must be a number.")
    except Exception as e:
        raise ValueError(f"Failed to load supplier: {e}")

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

def update_customer(connection, cursor, customer_id, customer_name_entry, customer_contact_entry, customer_address_entry):
    # Updates a customer in the database
    try:
        name = customer_name_entry.get()
        contact_info = customer_contact_entry.get()
        address = customer_address_entry.get()
        
        if not all([name, contact_info, address]):
            raise ValueError("All customer details are required.")
        
        customer_id_int = int(customer_id)
        customers.update_customer(connection, cursor, customer_id_int, name, contact_info, address)
        messagebox.showinfo("Success", f"Customer with ID '{customer_id}' updated successfully.")
        
        # Clear the form fields
        customer_name_entry.delete(0, tk.END)
        customer_contact_entry.delete(0, tk.END)
        customer_address_entry.delete(0, tk.END)
        
    except ValueError as ve:
        handle_error(f"Invalid input: {ve}")
    except Exception as e:
        handle_error(f"An error occurred while updating the customer: {e}")

def load_customer(cursor, customer_id):
    # Loads a customer's data for updating
    try:
        customer_id_int = int(customer_id)
        customer_data = customers.get_customer(cursor, customer_id_int)
        return customer_data
    except ValueError:
        raise ValueError("Customer ID must be a number.")
    except Exception as e:
        raise ValueError(f"Failed to load customer: {e}")
           

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
def add_item(connection, cursor, sku_entry, item_name_entry, category_entry, price_entry, stock_entry, supplier_id_entry, cost_entry=None):
    try:
        sku = sku_entry.get()
        name = item_name_entry.get()
        category = category_entry.get()
        price_str = price_entry.get()
        stock_str = stock_entry.get()
        supplier_id_str = supplier_id_entry.get()
        cost_str = cost_entry.get() if cost_entry else "0.00"
        
        if not all([sku, name, category, price_str, stock_str, supplier_id_str]):
            raise ValueError("All required fields must be filled out to add an item.")
        if not is_valid_number(price_str) or not is_valid_number(stock_str):
            raise ValueError("Price and stock must be valid numbers.")
        if cost_str and not is_valid_number(cost_str):
            raise ValueError("Cost must be a valid number.")
            
        price = float(price_str)
        stock = int(stock_str)
        supplier_id = int(supplier_id_str)
        cost = float(cost_str) if cost_str else 0.00
        
        # Convert category name to category_id
        cursor.execute("SELECT category_id FROM Categories WHERE name = %s", (category,))
        category_result = cursor.fetchone()
        if not category_result:
            raise ValueError(f"Category '{category}' does not exist. Please select a valid category.")
        category_id = category_result['category_id']
        
        inventory.add_item(connection, cursor, sku, name, category_id, price, stock, supplier_id, cost)
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
        formatted_values = format_treeview_values((supplier['supplier_id'], supplier['name'], supplier['contact_info'], supplier['address']))
        suppliers_tree.insert("", "end", values=formatted_values)
    alternate_treeview_rows(suppliers_tree)

def _populate_inventory_treeview(inventory_list, inventory_tree):
    """Populates the inventory treeview with data."""
    inventory_tree.delete(*inventory_tree.get_children())
    for item in inventory_list:
        formatted_values = format_treeview_values((item['SKU'], item['name'], item['category'], item['price'], item['stock'], item['supplier_id'], item['cost']))
        inventory_tree.insert("", "end", values=formatted_values)
    alternate_treeview_rows(inventory_tree)

def populate_employees_treeview(employees_list, employee_tree):    
    employee_tree.delete(*employee_tree.get_children())    
    for employee in employees_list:
        formatted_values = format_treeview_values((employee['employee_id'], employee['name'], employee['role']))
        employee_tree.insert("", "end", values=formatted_values)
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
        formatted_values = format_treeview_values((item['SKU'], item['name'], item['quantity'], item['price']))
        receipt_tree.insert("", "end", values=formatted_values)
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
                    formatted_values = format_treeview_values((item['SKU'], product['name'], item['quantity'], item['price']))
                    receipt_tree.insert("", "end", values=formatted_values)
                else:
                    formatted_values = format_treeview_values((item['SKU'], "Product Name Not Found", item['quantity'], item['price']))
                    receipt_tree.insert("", "end", values=formatted_values)
        
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
        formatted_values = format_treeview_values((c['customer_id'], c['name'], c['contact_info'], c['address']))
        customer_tree.insert("", "end", values=formatted_values)
    alternate_treeview_rows(customer_tree)

def sales_by_employee_callback(employee_id):
    try:
        sales_list = sales_by_employee(cursor, employee_id)
        columns = ("Sale ID", "Date/Time", "Total", "Customer ID", "Customer Name")
        rows = []
        grand_total = 0.0
        
        # Process individual sales and calculate grand total
        for sale in sales_list:
            sale_total = float(sale['total'])
            grand_total += sale_total
            rows.append((
                sale['sale_id'], 
                sale['sale_datetime'], 
                f"${sale_total:.2f}", 
                sale['customer_id'], 
                sale['customer_name']
            ))
        
        if not rows:
            rows = [("No sales found for this employee.", "", "", "", "")]
        else:
            # Add separator row and grand total row
            rows.append(("", "", "", "", ""))
            rows.append(("─" * 10, "─" * 15, "─" * 12, "─" * 12, "─" * 15))
            rows.append((
                "GRAND TOTAL",
                f"{len(sales_list)} sales",
                f"${grand_total:.2f}",
                "",
                ""
            ))
        
        pos_app.reports_ui.display_report(columns, rows)
    except Exception as e:
        handle_error(f"An error occurred while generating the sales by employee report: {e}")

def supplier_purchase_callback(supplier_id):
    try:
        purchases = supplier_purchase_report(cursor, supplier_id)
        columns = ("Purchase ID", "Date/Time", "SKU", "Product Name", "Quantity", "Price", "Line Total")
        rows = []
        grand_total = 0.0
        total_quantity = 0
        
        # Process individual purchases and calculate grand total
        for p in purchases:
            line_total = float(p['line_total'])
            quantity = int(p['quantity'])
            grand_total += line_total
            total_quantity += quantity
            
            rows.append((
                p['purchase_id'], 
                p['purchase_date'], 
                p['SKU'], 
                p['product_name'], 
                quantity,
                f"${p['price']:.2f}", 
                f"${line_total:.2f}"
            ))
        
        if not rows:
            rows = [("No purchases found for this supplier.", "", "", "", "", "", "")]
        else:
            # Add separator row and grand total row
            rows.append(("", "", "", "", "", "", ""))
            rows.append(("─" * 12, "─" * 15, "─" * 8, "─" * 15, "─" * 8, "─" * 10, "─" * 12))
            rows.append((
                "GRAND TOTAL",
                f"{len(purchases)} purchases",
                "",
                "",
                str(total_quantity),
                "",
                f"${grand_total:.2f}"
            ))
        
        pos_app.reports_ui.display_report(columns, rows)
    except Exception as e:
        handle_error(f"An error occurred while generating the supplier purchase report: {e}")

def inventory_adjustment_history_callback():
    try:
        adjustments = inventory_adjustment_history(cursor)
        columns = ("Adjustment ID", "Date/Time", "SKU", "Quantity Change", "Employee Name", "Reason")
        rows = []
        net_change = 0
        
        # Process individual adjustments and calculate net change
        for a in adjustments:
            quantity_change = int(a['quantity_change'])
            net_change += quantity_change
            
            rows.append((
                a['adjustment_id'], 
                a['date'], 
                a['SKU'], 
                quantity_change, 
                a['employee_name'], 
                a['reason']
            ))
        
        if not rows:
            rows = [("No adjustments found.", "", "", "", "", "")]
        else:
            # Add separator row and summary row
            rows.append(("", "", "", "", "", ""))
            rows.append(("─" * 12, "─" * 15, "─" * 8, "─" * 12, "─" * 15, "─" * 15))
            
            # Show net change (positive = additions, negative = reductions)
            net_change_str = f"+{net_change}" if net_change > 0 else str(net_change)
            rows.append((
                "SUMMARY",
                f"{len(adjustments)} adjustments",
                "",
                net_change_str,
                "Net Change",
                ""
            ))
        
        pos_app.reports_ui.display_report(columns, rows)
    except Exception as e:
        handle_error(f"An error occurred while generating the inventory adjustment history: {e}")

def inventory_value_report(cursor):
    try:
        # Fetch all inventory items
        inventory_list = inventory.view_inventory(db_connection, cursor)
        if not inventory_list:
            raise ValueError("No items found in inventory.")
        
        columns = ("SKU", "Product Name", "Stock", "Cost", "Total Value")
        rows = []
        grand_total = 0.0
        
        # Process individual items and calculate grand total
        for item in inventory_list:
            stock = int(item.get('stock', 0))
            cost = float(item.get('cost', 0))  # Use cost instead of price for inventory valuation
            item_total = stock * cost
            grand_total += item_total
            
            rows.append((
                str(item.get('SKU', '')),
                str(item.get('name', '')),
                str(stock),
                f"${cost:.2f}",
                f"${item_total:.2f}"
            ))
        
        # Add a separator row and grand total row
        if rows:
            # Add separator row
            rows.append(("", "", "", "", ""))
            rows.append(("─" * 15, "─" * 20, "─" * 8, "─" * 10, "─" * 12))
            
            # Add grand total row
            rows.append((
                "GRAND TOTAL",
                f"{len(inventory_list)} items",
                "",
                "",
                f"${grand_total:.2f}"
            ))
        
        pos_app.reports_ui.display_report(columns, rows)
    except Exception as e:
        handle_error(f"An error occurred while generating the Inventory Value Report: {e}")

def customer_purchase_history_callback(customer_id):
    try:
        purchases = customer_purchase_history(cursor, customer_id)
        columns = ("Sale ID", "Date/Time", "SKU", "Product Name", "Quantity", "Price", "Total")
        rows = []
        grand_total = 0.0
        total_quantity = 0
        
        # Process individual purchases and calculate grand total
        for p in purchases:
            purchase_total = float(p['total'])
            quantity = int(p['quantity'])
            grand_total += purchase_total
            total_quantity += quantity
            
            rows.append((
                p['sale_id'],
                p['sale_datetime'],
                p['SKU'],
                p['product_name'],
                quantity,
                f"${p['price']:.2f}",
                f"${purchase_total:.2f}"
            ))
        
        if not rows:
            rows = [("No purchases found for this customer.", "", "", "", "", "", "")]
        else:
            # Add separator row and grand total row
            rows.append(("", "", "", "", "", "", ""))
            rows.append(("─" * 10, "─" * 15, "─" * 8, "─" * 15, "─" * 8, "─" * 10, "─" * 12))
            rows.append((
                "GRAND TOTAL",
                f"{len(purchases)} purchases",
                "",
                "",
                str(total_quantity),
                "",
                f"${grand_total:.2f}"
            ))
        
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
    Create a beautiful, modern login window with enhanced visual appeal
    """
  
    # Hide the main root window until login is successful
    root.withdraw()
    
    # Create login window with modern styling
    login_window = tk.Toplevel(root)
    login_window.title("DigiClimate Store Hub - Login")
    login_window.protocol("WM_DELETE_WINDOW", lambda: exit())
    login_window.resizable(False, False)
    
    # Set larger, more modern size
    window_width = 520
    window_height = 650
    login_window.geometry(f"{window_width}x{window_height}")
    
    # Force update to ensure window has processed size
    login_window.update_idletasks()
    
    # Center the login window
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    login_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Set window icon and properties
    login_window.lift()
    login_window.focus_force()
    
    # Create gradient background effect using canvas
    canvas = tk.Canvas(login_window, width=window_width, height=window_height, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Create beautiful gradient background
    def create_gradient():
        # Professional blue gradient
        gradient_colors = [
            "#1a365d",  # Dark blue
            "#2d4a6b", 
            "#405e79", 
            "#537287", 
            "#668695", 
            "#799aa3"   # Light blue
        ]
        
        strip_height = window_height // len(gradient_colors)
        for i, color in enumerate(gradient_colors):
            y1 = i * strip_height
            y2 = (i + 1) * strip_height
            canvas.create_rectangle(0, y1, window_width, y2, fill=color, outline=color)
    
    create_gradient()
    
    # Create main container frame with elegant styling
    main_frame = tk.Frame(canvas, bg="white", relief="raised", bd=2)
    main_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)
    
    # Add subtle shadow effect
    shadow_frame = tk.Frame(canvas, bg="#2d4a6b", relief="flat")
    shadow_frame.place(relx=0.5, rely=0.5, anchor="center", width=406, height=506)
    main_frame.lift()
    
    # === HEADER SECTION ===
    
    # Header with company branding
    header_frame = tk.Frame(main_frame, bg="#1a365d", height=120)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)
    
    # Add logo with enhanced styling
    logo_added = False
    try:
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            # Create circular logo effect
            logo_image = logo_image.resize((80, 80), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(header_frame, image=logo_photo, bg="#1a365d")
            logo_label.image = logo_photo  # Keep a reference
            logo_label.place(relx=0.5, rely=0.3, anchor="center")
            logo_added = True
    except Exception as e:
        print(f"Error loading logo: {e}")
    
    # Company name with elegant typography
    if not logo_added:
        company_icon = tk.Label(header_frame, text="🏢", font=("Arial", 32), 
                               bg="#1a365d", fg="white")
        company_icon.place(relx=0.5, rely=0.25, anchor="center")
    
    title_label = tk.Label(header_frame, text="DigiClimate Store Hub", 
                          font=("Segoe UI", 16, "bold"), bg="#1a365d", fg="white")
    title_label.place(relx=0.5, rely=0.55, anchor="center")
    
    tagline_label = tk.Label(header_frame, text="Resilience meets innovation",  
                             font=("Segoe UI", 9), bg="#1a365d", fg="#b3c6d9")
    tagline_label.place(relx=0.5, rely=0.75, anchor="center")
    
    
    # === LOGIN FORM SECTION ===
    
    # Create form container with padding
    form_frame = tk.Frame(main_frame, bg="white", padx=40, pady=30)
    form_frame.pack(fill=tk.BOTH, expand=True)
    
    # Welcome message
    welcome_label = tk.Label(form_frame, text="Welcome Back!", 
                            font=("Segoe UI", 18, "bold"), 
                            bg="white", fg="#1a365d")
    welcome_label.pack(pady=(0, 5))
    
    login_instruction = tk.Label(form_frame, text="Please sign in to continue", 
                                font=("Segoe UI", 10), 
                                bg="white", fg="#666666")
    login_instruction.pack(pady=(0, 30))
    
    # Custom entry style
    def create_styled_entry(parent, placeholder, show=None):
        entry_frame = tk.Frame(parent, bg="white")
        entry_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Icon and label frame
        icon_frame = tk.Frame(entry_frame, bg="white")
        icon_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Add icons for username and password
        if show is None:  # Username
            icon_label = tk.Label(icon_frame, text="👤", font=("Arial", 12), bg="white")
        else:  # Password
            icon_label = tk.Label(icon_frame, text="🔒", font=("Arial", 12), bg="white")
        
        icon_label.pack(side=tk.LEFT)
        
        field_label = tk.Label(icon_frame, text=placeholder, 
                              font=("Segoe UI", 10, "bold"), 
                              bg="white", fg="#1a365d")
        field_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Entry field with custom styling
        entry = tk.Entry(entry_frame, font=("Segoe UI", 12), 
                        relief="flat", bd=2, highlightthickness=2,
                        highlightcolor="#4a90e2", highlightbackground="#e0e0e0",
                        show=show)
        entry.pack(fill=tk.X, ipady=8)
        
        # Add focus effects
        def on_focus_in(event):
            entry.config(highlightbackground="#4a90e2")
            
        def on_focus_out(event):
            entry.config(highlightbackground="#e0e0e0")
            
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
        return entry
    
    # Username field
    username_entry = create_styled_entry(form_frame, "Username")
    
    # Password field  
    password_entry = create_styled_entry(form_frame, "Password", show="*")
    
    # Error message with better styling
    error_label = tk.Label(form_frame, text="", 
                          font=("Segoe UI", 9), 
                          bg="white", fg="#e74c3c")
    error_label.pack(pady=(0, 15))
    
    # Modern login button with improved readability
    def create_login_button():
        button_frame = tk.Frame(form_frame, bg="white")
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        login_btn = tk.Button(button_frame, text="Sign In", 
                             font=("Segoe UI", 13, "bold"),
                             bg="#1a1a1a", fg="white",  # Dark charcoal to match screen vibe
                             relief="flat", bd=0,
                             cursor="hand2",
                             padx=20, pady=14,
                             activebackground="#0d0d0d",  # Even darker when clicked
                             activeforeground="white")
        login_btn.pack(fill=tk.X)
        
        # Enhanced hover effects with dark theme colors
        def on_enter(event):
            login_btn.config(bg="#333333", fg="white")  # Lighter dark gray on hover
            
        def on_leave(event):
            login_btn.config(bg="#1a1a1a", fg="white")  # Back to dark charcoal
            
        login_btn.bind("<Enter>", on_enter)
        login_btn.bind("<Leave>", on_leave)
        
        return login_btn
    
    login_button = create_login_button()
    
    # === FOOTER SECTION ===
    
    # Version and help info
    footer_frame = tk.Frame(main_frame, bg="#f8f9fa", height=60)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
    footer_frame.pack_propagate(False)
    
    # Default credentials hint
    hint_frame = tk.Frame(footer_frame, bg="#f8f9fa")
    hint_frame.place(relx=0.5, rely=0.3, anchor="center")
    
    hint_label = tk.Label(hint_frame, text="💡 Default Login:", 
                         font=("Segoe UI", 9, "bold"), 
                         bg="#f8f9fa", fg="#666666")
    hint_label.pack()
    
    hint_details = tk.Label(hint_frame, text="manager/manager123 or sales/sales123", 
                           font=("Segoe UI", 8), 
                           bg="#f8f9fa", fg="#999999")
    hint_details.pack()
    
    # Version info
    version_label = tk.Label(footer_frame, text="v2.0 Enterprise Edition", 
                            font=("Segoe UI", 8), 
                            bg="#f8f9fa", fg="#cccccc")
    version_label.place(relx=0.5, rely=0.8, anchor="center")
    
    # === ANIMATION AND INTERACTION LOGIC ===
    
    # Return data structure
    result = {"role": None}
    
    # Enhanced login function with visual feedback
    def on_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        # Clear previous error
        error_label.config(text="")
        
        # Validation with better messaging
        if not username or not password:
            error_label.config(text="⚠️ Please enter both username and password", fg="#e74c3c")
            # Add visual feedback to the empty field
            shake_widget(username_entry if not username else password_entry)
            return
        
        # Show loading state with dark theme
        login_button.config(text="Signing In...", state="disabled", bg="#666666", fg="white")
        login_window.update()
        
        # Simulate brief loading for better UX
        login_window.after(300, lambda: complete_login(username, password))
    
    def complete_login(username, password):
        role = load_and_verify_credentials(username, password)
        if role:
            # Success animation with better contrast
            login_button.config(text="✓ Success!", bg="#27ae60", fg="white")
            error_label.config(text="✅ Login successful! Loading application...", fg="#27ae60")
            result["role"] = role
            result["username"] = username
            # Delay to show success message
            login_window.after(800, login_window.destroy)
        else:
            # Error state with dark theme - restore button to normal state
            login_button.config(text="Sign In", state="normal", bg="#1a1a1a", fg="white")
            error_label.config(text="❌ Invalid username or password. Please try again.", fg="#e74c3c")
            
            # Use safe visual feedback instead of position-based shake
            shake_widget(password_entry)  # Flash the password field border
            
            # Clear password field and focus username for retry
            password_entry.delete(0, tk.END)
            username_entry.focus_set()
    
    # Add shake animation for failed login that works with pack() layout
    def shake_widget(widget):
        """Safe shake animation using color/border effects instead of position changes"""
        def flash_error():
            try:
                # Check if widget still exists before animating
                if not widget.winfo_exists():
                    return
                
                # Save original styling
                original_bg = widget.cget("bg") if hasattr(widget, 'cget') else None
                original_highlightbg = None
                
                # For Entry widgets, use highlight color changes
                if isinstance(widget, tk.Entry):
                    try:
                        original_highlightbg = widget.cget("highlightbackground")
                        # Flash red border for error indication
                        for i in range(4):  # Flash 4 times
                            if not widget.winfo_exists():
                                break
                            widget.config(highlightbackground="#e74c3c", highlightcolor="#e74c3c")
                            widget.update_idletasks()
                            login_window.after(100)
                            
                            if not widget.winfo_exists():
                                break
                            widget.config(highlightbackground="#ffffff", highlightcolor="#ffffff")
                            widget.update_idletasks()
                            login_window.after(100)
                        
                        # Restore original colors
                        if widget.winfo_exists() and original_highlightbg:
                            widget.config(highlightbackground=original_highlightbg, highlightcolor="#4a90e2")
                    except tk.TclError:
                        pass
                        
                # For Frame widgets (like main_frame), use a subtle visual feedback
                elif isinstance(widget, tk.Frame):
                    try:
                        # Create a temporary visual indicator without disrupting layout
                        # Just update the error label with a more prominent message
                        if error_label.winfo_exists():
                            error_label.config(fg="#e74c3c", font=("Segoe UI", 10, "bold"))
                            login_window.after(1000, lambda: error_label.config(fg="#e74c3c", font=("Segoe UI", 9)) if error_label.winfo_exists() else None)
                    except tk.TclError:
                        pass
                    
            except (tk.TclError, AttributeError):
                # Widget was destroyed during animation - ignore error silently
                pass
                
        # Start animation with delay and safety check
        if widget and hasattr(widget, 'winfo_exists') and widget.winfo_exists():
            login_window.after(10, flash_error)
    
    # Configure login button command
    login_button.config(command=on_login)
    
    # Enhanced keyboard bindings
    def on_enter_key(event):
        if login_button['state'] == 'normal':
            on_login()
    
    login_window.bind("<Return>", on_enter_key)
    login_window.bind("<KP_Enter>", on_enter_key)  # Numpad Enter
    
    # Tab navigation
    username_entry.bind("<Tab>", lambda e: password_entry.focus_set())
    password_entry.bind("<Shift-Tab>", lambda e: username_entry.focus_set())
    
    # Escape to exit
    login_window.bind("<Escape>", lambda e: exit())
    
    # Auto-focus username field
    username_entry.focus_set()
    
    # Add loading animation (optional visual enhancement)
    def add_loading_dots():
        current_text = login_button.cget("text")
        if "Signing In" in current_text:
            dots = current_text.count(".")
            if dots >= 3:
                login_button.config(text="Signing In")
            else:
                login_button.config(text=current_text + ".")
            login_window.after(200, add_loading_dots)
    
    # Wait for the login window to be destroyed
    login_window.wait_window()
    
    return result["role"], result.get("username", "")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    root.title("DigiClimate Store Hub - Resilience meets innovation")
    
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
            update_supplier_callback=lambda supplier_id, supplier_name_entry, supplier_contact_entry, supplier_address_entry, *_: update_supplier(
                db_connection, cursor, supplier_id, supplier_name_entry, supplier_contact_entry, supplier_address_entry
            ),
            load_supplier_callback=lambda supplier_id, *_: load_supplier(cursor, supplier_id),
            search_suppliers_callback=lambda search_supplier_entry, *_: search_suppliers(search_supplier_entry, cursor),
            delete_supplier_callback=lambda delete_supplier_id_entry, *_: delete_supplier(
                db_connection, cursor, delete_supplier_id_entry
            ),
            add_customer_callback=lambda customer_name_entry, customer_contact_entry, customer_address_entry, *_: add_customer(
                db_connection, cursor, customer_name_entry, customer_contact_entry, customer_address_entry
            ),
            update_customer_callback=lambda customer_id, customer_name_entry, customer_contact_entry, customer_address_entry, *_: update_customer(
                db_connection, cursor, customer_id, customer_name_entry, customer_contact_entry, customer_address_entry
            ),
            load_customer_callback=lambda customer_id, *_: load_customer(cursor, customer_id),
            delete_customer_callback=lambda delete_customer_id_entry, *_: delete_customer(
                db_connection, cursor, delete_customer_id_entry
            ),
            add_item_callback=lambda sku_entry, item_name_entry, category_entry, price_entry, stock_entry, supplier_id_entry, cost_entry, *_: add_item(
                db_connection, cursor, sku_entry, item_name_entry, category_entry, price_entry, stock_entry, supplier_id_entry, cost_entry
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
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
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
        update_supplier_callback=lambda supplier_id, supplier_name_entry, supplier_contact_entry, supplier_address_entry, *_: update_supplier(
            db_connection, cursor, supplier_id, supplier_name_entry, supplier_contact_entry, supplier_address_entry
        ),
        load_supplier_callback=lambda supplier_id, *_: load_supplier(cursor, supplier_id),
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
        update_customer_callback=lambda customer_id, customer_name_entry, customer_contact_entry, customer_address_entry, *_: update_customer(
            db_connection, cursor, customer_id, customer_name_entry, customer_contact_entry, customer_address_entry
        ),
        load_customer_callback=lambda customer_id, *_: load_customer(cursor, customer_id),
        delete_customer_callback=lambda delete_customer_id_entry, *_: delete_customer(
            db_connection,
            cursor,
            delete_customer_id_entry
        ),
        add_item_callback=lambda sku_entry, item_name_entry, category_entry, price_entry, stock_entry, supplier_id_entry, cost_entry, *_: add_item(
            db_connection,
            cursor,
            sku_entry,
            item_name_entry,
            category_entry,
            price_entry,
            stock_entry,
            supplier_id_entry,
            cost_entry
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