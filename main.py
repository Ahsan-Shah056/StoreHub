import tkinter as tk
from tkinter import ttk, messagebox

from database import get_db, close_db
import suppliers
import inventory
import sales
import customers
import employees
from datetime import datetime
import reporting
from Ui import POSApp
from ttkthemes import ThemedTk


def handle_error(error_message):
    """
    Displays an error message in a message box.
    Args:
    """
    messagebox.showerror("Error", error_message)


def get_selected_customer_id():
    if 'selected_customer_id' not in get_selected_customer_id.__dict__:
        get_selected_customer_id.selected_customer_id = None
    return get_selected_customer_id.selected_customer_id



def set_selected_customer_id(customer_id):
    """Sets the ID of the currently selected customer."""
    get_selected_customer_id.selected_customer_id = customer_id

def _update_cart_display(cart, cart_tree, cursor):
    """Updates the cart display in the UI with the current items in the cart.
    
    Args:
        cart: The cart with the products
    
    Args:    
        cart (list): The list of items in the cart.
        cart_tree (ttk.Treeview): The Treeview widget to display the cart items.
        cursor (cursor): The database cursor object.
    """
    try:
        
        cart_tree.delete(*cart_tree.get_children())
        for item in cart:# for every item in the cart
            product = sales.get_product(cursor, item['SKU'])# gets the product
            if product:
                cart_tree.insert("", "end", values=(item['SKU'], product['name'], item['quantity'], product['price']))
    except Exception as e:
        handle_error(f"An error occurred while updating the cart display: {e}")




def _display_product_details(product_listbox, cursor):
    """Args:
        product_listbox (tk.Listbox): The Listbox widget containing the products.
        cursor (cursor): The database cursor object.
    """
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
    """Adds a selected product to the cart with a specified quantity."""
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
    """Updates the quantity of an item in the cart."""
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
    """Calculates the subtotal, taxes, and total for the items in the cart and updates the UI labels. it is now reciving the cursor and the cart as parameters.
    Args:        
        subtotal_label (ttk.Label): The Label widget to display the subtotal.            
    """    
    try:

        totals = sales.calculate_totals(cart, cursor)
        subtotal_label.config(text=f"Subtotal: ${totals['subtotal']:.2f}")
        taxes_label.config(text=f"Taxes: ${totals['taxes']:.2f}")
        total_label.config(text=f"Total: ${totals['total']:.2f}")
    except Exception as e:        
        handle_error(f"An error occurred while calculating the totals: {e}")





        
# Sales Management function
def checkout(receipt_tree, cart_tree, cart, connection, cursor, employee_id):
    """Completes the checkout process for the current cart."""
    try:
        selected_customer_id = get_selected_customer_id()
        if not cart:
            raise ValueError("Cart is empty. Add items before checkout.")
        if not selected_customer_id:
            raise ValueError("Please select a customer")
        # Calculate totals before clearing the cart
        totals = sales.calculate_totals(cart, cursor)
        sale_id = sales.log_sale(connection, cursor, cart, employee_id, selected_customer_id)
        receipt_data = sales.generate_receipt_dict(cursor, sale_id)
        _display_receipt(receipt_data, receipt_tree, cursor)
        # Show total bill to the customer
        messagebox.showinfo("Total Bill", f"Your total bill is: ${totals['total']:.2f}")
        cart.clear()
        _update_cart_display(cart, cart_tree, cursor)
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:
        handle_error(f"An error occurred while checking out: {e}")

def select_customer(customer_listbox):
    """Select a customer"""
    try:
        selected_index = customer_listbox.curselection()
        if not selected_index:
            raise ValueError("Please select a customer from the list.")
        selected_customer = customer_listbox.get(selected_index[0])
        customer_id = int(selected_customer.split('(ID: ')[1][:-1])
        set_selected_customer_id(customer_id)
        messagebox.showinfo("Customer Selected", f"Customer ID {customer_id} has been selected.")

    except Exception as e:
        handle_error(f"An error occurred while selecting a customer: {e}")    
    except ValueError as ve:
        handle_error(str(ve))
    except Exception as e:        
        
        handle_error(f"An error occurred while selecting a customer: {e}")
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
    """Deletes a supplier from the database.    
    
    Args:
    """
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
    """Deletes suppliers from the database by name or id.
    
    Args:
    
    """
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
    """Adds a customer to the database."""
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
    """Check if a value is a number"""
    try:
        float(value)
        return True
    except ValueError:
        return False

def validate_date_input(date_str):
    """validate a date"""
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
    """Empties the cart and updates the display."""
    cart.clear()
    _update_cart_display(cart, cart_tree, cursor)
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
    """Displays a list of all employees.
    Args:    
    """
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

def _populate_inventory_treeview(inventory_list, inventory_tree):
    """Populates the inventory treeview with data."""
    inventory_tree.delete(*inventory_tree.get_children())
    for item in inventory_list:
        inventory_tree.insert("", "end", values=(item['SKU'], item['name'], item['category'], item['price'], item['stock'], item['supplier_id']))

def populate_employees_treeview(employees_list, employee_tree):    
    employee_tree.delete(*employee_tree.get_children())    
    for employee in employees_list:
        employee_tree.insert("", "end", values=(employee['employee_id'], employee['name'], employee['role']))

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


def generate_receipt(cursor, sale_id): # generate a receipt
    """Generates a receipt for the completed sale. The cursor is being received as parameter
    Args:    
   """
    try:# generate a receipt
        return sales.generate_receipt_dict(cursor, sale_id)
    except Exception as e:
        handle_error(f"An error occurred while generating the receipt: {e}")
def _display_receipt(receipt_data, receipt_tree, cursor):
    """Displays the receipt data in the receipt Treeview. The function now receives the receipt data, and the cursor as parameter, it does not need to generate it again.
    Args:
   """

    
    try:
        receipt_tree.delete(*receipt_tree.get_children())
        for item in receipt_data:            
                product = sales.get_product(cursor, item['SKU'])
                if product:
                  receipt_tree.insert("", "end", values=(item['SKU'], product['name'], item['quantity'], item['price']))
                else:
                    receipt_tree.insert("", "end", values=(item['SKU'], "Product Name Not Found", item['quantity'], item['price']))
    except Exception as e:
        handle_error(f"An error occurred while displaying the receipt: {e}")
def low_stock_report(cursor):
    try:
        low_stock_items = inventory.check_low_stock(cursor)
        if not low_stock_items:
            raise ValueError("No items are currently low in stock.")
        columns = ("SKU", "Product Name", "Quantity")
        # Ensure all values are strings for display
        rows = [(
            str(item.get('SKU', '')),
            str(item.get('name', '')),
            str(item.get('stock', ''))
        ) for item in low_stock_items]
        # Call the report display with a flag for compact mode
        pos_app.reports_ui.display_report(columns, rows, compact=True)
    except Exception as e:
        handle_error(f"An error occurred while generating the Low Stock Report: {e}")

def _populate_customers_treeview(customers_list, customer_tree):
    customer_tree.delete(*customer_tree.get_children())
    for c in customers_list:
        customer_tree.insert("", "end", values=(c['customer_id'], c['name'], c['contact_info'], c['address']))

def sales_by_employee_callback(employee_id):
    try:
        from reporting import sales_by_employee
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
        from reporting import supplier_purchase_report
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
        from reporting import inventory_adjustment_history
        adjustments = inventory_adjustment_history(cursor)
        columns = ("Adjustment ID", "Date/Time", "SKU", "Quantity Change", "Employee Name")
        rows = [
            (a['adjustment_id'], a['date'], a['SKU'], a['quantity_change'], a['employee_name'])
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
        from reporting import customer_purchase_history
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

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    root.title("Storecore")
    # Force all widgets/dialogs to use the main root
    if hasattr(tk, '_default_root'):
        tk._default_root = root
    print("Main root window:", root)

    db_connection, cursor = get_db()
    cart = []

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
        view_employees_callback=lambda *_: view_employees(cursor, pos_app.customer_ui.customer_tree),
        view_suppliers_callback=lambda suppliers_tree, *_: _populate_suppliers_treeview(suppliers.view_suppliers(cursor), suppliers_tree),
        adjust_stock_callback=lambda adjust_sku_entry, adjust_quantity_entry, employee_id, reason, *_: adjust_stock(
            db_connection,
            cursor,
            adjust_sku_entry,
            adjust_quantity_entry,
            employee_id,
            reason
        ),
        low_stock_report_callback=lambda *_: low_stock_report(cursor),
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
    )

    root.mainloop()
    close_db(db_connection, cursor)