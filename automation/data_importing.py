import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from ..core.database import get_db, close_db
from ..core import customers

class DataImportError(Exception):
    """Custom exception for data import errors"""
    pass

def validate_customer_row(row, row_number):
    """
    Validate a single customer row from CSV data.
    Expected columns: name, contact_info, address
    """
    errors = []
    
    # Check if row has the correct number of columns
    if len(row) < 3:
        errors.append(f"Row {row_number}: Insufficient columns. Expected: name, contact_info, address")
        return errors
    
    name, contact_info, address = row[0:3]  # Take first 3 columns
    
    # Validate name (required)
    if not name or not name.strip():
        errors.append(f"Row {row_number}: Name is required and cannot be empty")
    elif len(name.strip()) > 255:
        errors.append(f"Row {row_number}: Name is too long (max 255 characters)")
    
    # Validate contact_info (optional but if provided, should be reasonable)
    if contact_info and len(contact_info.strip()) > 255:
        errors.append(f"Row {row_number}: Contact info is too long (max 255 characters)")
    
    # Validate address (optional but if provided, should be reasonable)
    if address and len(address.strip()) > 255:
        errors.append(f"Row {row_number}: Address is too long (max 255 characters)")
    
    return errors

def validate_csv_structure(file_path):
    """
    Validate the CSV file structure and content before importing.
    Returns (is_valid, errors, row_count, sample_data)
    """
    errors = []
    row_count = 0
    sample_data = []
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            # Try to detect CSV dialect
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            
            try:
                dialect = sniffer.sniff(sample)
            except csv.Error:
                # Use default dialect if detection fails
                dialect = csv.excel
            
            reader = csv.reader(csvfile, dialect)
            
            # Read header row
            try:
                header = next(reader)
                row_count += 1
                
                # Validate header
                expected_headers = ['name', 'contact_info', 'address']
                if len(header) < 3:
                    errors.append("CSV must have at least 3 columns: name, contact_info, address")
                    return False, errors, 0, []
                
                # Check if header looks reasonable (optional validation)
                header_lower = [h.lower().strip() for h in header[:3]]
                if not any('name' in h for h in header_lower):
                    errors.append("Warning: First column should be 'name' but header doesn't contain 'name'")
                
            except StopIteration:
                errors.append("CSV file is empty")
                return False, errors, 0, []
            
            # Validate data rows
            for row in reader:
                row_count += 1
                if row_count > 1000:  # Limit validation to first 1000 rows for performance
                    break
                
                # Skip empty rows
                if not any(cell.strip() for cell in row if cell):
                    continue
                
                # Validate this row
                row_errors = validate_customer_row(row, row_count)
                errors.extend(row_errors)
                
                # Collect sample data (first 5 valid rows)
                if len(sample_data) < 5 and not row_errors:
                    sample_data.append({
                        'name': row[0].strip(),
                        'contact_info': row[1].strip() if len(row) > 1 else '',
                        'address': row[2].strip() if len(row) > 2 else ''
                    })
    
    except UnicodeDecodeError:
        errors.append("File encoding error. Please ensure the CSV file is saved in UTF-8 format.")
        return False, errors, 0, []
    except Exception as e:
        errors.append(f"Error reading CSV file: {str(e)}")
        return False, errors, 0, []
    
    # Determine if validation passed
    is_valid = len(errors) == 0 or all('Warning:' in error for error in errors)
    
    return is_valid, errors, row_count - 1, sample_data  # -1 to exclude header row

def import_customers_from_csv(file_path, parent_window=None, skip_duplicates=True):
    """
    Import customers from CSV file into the database.
    Returns (success_count, error_count, errors)
    """
    success_count = 0
    error_count = 0
    errors = []
    
    try:
        # First validate the file
        is_valid, validation_errors, total_rows, sample_data = validate_csv_structure(file_path)
        
        if not is_valid:
            error_msg = "CSV validation failed:\n" + "\n".join(validation_errors)
            if parent_window:
                messagebox.showerror("Import Failed", error_msg, parent=parent_window)
            return 0, 0, validation_errors
        
        # Show preview and confirmation
        if validation_errors:  # Show warnings
            warning_msg = "Validation warnings found:\n" + "\n".join(validation_errors)
            warning_msg += f"\n\nProceed with import? ({total_rows} rows found)"
            if parent_window:
                if not messagebox.askyesno("Import Warning", warning_msg, parent=parent_window):
                    return 0, 0, ["Import cancelled by user"]
        
        # Get database connection
        connection, cursor = get_db()
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                
                # Skip header row
                next(reader)
                
                # Import each row
                for row_num, row in enumerate(reader, start=2):  # Start at 2 since we skipped header
                    # Skip empty rows
                    if not any(cell.strip() for cell in row if cell):
                        continue
                    
                    try:
                        # Extract data
                        name = row[0].strip() if len(row) > 0 else ''
                        contact_info = row[1].strip() if len(row) > 1 else ''
                        address = row[2].strip() if len(row) > 2 else ''
                        
                        if not name:
                            errors.append(f"Row {row_num}: Skipped - Name is required")
                            error_count += 1
                            continue
                        
                        # Check for duplicates if skip_duplicates is True
                        if skip_duplicates:
                            cursor.execute(
                                "SELECT customer_id FROM Customers WHERE name = %s AND contact_info = %s",
                                (name, contact_info)
                            )
                            if cursor.fetchone():
                                errors.append(f"Row {row_num}: Skipped - Duplicate customer (name: {name}, contact: {contact_info})")
                                error_count += 1
                                continue
                        
                        # Add customer to database
                        customers.add_customer(connection, cursor, name, contact_info, address)
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error - {str(e)}")
                        error_count += 1
                        continue
        
        finally:
            close_db(connection, cursor)
    
    except Exception as e:
        errors.append(f"Import failed: {str(e)}")
        error_count += 1
    
    return success_count, error_count, errors

def show_import_dialog(parent_window=None, refresh_callback=None):
    """
    Show the CSV import dialog for customers.
    """
    # File selection dialog
    file_path = filedialog.askopenfilename(
        parent=parent_window,
        title="Select Customer CSV File",
        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )
    
    if not file_path:
        return  # User cancelled
    
    try:
        # Show preview dialog
        preview_dialog = ImportPreviewDialog(parent_window, file_path, refresh_callback)
        
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to process file: {str(e)}", parent=parent_window)

class ImportPreviewDialog:
    """
    Dialog to preview CSV data before importing.
    """
    
    def __init__(self, parent_window, file_path, refresh_callback=None):
        self.parent_window = parent_window
        self.file_path = file_path
        self.refresh_callback = refresh_callback
        
        # Validate file first
        self.is_valid, self.errors, self.row_count, self.sample_data = validate_csv_structure(file_path)
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the preview dialog window."""
        self.dialog = tk.Toplevel(self.parent_window)
        self.dialog.title("Import Preview - Customer Data")
        self.dialog.geometry("700x600")
        self.dialog.minsize(600, 400)
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent_window)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (self.parent_window.winfo_rootx() + 50, 
                                       self.parent_window.winfo_rooty() + 50))
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="CSV Import Preview", font=("TkDefaultFont", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # File info
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(info_frame, text=f"File: {self.file_path.split('/')[-1]}", font=("TkDefaultFont", 10)).pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Rows to import: {self.row_count}", font=("TkDefaultFont", 10)).pack(anchor=tk.W)
        
        # Validation status
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        if self.is_valid:
            status_label = tk.Label(status_frame, text="✅ Validation: PASSED", fg="green", font=("TkDefaultFont", 10, "bold"))
        else:
            status_label = tk.Label(status_frame, text="❌ Validation: FAILED", fg="red", font=("TkDefaultFont", 10, "bold"))
        status_label.pack(anchor=tk.W)
        
        # Errors/Warnings
        if self.errors:
            error_frame = tk.LabelFrame(main_frame, text="Validation Messages")
            error_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            error_text = tk.Text(error_frame, height=8, wrap=tk.WORD)
            error_scrollbar = tk.Scrollbar(error_frame, orient=tk.VERTICAL, command=error_text.yview)
            error_text.configure(yscrollcommand=error_scrollbar.set)
            
            error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            error_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
            
            for error in self.errors:
                error_text.insert(tk.END, f"• {error}\n")
            error_text.configure(state=tk.DISABLED)
        
        # Sample data preview
        if self.sample_data:
            preview_frame = tk.LabelFrame(main_frame, text="Sample Data (First 5 rows)")
            preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Create treeview for sample data
            from tkinter import ttk
            columns = ("Name", "Contact Info", "Address")
            tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=6)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            for sample in self.sample_data:
                tree.insert("", tk.END, values=(sample['name'], sample['contact_info'], sample['address']))
            
            tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Options
        options_frame = tk.Frame(self.dialog)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        self.skip_duplicates_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Skip duplicate customers (same name)", 
                      variable=self.skip_duplicates_var).pack(anchor='w')
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        if self.is_valid:
            import_btn = tk.Button(button_frame, text="Import Data", command=self.import_data,
                                 bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
            import_btn.pack(side='right', padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                             bg="#f44336", fg="white", font=('Arial', 10))
        cancel_btn.pack(side='right', padx=5)
    
    def import_data(self):
        """Perform the actual data import."""
        try:
            # Show progress
            self.dialog.configure(cursor="wait")
            self.dialog.update()
            
            # Perform import
            success_count, error_count, errors = import_customers_from_csv(
                self.file_path, 
                self.parent_window, 
                self.skip_duplicates_var.get()
            )
            
            self.dialog.configure(cursor="")
            
            # Show results
            if success_count > 0:
                result_msg = f"Import completed!\n\n✅ Successfully imported: {success_count} customers"
                if error_count > 0:
                    result_msg += f"\n❌ Errors/Skipped: {error_count} rows"
                
                if errors and error_count > 0:
                    result_msg += "\n\nFirst few errors:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        result_msg += f"\n... and {len(errors) - 5} more errors"
                
                messagebox.showinfo("Import Results", result_msg, parent=self.parent_window)
                
                # Refresh the customer list if callback provided
                if self.refresh_callback:
                    self.refresh_callback()
                
                self.dialog.destroy()
            else:
                error_msg = f"Import failed! No customers were imported.\n\nErrors:\n" + "\n".join(errors[:10])
                messagebox.showerror("Import Failed", error_msg, parent=self.parent_window)
        
        except Exception as e:
            self.dialog.configure(cursor="")
            messagebox.showerror("Import Error", f"An unexpected error occurred: {str(e)}", parent=self.parent_window)



# Helper function for easy integration
def show_customer_import_dialog(parent_window=None, refresh_callback=None):
    """
    Main entry point for customer CSV import functionality.
    """
    show_import_dialog(parent_window, refresh_callback)

# ============================================================================
# INVENTORY IMPORT FUNCTIONALITY
# ============================================================================

def validate_inventory_row(row, row_number):
    """
    Validate a single inventory row from CSV data.
    Expected columns: sku, name, category_id, price, stock, supplier_id, cost
    """
    errors = []
    
    # Check if row has the correct number of columns
    if len(row) < 7:
        errors.append(f"Row {row_number}: Insufficient columns. Expected: sku, name, category_id, price, stock, supplier_id, cost")
        return errors
    
    sku, name, category_id, price, stock, supplier_id, cost = row[0:7]
    
    # Validate SKU (required)
    if not sku or not sku.strip():
        errors.append(f"Row {row_number}: SKU is required and cannot be empty")
    elif len(sku.strip()) > 255:
        errors.append(f"Row {row_number}: SKU is too long (max 255 characters)")
    
    # Validate name (required)
    if not name or not name.strip():
        errors.append(f"Row {row_number}: Name is required and cannot be empty")
    elif len(name.strip()) > 255:
        errors.append(f"Row {row_number}: Name is too long (max 255 characters)")
    
    # Validate category_id (required, must be positive integer)
    try:
        category_id_val = int(category_id.strip()) if category_id.strip() else 0
        if category_id_val <= 0:
            errors.append(f"Row {row_number}: Category ID must be a positive integer")
    except ValueError:
        errors.append(f"Row {row_number}: Category ID must be a valid integer")
    
    # Validate price (required, must be positive number)
    try:
        price_val = float(price.strip()) if price.strip() else 0
        if price_val <= 0:
            errors.append(f"Row {row_number}: Price must be greater than 0")
    except ValueError:
        errors.append(f"Row {row_number}: Price must be a valid number")
    
    # Validate stock (required, must be non-negative integer)
    try:
        stock_val = int(stock.strip()) if stock.strip() else 0
        if stock_val < 0:
            errors.append(f"Row {row_number}: Stock cannot be negative")
    except ValueError:
        errors.append(f"Row {row_number}: Stock must be a valid integer")
    
    # Validate supplier_id (optional, but if provided must be positive integer)
    if supplier_id and supplier_id.strip():
        try:
            supplier_id_val = int(supplier_id.strip())
            if supplier_id_val <= 0:
                errors.append(f"Row {row_number}: Supplier ID must be a positive integer")
        except ValueError:
            errors.append(f"Row {row_number}: Supplier ID must be a valid integer")
    
    # Validate cost (optional, but if provided must be non-negative number)
    if cost and cost.strip():
        try:
            cost_val = float(cost.strip())
            if cost_val < 0:
                errors.append(f"Row {row_number}: Cost cannot be negative")
        except ValueError:
            errors.append(f"Row {row_number}: Cost must be a valid number")
    
    return errors

def validate_inventory_csv_structure(file_path):
    """
    Validate the inventory CSV file structure and content before importing.
    Returns (is_valid, errors, row_count, sample_data)
    """
    errors = []
    row_count = 0
    sample_data = []
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            
            # Check header row
            try:
                header = next(reader)
                expected_headers = ['sku', 'name', 'category_id', 'price', 'stock', 'supplier_id', 'cost']
                
                if len(header) < len(expected_headers):
                    errors.append(f"Missing columns. Expected: {', '.join(expected_headers)}")
                    return False, errors, 0, []
                
                # Check if headers match (case insensitive)
                # Strip BOM and whitespace from headers
                header_clean = [h.strip().lower().replace('\ufeff', '') for h in header[:len(expected_headers)]]
                if header_clean != expected_headers:
                    errors.append(f"Header mismatch. Expected: {', '.join(expected_headers)}, Found: {', '.join(header[:len(expected_headers)])}")
            
            except StopIteration:
                errors.append("File is empty or has no header row")
                return False, errors, 0, []
            
            # Validate data rows
            for row_num, row in enumerate(reader, start=2):
                # Skip empty rows
                if not any(cell.strip() for cell in row if cell):
                    continue
                
                row_count += 1
                
                # Validate row structure
                row_errors = validate_inventory_row(row, row_num)
                if row_errors:
                    errors.extend(row_errors)
                
                # Store sample data (first 5 valid rows)
                if len(sample_data) < 5 and not row_errors:
                    sample_data.append({
                        'sku': row[0].strip() if len(row) > 0 else '',
                        'name': row[1].strip() if len(row) > 1 else '',
                        'category_id': row[2].strip() if len(row) > 2 else '',
                        'price': row[3].strip() if len(row) > 3 else '',
                        'stock': row[4].strip() if len(row) > 4 else '',
                        'supplier_id': row[5].strip() if len(row) > 5 else '',
                        'cost': row[6].strip() if len(row) > 6 else '0.00'
                    })
    
    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")
        return False, errors, 0, []
    
    # Determine if file is valid (no critical errors)
    critical_errors = [e for e in errors if "Error reading file" in e or "Missing columns" in e or "Header mismatch" in e]
    is_valid = len(critical_errors) == 0 and row_count > 0
    
    return is_valid, errors, row_count, sample_data

def import_inventory_from_csv(file_path, parent_window=None, skip_duplicates=True):
    """
    Import inventory items from CSV file into the database.
    Returns (success_count, error_count, errors)
    """
    success_count = 0
    error_count = 0
    errors = []
    
    try:
        # First validate the file
        is_valid, validation_errors, total_rows, sample_data = validate_inventory_csv_structure(file_path)
        
        if not is_valid:
            error_msg = "CSV validation failed:\n" + "\n".join(validation_errors)
            if parent_window:
                messagebox.showerror("Import Failed", error_msg, parent=parent_window)
            return 0, 0, validation_errors
        
        # Show preview and confirmation
        if validation_errors:  # Show warnings
            warning_msg = "Validation warnings found:\n" + "\n".join(validation_errors)
            warning_msg += f"\n\nProceed with import? ({total_rows} rows found)"
            if parent_window:
                if not messagebox.askyesno("Import Warning", warning_msg, parent=parent_window):
                    return 0, 0, ["Import cancelled by user"]
        
        # Get database connection
        connection, cursor = get_db()
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                
                # Skip header row
                next(reader)
                
                # Import each row
                for row_num, row in enumerate(reader, start=2):
                    # Skip empty rows
                    if not any(cell.strip() for cell in row if cell):
                        continue
                    
                    try:
                        # Extract data
                        sku = row[0].strip() if len(row) > 0 else ''
                        name = row[1].strip() if len(row) > 1 else ''
                        category_id = row[2].strip() if len(row) > 2 else ''
                        price = row[3].strip() if len(row) > 3 else ''
                        stock = row[4].strip() if len(row) > 4 else ''
                        supplier_id = row[5].strip() if len(row) > 5 else ''
                        cost = row[6].strip() if len(row) > 6 else '0.00'
                        
                        if not all([sku, name, category_id, price, stock]):
                            errors.append(f"Row {row_num}: Skipped - Required fields are missing")
                            error_count += 1
                            continue
                        
                        # Convert values to appropriate types
                        try:
                            category_id_val = int(category_id)
                            price_val = float(price)
                            stock_val = int(stock)
                            supplier_id_val = int(supplier_id) if supplier_id else None
                            cost_val = float(cost) if cost else 0.00
                        except ValueError as ve:
                            errors.append(f"Row {row_num}: Invalid data format - {str(ve)}")
                            error_count += 1
                            continue
                        
                        # Check for duplicates if skip_duplicates is True
                        if skip_duplicates:
                            cursor.execute("SELECT SKU FROM Products WHERE SKU = %s", (sku,))
                            if cursor.fetchone():
                                errors.append(f"Row {row_num}: Skipped - Duplicate SKU ({sku})")
                                error_count += 1
                                continue
                        
                        # Add item to database using inventory module
                        from ..core import inventory
                        inventory.add_item(connection, cursor, sku, name, category_id_val, price_val, stock_val, supplier_id_val, cost_val)
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error - {str(e)}")
                        error_count += 1
                        continue
        
        finally:
            close_db(connection, cursor)
    
    except Exception as e:
        errors.append(f"Import failed: {str(e)}")
        error_count += 1
    
    return success_count, error_count, errors

# ============================================================================
# SUPPLIER IMPORT FUNCTIONALITY
# ============================================================================

def validate_supplier_row(row, row_number):
    """
    Validate a single supplier row from CSV data.
    Expected columns: name, contact_info, address
    """
    errors = []
    
    # Check if row has the correct number of columns
    if len(row) < 3:
        errors.append(f"Row {row_number}: Insufficient columns. Expected: name, contact_info, address")
        return errors
    
    name, contact_info, address = row[0:3]
    
    # Validate name (required)
    if not name or not name.strip():
        errors.append(f"Row {row_number}: Name is required and cannot be empty")
    elif len(name.strip()) > 255:
        errors.append(f"Row {row_number}: Name is too long (max 255 characters)")
    
    # Validate contact_info (optional but if provided, should be reasonable)
    if contact_info and len(contact_info.strip()) > 255:
        errors.append(f"Row {row_number}: Contact info is too long (max 255 characters)")
    
    # Validate address (optional but if provided, should be reasonable)
    if address and len(address.strip()) > 255:
        errors.append(f"Row {row_number}: Address is too long (max 255 characters)")
    
    return errors

def validate_supplier_csv_structure(file_path):
    """
    Validate the supplier CSV file structure and content before importing.
    Returns (is_valid, errors, row_count, sample_data)
    """
    errors = []
    row_count = 0
    sample_data = []
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            
            # Check header row
            try:
                header = next(reader)
                expected_headers = ['name', 'contact_info', 'address']
                
                if len(header) < len(expected_headers):
                    errors.append(f"Missing columns. Expected: {', '.join(expected_headers)}")
                    return False, errors, 0, []
                
                # Check if headers match (case insensitive)
                # Strip BOM and whitespace from headers
                header_clean = [h.strip().lower().replace('\ufeff', '') for h in header[:len(expected_headers)]]
                if header_clean != expected_headers:
                    errors.append(f"Header mismatch. Expected: {', '.join(expected_headers)}, Found: {', '.join(header[:len(expected_headers)])}")
            
            except StopIteration:
                errors.append("File is empty or has no header row")
                return False, errors, 0, []
            
            # Validate data rows
            for row_num, row in enumerate(reader, start=2):
                # Skip empty rows
                if not any(cell.strip() for cell in row if cell):
                    continue
                
                row_count += 1
                
                # Validate row structure
                row_errors = validate_supplier_row(row, row_num)
                if row_errors:
                    errors.extend(row_errors)
                
                # Store sample data (first 5 valid rows)
                if len(sample_data) < 5 and not row_errors:
                    sample_data.append({
                        'name': row[0].strip() if len(row) > 0 else '',
                        'contact_info': row[1].strip() if len(row) > 1 else '',
                        'address': row[2].strip() if len(row) > 2 else ''
                    })
    
    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")
        return False, errors, 0, []
    
    # Determine if file is valid (no critical errors)
    critical_errors = [e for e in errors if "Error reading file" in e or "Missing columns" in e or "Header mismatch" in e]
    is_valid = len(critical_errors) == 0 and row_count > 0
    
    return is_valid, errors, row_count, sample_data

def import_suppliers_from_csv(file_path, parent_window=None, skip_duplicates=True):
    """
    Import suppliers from CSV file into the database.
    Returns (success_count, error_count, errors)
    """
    success_count = 0
    error_count = 0
    errors = []
    
    try:
        # First validate the file
        is_valid, validation_errors, total_rows, sample_data = validate_supplier_csv_structure(file_path)
        
        if not is_valid:
            error_msg = "CSV validation failed:\n" + "\n".join(validation_errors)
            if parent_window:
                messagebox.showerror("Import Failed", error_msg, parent=parent_window)
            return 0, 0, validation_errors
        
        # Show preview and confirmation
        if validation_errors:  # Show warnings
            warning_msg = "Validation warnings found:\n" + "\n".join(validation_errors)
            warning_msg += f"\n\nProceed with import? ({total_rows} rows found)"
            if parent_window:
                if not messagebox.askyesno("Import Warning", warning_msg, parent=parent_window):
                    return 0, 0, ["Import cancelled by user"]
        
        # Get database connection
        connection, cursor = get_db()
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                
                # Skip header row
                next(reader)
                
                # Import each row
                for row_num, row in enumerate(reader, start=2):
                    # Skip empty rows
                    if not any(cell.strip() for cell in row if cell):
                        continue
                    
                    try:
                        # Extract data
                        name = row[0].strip() if len(row) > 0 else ''
                        contact_info = row[1].strip() if len(row) > 1 else ''
                        address = row[2].strip() if len(row) > 2 else ''
                        
                        if not name:
                            errors.append(f"Row {row_num}: Skipped - Name is required")
                            error_count += 1
                            continue
                        
                        # Check for duplicates if skip_duplicates is True
                        if skip_duplicates:
                            cursor.execute("SELECT supplier_id FROM Suppliers WHERE name = %s", (name,))
                            if cursor.fetchone():
                                errors.append(f"Row {row_num}: Skipped - Duplicate supplier name ({name})")
                                error_count += 1
                                continue
                        
                        # Add supplier to database
                        from ..core import suppliers
                        suppliers.add_supplier(connection, cursor, name, contact_info, address)
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error - {str(e)}")
                        error_count += 1
                        continue
        
        finally:
            close_db(connection, cursor)
    
    except Exception as e:
        errors.append(f"Import failed: {str(e)}")
        error_count += 1
    
    return success_count, error_count, errors

# ============================================================================
# DIALOG WRAPPER FUNCTIONS
# ============================================================================

def show_inventory_import_dialog(parent_window=None, refresh_callback=None):
    """
    Show the CSV import dialog for inventory items.
    """
    # File selection dialog
    file_path = filedialog.askopenfilename(
        parent=parent_window,
        title="Select Inventory CSV File",
        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )
    
    if not file_path:
        return  # User cancelled
    
    try:
        # Show preview dialog
        InventoryImportPreviewDialog(parent_window, file_path, refresh_callback)
        
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to process file: {str(e)}", parent=parent_window)

def show_supplier_import_dialog(parent_window=None, refresh_callback=None):
    """
    Show the CSV import dialog for suppliers.
    """
    # File selection dialog
    file_path = filedialog.askopenfilename(
        parent=parent_window,
        title="Select Supplier CSV File",
        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )
    
    if not file_path:
        return  # User cancelled
    
    try:
        # Show preview dialog
        SupplierImportPreviewDialog(parent_window, file_path, refresh_callback)
        
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to process file: {str(e)}", parent=parent_window)

# ============================================================================
# PREVIEW DIALOG CLASSES
# ============================================================================

class InventoryImportPreviewDialog(ImportPreviewDialog):
    """
    Dialog to preview inventory CSV data before importing.
    """
    
    def __init__(self, parent_window, file_path, refresh_callback=None):
        self.parent_window = parent_window
        self.file_path = file_path
        self.refresh_callback = refresh_callback
        
        # Validate file first
        self.is_valid, self.errors, self.row_count, self.sample_data = validate_inventory_csv_structure(file_path)
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the preview dialog window."""
        self.dialog = tk.Toplevel(self.parent_window)
        self.dialog.title("Import Preview - Inventory Data")
        self.dialog.geometry("800x600")
        self.dialog.minsize(700, 450)
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent_window)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (self.parent_window.winfo_rootx() + 50, 
                                       self.parent_window.winfo_rooty() + 50))
        
        # File info
        info_frame = tk.Frame(self.dialog)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(info_frame, text=f"File: {self.file_path}", font=('Arial', 10, 'bold')).pack(anchor='w')
        tk.Label(info_frame, text=f"Rows to import: {self.row_count}", font=('Arial', 10)).pack(anchor='w')
        
        # Status
        status_frame = tk.Frame(self.dialog)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        if self.is_valid:
            status_text = "✅ File is valid and ready to import"
            status_color = "green"
        else:
            status_text = "❌ File has errors that must be fixed"
            status_color = "red"
        
        tk.Label(status_frame, text=status_text, fg=status_color, font=('Arial', 10, 'bold')).pack(anchor='w')
        
        # Preview data
        preview_frame = tk.LabelFrame(self.dialog, text="Data Preview (first 5 rows)", font=('Arial', 9, 'bold'))
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for preview
        columns = ('SKU', 'Name', 'Category ID', 'Price', 'Stock', 'Supplier ID', 'Cost')
        preview_tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        for col in columns:
            preview_tree.heading(col, text=col)
            preview_tree.column(col, width=100)
        
        # Add sample data
        for item in self.sample_data:
            preview_tree.insert('', 'end', values=(
                item['sku'], item['name'], item['category_id'], 
                item['price'], item['stock'], item['supplier_id'], item['cost']
            ))
        
        preview_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Errors/warnings
        if self.errors:
            error_frame = tk.LabelFrame(self.dialog, text="Validation Messages", font=('Arial', 9, 'bold'))
            error_frame.pack(fill='x', padx=10, pady=5)
            
            error_text = tk.Text(error_frame, height=6, wrap='word')
            error_scroll = ttk.Scrollbar(error_frame, orient='vertical', command=error_text.yview)
            error_text.configure(yscrollcommand=error_scroll.set)
            
            error_text.insert('1.0', '\n'.join(self.errors))
            error_text.configure(state='disabled')
            
            error_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
            error_scroll.pack(side='right', fill='y', pady=5)
        
        # Options
        options_frame = tk.Frame(self.dialog)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        self.skip_duplicates_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Skip duplicate items (same SKU)", 
                      variable=self.skip_duplicates_var).pack(anchor='w')
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        if self.is_valid:
            import_btn = tk.Button(button_frame, text="Import Data", command=self.start_import,
                                 bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
            import_btn.pack(side='right', padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                             bg="#f44336", fg="white", font=('Arial', 10))
        cancel_btn.pack(side='right', padx=5)
    
    def start_import(self):
        """Start the import process."""
        try:
            self.dialog.configure(cursor="watch")
            
            # Import the data
            success_count, error_count, errors = import_inventory_from_csv(
                self.file_path, 
                self.parent_window, 
                self.skip_duplicates_var.get()
            )
            
            self.dialog.configure(cursor="")
            
            # Show results
            if success_count > 0:
                result_msg = f"Import completed!\n\n✅ Successfully imported: {success_count} inventory items"
                if error_count > 0:
                    result_msg += f"\n❌ Errors/Skipped: {error_count} rows"
                
                if errors and error_count > 0:
                    result_msg += "\n\nFirst few errors:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        result_msg += f"\n... and {len(errors) - 5} more errors"
                
                messagebox.showinfo("Import Results", result_msg, parent=self.parent_window)
                
                # Refresh the inventory list if callback provided
                if self.refresh_callback:
                    self.refresh_callback()
                
                self.dialog.destroy()
            else:
                error_msg = f"Import failed! No inventory items were imported.\n\nErrors:\n" + "\n".join(errors[:10])
                messagebox.showerror("Import Failed", error_msg, parent=self.parent_window)
        
        except Exception as e:
            self.dialog.configure(cursor="")
            messagebox.showerror("Import Error", f"An unexpected error occurred: {str(e)}", parent=self.parent_window)


class SupplierImportPreviewDialog(ImportPreviewDialog):
    """
    Dialog to preview supplier CSV data before importing.
    """
    
    def __init__(self, parent_window, file_path, refresh_callback=None):
        self.parent_window = parent_window
        self.file_path = file_path
        self.refresh_callback = refresh_callback
        
        # Validate file first
        self.is_valid, self.errors, self.row_count, self.sample_data = validate_supplier_csv_structure(file_path)
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the preview dialog window."""
        self.dialog = tk.Toplevel(self.parent_window)
        self.dialog.title("Import Preview - Supplier Data")
        self.dialog.geometry("700x600")
        self.dialog.minsize(600, 400)
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent_window)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (self.parent_window.winfo_rootx() + 50, 
                                       self.parent_window.winfo_rooty() + 50))
        
        # File info
        info_frame = tk.Frame(self.dialog)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(info_frame, text=f"File: {self.file_path}", font=('Arial', 10, 'bold')).pack(anchor='w')
        tk.Label(info_frame, text=f"Rows to import: {self.row_count}", font=('Arial', 10)).pack(anchor='w')
        
        # Status
        status_frame = tk.Frame(self.dialog)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        if self.is_valid:
            status_text = "✅ File is valid and ready to import"
            status_color = "green"
        else:
            status_text = "❌ File has errors that must be fixed"
            status_color = "red"
        
        tk.Label(status_frame, text=status_text, fg=status_color, font=('Arial', 10, 'bold')).pack(anchor='w')
        
        # Preview data
        preview_frame = tk.LabelFrame(self.dialog, text="Data Preview (first 5 rows)", font=('Arial', 9, 'bold'))
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for preview
        columns = ('Name', 'Contact Info', 'Address')
        preview_tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        for col in columns:
            preview_tree.heading(col, text=col)
            preview_tree.column(col, width=150)
        
        # Add sample data
        for item in self.sample_data:
            preview_tree.insert('', 'end', values=(
                item['name'], item['contact_info'], item['address']
            ))
        
        preview_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Errors/warnings
        if self.errors:
            error_frame = tk.LabelFrame(self.dialog, text="Validation Messages", font=('Arial', 9, 'bold'))
            error_frame.pack(fill='x', padx=10, pady=5)
            
            error_text = tk.Text(error_frame, height=6, wrap='word')
            error_scroll = ttk.Scrollbar(error_frame, orient='vertical', command=error_text.yview)
            error_text.configure(yscrollcommand=error_scroll.set)
            
            error_text.insert('1.0', '\n'.join(self.errors))
            error_text.configure(state='disabled')
            
            error_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
            error_scroll.pack(side='right', fill='y', pady=5)
        
        # Options
        options_frame = tk.Frame(self.dialog)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        self.skip_duplicates_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Skip duplicate suppliers (same name)", 
                      variable=self.skip_duplicates_var).pack(anchor='w')
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        if self.is_valid:
            import_btn = tk.Button(button_frame, text="Import Data", command=self.start_import,
                                 bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
            import_btn.pack(side='right', padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                             bg="#f44336", fg="white", font=('Arial', 10))
        cancel_btn.pack(side='right', padx=5)
    
    def start_import(self):
        """Start the import process."""
        try:
            self.dialog.configure(cursor="watch")
            
            # Import the data
            success_count, error_count, errors = import_suppliers_from_csv(
                self.file_path, 
                self.parent_window, 
                self.skip_duplicates_var.get()
            )
            
            self.dialog.configure(cursor="")
            
            # Show results
            if success_count > 0:
                result_msg = f"Import completed!\n\n✅ Successfully imported: {success_count} suppliers"
                if error_count > 0:
                    result_msg += f"\n❌ Errors/Skipped: {error_count} rows"
                
                if errors and error_count > 0:
                    result_msg += "\n\nFirst few errors:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        result_msg += f"\n... and {len(errors) - 5} more errors"
                
                messagebox.showinfo("Import Results", result_msg, parent=self.parent_window)
                
                # Refresh the supplier list if callback provided
                if self.refresh_callback:
                    self.refresh_callback()
                
                self.dialog.destroy()
            else:
                error_msg = f"Import failed! No suppliers were imported.\n\nErrors:\n" + "\n".join(errors[:10])
                messagebox.showerror("Import Failed", error_msg, parent=self.parent_window)
        
        except Exception as e:
            self.dialog.configure(cursor="")
            messagebox.showerror("Import Error", f"An unexpected error occurred: {str(e)}", parent=self.parent_window)

def create_sample_inventory_csv(file_path):
    """
    Create a sample CSV file with the correct format for inventory import.
    """
    sample_data = [
        ["sku", "name", "category", "price", "stock", "supplier_id"],
        ["LAPTOP001", "Dell Laptop", "Electronics", "999.99", "10", "1"],
        ["MOUSE001", "Wireless Mouse", "Electronics", "29.99", "50", "1"],
        ["CHAIR001", "Office Chair", "Furniture", "199.99", "15", "2"],
        ["DESK001", "Standing Desk", "Furniture", "399.99", "8", "2"],
        ["BOOK001", "Python Programming", "Books", "49.99", "25", "3"]
    ]
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sample_data)
        return True
    except Exception as e:
        return False, str(e)

def create_sample_supplier_csv(file_path):
    """
    Create a sample CSV file with the correct format for supplier import.
    """
    sample_data = [
        ["name", "contact_info", "address"],
        ["Tech Supplies Inc", "tech@supplies.com", "123 Tech St, Silicon Valley, CA"],
        ["Office Furniture Co", "+1-555-123-4567", "456 Furniture Ave, Dallas, TX"],
        ["Book Distributors LLC", "orders@bookdist.com", "789 Literary Ln, New York, NY"],
        ["Electronics Wholesale", "+1-555-987-6543", "321 Circuit Rd, Austin, TX"],
        ["Global Suppliers", "sales@globalsuppliers.com", "654 International Blvd, Miami, FL"]
    ]
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sample_data)
        return True
    except Exception as e:
        return False, str(e)
