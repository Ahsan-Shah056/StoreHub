import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import tkinter.font as tkFont  
import inventory
import customers 
import sales  
import threading
import sys
import os
from PIL import Image, ImageTk

# Add Climate Tab path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Climate Tab'))

# Standard imports
from Data_exporting import export_treeview_to_csv
from dashboard_ui import DashboardUI
from data_importing import show_customer_import_dialog, show_inventory_import_dialog, show_supplier_import_dialog
from typing import Any, Optional

# Climate Tab imports with proper path handling
CLIMATE_AVAILABLE = False
ClimateUI: Optional[Any] = None
climate_data: Optional[Any] = None

try:
    # First ensure the Climate Tab path is in sys.path
    climate_tab_path = os.path.join(os.path.dirname(__file__), 'Climate Tab')
    if climate_tab_path not in sys.path:
        sys.path.insert(0, climate_tab_path)
    
    # Now import the climate modules
    from climate_ui import ClimateUI  # type: ignore
    import climate_data  # type: ignore
    CLIMATE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Climate Tab imports failed: {e}")
    ClimateUI = None
    climate_data = None
    CLIMATE_AVAILABLE = False

# Import formatting functions from main
try:
    from main import format_treeview_values, format_treeview_text, handle_error
except ImportError:
    # Fallback functions if import fails
    def format_treeview_text(value):
        if value is None:
            return ""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            text = str(value).strip()
            if text.upper() in ['SKU', 'ID', 'N/A', 'USA', 'UK', 'CA']:
                return text.upper()
            if '@' in text and '.' in text:
                return text.lower()
            if any(char in text for char in ['-', '(', ')', '+']) and any(char.isdigit() for char in text):
                return text
            return text.title()
        return str(value)
    
    def format_treeview_values(values):
        return tuple(format_treeview_text(value) for value in values)
    
    def handle_error(error_message):
        messagebox.showerror("Error", error_message)


# Ensure there is NO root = tk.Tk() or root = ThemedTk() anywhere in this file
# Ensure there is NO widget creation at the top level in this file
# All widget creation should be inside class methods and only after root is created in main.py

def apply_styles(widget, master=None):
    # Apply custom styles to the given widget and its children
    if master is None:
        master = widget.winfo_toplevel()
    font = tkFont.Font(master=master, family="Helvetica", size=10, weight="bold")
    for child in widget.winfo_children():
        if isinstance(child, (ttk.Label, ttk.Button)):
            child.configure(font=font, foreground="#333", background="#f0f0f0")
        elif isinstance(child, ttk.Entry):
            child.configure(font=font, foreground="#555")
        elif isinstance(child, tk.Listbox):
            child.configure(font=font, foreground="#444", background="#fff")
        elif isinstance(child, ttk.Treeview):
            child.tag_configure("evenrow", background="#f9f9f9")
            child.tag_configure("oddrow", background="#e9e9e9")
        apply_styles(child, master=master)

def alternate_treeview_rows(treeview):
    # Alternate row colors for a Treeview widget
    # Configure tags in case they're not already configured
    treeview.tag_configure("evenrow", background="#f9f9f9")
    treeview.tag_configure("oddrow", background="#e9e9e9")
    
    # Apply tags to each item
    for i, item in enumerate(treeview.get_children()):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        treeview.item(item, tags=(tag,))

class SalesUI:
    # UI class for sales operations
    def __init__(self, master):
        # Title and description
        self.title_label = ttk.Label(master, text="Sales Dashboard", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=(10, 2), padx=10, anchor="w")
        self.desc_label = ttk.Label(master, text="Manage product sales, add items to cart, and complete customer checkouts.", font=("Helvetica", 12))
        self.desc_label.pack(pady=(0, 15), padx=10, anchor="w")
        # Define a custom style for blue buttons with white text for sales tab
        style = ttk.Style(master)
        style.theme_use('clam')  # Use a theme that supports custom styles
        style.configure("Blue.TButton",
                        background="#1976D2",
                        foreground="white",
                        relief="raised",
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="#1976D2")
        style.map("Blue.TButton",
                  background=[('active', '#1565C0'), ('pressed', '#0D47A1')],
                  foreground=[('active', 'white'), ('pressed', 'white')],
                  bordercolor=[('focus', '#1976D2'), ('!focus', '#1976D2')],
                  focuscolor=[('focus', '#1976D2'), ('!focus', '#1976D2')])
        self.get_customers_callback = None  # Ensure this is set before _init_purchase_tab
        self.get_employees_callback = None  # Add for employee dropdown
        self.sales_notebook = ttk.Notebook(master)
        self.sales_notebook.pack(fill='both', expand=True)
        self.purchase_tab = ttk.Frame(self.sales_notebook)
        self.sales_notebook.add(self.purchase_tab, text='Purchase')
        self._init_purchase_tab()
        # Callback attributes
        self._display_product_details_callback = None
        self.add_to_cart_callback = None
        self.remove_from_cart_callback = None
        self.update_cart_quantity_callback = None
        self.empty_cart_callback = None
        self.checkout_callback = None
        self.select_customer_callback = None
        self.get_customers_callback = None  # Add this line
        self.resend_receipt_callback = None  # Add resend receipt callback

    def _init_purchase_tab(self):
        # Title and description for Purchase subtab
        title = ttk.Label(self.purchase_tab, text="Purchase", font=("Helvetica", 14, "bold"))
        title.pack(pady=(10, 2), padx=10, anchor="w")
        desc = ttk.Label(self.purchase_tab, text="Add products to cart and complete sales for customers.", font=("Helvetica", 10))
        desc.pack(pady=(0, 10), padx=10, anchor="w")
        
        # Main container with better space management
        main_container = ttk.Frame(self.purchase_tab)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Configure main container grid weights
        main_container.grid_rowconfigure(1, weight=1)  # Cart section will expand
        main_container.grid_columnconfigure(0, weight=1)
        
        # Input section (fixed height)
        input_frame = ttk.LabelFrame(main_container, text="Order Entry", padding=10)
        input_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        # Row 1: Product SKU and Quantity
        ttk.Label(input_frame, text='Product SKU:').grid(row=0, column=0, sticky='w', padx=(0, 5), pady=2)
        self.product_id_entry = ttk.Entry(input_frame, width=15)
        self.product_id_entry.grid(row=0, column=1, padx=(0, 10), pady=2, sticky='w')
        
        ttk.Label(input_frame, text='Quantity:').grid(row=0, column=2, sticky='w', padx=(0, 5), pady=2)
        self.quantity_entry = ttk.Entry(input_frame, width=8)
        self.quantity_entry.grid(row=0, column=3, padx=(0, 10), pady=2, sticky='w')
        
        add_to_cart_btn = ttk.Button(input_frame, text='Add to Cart', command=self._on_add_to_cart, style="Blue.TButton")
        add_to_cart_btn.grid(row=0, column=4, padx=(0, 20), pady=2)
        
        # Row 2: Customer and Employee selection
        ttk.Label(input_frame, text='Customer:').grid(row=0, column=5, sticky='w', padx=(0, 5), pady=2)
        self.customer_combobox = ttk.Combobox(input_frame, state='readonly', width=20)
        self.customer_combobox.grid(row=0, column=6, padx=(0, 10), pady=2, sticky='w')
        self.customer_combobox.bind('<<ComboboxSelected>>', self._on_customer_selected)
        
        ttk.Label(input_frame, text='Employee:').grid(row=0, column=7, sticky='w', padx=(0, 5), pady=2)
        self.employee_combobox = ttk.Combobox(input_frame, state='readonly', width=20)
        self.employee_combobox.grid(row=0, column=8, padx=(0, 5), pady=2, sticky='w')
        
        self._populate_customers()
        self._populate_employees()
        
        # Cart and checkout section (expandable)
        cart_checkout_frame = ttk.Frame(main_container)
        cart_checkout_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 5))
        cart_checkout_frame.grid_rowconfigure(0, weight=1)
        cart_checkout_frame.grid_columnconfigure(0, weight=1)
        
        # Cart section
        cart_frame = ttk.LabelFrame(cart_checkout_frame, text="Shopping Cart", padding=5)
        cart_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Cart tree with moderate height
        cart_container = ttk.Frame(cart_frame)
        cart_container.pack(fill='both', expand=True)
        
        self.cart_tree = ttk.Treeview(cart_container, columns=('SKU', 'Name', 'Quantity', 'Price', 'Total'), show='headings', height=8)
        self.cart_tree.heading('SKU', text='SKU')
        self.cart_tree.heading('Name', text='Name')
        self.cart_tree.heading('Quantity', text='Quantity')
        self.cart_tree.heading('Price', text='Price')
        self.cart_tree.heading('Total', text='Total')
        
        # Set column widths
        self.cart_tree.column('SKU', width=100)
        self.cart_tree.column('Name', width=200)
        self.cart_tree.column('Quantity', width=80)
        self.cart_tree.column('Price', width=80)
        self.cart_tree.column('Total', width=80)
        
        # Add scrollbar for cart
        cart_scrollbar = ttk.Scrollbar(cart_container, orient='vertical', command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side='left', fill='both', expand=True)
        cart_scrollbar.pack(side='right', fill='y')
        
        # Right panel for totals and actions
        right_panel = ttk.Frame(cart_checkout_frame)
        right_panel.grid(row=0, column=1, sticky='ns', padx=(5, 0))
        
        # Totals section
        totals_frame = ttk.LabelFrame(right_panel, text="Order Total", padding=10)
        totals_frame.pack(fill='x', pady=(0, 10))
        
        self.subtotal_label = ttk.Label(totals_frame, text="Subtotal: $0.00", font=("Helvetica", 10))
        self.subtotal_label.pack(anchor='w')
        
        self.taxes_label = ttk.Label(totals_frame, text="Taxes: $0.00", font=("Helvetica", 10))
        self.taxes_label.pack(anchor='w')
        
        self.total_label = ttk.Label(totals_frame, text="Total: $0.00", font=("Helvetica", 12, "bold"))
        self.total_label.pack(anchor='w')
        
        # Actions section
        actions_frame = ttk.LabelFrame(right_panel, text="Actions", padding=10)
        actions_frame.pack(fill='x', pady=(0, 10))
        
        checkout_btn = ttk.Button(actions_frame, text='Checkout', command=self._on_checkout, style="Blue.TButton")
        checkout_btn.pack(fill='x', pady=(0, 5))
        
        empty_cart_btn = ttk.Button(actions_frame, text='Empty Cart', command=self._on_empty_cart, style="Blue.TButton")
        empty_cart_btn.pack(fill='x', pady=(0, 5))
        
        send_receipt_btn = ttk.Button(actions_frame, text='Resend Last Receipt', command=self._on_resend_receipt, style="Blue.TButton")
        send_receipt_btn.pack(fill='x')
        
        # Status section
        self.purchase_status = ttk.Label(right_panel, text='', font=("Helvetica", 9))
        self.purchase_status.pack(pady=(10, 0))
        
        # Compact receipt section at bottom
        receipt_frame = ttk.LabelFrame(main_container, text="Last Receipt", padding=5)
        receipt_frame.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        
        self.receipt_tree = ttk.Treeview(receipt_frame, columns=('SKU', 'Name', 'Quantity', 'Price', 'Total'), show='headings', height=3)
        self.receipt_tree.heading('SKU', text='SKU')
        self.receipt_tree.heading('Name', text='Name')
        self.receipt_tree.heading('Quantity', text='Quantity')
        self.receipt_tree.heading('Price', text='Price')
        self.receipt_tree.heading('Total', text='Total')
        
        # Set column widths for receipt tree
        self.receipt_tree.column('SKU', width=80)
        self.receipt_tree.column('Name', width=150)
        self.receipt_tree.column('Quantity', width=60)
        self.receipt_tree.column('Price', width=60)
        self.receipt_tree.column('Total', width=60)
        
        self.receipt_tree.pack(fill='x')
        # Remove View Customers button and customers_tree from sales tab

    def _populate_customers(self):
        if self.get_customers_callback:
            customers_list = self.get_customers_callback()
            self.customers_map = {f"{c['name']} (ID: {c['customer_id']})": c['customer_id'] for c in customers_list}
            self.customer_combobox['values'] = list(self.customers_map.keys())
            if self.customer_combobox['values']:
                self.customer_combobox.current(0)
                self._on_customer_selected()
        else:
            self.customer_combobox['values'] = []

    def _populate_employees(self):
        if self.get_employees_callback:
            employees_list = self.get_employees_callback()
            self.employees_map = {f"{e['name']} (ID: {e['employee_id']})": e['employee_id'] for e in employees_list}
            self.employee_combobox['values'] = list(self.employees_map.keys())
            if self.employee_combobox['values']:
                self.employee_combobox.current(0)
        else:
            self.employee_combobox['values'] = []

    def _on_customer_selected(self, event=None):
        if hasattr(self, 'customers_map'):
            selected = self.customer_combobox.get()
            customer_id = self.customers_map.get(selected)
            if self.select_customer_callback and customer_id is not None:
                self.select_customer_callback(customer_id)

    def _on_add_to_cart(self):
        sku = self.product_id_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        if not sku or not quantity.isdigit():
            self.purchase_status.config(text='Please enter a valid SKU and quantity.', foreground='red')
            return
        if self.add_to_cart_callback:
            self.add_to_cart_callback(self.product_id_entry, self.quantity_entry, self.cart_tree)
        self.purchase_status.config(text=f"Added {quantity} of SKU {sku} to cart.", foreground='green')
        self.product_id_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        alternate_treeview_rows(self.cart_tree)

    def _on_checkout(self):
        # Check if customer is selected
        selected_customer = self.customer_combobox.get()
        if not selected_customer:
            messagebox.showerror("Error", "Please select a customer before checkout")
            return
            
        if self.checkout_callback:
            selected_employee = self.employee_combobox.get()
            employee_id = self.employees_map.get(selected_employee)
            
            # Set the customer ID before checkout
            if self.select_customer_callback and hasattr(self, 'customers_map'):
                customer_id = self.customers_map.get(selected_customer)
                if customer_id:
                    self.select_customer_callback(customer_id)
                
            self.checkout_callback(self.cart_tree, self.receipt_tree, employee_id)
        self.purchase_status.config(text="Checkout complete.", foreground='green')
        alternate_treeview_rows(self.receipt_tree)

    def _on_empty_cart(self):
        if self.empty_cart_callback:
            self.empty_cart_callback(self.cart_tree)
        self.purchase_status.config(text="Cart emptied.", foreground='blue')

    def _on_resend_receipt(self):
        # Resend the last receipt to customer email
        if self.resend_receipt_callback:
            self.resend_receipt_callback()
        else:
            messagebox.showinfo("Feature Unavailable", "Resend receipt feature not available")

    def _threaded_add_to_cart(self):
        threading.Thread(target=self._on_add_to_cart).start()

    def _threaded_checkout(self):
        threading.Thread(target=self._on_checkout).start()

    def _threaded_empty_cart(self):
        threading.Thread(target=self._on_empty_cart).start()

class CustomerUI:
    def __init__(self, master):
        # Title and description
        self.title_label = ttk.Label(master, text="Customers Dashboard", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=(10, 2), padx=10, anchor="w")
        self.desc_label = ttk.Label(master, text="Add, view, and manage customer information.", font=("Helvetica", 12))
        self.desc_label.pack(pady=(0, 15), padx=10, anchor="w")
        self.frame = ttk.LabelFrame(master, text="Customer", padding="10")
        self.frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Configure frame grid weights for proper expansion
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Sub-tabs for Add, Delete (remove Update tab)
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        # Add Tab
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Add")
        self.add_customer_name_label = ttk.Label(self.add_tab, text="Name:")
        self.add_customer_name_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.add_customer_name_entry = ttk.Entry(self.add_tab, width=20)
        self.add_customer_name_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.add_customer_contact_label = ttk.Label(self.add_tab, text="Contact Info:")
        self.add_customer_contact_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.add_customer_contact_entry = ttk.Entry(self.add_tab, width=20)
        self.add_customer_contact_entry.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        self.add_customer_address_label = ttk.Label(self.add_tab, text="Address:")
        self.add_customer_address_label.grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.add_customer_address_entry = ttk.Entry(self.add_tab, width=20)
        self.add_customer_address_entry.grid(row=2, column=1, sticky=tk.W, padx=2, pady=2)
        self.add_customer_button = ttk.Button(self.add_tab, text="Add Customer", command=self._threaded_add_customer, style="Blue.TButton")
        self.add_customer_button.grid(row=3, column=0, columnspan=2, pady=5)
        # Add title and description to Add subtab
        add_title = ttk.Label(self.add_tab, text="Add Customer", font=("Helvetica", 14, "bold"))
        add_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        add_desc = ttk.Label(self.add_tab, text="Enter customer details and add them to the system.", font=("Helvetica", 10))
        add_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        
        # Update Tab
        self.update_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.update_tab, text="Update")
        
        # Customer ID field for update
        self.update_customer_id_label = ttk.Label(self.update_tab, text="Customer ID:")
        self.update_customer_id_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_customer_id_entry = ttk.Entry(self.update_tab, width=10)
        self.update_customer_id_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        
        # Load customer button
        self.load_customer_button = ttk.Button(self.update_tab, text="Load Customer", command=self._load_customer_for_update, style="Blue.TButton")
        self.load_customer_button.grid(row=0, column=2, padx=5, pady=2)
        
        # Update form fields
        self.update_customer_name_label = ttk.Label(self.update_tab, text="Name:")
        self.update_customer_name_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_customer_name_entry = ttk.Entry(self.update_tab, width=20)
        self.update_customer_name_entry.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        
        self.update_customer_contact_label = ttk.Label(self.update_tab, text="Contact Info:")
        self.update_customer_contact_label.grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_customer_contact_entry = ttk.Entry(self.update_tab, width=20)
        self.update_customer_contact_entry.grid(row=2, column=1, sticky=tk.W, padx=2, pady=2)
        
        self.update_customer_address_label = ttk.Label(self.update_tab, text="Address:")
        self.update_customer_address_label.grid(row=3, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_customer_address_entry = ttk.Entry(self.update_tab, width=20)
        self.update_customer_address_entry.grid(row=3, column=1, sticky=tk.W, padx=2, pady=2)
        
        # Update button
        self.update_customer_button = ttk.Button(self.update_tab, text="Update Customer", command=self._threaded_update_customer, style="Blue.TButton")
        self.update_customer_button.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Add title and description to Update subtab
        update_title = ttk.Label(self.update_tab, text="Update Customer", font=("Helvetica", 14, "bold"))
        update_title.grid(row=0, column=3, sticky=tk.W, padx=10, pady=(10,2))
        update_desc = ttk.Label(self.update_tab, text="Load a customer by ID and update their information.", font=("Helvetica", 10))
        update_desc.grid(row=1, column=3, sticky=tk.W, padx=10, pady=(0,10))
        
        # Delete Tab
        self.delete_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.delete_tab, text="Delete")
        self.delete_customer_id_label = ttk.Label(self.delete_tab, text="Customer ID:")
        self.delete_customer_id_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.delete_customer_id_entry = ttk.Entry(self.delete_tab, width=10)
        self.delete_customer_id_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.delete_customer_button = ttk.Button(self.delete_tab, text="Delete Customer", command=self._threaded_delete_customer, style="Blue.TButton")
        self.delete_customer_button.grid(row=1, column=0, columnspan=2, pady=5)
        # Add title and description to Delete subtab
        del_title = ttk.Label(self.delete_tab, text="Delete Customer", font=("Helvetica", 14, "bold"))
        del_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        del_desc = ttk.Label(self.delete_tab, text="Remove a customer from the system by their ID.", font=("Helvetica", 10))
        del_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        # Customer Listbox and Treeview (always visible)
        self.customer_tree = ttk.Treeview(self.frame, columns=('ID', 'Name', 'Contact Info', 'Address'), show='headings', height=8)
        self.customer_tree.heading('ID', text='ID')
        self.customer_tree.heading('Name', text='Name')
        self.customer_tree.heading('Contact Info', text='Contact Info')
        self.customer_tree.heading('Address', text='Address')
        self.customer_tree.grid(row=0, column=1, rowspan=5, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=5)
        
        # Configure grid weights for proper expansion
        self.frame.rowconfigure(0, weight=1)  # Tree row expands
        self.frame.rowconfigure(1, weight=0)  # Button rows fixed  
        self.frame.rowconfigure(2, weight=0)
        self.frame.rowconfigure(3, weight=0)
        self.frame.rowconfigure(4, weight=0)
        self.frame.columnconfigure(0, weight=0)  # Button column fixed
        self.frame.columnconfigure(1, weight=1)  # Tree column expands
        # Add View Customers button to customers tab
        self.view_customers_button = ttk.Button(self.frame, text="View Customers", command=self._on_view_customers, style="Blue.TButton")
        self.view_customers_button.grid(row=2, column=0, pady=10, sticky=tk.W)
        # Add Export Data button next to View Customers
        self.export_data_button = ttk.Button(self.frame, text="Export Data", command=self._on_export_data, style="Blue.TButton")
        self.export_data_button.grid(row=3, column=0, pady=10, sticky=tk.W)
        # Add Import Data button below Export Data
        self.import_data_button = ttk.Button(self.frame, text="Import Data", command=self._on_import_data, style="Blue.TButton")
        self.import_data_button.grid(row=4, column=0, pady=10, sticky=tk.W)
        # Do not auto-populate customer_listbox or customer_tree on init
        self.view_customers_callback = None
    def _threaded_search_customer(self):
        threading.Thread(target=self.search_customer).start()
    def _threaded_add_customer(self):
        threading.Thread(target=self.add_customer).start()
    def _threaded_update_customer(self):
        threading.Thread(target=self.update_customer).start()
    def _threaded_delete_customer(self):
        threading.Thread(target=self.delete_customer).start()
    def search_customer(self):
        if self.search_customer_callback:
            self.search_customer_callback(self.customer_listbox)
    def view_customers(self):
        if self.view_customers_callback:
            self.view_customers_callback(self.customer_tree)
    def add_customer(self):
        if self.add_customer_callback:
            self.add_customer_callback(
                self.add_customer_name_entry,
                self.add_customer_contact_entry,
                self.add_customer_address_entry
            )
            self.add_customer_name_entry.delete(0, tk.END)
            self.add_customer_contact_entry.delete(0, tk.END)
            self.add_customer_address_entry.delete(0, tk.END)
            self.add_customer_name_entry.focus_set()
    
    def _load_customer_for_update(self):
        """Load customer data into update form"""
        if hasattr(self, 'load_customer_callback') and self.load_customer_callback:
            customer_id = self.update_customer_id_entry.get().strip()
            if customer_id:
                try:
                    customer_data = self.load_customer_callback(customer_id)
                    if customer_data:
                        # Populate the update form fields
                        self.update_customer_name_entry.delete(0, tk.END)
                        self.update_customer_name_entry.insert(0, customer_data.get('name', ''))
                        
                        self.update_customer_contact_entry.delete(0, tk.END)
                        self.update_customer_contact_entry.insert(0, customer_data.get('contact_info', ''))
                        
                        self.update_customer_address_entry.delete(0, tk.END)
                        self.update_customer_address_entry.insert(0, customer_data.get('address', ''))
                        
                        messagebox.showinfo("Success", f"Customer {customer_data.get('name', '')} loaded successfully!")
                    else:
                        messagebox.showerror("Error", f"Customer with ID {customer_id} not found.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load customer: {str(e)}")
            else:
                messagebox.showwarning("Warning", "Please enter a Customer ID.")
    
    def update_customer(self):
        if hasattr(self, 'update_customer_callback') and self.update_customer_callback:
            customer_id = self.update_customer_id_entry.get().strip()
            if customer_id:
                self.update_customer_callback(
                    customer_id,
                    self.update_customer_name_entry,
                    self.update_customer_contact_entry,
                    self.update_customer_address_entry
                )
                # Clear the form after successful update
                self.update_customer_id_entry.delete(0, tk.END)
                self.update_customer_name_entry.delete(0, tk.END)
                self.update_customer_contact_entry.delete(0, tk.END)
                self.update_customer_address_entry.delete(0, tk.END)
                self.update_customer_id_entry.focus_set()
            else:
                messagebox.showwarning("Warning", "Please enter a Customer ID.")
    
    def delete_customer(self):
        if self.delete_customer_callback:
            self.delete_customer_callback(self.delete_customer_id_entry)
            self.delete_customer_id_entry.delete(0, tk.END)
            self.delete_customer_id_entry.focus_set()
    def _on_view_customers(self):
        if self.view_customers_callback:
            self.view_customers_callback(self.customer_tree)
            alternate_treeview_rows(self.customer_tree)
    def _on_export_data(self):
        export_treeview_to_csv(self.customer_tree, self.frame)
    
    def _on_import_data(self):
        # Create a refresh callback that updates the customer tree
        def refresh_customers():
            if self.view_customers_callback:
                self.view_customers_callback(self.customer_tree)
                alternate_treeview_rows(self.customer_tree)
        
        # Show the import dialog with refresh callback
        show_customer_import_dialog(self.frame, refresh_customers)

class EmployeeUI:
    def __init__(self, master):
        self.frame = ttk.LabelFrame(master, text="Employee", padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        # Sub-tabs for Add, Update, Delete
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NW)
        # Add Tab
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Add")
        self.add_employee_name_label = ttk.Label(self.add_tab, text="Name:")
        self.add_employee_name_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.add_employee_name_entry = ttk.Entry(self.add_tab, width=20)
        self.add_employee_name_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.add_employee_button = ttk.Button(self.add_tab, text="Add Employee", command=self._threaded_add_employee)
        self.add_employee_button.grid(row=2, column=0, columnspan=2, pady=5)
        # Add title and description to Add subtab
        add_title = ttk.Label(self.add_tab, text="Add Employee", font=("Helvetica", 14, "bold"))
        add_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        add_desc = ttk.Label(self.add_tab, text="Add a new employee to the system.", font=("Helvetica", 10))
        add_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        # Update Tab
        self.update_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.update_tab, text="Update")
        self.update_employee_id_label = ttk.Label(self.update_tab, text="Employee ID:")
        self.update_employee_id_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_employee_id_entry = ttk.Entry(self.update_tab, width=10)
        self.update_employee_id_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.update_employee_name_label = ttk.Label(self.update_tab, text="Name:")
        self.update_employee_name_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_employee_name_entry = ttk.Entry(self.update_tab, width=20)
        self.update_employee_name_entry.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        self.update_employee_button = ttk.Button(self.update_tab, text="Update Employee", command=self._threaded_update_employee)
        self.update_employee_button.grid(row=3, column=0, columnspan=2, pady=5)
        # Add title and description to Update subtab
        upd_title = ttk.Label(self.update_tab, text="Update Employee", font=("Helvetica", 14, "bold"))
        upd_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        upd_desc = ttk.Label(self.update_tab, text="Update employee details by their ID.", font=("Helvetica", 10))
        upd_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        # Delete Tab
        self.delete_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.delete_tab, text="Delete")
        self.delete_employee_id_label = ttk.Label(self.delete_tab, text="Employee ID:")
        self.delete_employee_id_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.delete_employee_id_entry = ttk.Entry(self.delete_tab, width=10)
        self.delete_employee_id_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.delete_employee_button = ttk.Button(self.delete_tab, text="Delete Employee", command=self._threaded_delete_employee)
        self.delete_employee_button.grid(row=1, column=0, columnspan=2, pady=5)
        # Add title and description to Delete subtab
        del_title = ttk.Label(self.delete_tab, text="Delete Employee", font=("Helvetica", 14, "bold"))
        del_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        del_desc = ttk.Label(self.delete_tab, text="Remove an employee from the system by their ID.", font=("Helvetica", 10))
        del_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        # Employees Treeview (always visible)
        self.employee_tree = ttk.Treeview(self.frame, columns=('ID', 'Name'), show='headings', height=10)
        self.employee_tree.heading('ID', text='ID')
        self.employee_tree.heading('Name', text='Name')
        self.employee_tree.grid(row=0, column=1, rowspan=4, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=5)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(1, weight=1)
        # Do not auto-populate employee_tree on init
    def _threaded_search_employee(self):
        threading.Thread(target=self.search_employee).start()
    def _threaded_add_employee(self):
        threading.Thread(target=self.add_employee).start()
    def _threaded_update_employee(self):
        threading.Thread(target=self.update_employee).start()
    def _threaded_delete_employee(self):
        threading.Thread(target=self.delete_employee).start()
    def search_employee(self):
        if self.search_employee_callback:
            self.search_employee_callback(self.employee_listbox)
    def view_employees(self):
        if self.view_employees_callback:
            self.view_employees_callback(self.employee_tree)
            alternate_treeview_rows(self.employee_tree)
    def update_employee(self):
        if self.update_employee_callback:
            self.update_employee_callback(self.update_employee_id_entry, self.update_employee_name_entry, self.update_employee_role_entry)
            self.update_employee_id_entry.delete(0, tk.END)
            self.update_employee_name_entry.delete(0, tk.END)
            self.update_employee_role_entry.delete(0, tk.END)
            self.update_employee_id_entry.focus_set()
    def add_employee(self):
        if self.add_employee_callback:
            self.add_employee_callback(
                self.add_employee_name_entry,
                self.add_employee_role_entry
            )
            self.add_employee_name_entry.delete(0, tk.END)
            self.add_employee_role_entry.delete(0, tk.END)
            self.add_employee_name_entry.focus_set()
    def delete_employee(self):
        if self.delete_employee_callback:
            self.delete_employee_callback(self.delete_employee_id_entry)
            self.delete_employee_id_entry.delete(0, tk.END)
            self.delete_employee_id_entry.focus_set()

class InventoryUI:
    def __init__(self, master):
        # Title and description
        self.title_label = ttk.Label(master, text="Inventory Dashboard", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=(10, 2), padx=10, anchor="w")
        self.desc_label = ttk.Label(master, text="Add, view, and manage inventory items and stock levels.", font=("Helvetica", 12))
        self.desc_label.pack(pady=(0, 15), padx=10, anchor="w")
        self.frame = ttk.LabelFrame(master, text="Inventory", padding="10")
        self.frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Configure frame grid weights for proper expansion
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        # Define a custom style for blue buttons with white text for inventory tab
        style = ttk.Style(master)
        style.theme_use('clam')
        style.configure("Blue.TButton",
                        background="#1976D2",
                        foreground="white",
                        relief="raised",
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="#1976D2")
        style.map("Blue.TButton",
                  background=[('active', '#1565C0'), ('pressed', '#0D47A1')],
                  foreground=[('active', 'white'), ('pressed', 'white')],
                  bordercolor=[('focus', '#1976D2'), ('!focus', '#1976D2')],
                  focuscolor=[('focus', '#1976D2'), ('!focus', '#1976D2')])
        # Add Tab
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Add")
        # Add labels for each entry box
        self.sku_label = ttk.Label(self.add_tab, text="SKU:")
        self.sku_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.sku_entry = ttk.Entry(self.add_tab, width=15)
        self.sku_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.item_name_label = ttk.Label(self.add_tab, text="Name:")
        self.item_name_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.item_name_entry = ttk.Entry(self.add_tab, width=15)
        self.item_name_entry.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        self.category_label = ttk.Label(self.add_tab, text="Category:")
        self.category_label.grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.category_entry = ttk.Entry(self.add_tab, width=15)
        self.category_entry.grid(row=2, column=1, sticky=tk.W, padx=2, pady=2)
        self.price_label = ttk.Label(self.add_tab, text="Price:")
        self.price_label.grid(row=3, column=0, sticky=tk.W, padx=2, pady=2)
        self.price_entry = ttk.Entry(self.add_tab, width=15)
        self.price_entry.grid(row=3, column=1, sticky=tk.W, padx=2, pady=2)
        self.stock_label = ttk.Label(self.add_tab, text="Stock:")
        self.stock_label.grid(row=4, column=0, sticky=tk.W, padx=2, pady=2)
        self.stock_entry = ttk.Entry(self.add_tab, width=15)
        self.stock_entry.grid(row=4, column=1, sticky=tk.W, padx=2, pady=2)
        self.supplier_id_label = ttk.Label(self.add_tab, text="Supplier ID:")
        self.supplier_id_label.grid(row=5, column=0, sticky=tk.W, padx=2, pady=2)
        self.supplier_id_entry = ttk.Entry(self.add_tab, width=15)
        self.supplier_id_entry.grid(row=5, column=1, sticky=tk.W, padx=2, pady=2)
        self.cost_label = ttk.Label(self.add_tab, text="Cost:")
        self.cost_label.grid(row=6, column=0, sticky=tk.W, padx=2, pady=2)
        self.cost_entry = ttk.Entry(self.add_tab, width=15)
        self.cost_entry.grid(row=6, column=1, sticky=tk.W, padx=2, pady=2)
        self.cost_entry.insert(0, "0.00")  # Default value
        self.add_item_button = ttk.Button(self.add_tab, text="Add Item", command=self._threaded_add_item, style="Blue.TButton")
        self.add_item_button.grid(row=7, column=0, columnspan=2, pady=5)
        # Add title and description to Add subtab
        add_title = ttk.Label(self.add_tab, text="Add Item", font=("Helvetica", 14, "bold"))
        add_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        add_desc = ttk.Label(self.add_tab, text="Add a new product to the inventory.", font=("Helvetica", 10))
        add_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        # Remove Update Tab and all related widgets/methods
        # Delete Tab
        self.delete_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.delete_tab, text="Delete")
        self.delete_item_sku_label = ttk.Label(self.delete_tab, text="SKU:")
        self.delete_item_sku_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.delete_item_sku_entry = ttk.Entry(self.delete_tab, width=15)
        self.delete_item_sku_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.delete_item_button = ttk.Button(self.delete_tab, text="Delete Item", command=self._threaded_delete_item, style="Blue.TButton")
        self.delete_item_button.grid(row=1, column=0, columnspan=2, pady=5)
        # Add title and description to Delete subtab
        del_title = ttk.Label(self.delete_tab, text="Delete Item", font=("Helvetica", 14, "bold"))
        del_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        del_desc = ttk.Label(self.delete_tab, text="Remove an item from inventory by SKU.", font=("Helvetica", 10))
        del_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        # Adjust Stock Tab (moved from main frame)
        self.adjust_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.adjust_tab, text="Adjust Stock")
        self.adjust_sku_label = ttk.Label(self.adjust_tab, text="SKU:")
        self.adjust_sku_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.adjust_sku_entry = ttk.Entry(self.adjust_tab, width=15)
        self.adjust_sku_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.adjust_quantity_label = ttk.Label(self.adjust_tab, text="Quantity Change:")
        self.adjust_quantity_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.adjust_quantity_entry = ttk.Entry(self.adjust_tab, width=15)
        self.adjust_quantity_entry.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        # Employee dropdown
        self.adjust_employee_label = ttk.Label(self.adjust_tab, text="Employee:")
        self.adjust_employee_label.grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.adjust_employee_combobox = ttk.Combobox(self.adjust_tab, state='readonly', width=25)
        self.adjust_employee_combobox.grid(row=2, column=1, padx=2, pady=2)
        self.get_employees_callback = None
        self._populate_employees()
        # Reason label and entry
        self.adjust_reason_label = ttk.Label(self.adjust_tab, text="Reason:")
        self.adjust_reason_label.grid(row=3, column=0, sticky=tk.W, padx=2, pady=2)
        self.adjust_reason_entry = ttk.Entry(self.adjust_tab, width=25)
        self.adjust_reason_entry.grid(row=3, column=1, sticky=tk.W, padx=2, pady=2)
        self.adjust_stock_button = ttk.Button(self.adjust_tab, text="Adjust Stock", command=self._threaded_adjust_stock, style="Blue.TButton")
        self.adjust_stock_button.grid(row=4, column=0, columnspan=2, pady=5)
        # Add title and description to Adjust Stock subtab
        adj_title = ttk.Label(self.adjust_tab, text="Adjust Stock", font=("Helvetica", 14, "bold"))
        adj_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        adj_desc = ttk.Label(self.adjust_tab, text="Increase the stock quantity for a product.", font=("Helvetica", 10))
        adj_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        # Inventory Treeview (always visible)
        self.inventory_tree = ttk.Treeview(self.frame, columns=('SKU', 'Name', 'Category', 'Price', 'Stock', 'Supplier ID', 'Cost'), show='headings')
        for col in ('SKU', 'Name', 'Category', 'Price', 'Stock', 'Supplier ID', 'Cost'):
            self.inventory_tree.heading(col, text=col)
            
        # Set appropriate column widths
        self.inventory_tree.column('SKU', width=80, minwidth=60)
        self.inventory_tree.column('Name', width=180, minwidth=100)
        self.inventory_tree.column('Category', width=120, minwidth=80)
        self.inventory_tree.column('Price', width=80, minwidth=60)
        self.inventory_tree.column('Stock', width=80, minwidth=60)
        self.inventory_tree.column('Supplier ID', width=100, minwidth=80)
        self.inventory_tree.column('Cost', width=80, minwidth=60)
        
        # Add horizontal scrollbar
        self.inventory_tree_scroll_x = ttk.Scrollbar(self.frame, orient='horizontal', command=self.inventory_tree.xview)
        self.inventory_tree.configure(xscrollcommand=self.inventory_tree_scroll_x.set)
        
        # Grid layout for tree and scrollbar with proper weights
        self.inventory_tree.grid(row=0, column=1, rowspan=3, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=5)
        self.inventory_tree_scroll_x.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=10)
        
        # Buttons in column 0
        self.view_inventory_button = ttk.Button(self.frame, text="View Inventory", command=self._threaded_view_inventory, style="Blue.TButton")
        self.view_inventory_button.grid(row=4, column=0, pady=10, sticky=tk.W)
        self.export_data_button = ttk.Button(self.frame, text="Export Data", command=self._on_export_data, style="Blue.TButton")
        self.export_data_button.grid(row=5, column=0, pady=10, sticky=tk.W)
        # Add Import Data button below Export Data
        self.import_data_button = ttk.Button(self.frame, text="Import Data", command=self._on_import_data, style="Blue.TButton")
        self.import_data_button.grid(row=6, column=0, pady=10, sticky=tk.W)
        
        # Configure grid weights for proper expansion
        self.frame.rowconfigure(0, weight=1)  # Tree row expands
        self.frame.rowconfigure(1, weight=0)  # Other rows fixed
        self.frame.rowconfigure(2, weight=0)
        self.frame.rowconfigure(3, weight=0)  # Scrollbar row
        self.frame.rowconfigure(4, weight=0)  # Button rows
        self.frame.rowconfigure(5, weight=0)
        self.frame.rowconfigure(6, weight=0)
        self.frame.columnconfigure(0, weight=0)  # Button column fixed
        self.frame.columnconfigure(1, weight=1)  # Tree column expands
        # Do not auto-populate inventory_tree on init

    def _populate_employees(self):
        if self.get_employees_callback:
            employees_list = self.get_employees_callback()
            self.employees_map = {f"{e['name']} (ID: {e['employee_id']})": e['employee_id'] for e in employees_list}
            self.adjust_employee_combobox['values'] = list(self.employees_map.keys())
            if self.adjust_employee_combobox['values']:
                self.adjust_employee_combobox.current(0)
        else:
            self.adjust_employee_combobox['values'] = []

    def _threaded_add_item(self):
        threading.Thread(target=self.add_item).start()
    def _threaded_delete_item(self):
        threading.Thread(target=self.delete_item).start()
    def _threaded_adjust_stock(self):
        threading.Thread(target=self.adjust_stock).start()
    def _threaded_view_inventory(self):
        threading.Thread(target=self.view_inventory).start()
    def add_item(self):
        if self.add_item_callback:
            self.add_item_callback(
                self.sku_entry, self.item_name_entry, self.category_entry, self.price_entry, self.stock_entry, self.supplier_id_entry, self.cost_entry
            )
            self.sku_entry.delete(0, tk.END)
            self.item_name_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.stock_entry.delete(0, tk.END)
            self.supplier_id_entry.delete(0, tk.END)
            self.cost_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.stock_entry.delete(0, tk.END)
            self.supplier_id_entry.delete(0, tk.END)
            self.sku_entry.focus_set()
    def delete_item(self):
        if self.delete_item_callback:
            self.delete_item_callback(self.delete_item_sku_entry)
            self.delete_item_sku_entry.delete(0, tk.END)
            self.delete_item_sku_entry.focus_set()
    def view_inventory(self):
        if self.view_inventory_callback:
            self.view_inventory_callback(self.inventory_tree)
            alternate_treeview_rows(self.inventory_tree)
    def adjust_stock(self):
        if self.adjust_stock_callback:
            selected_employee = self.adjust_employee_combobox.get()
            employee_id = self.employees_map.get(selected_employee)
            reason = self.adjust_reason_entry.get()
            self.adjust_stock_callback(self.adjust_sku_entry, self.adjust_quantity_entry, employee_id, reason)
            self.adjust_sku_entry.delete(0, tk.END)
            self.adjust_quantity_entry.delete(0, tk.END)
            self.adjust_reason_entry.delete(0, tk.END)
            self.adjust_sku_entry.focus_set()
    def _on_export_data(self):
        export_treeview_to_csv(self.inventory_tree, self.frame)
    
    def _on_import_data(self):
        # Create a refresh callback that updates the inventory tree
        def refresh_inventory():
            if self.view_inventory_callback:
                self.view_inventory_callback(self.inventory_tree)
                alternate_treeview_rows(self.inventory_tree)
        
        # Show the import dialog with refresh callback
        show_inventory_import_dialog(self.frame, refresh_inventory)

class ReportsUI:
    def __init__(self, master):
        self.get_customers_callback = None
        self.customers_map = {}
        self.frame = ttk.Frame(master, padding="10")
        self.frame.pack(fill='both', expand=True)

        # Title
        self.title_label = ttk.Label(self.frame, text="Reports Dashboard", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=(10, 2), padx=10, anchor="w")
        self.desc_label = ttk.Label(self.frame, text="Generate and view business reports.", font=("Helvetica", 12))
        self.desc_label.pack(pady=(0, 15), padx=10, anchor="w")

        # Section for report options
        self.options_frame = ttk.Frame(self.frame)
        self.options_frame.pack(fill='x', padx=10, pady=5)

        # Define a custom style for blue buttons with white text for reports tab
        style = ttk.Style(master)
        style.theme_use('clam')
        style.configure("Blue.TButton",
                        background="#1976D2",
                        foreground="white",
                        relief="raised",
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="#1976D2")
        style.map("Blue.TButton",
                  background=[('active', '#1565C0'), ('pressed', '#0D47A1')],
                  foreground=[('active', 'white'), ('pressed', 'white')],
                  bordercolor=[('focus', '#1976D2'), ('!focus', '#1976D2')],
                  focuscolor=[('focus', '#1976D2'), ('!focus', '#1976D2')])

        # Low Stock Report
        self.low_stock_btn = ttk.Button(self.options_frame, text="Low Stock Report", command=self._on_low_stock_report, style="Blue.TButton")
        self.low_stock_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Sales by Employee
        self.employee_label = ttk.Label(self.options_frame, text="Sales by Employee:")
        self.employee_label.grid(row=2, column=1, padx=5, pady=5, sticky="e")
        self.employee_combobox = ttk.Combobox(self.options_frame, state='readonly', width=18)
        self.employee_combobox.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        self.sales_by_employee_btn = ttk.Button(self.options_frame, text="Show", command=self._on_sales_by_employee_report, style="Blue.TButton")
        self.sales_by_employee_btn.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # Supplier Purchase Report
        self.supplier_label = ttk.Label(self.options_frame, text="Supplier Purchases:")
        self.supplier_label.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.supplier_combobox = ttk.Combobox(self.options_frame, state='readonly', width=18)
        self.supplier_combobox.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        self.supplier_purchase_btn = ttk.Button(self.options_frame, text="Show", command=self._on_supplier_purchase_report, style="Blue.TButton")
        self.supplier_purchase_btn.grid(row=0, column=6, padx=5, pady=5, sticky="ew")

        # Inventory Adjustment History
        self.adjustment_history_btn = ttk.Button(self.options_frame, text="Inventory Adjustment History", command=self._on_adjustment_history_report, style="Blue.TButton")
        self.adjustment_history_btn.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Inventory Value Report
        self.inventory_value_btn = ttk.Button(self.options_frame, text="Inventory Value Report", command=self._on_inventory_value_report, style="Blue.TButton")
        self.inventory_value_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Customer Purchase History Report
        self.customer_label = ttk.Label(self.options_frame, text="Customer Purchase History:")
        self.customer_label.grid(row=2, column=4, padx=5, pady=5, sticky="e")
        self.customer_combobox = ttk.Combobox(self.options_frame, state='readonly', width=18)
        self.customer_combobox.grid(row=2, column=5, padx=5, pady=5, sticky="ew")
        self.customer_purchase_history_btn = ttk.Button(self.options_frame, text="Show", command=self._on_customer_purchase_history_report, style="Blue.TButton")
        self.customer_purchase_history_btn.grid(row=2, column=6, padx=5, pady=5, sticky="ew")

        # Export Data button for exporting report_tree to CSV (larger, square shape)
        style.configure("Square.TButton",
                        background="#1976D2",
                        foreground="white",
                        relief="raised",
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="#1976D2",
                        width=13,
                        height=7)
        self.export_data_btn = ttk.Button(
            self.options_frame,
            text="Export Data",
            command=self._on_export_data,
            style="Square.TButton",
            width=10
        )
        self.export_data_btn.grid(row=0, column=7, padx=10, pady=10, sticky="nsew")

        # Remove problematic custom style.layout for scrollbar
        # Output Report Table
        self.report_tree = ttk.Treeview(self.frame, columns=(), show='headings', height=14)
        self.report_tree.pack(fill='both', expand=True, padx=10, pady=(10,0))

        # Horizontal Scrollbar (standard style)
        self.report_tree_scroll_x = ttk.Scrollbar(self.frame, orient='horizontal', command=self.report_tree.xview)
        self.report_tree.configure(xscrollcommand=self.report_tree_scroll_x.set)
        self.report_tree_scroll_x.pack(fill='x', padx=10, pady=(0,10))

        # Callbacks and initialization
        self.low_stock_report_callback = None
        self.sales_by_employee_callback = None
        self.supplier_purchase_callback = None
        self.adjustment_history_callback = None
        self.get_employees_callback = None
        self.get_suppliers_callback = None
        self._populate_employees()
        self._populate_suppliers()

    def _on_adjustment_history_report(self):
        if self.adjustment_history_callback:
            self.adjustment_history_callback()

    def _populate_employees(self):
        if self.get_employees_callback:
            employees_list = self.get_employees_callback()
            self.employees_map = {f"{e['name']} (ID: {e['employee_id']})": e['employee_id'] for e in employees_list}
            self.employee_combobox['values'] = list(self.employees_map.keys())
            if self.employee_combobox['values']:
                self.employee_combobox.current(0)
        else:
            self.employee_combobox['values'] = []

    def _populate_suppliers(self):
        if self.get_suppliers_callback:
            suppliers_list = self.get_suppliers_callback()
            self.suppliers_map = {f"{s['name']} (ID: {s['supplier_id']})": s['supplier_id'] for s in suppliers_list}
            self.supplier_combobox['values'] = list(self.suppliers_map.keys())
            if self.supplier_combobox['values']:
                self.supplier_combobox.current(0)
        else:
            self.supplier_combobox['values'] = []

    def _on_sales_by_employee_report(self):
        if self.sales_by_employee_callback:
            selected_employee = self.employee_combobox.get()
            employee_id = self.employees_map.get(selected_employee)
            self.sales_by_employee_callback(employee_id)

    def _on_supplier_purchase_report(self):
        if self.supplier_purchase_callback and self.supplier_combobox.get():
            selected_supplier = self.supplier_combobox.get()
            supplier_id = self.suppliers_map.get(selected_supplier)
            if supplier_id:
                self.supplier_purchase_callback(supplier_id)

    def _on_low_stock_report(self):
        if self.low_stock_report_callback:
            self.low_stock_report_callback()

    def _on_inventory_value_report(self):
        if hasattr(self, 'inventory_value_report_callback') and self.inventory_value_report_callback:
            self.inventory_value_report_callback()

    def _on_customer_purchase_history_report(self):
        if hasattr(self, 'customer_purchase_history_callback') and self.customer_purchase_history_callback:
            selected_customer = self.customer_combobox.get()
            customer_id = self.customers_map.get(selected_customer) if hasattr(self, 'customers_map') else None
            if customer_id:
                self.customer_purchase_history_callback(customer_id)

    def _populate_customers(self):
        if self.get_customers_callback:
            customers_list = self.get_customers_callback()
            self.customers_map = {f"{c['name']} (ID: {c['customer_id']})": c['customer_id'] for c in customers_list}
            self.customer_combobox['values'] = list(self.customers_map.keys())
            if self.customer_combobox['values']:
                self.customer_combobox.current(0)
        else:
            self.customers_map = {}
            self.customer_combobox['values'] = []

    def display_report(self, columns, rows, compact=False):
        self.report_tree.delete(*self.report_tree.get_children())
        self.report_tree['columns'] = columns
        
        # Define column widths based on content type
        if compact and columns == ("SKU", "Product Name", "Quantity"):
            # Compact view for low stock report
            widths = [160, 160, 160]
            show_scroll = False
        else:
            # More intelligent column width assignment
            widths = []
            for col in columns:
                col_lower = col.lower()
                if col_lower in ("sku", "id", "employee_id", "supplier_id", "customer_id"):
                    widths.append(160)  # IDs are usually short
                elif col_lower in ("quantity", "stock", "price", "amount"):
                    widths.append(100)  # Numeric values
                elif col_lower in ("date", "time", "datetime", "date/time"):
                    widths.append(180)  # Date/time fields
                elif "name" in col_lower:
                    widths.append(180)  # Names need more space
                elif "address" in col_lower or "description" in col_lower or "reason" in col_lower:
                    widths.append(250)  # Long text fields
                else:
                    widths.append(180)  # Default width for other columns
            
            show_scroll = True
        
        # Apply column settings
        for idx, col in enumerate(columns):
            self.report_tree.heading(col, text=col)
            # Set width, anchor and minimum width
            width = widths[idx] if idx < len(widths) else 120
            anchor = 'e' if any(term in col.lower() for term in ["price", "quantity", "stock", "amount", "id"]) else 'w'
            self.report_tree.column(col, width=width, anchor=anchor, minwidth=50, stretch=False)
        
        # Insert data rows
        for row in rows:
            formatted_values = format_treeview_values(row)
            self.report_tree.insert("", "end", values=formatted_values)
        
        # Finalize appearance
        alternate_treeview_rows(self.report_tree)
        self.report_tree.update_idletasks()
        
        # Manage horizontal scrollbar visibility
        if not show_scroll:
            self.report_tree_scroll_x.pack_forget()
        else:
            self.report_tree_scroll_x.pack(fill='x', padx=10, pady=(0,10))
        
        self.report_tree.xview_moveto(0)

    def _on_export_data(self):
        export_treeview_to_csv(self.report_tree, self.frame)

class SuppliersUI:
    def __init__(self, master):
        # Title and description
        self.title_label = ttk.Label(master, text="Suppliers Dashboard", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=(10, 2), padx=10, anchor="w")
        self.desc_label = ttk.Label(master, text="Add, view, and manage supplier information.", font=("Helvetica", 12))
        self.desc_label.pack(pady=(0, 15), padx=10, anchor="w")
        self.frame = ttk.LabelFrame(master, text='Suppliers', padding='10')
        self.frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Configure frame grid weights for proper expansion
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        # Define a custom style for blue buttons with white text for suppliers tab
        style = ttk.Style(master)
        style.theme_use('clam')
        style.configure("Blue.TButton",
                        background="#1976D2",
                        foreground="white",
                        relief="raised",
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="#1976D2")
        style.map("Blue.TButton",
                  background=[('active', '#1565C0'), ('pressed', '#0D47A1')],
                  foreground=[('active', 'white'), ('pressed', 'white')],
                  bordercolor=[('focus', '#1976D2'), ('!focus', '#1976D2')],
                  focuscolor=[('focus', '#1976D2'), ('!focus', '#1976D2')])
        # Add Tab
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Add")
        # Add labels for each entry box in Add tab
        self.add_supplier_name_label = ttk.Label(self.add_tab, text="Name:")
        self.add_supplier_name_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.add_supplier_name_entry = ttk.Entry(self.add_tab, width=20)
        self.add_supplier_name_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.add_supplier_contact_label = ttk.Label(self.add_tab, text="Contact Info:")
        self.add_supplier_contact_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.add_supplier_contact_entry = ttk.Entry(self.add_tab, width=20)
        self.add_supplier_contact_entry.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        self.add_supplier_address_label = ttk.Label(self.add_tab, text="Address:")
        self.add_supplier_address_label.grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.add_supplier_address_entry = ttk.Entry(self.add_tab, width=20)
        self.add_supplier_address_entry.grid(row=2, column=1, sticky=tk.W, padx=2, pady=2)
        self.add_supplier_button = ttk.Button(self.add_tab, text='Add Supplier', command=self._threaded_add_supplier, style="Blue.TButton")
        self.add_supplier_button.grid(row=3, column=0, columnspan=2, pady=5)
        # Add title and description to Add subtab
        add_title = ttk.Label(self.add_tab, text="Add Supplier", font=("Helvetica", 14, "bold"))
        add_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        add_desc = ttk.Label(self.add_tab, text="Add a new supplier to the system.", font=("Helvetica", 10))
        add_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        
        # Update Tab
        self.update_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.update_tab, text="Update")
        
        # Supplier ID field for update
        self.update_supplier_id_label = ttk.Label(self.update_tab, text="Supplier ID:")
        self.update_supplier_id_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_supplier_id_entry = ttk.Entry(self.update_tab, width=10)
        self.update_supplier_id_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        
        # Load supplier button
        self.load_supplier_button = ttk.Button(self.update_tab, text="Load Supplier", command=self._load_supplier_for_update, style="Blue.TButton")
        self.load_supplier_button.grid(row=0, column=2, padx=5, pady=2)
        
        # Update form fields
        self.update_supplier_name_label = ttk.Label(self.update_tab, text="Name:")
        self.update_supplier_name_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_supplier_name_entry = ttk.Entry(self.update_tab, width=20)
        self.update_supplier_name_entry.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        
        self.update_supplier_contact_label = ttk.Label(self.update_tab, text="Contact Info:")
        self.update_supplier_contact_label.grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_supplier_contact_entry = ttk.Entry(self.update_tab, width=20)
        self.update_supplier_contact_entry.grid(row=2, column=1, sticky=tk.W, padx=2, pady=2)
        
        self.update_supplier_address_label = ttk.Label(self.update_tab, text="Address:")
        self.update_supplier_address_label.grid(row=3, column=0, sticky=tk.W, padx=2, pady=2)
        self.update_supplier_address_entry = ttk.Entry(self.update_tab, width=20)
        self.update_supplier_address_entry.grid(row=3, column=1, sticky=tk.W, padx=2, pady=2)
        
        # Update button
        self.update_supplier_button = ttk.Button(self.update_tab, text="Update Supplier", command=self._threaded_update_supplier, style="Blue.TButton")
        self.update_supplier_button.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Add title and description to Update subtab
        update_title = ttk.Label(self.update_tab, text="Update Supplier", font=("Helvetica", 14, "bold"))
        update_title.grid(row=0, column=3, sticky=tk.W, padx=10, pady=(10,2))
        update_desc = ttk.Label(self.update_tab, text="Load a supplier by ID and update their information.", font=("Helvetica", 10))
        update_desc.grid(row=1, column=3, sticky=tk.W, padx=10, pady=(0,10))
        
        # Delete Tab
        self.delete_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.delete_tab, text="Delete")
        self.delete_supplier_id_label = ttk.Label(self.delete_tab, text="Supplier ID:")
        self.delete_supplier_id_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.delete_supplier_id_entry = ttk.Entry(self.delete_tab, width=10)
        self.delete_supplier_id_entry.grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)
        self.delete_supplier_button = ttk.Button(self.delete_tab, text='Delete Supplier', command=self._threaded_delete_supplier, style="Blue.TButton")
        self.delete_supplier_button.grid(row=1, column=0, columnspan=2, pady=5)
        # Add title and description to Delete subtab
        del_title = ttk.Label(self.delete_tab, text="Delete Supplier", font=("Helvetica", 14, "bold"))
        del_title.grid(row=0, column=2, sticky=tk.W, padx=10, pady=(10,2))
        del_desc = ttk.Label(self.delete_tab, text="Remove a supplier from the system by their ID.", font=("Helvetica", 10))
        del_desc.grid(row=1, column=2, sticky=tk.W, padx=10, pady=(0,10))
        # View Suppliers button and Treeview
        self.view_suppliers_button = ttk.Button(self.frame, text="View Suppliers", command=self._on_view_suppliers, style="Blue.TButton")
        self.view_suppliers_button.grid(row=2, column=0, pady=10, sticky=tk.W)
        self.export_data_button = ttk.Button(self.frame, text="Export Data", command=self._on_export_data, style="Blue.TButton")
        self.export_data_button.grid(row=3, column=0, pady=10, sticky=tk.W)
        # Add Import Data button below Export Data
        self.import_data_button = ttk.Button(self.frame, text="Import Data", command=self._on_import_data, style="Blue.TButton")
        self.import_data_button.grid(row=4, column=0, pady=10, sticky=tk.W)
        self.suppliers_tree = ttk.Treeview(self.frame, columns=('ID', 'Name', 'Contact', 'Address'), show='headings', height=10)
        self.suppliers_tree.heading('ID', text='ID')
        self.suppliers_tree.heading('Name', text='Name')
        self.suppliers_tree.heading('Contact', text='Contact Info')
        self.suppliers_tree.heading('Address', text='Address')
        self.suppliers_tree.grid(row=0, column=1, rowspan=4, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=5)
        
        # Configure grid weights for proper expansion
        self.frame.rowconfigure(0, weight=1)  # Tree row expands
        self.frame.rowconfigure(1, weight=0)  # Button rows fixed
        self.frame.rowconfigure(2, weight=0)
        self.frame.rowconfigure(3, weight=0)
        self.frame.rowconfigure(4, weight=0)
        self.frame.columnconfigure(0, weight=0)  # Button column fixed
        self.frame.columnconfigure(1, weight=1)  # Tree column expands
        self.view_suppliers_callback = None
    def _on_view_suppliers(self):
        if self.view_suppliers_callback:
            self.view_suppliers_callback(self.suppliers_tree)
            alternate_treeview_rows(self.suppliers_tree)
    def _threaded_add_supplier(self):
        
        threading.Thread(target=self.add_supplier).start()
    def _threaded_update_supplier(self):
        threading.Thread(target=self.update_supplier).start()
    def _threaded_delete_supplier(self):
        
        threading.Thread(target=self.delete_supplier).start()
        if self.add_supplier_callback:
            self.add_supplier_callback(
                self.add_supplier_name_entry,
                self.add_supplier_contact_entry,
                self.add_supplier_address_entry
            )
            self.add_supplier_name_entry.delete(0, tk.END)
            self.add_supplier_contact_entry.delete(0, tk.END)
            self.add_supplier_address_entry.delete(0, tk.END)
            self.add_supplier_name_entry.focus_set()
    
    def _load_supplier_for_update(self):
        """Load supplier data into update form"""
        if hasattr(self, 'load_supplier_callback') and self.load_supplier_callback:
            supplier_id = self.update_supplier_id_entry.get().strip()
            if supplier_id:
                try:
                    supplier_data = self.load_supplier_callback(supplier_id)
                    if supplier_data:
                        # Populate the update form fields
                        self.update_supplier_name_entry.delete(0, tk.END)
                        self.update_supplier_name_entry.insert(0, supplier_data.get('name', ''))
                        
                        self.update_supplier_contact_entry.delete(0, tk.END)
                        self.update_supplier_contact_entry.insert(0, supplier_data.get('contact_info', ''))
                        
                        self.update_supplier_address_entry.delete(0, tk.END)
                        self.update_supplier_address_entry.insert(0, supplier_data.get('address', ''))
                        
                        messagebox.showinfo("Success", f"Supplier {supplier_data.get('name', '')} loaded successfully!")
                    else:
                        messagebox.showerror("Error", f"Supplier with ID {supplier_id} not found.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load supplier: {str(e)}")
            else:
                messagebox.showwarning("Warning", "Please enter a Supplier ID.")
    
    def update_supplier(self):
        if hasattr(self, 'update_supplier_callback') and self.update_supplier_callback:
            supplier_id = self.update_supplier_id_entry.get().strip()
            if supplier_id:
                self.update_supplier_callback(
                    supplier_id,
                    self.update_supplier_name_entry,
                    self.update_supplier_contact_entry,
                    self.update_supplier_address_entry
                )
                # Clear the form after successful update
                self.update_supplier_id_entry.delete(0, tk.END)
                self.update_supplier_name_entry.delete(0, tk.END)
                self.update_supplier_contact_entry.delete(0, tk.END)
                self.update_supplier_address_entry.delete(0, tk.END)
                self.update_supplier_id_entry.focus_set()
            else:
                messagebox.showwarning("Warning", "Please enter a Supplier ID.")
    
    def delete_supplier(self):
        if self.delete_supplier_callback:
            self.delete_supplier_callback(self.delete_supplier_id_entry)
            self.delete_supplier_id_entry.delete(0, tk.END)
            self.delete_supplier_id_entry.focus_set()
    def _on_export_data(self):
        export_treeview_to_csv(self.suppliers_tree, self.frame)
    
    def _on_import_data(self):
        # Create a refresh callback that updates the suppliers tree
        def refresh_suppliers():
            if self.view_suppliers_callback:
                self.view_suppliers_callback(self.suppliers_tree)
                alternate_treeview_rows(self.suppliers_tree)
        
        # Show the import dialog with refresh callback
        show_supplier_import_dialog(self.frame, refresh_suppliers)

def view_inventory(cursor, inventory_tree):
    try:
        inventory_list = inventory.view_inventory(cursor)
        if not inventory_list:
            raise ValueError("No items found in inventory.")
        
        # Populate the inventory Treeview
        _populate_inventory_treeview(inventory_list, inventory_tree)
    except Exception as e:
        handle_error(f"An error occurred while viewing inventory: {e}")

def _populate_inventory_treeview(inventory_list, inventory_tree):
    inventory_tree.delete(*inventory_tree.get_children())
    for item in inventory_list:
        formatted_values = format_treeview_values((item['SKU'], item['name'], item['category'], item['price'], item['stock'], item['supplier_id'], item['cost']))
        inventory_tree.insert("", "end", values=formatted_values)
    alternate_treeview_rows(inventory_tree)

class POSApp:
    def __init__(self, root,
                 # Sales callbacks
                 add_to_cart_callback=None,
                 checkout_callback=None,
                 empty_cart_callback=None,
                 remove_from_cart_callback=None,
                 update_cart_quantity_callback=None,
                 calculate_and_display_totals_callback=None,
                 select_customer_callback=None,
                 resend_receipt_callback=None,
                 # Supplier callbacks
                 add_supplier_callback=None,
                 update_supplier_callback=None,
                 load_supplier_callback=None,
                 search_suppliers_callback=None,
                 delete_supplier_callback=None,
                 # Customer callbacks
                 add_customer_callback=None,
                 update_customer_callback=None,
                 load_customer_callback=None,
                 delete_customer_callback=None,
                 # Inventory callbacks
                 add_item_callback=None,
                 delete_item_callback=None,
                 view_inventory_callback=None,
                 view_employees_callback=None,
                 view_suppliers_callback=None,
                 adjust_stock_callback=None,
                 low_stock_report_callback=None,
                 # Misc callbacks
                 _update_cart_display_callback=None,
                 _display_receipt_callback=None,
                 get_customers_callback=None,
                 get_employees_callback=None,
                 view_customers_callback=None,
                 # Reports callbacks
                 sales_by_employee_callback=None,
                 get_suppliers_callback=None,
                 supplier_purchase_callback=None,
                 adjustment_history_callback=None,
                 inventory_value_report_callback=None,
                 customer_purchase_history_callback=None,
                 # User info
                 user_role="manager",
                 username="Unknown"
                 ):
        self.root = root
        self.callbacks = locals()
        self.user_role = user_role
        self.username = username

        # Create a main frame to hold all UI components
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        # Add user information and logout button at the top
        user_info_frame = ttk.Frame(self.main_frame)
        user_info_frame.grid(row=0, column=0, sticky=(tk.W), padx=5, pady=5)
        username= username.upper()
        welcome_label = ttk.Label(user_info_frame, text=f"Welcome, {username}", font=("Helvetica", 15, "bold"))
        welcome_label.pack(side=tk.LEFT, padx=5)
        
        role_label = ttk.Label(user_info_frame, text=f"Role: {user_role.capitalize()}", font=("Helvetica", 13))
        role_label.pack(side=tk.LEFT, padx=5)
        
        # Add logout button with the same style as other buttons
        self.logout_button = ttk.Button(user_info_frame, text="Logout", command=self._logout, style="Blue.TButton")
        self.logout_button.pack(side=tk.LEFT, padx=20)
        
        # Add logo to the top right corner
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                # Resize the image to a reasonable size
                logo_img = logo_img.resize((250, 110), Image.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                self.logo_label = ttk.Label(self.main_frame, image=self.logo_photo)
                self.logo_label.grid(row=0, column=2, sticky=(tk.N, tk.E), padx=5, pady=5)
                
                
        except Exception as e:
            print(f"Could not load logo image: {e}")
            # Add tagline even if logo fails to load
            tagline_label = ttk.Label(self.main_frame, text="DigiClimate Store Hub - Resilience meets innovation", 
                                    font=("Helvetica", 12, "italic"),
                                    foreground="#666666")
            tagline_label.grid(row=0, column=2, sticky=(tk.N, tk.E), padx=5, pady=5)

        # Configure row and column weights for resizing
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # Header row - fixed height
        self.main_frame.rowconfigure(1, weight=1)  # Notebook row - expandable
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=0)

        # Create a notebook (tabbed interface) for different sections
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.dashboard_tab = ttk.Frame(self.notebook)
        self.climate_tab = ttk.Frame(self.notebook)
        self.sales_tab = ttk.Frame(self.notebook)
        self.customer_tab = ttk.Frame(self.notebook)
        self.inventory_tab = ttk.Frame(self.notebook)
        self.suppliers_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)

        # Add tabs based on user role
        # Dashboard tab access for manager and accountant (business intelligence users)
        if user_role in ["manager", "accountant"]:
            self.notebook.add(self.dashboard_tab, text="📊 Dashboard")
        
        self.notebook.add(self.sales_tab, text="🧾Sales")
        
        # All roles have access to the customer tab except accountants have read-only access
        self.notebook.add(self.customer_tab, text="🙎🏻‍♂️Customers")
        
        # Inventory tab access for manager, inventory_manager, and store_admin
        if user_role in ["manager", "inventory_manager", "store_admin"]:
            self.notebook.add(self.inventory_tab, text="🗃️Inventory")
        
        # Suppliers tab access for manager, inventory_manager, and store_admin
        if user_role in ["manager", "inventory_manager", "store_admin"]:
            self.notebook.add(self.suppliers_tab, text="🚚Suppliers")
        
        # Reports tab access for manager and accountant
        if user_role in ["manager", "accountant"]:
            self.notebook.add(self.reports_tab, text="📂Reports")
        
        # Climate tab as the last tab for manager and accountant
        if user_role in ["manager", "accountant","store_admin"]:
            self.notebook.add(self.climate_tab, text="🌍 Climate")

        # Always instantiate these UI classes as all roles have some form of access
        self.sales_ui = SalesUI(self.sales_tab)
        self.customer_ui = CustomerUI(self.customer_tab)
        
        # Create UIs based on role permissions
        if user_role in ["manager", "accountant"]:
            # Create dashboard UI with all callbacks
            dashboard_callbacks = {
                'get_employees_callback': get_employees_callback,
                'get_suppliers_callback': get_suppliers_callback,
                'get_customers_callback': get_customers_callback,
                'sales_by_employee_callback': sales_by_employee_callback,
                'supplier_purchase_callback': supplier_purchase_callback,
                'inventory_value_report_callback': inventory_value_report_callback,
                'customer_purchase_history_callback': customer_purchase_history_callback,
                'navigate_to_sales': lambda: self.notebook.select(self.sales_tab),
                'navigate_to_inventory': lambda: self.notebook.select(self.inventory_tab),
                'navigate_to_reports': lambda: self.notebook.select(self.reports_tab),
                'navigate_to_customers': lambda: self.notebook.select(self.customer_tab),
                'navigate_to_suppliers': lambda: self.notebook.select(self.suppliers_tab)
            }
            self.dashboard_ui = DashboardUI(self.dashboard_tab, **dashboard_callbacks)
            
            # Create climate UI with callbacks
            if CLIMATE_AVAILABLE and ClimateUI is not None:
                climate_callbacks = {
                    'get_materials_callback': self.get_climate_materials,
                    'get_forecast_callback': self.get_climate_forecast,
                    'refresh_data': self.refresh_climate_data,
                    'export_data': self.export_climate_data,
                    'navigate_to_inventory': lambda: self.notebook.select(self.inventory_tab),
                    'navigate_to_suppliers': lambda: self.notebook.select(self.suppliers_tab)
                }
                self.climate_ui = ClimateUI(self.climate_tab, **climate_callbacks)
            else:
                # Create a simple message if climate UI is not available
                error_label = ttk.Label(self.climate_tab, 
                                      text="Climate Tab is currently unavailable.\nPlease check the Climate Tab folder and files.",
                                      font=('Arial', 12),
                                      anchor='center')
                error_label.pack(expand=True, fill='both')
            
            self.reports_ui = ReportsUI(self.reports_tab)
        
        if user_role in ["manager", "inventory_manager", "store_admin"]:
            self.inventory_ui = InventoryUI(self.inventory_tab)
            self.suppliers_ui = SuppliersUI(self.suppliers_tab)

        # Wire up callbacks if provided
        # Common callbacks for all users
        if add_to_cart_callback:
            self.sales_ui.add_to_cart_callback = add_to_cart_callback
        if remove_from_cart_callback:
            self.sales_ui.remove_from_cart_callback = remove_from_cart_callback
        if update_cart_quantity_callback:
            self.sales_ui.update_cart_quantity_callback = update_cart_quantity_callback
        if checkout_callback:
            self.sales_ui.checkout_callback = checkout_callback
        if empty_cart_callback:
            self.sales_ui.empty_cart_callback = empty_cart_callback
        if select_customer_callback:
            self.sales_ui.select_customer_callback = select_customer_callback
        if resend_receipt_callback:
            self.sales_ui.resend_receipt_callback = resend_receipt_callback
            
        # Only allow write access to customer data for roles other than accountant
        if user_role != "accountant":
            if add_customer_callback:
                self.customer_ui.add_customer_callback = add_customer_callback
            if update_customer_callback:
                self.customer_ui.update_customer_callback = update_customer_callback
            if load_customer_callback:
                self.customer_ui.load_customer_callback = load_customer_callback
            if delete_customer_callback:
                self.customer_ui.delete_customer_callback = delete_customer_callback
                
        # All roles need to view customer data
        if view_customers_callback:
            self.customer_ui.view_customers_callback = view_customers_callback
        if get_customers_callback:
            self.sales_ui.get_customers_callback = get_customers_callback
            self.sales_ui._populate_customers()
        if get_employees_callback:
            self.sales_ui.get_employees_callback = get_employees_callback
            self.sales_ui._populate_employees()
        
        # Inventory manager, store admin and manager callbacks
        if user_role in ["manager", "inventory_manager", "store_admin"]:
            if hasattr(self, 'inventory_ui'):
                if add_item_callback:
                    self.inventory_ui.add_item_callback = add_item_callback
                if delete_item_callback:
                    self.inventory_ui.delete_item_callback = delete_item_callback
                if view_inventory_callback:
                    self.inventory_ui.view_inventory_callback = view_inventory_callback
                if adjust_stock_callback:
                    self.inventory_ui.adjust_stock_callback = adjust_stock_callback
                if get_employees_callback:
                    self.inventory_ui.get_employees_callback = get_employees_callback
                    self.inventory_ui._populate_employees()
            
            if hasattr(self, 'suppliers_ui'):
                if add_supplier_callback:
                    self.suppliers_ui.add_supplier_callback = add_supplier_callback
                if update_supplier_callback:
                    self.suppliers_ui.update_supplier_callback = update_supplier_callback
                if load_supplier_callback:
                    self.suppliers_ui.load_supplier_callback = load_supplier_callback
                if delete_supplier_callback:
                    self.suppliers_ui.delete_supplier_callback = delete_supplier_callback
                if view_suppliers_callback:
                    self.suppliers_ui.view_suppliers_callback = view_suppliers_callback
                if search_suppliers_callback:
                    self.suppliers_ui.search_suppliers_callback = search_suppliers_callback
        
        # Reports tab callbacks for manager and accountant
        if user_role in ["manager", "accountant"] and hasattr(self, 'reports_ui'):
            if get_customers_callback:
                self.reports_ui.get_customers_callback = get_customers_callback
                self.reports_ui._populate_customers()
            
            if get_employees_callback:
                self.reports_ui.get_employees_callback = get_employees_callback
                self.reports_ui._populate_employees()
                
            if low_stock_report_callback:
                self.reports_ui.low_stock_report_callback = low_stock_report_callback
            if sales_by_employee_callback:
                self.reports_ui.sales_by_employee_callback = sales_by_employee_callback
            if get_suppliers_callback:
                self.reports_ui.get_suppliers_callback = get_suppliers_callback
                self.reports_ui._populate_suppliers()
            if supplier_purchase_callback:
                self.reports_ui.supplier_purchase_callback = supplier_purchase_callback
            if adjustment_history_callback:
                self.reports_ui.adjustment_history_callback = adjustment_history_callback
            if inventory_value_report_callback:
                self.reports_ui.inventory_value_report_callback = inventory_value_report_callback
            if customer_purchase_history_callback:
                self.reports_ui.customer_purchase_history_callback = customer_purchase_history_callback

    def display_receipt(self, receipt_data):
        if self._display_receipt_callback:
            self._display_receipt_callback(self.sales_ui.receipt_tree, receipt_data)

    def calculate_and_display_totals(self):
        if self.calculate_and_display_totals_callback:
            self.calculate_and_display_totals_callback(self.sales_ui.subtotal_label, self.sales_ui.taxes_label, self.sales_ui.total_label)

    def update_cart_treeview(self, cart_items):
        self.sales_ui.cart_tree.delete(*self.sales_ui.cart_tree.get_children())
        for item in cart_items:
            formatted_values = format_treeview_values((item['SKU'], item['name'], item['quantity'], item['price']))
            self.sales_ui.cart_tree.insert("", "end", values=formatted_values)
        self.calculate_and_display_totals()

    def _logout(self):
        # Handle logout button click - notify main app that user wants to logout
        if hasattr(self, 'logout_callback') and self.logout_callback:
            self.logout_callback()
    
    def refresh_climate_data(self):
        """Refresh climate data callback"""
        try:
            # This would typically trigger a data refresh in the climate system
            # For now, just show a success message
            messagebox.showinfo("Success", "Climate data refreshed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh climate data: {str(e)}")
    
    def export_climate_data(self):
        """Export climate data callback"""
        try:
            # This would typically export climate data to CSV or other format
            # For now, just show a placeholder message
            messagebox.showinfo("Export", "Climate data export feature coming soon")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export climate data: {str(e)}")

    def get_climate_materials(self):
        """Get climate materials data callback for Phase 6 integration"""
        try:
            if not CLIMATE_AVAILABLE or climate_data is None:
                print("Climate data not available")
                return []
            
            # Get current climate status for all materials
            materials = climate_data.get_current_climate_status()
            return materials
            
        except Exception as e:
            print(f"Error getting climate materials: {e}")
            return []

    def get_climate_forecast(self, days_ahead=7):
        """Get climate forecast data callback for Phase 6 integration"""
        try:
            if not CLIMATE_AVAILABLE or climate_data is None:
                print("Climate data not available")
                return []
            
            # Get climate forecast
            forecast = climate_data.get_climate_forecast(days_ahead)
            return forecast
            
        except Exception as e:
            print(f"Error getting climate forecast: {e}")
            return []


