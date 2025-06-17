"""
Main Dashboard UI Module - Orchestrator
Main dashboard controller with global filters and subtab management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import csv
import json
from PIL import Image, ImageTk
from tkcalendar import DateEntry

# Import modular dashboard components
from dashboard_base import DashboardBaseUI, DashboardConstants
from dashboard_overview_ui import OverviewUI
from dashboard_analytics_ui import AnalyticsUI
from dashboard_performance_ui import PerformanceUI
from dashboard_simulation_ui import SimulationUI

class DashboardUI:
    """Main Dashboard UI class with 4 subtabs: Overview, Analytics, Performance, Simulation"""
    
    def __init__(self, parent_frame, **callbacks):
        self.parent = parent_frame
        self.callbacks = callbacks
        
        # Initialize filter variables
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.employee_filter_var = tk.StringVar()
        self.supplier_filter_var = tk.StringVar()
        self.category_filter_var = tk.StringVar()
        
        # Set default date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
        
        # Create main dashboard layout
        self.create_dashboard_layout()
        
    def create_dashboard_layout(self):
        """Create the main dashboard structure with filters and subtabs"""
        
        # Main dashboard frame
        self.main_frame = ttk.Frame(self.parent, padding="10")
        self.main_frame.pack(fill='both', expand=True)
        
        # Dashboard header
        self.create_dashboard_header()
        
        # Global filter controls
        self.create_filter_controls()
        
        # Separator
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
        # Create subtabs notebook
        self.create_subtabs()
        
    def create_dashboard_header(self):
        """Create dashboard header with title and info"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Dashboard title
        title_label = ttk.Label(
            header_frame, 
            text="📊 Enhanced Business Intelligence Dashboard", 
            font=DashboardConstants.HEADER_FONT
        )
        title_label.pack(side=tk.LEFT)
        
        # Current time display
        self.time_label = ttk.Label(
            header_frame, 
            text=f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
            font=DashboardConstants.BODY_FONT
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Update time every minute
        self.update_time()
        
    def update_time(self):
        """Update the current time display"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.time_label.config(text=f"📅 {current_time}")
        # Schedule next update in 60 seconds
        self.parent.after(60000, self.update_time)
        
    def create_filter_controls(self):
        """Create comprehensive filter controls panel"""
        filter_frame = ttk.LabelFrame(self.main_frame, text="🔍 Global Filters", padding="10")
        filter_frame.pack(fill='x', pady=(0, 10))
        
        # Row 1: Date filters and quick buttons
        date_row = ttk.Frame(filter_frame)
        date_row.pack(fill='x', pady=(0, 5))
        
        # Date range selection
        ttk.Label(date_row, text="Date Range:", font=DashboardConstants.SUBHEADER_FONT).pack(side=tk.LEFT, padx=(0, 5))
        
        # Start date
        ttk.Label(date_row, text="From:").pack(side=tk.LEFT, padx=(10, 2))
        try:
            self.start_date_picker = DateEntry(
                date_row, 
                width=10, 
                background='darkblue',
                foreground='white', 
                borderwidth=2,
                textvariable=self.start_date_var,
                date_pattern='yyyy-mm-dd'
            )
            self.start_date_picker.pack(side=tk.LEFT, padx=(0, 10))
        except:
            # Fallback to regular entry if DateEntry not available
            self.start_date_entry = ttk.Entry(date_row, textvariable=self.start_date_var, width=12)
            self.start_date_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # End date
        ttk.Label(date_row, text="To:").pack(side=tk.LEFT, padx=(0, 2))
        try:
            self.end_date_picker = DateEntry(
                date_row, 
                width=10, 
                background='darkblue',
                foreground='white', 
                borderwidth=2,
                textvariable=self.end_date_var,
                date_pattern='yyyy-mm-dd'
            )
            self.end_date_picker.pack(side=tk.LEFT, padx=(0, 15))
        except:
            # Fallback to regular entry if DateEntry not available
            self.end_date_entry = ttk.Entry(date_row, textvariable=self.end_date_var, width=12)
            self.end_date_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Quick date buttons
        quick_buttons_frame = ttk.Frame(date_row)
        quick_buttons_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(quick_buttons_frame, text="Today", command=self.set_today, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_buttons_frame, text="This Week", command=self.set_this_week, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_buttons_frame, text="This Month", command=self.set_this_month, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_buttons_frame, text="Last Quarter", command=self.set_last_quarter, width=12).pack(side=tk.LEFT, padx=2)
        
        # Row 2: Entity filters
        entity_row = ttk.Frame(filter_frame)
        entity_row.pack(fill='x', pady=(5, 0))
        
        # Employee filter
        ttk.Label(entity_row, text="Employee:", font=DashboardConstants.SUBHEADER_FONT).pack(side=tk.LEFT, padx=(0, 5))
        self.employee_combobox = ttk.Combobox(
            entity_row, 
            textvariable=self.employee_filter_var, 
            width=15, 
            state="readonly"
        )
        self.employee_combobox.pack(side=tk.LEFT, padx=(0, 15))
        
        # Supplier filter
        ttk.Label(entity_row, text="Supplier:", font=DashboardConstants.SUBHEADER_FONT).pack(side=tk.LEFT, padx=(0, 5))
        self.supplier_combobox = ttk.Combobox(
            entity_row, 
            textvariable=self.supplier_filter_var, 
            width=15, 
            state="readonly"
        )
        self.supplier_combobox.pack(side=tk.LEFT, padx=(0, 15))
        
        # Category filter
        ttk.Label(entity_row, text="Category:", font=DashboardConstants.SUBHEADER_FONT).pack(side=tk.LEFT, padx=(0, 5))
        self.category_combobox = ttk.Combobox(
            entity_row, 
            textvariable=self.category_filter_var, 
            width=15, 
            state="readonly"
        )
        self.category_combobox.pack(side=tk.LEFT, padx=(0, 15))
        
        # Action buttons
        action_frame = ttk.Frame(entity_row)
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_frame, text="🔄 Refresh", command=self.refresh_dashboard, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="📤 Export", command=self.show_export_options, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="🔧 Settings", command=self.show_settings, width=10).pack(side=tk.LEFT, padx=2)
        
        # Initialize filter data
        self.employees_data = []  # Store full employee data for ID mapping
        self.suppliers_data = []  # Store full supplier data for ID mapping
        self.categories_data = []  # Store full category data for ID mapping
        self.load_filter_data()
        
        # Bind filter change events to auto-refresh
        self.employee_combobox.bind('<<ComboboxSelected>>', self.on_filter_changed)
        self.supplier_combobox.bind('<<ComboboxSelected>>', self.on_filter_changed)
        self.category_combobox.bind('<<ComboboxSelected>>', self.on_filter_changed)
        
        # Bind date change events
        try:
            if hasattr(self, 'start_date_picker'):
                self.start_date_picker.bind('<<DateEntrySelected>>', self.on_filter_changed)
            if hasattr(self, 'end_date_picker'):
                self.end_date_picker.bind('<<DateEntrySelected>>', self.on_filter_changed)
        except:
            pass
        
    def create_subtabs(self):
        """Create the 4 main subtabs: Overview, Analytics, Performance, Simulation"""
        
        # Subtabs notebook
        self.subtabs_notebook = ttk.Notebook(self.main_frame)
        self.subtabs_notebook.pack(fill='both', expand=True)
        
        # Create subtab frames
        self.overview_tab = ttk.Frame(self.subtabs_notebook)
        self.analytics_tab = ttk.Frame(self.subtabs_notebook)
        self.performance_tab = ttk.Frame(self.subtabs_notebook)
        self.simulation_tab = ttk.Frame(self.subtabs_notebook)
        
        # Add subtabs to notebook
        self.subtabs_notebook.add(self.overview_tab, text="📈 Overview")
        self.subtabs_notebook.add(self.analytics_tab, text="📊 Analytics")
        self.subtabs_notebook.add(self.performance_tab, text="👤 Performance")
        self.subtabs_notebook.add(self.simulation_tab, text="🎲 Simulation")
        
        # Initialize subtab UIs
        self.overview_ui = OverviewUI(self.overview_tab, self.callbacks)
        self.analytics_ui = AnalyticsUI(self.analytics_tab, self.callbacks)
        self.performance_ui = PerformanceUI(self.performance_tab, self.callbacks)
        self.simulation_ui = SimulationUI(self.simulation_tab, self.callbacks)
        
        # Bind tab change event
        self.subtabs_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def load_filter_data(self):
        """Load data for filter dropdowns"""
        try:
            # Load employees with full data
            if 'get_employees_callback' in self.callbacks and self.callbacks['get_employees_callback']:
                self.employees_data = self.callbacks['get_employees_callback']()
                employee_names = ["All Employees"] + [emp['name'] for emp in self.employees_data if emp['name']]
                self.employee_combobox['values'] = employee_names
                self.employee_combobox.set("All Employees")
            
            # Load suppliers with full data
            if 'get_suppliers_callback' in self.callbacks and self.callbacks['get_suppliers_callback']:
                self.suppliers_data = self.callbacks['get_suppliers_callback']()
                supplier_names = ["All Suppliers"] + [sup['name'] for sup in self.suppliers_data if sup['name']]
                self.supplier_combobox['values'] = supplier_names
                self.supplier_combobox.set("All Suppliers")
            
            # Load categories from database
            try:
                from dashboard import get_categories
                self.categories_data = get_categories()
                category_names = ["All Categories"] + [cat['name'] for cat in self.categories_data if cat['name']]
                self.category_combobox['values'] = category_names
                self.category_combobox.set("All Categories")
            except Exception as e:
                # Fallback to hardcoded categories if database fails
                categories = ["All Categories", "Bread", "Buns", "Pasta", "Doughnuts", "Noodles", "Clothing", "Beverages"]
                self.category_combobox['values'] = categories
                self.category_combobox.set("All Categories")
            
        except Exception as e:
            print(f"Error loading filter data: {e}")
    
    def get_employee_id_from_name(self, employee_name):
        """Get employee ID from employee name"""
        if employee_name == "All Employees" or not employee_name:
            return None
        
        for emp in self.employees_data:
            if emp['name'] == employee_name:
                return emp['employee_id']
        return None
    
    def get_supplier_id_from_name(self, supplier_name):
        """Get supplier ID from supplier name"""
        if supplier_name == "All Suppliers" or not supplier_name:
            return None
            
        for sup in self.suppliers_data:
            if sup['name'] == supplier_name:
                return sup['supplier_id']
        return None
    
    def get_category_id_from_name(self, category_name):
        """Get category ID from category name"""
        if category_name == "All Categories" or not category_name:
            return None
            
        for cat in self.categories_data:
            if cat['name'] == category_name:
                return cat['category_id']
        return None
    
    def on_filter_changed(self, event=None):
        """Handle filter change events - auto refresh dashboard"""
        self.refresh_dashboard()
    
    # Quick date filter methods
    def set_today(self):
        """Set date range to today"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.start_date_var.set(today)
        self.end_date_var.set(today)
        self.refresh_dashboard()
    
    def set_this_week(self):
        """Set date range to this week"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        self.start_date_var.set(start_of_week.strftime('%Y-%m-%d'))
        self.end_date_var.set(today.strftime('%Y-%m-%d'))
        self.refresh_dashboard()
    
    def set_this_month(self):
        """Set date range to this month"""
        today = datetime.now()
        start_of_month = today.replace(day=1)
        self.start_date_var.set(start_of_month.strftime('%Y-%m-%d'))
        self.end_date_var.set(today.strftime('%Y-%m-%d'))
        self.refresh_dashboard()
    
    def set_last_quarter(self):
        """Set date range to last quarter"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
        self.refresh_dashboard()
    
    def get_current_filters(self):
        """Get current filter values with proper ID mapping"""
        return {
            'start_date': self.start_date_var.get(),
            'end_date': self.end_date_var.get(),
            'employee': self.employee_filter_var.get(),
            'employee_id': self.get_employee_id_from_name(self.employee_filter_var.get()),
            'supplier': self.supplier_filter_var.get(),
            'supplier_id': self.get_supplier_id_from_name(self.supplier_filter_var.get()),
            'category': self.category_filter_var.get(),
            'category_id': self.get_category_id_from_name(self.category_filter_var.get())
        }
    
    def fetch_dashboard_data(self, filters):
        """Fetch all dashboard data for export based on current filters"""
        try:
            # Import dashboard functions
            from dashboard import (
                get_sales_summary, get_top_products, get_recent_activities,
                get_inventory_value, calculate_profit_margins
            )
            
            # Get sales summary data
            sales_data = get_sales_summary(
                filters['start_date'], 
                filters['end_date'],
                filters['employee_id'],
                filters['supplier_id'],
                filters['category_id']
            )
            
            # Get top products data  
            top_products = get_top_products(
                filters['start_date'],
                filters['end_date'],
                10,  # Get top 10 products
                filters['employee_id'],
                filters['supplier_id'],
                filters['category_id']
            )
            
            # Get recent activities
            recent_activities = get_recent_activities(
                filters['start_date'],
                filters['end_date'],
                20,  # Get last 20 activities
                filters['employee_id'],
                filters['supplier_id'],
                filters['category_id']
            )
            
            # Format data for export
            data = {
                'columns': [
                    'Metric', 'Value', 'Period', 'Employee Filter', 
                    'Supplier Filter', 'Category Filter'
                ],
                'rows': []
            }
            
            # Add sales summary
            if sales_data:
                data['rows'].extend([
                    ['Total Sales', f"${sales_data.get('total_sales', 0):.2f}", 
                     f"{filters['start_date']} to {filters['end_date']}", 
                     filters['employee'], filters['supplier'], filters['category']],
                    ['Total Transactions', sales_data.get('total_transactions', 0),
                     f"{filters['start_date']} to {filters['end_date']}", 
                     filters['employee'], filters['supplier'], filters['category']],
                    ['Average Transaction', f"${sales_data.get('avg_transaction', 0):.2f}",
                     f"{filters['start_date']} to {filters['end_date']}", 
                     filters['employee'], filters['supplier'], filters['category']]
                ])
            
            # Add top products section
            data['rows'].append(['--- TOP PRODUCTS ---', '', '', '', '', ''])
            for i, product in enumerate(top_products[:5], 1):
                data['rows'].append([
                    f'Top Product #{i}',
                    product.get('name', 'N/A'),
                    f"{product.get('units_sold', 0)} units sold",
                    filters['employee'], filters['supplier'], filters['category']
                ])
            
            # Add recent activities section  
            data['rows'].append(['--- RECENT ACTIVITIES ---', '', '', '', '', ''])
            for activity in recent_activities[:5]:
                data['rows'].append([
                    'Activity',
                    activity.get('type', 'Sale'),
                    f"${activity.get('total', 0):.2f}",
                    activity.get('employee_name', 'N/A'),
                    activity.get('activity_datetime', 'N/A'),
                    filters['category']
                ])
            
            return data
            
        except Exception as e:
            print(f"Error fetching dashboard data: {e}")
            # Return empty data structure
            return {
                'columns': ['Metric', 'Value', 'Period', 'Employee', 'Supplier', 'Category'],
                'rows': [['No data available', '', '', '', '', '']]
            }
    
    def refresh_dashboard(self):
        """Refresh all dashboard data based on current filters"""
        try:
            filters = self.get_current_filters()
            
            # Refresh all subtabs
            if hasattr(self, 'overview_ui'):
                self.overview_ui.refresh_data(filters)
            if hasattr(self, 'analytics_ui'):
                self.analytics_ui.refresh_data(filters)
            if hasattr(self, 'performance_ui'):
                self.performance_ui.refresh_data(filters)
            if hasattr(self, 'simulation_ui'):
                self.simulation_ui.refresh_data(filters)
                
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
    
    def on_tab_changed(self, event):
        """Handle tab change events"""
        selected_tab = self.subtabs_notebook.select()
        tab_text = self.subtabs_notebook.tab(selected_tab, "text")
        
        # Refresh data for the selected tab
        self.refresh_dashboard()
    
    def show_export_options(self):
        """Show export options dialog"""
        export_window = tk.Toplevel(self.parent)
        export_window.title("Export Dashboard Data")
        export_window.geometry("400x300")
        export_window.transient(self.parent)
        export_window.grab_set()
        
        # Export options
        ttk.Label(export_window, text="Export Options", font=DashboardConstants.HEADER_FONT).pack(pady=10)
        
        export_frame = ttk.Frame(export_window)
        export_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        ttk.Button(export_frame, text="📄 Export to CSV", width=20, command=self.export_to_csv).pack(pady=5)
        ttk.Button(export_frame, text="📊 Export to Excel", width=20, command=self.export_to_excel).pack(pady=5)
        ttk.Button(export_frame, text="📑 Generate PDF Report", width=20, command=self.generate_pdf_report).pack(pady=5)
        ttk.Button(export_frame, text="📈 Export Charts", width=20, command=self.export_charts).pack(pady=5)
        
        ttk.Button(export_window, text="Close", command=export_window.destroy).pack(pady=10)
    
    def export_to_csv(self):
        """Export dashboard data to CSV file"""
        try:
            filters = self.get_current_filters()
            data = self.fetch_dashboard_data(filters)
            
            # Ask user for file save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save CSV File"
            )
            if not file_path:
                return  # User cancelled save dialog
            
            # Write data to CSV file
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write header row
                writer.writerow(data['columns'])
                
                # Write data rows
                for row in data['rows']:
                    writer.writerow(row)
            
            messagebox.showinfo("Export to CSV", "Data exported successfully to CSV file.")
        
        except Exception as e:
            messagebox.showerror("Export to CSV", f"Error exporting data to CSV: {e}")
    
    def export_to_excel(self):
        """Export dashboard data to Excel file (XLSX)"""
        try:
            filters = self.get_current_filters()
            data = self.fetch_dashboard_data(filters)
            
            # Ask user for file save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Excel File"
            )
            if not file_path:
                return  # User cancelled save dialog
            
            # Try to write data to Excel file
            try:
                import xlsxwriter
                
                workbook = xlsxwriter.Workbook(file_path)
                worksheet = workbook.add_worksheet("Dashboard Data")
                
                # Write header row with formatting
                header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
                for col_num, column_title in enumerate(data['columns']):
                    worksheet.write(0, col_num, column_title, header_format)
                
                # Write data rows
                for row_num, row_data in enumerate(data['rows'], start=1):
                    for col_num, cell_data in enumerate(row_data):
                        worksheet.write(row_num, col_num, cell_data)
                
                # Auto-adjust column widths
                for col_num, column_title in enumerate(data['columns']):
                    worksheet.set_column(col_num, col_num, 20)
                
                workbook.close()
                
                messagebox.showinfo("Export to Excel", "Data exported successfully to Excel file.")
                
            except ImportError:
                # xlsxwriter not available, fall back to CSV
                csv_path = file_path.replace('.xlsx', '.csv')
                with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(data['columns'])
                    for row in data['rows']:
                        writer.writerow(row)
                
                messagebox.showinfo("Export Data", 
                    "Excel library not available. Data saved as CSV file instead.")
        
        except Exception as e:
            messagebox.showerror("Export to Excel", f"Error exporting data to Excel: {e}")
    
    def generate_pdf_report(self):
        """Generate PDF report of dashboard data"""
        try:
            filters = self.get_current_filters()
            data = self.fetch_dashboard_data(filters)
            
            # Ask user for file save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Save PDF Report"
            )
            if not file_path:
                return  # User cancelled save dialog
            
            # Try to generate PDF report
            try:
                from fpdf import FPDF
                
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                
                # Set font
                pdf.set_font("Arial", size=12)
                
                # Title
                pdf.cell(0, 10, "Dashboard Report", ln=True, align="C")
                pdf.ln(10)
                
                # Date range
                pdf.cell(0, 10, f"Date Range: {filters['start_date']} to {filters['end_date']}", ln=True, align="L")
                pdf.ln(5)
                
                # Table header
                pdf.set_font("Arial", style='B', size=10)
                for column_title in data['columns']:
                    pdf.cell(30, 10, column_title, border=1, align="C")
                pdf.ln()
                
                # Table rows
                pdf.set_font("Arial", size=8)
                for row_data in data['rows']:
                    for cell_data in row_data:
                        pdf.cell(30, 10, str(cell_data)[:15], border=1, align="C")  # Truncate long text
                    pdf.ln()
                
                # Output to file
                pdf.output(file_path)
                
                messagebox.showinfo("Generate PDF Report", "PDF report generated successfully.")
                
            except ImportError:
                # FPDF not available, create a text-based report instead
                with open(file_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                    f.write("DASHBOARD REPORT\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Date Range: {filters['start_date']} to {filters['end_date']}\n")
                    f.write(f"Employee Filter: {filters['employee']}\n")
                    f.write(f"Supplier Filter: {filters['supplier']}\n")
                    f.write(f"Category Filter: {filters['category']}\n\n")
                    
                    # Write data
                    f.write(" | ".join(data['columns']) + "\n")
                    f.write("-" * 100 + "\n")
                    for row in data['rows']:
                        f.write(" | ".join(str(cell) for cell in row) + "\n")
                
                messagebox.showinfo("Generate Report", 
                    "PDF library not available. Report saved as text file instead.")
        
        except Exception as e:
            messagebox.showerror("Generate PDF Report", f"Error generating PDF report: {e}")
            pdf.ln(5)
            
            # Table header
            pdf.set_font("Arial", style='B', size=12)
            for column_title in data['columns']:
                pdf.cell(40, 10, column_title, border=1, align="C")
            pdf.ln()
            
            # Table rows
            pdf.set_font("Arial", size=12)
            for row_data in data['rows']:
                for cell_data in row_data:
                    pdf.cell(40, 10, str(cell_data), border=1, align="C")
                pdf.ln()
            
            # Output to file
            pdf.output(file_path)
            
            messagebox.showinfo("Generate PDF Report", "PDF report generated successfully.")
        
        except Exception as e:
            messagebox.showerror("Generate PDF Report", f"Error generating PDF report: {e}")
    
    def export_charts(self):
        """Export dashboard charts as images"""
        try:
            # Ask user for directory to save chart images
            dir_path = filedialog.askdirectory(title="Select Directory to Save Chart Images")
            if not dir_path:
                return  # User cancelled directory dialog
            
            # Get current filters
            filters = self.get_current_filters()
            
            # Export each subtab's chart
            if hasattr(self.overview_ui, 'chart'):
                self.overview_ui.chart.export_as_image(dir_path, "overview_chart", filters)
            if hasattr(self.analytics_ui, 'chart'):
                self.analytics_ui.chart.export_as_image(dir_path, "analytics_chart", filters)
            if hasattr(self.performance_ui, 'chart'):
                self.performance_ui.chart.export_as_image(dir_path, "performance_chart", filters)
            if hasattr(self.simulation_ui, 'chart'):
                self.simulation_ui.chart.export_as_image(dir_path, "simulation_chart", filters)
            
            messagebox.showinfo("Export Charts", "Charts exported successfully as images.")
        
        except Exception as e:
            messagebox.showerror("Export Charts", f"Error exporting charts: {e}")
    
    def show_settings(self):
        """Show dashboard settings dialog"""
        settings_window = tk.Toplevel(self.parent)
        settings_window.title("Dashboard Settings")
        settings_window.geometry("350x250")
        settings_window.transient(self.parent)
        settings_window.grab_set()
        
        ttk.Label(settings_window, text="Dashboard Settings", font=DashboardConstants.HEADER_FONT).pack(pady=10)
        
        settings_frame = ttk.Frame(settings_window)
        settings_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Auto-refresh setting
        auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Auto-refresh data", variable=auto_refresh_var).pack(anchor='w', pady=5)
        
        # Default date range
        ttk.Label(settings_frame, text="Default date range:").pack(anchor='w', pady=(10, 2))
        date_range_var = tk.StringVar(value="Last 30 days")
        date_range_combo = ttk.Combobox(settings_frame, textvariable=date_range_var, 
                                       values=["Today", "Last 7 days", "Last 30 days", "Last quarter"], 
                                       state="readonly")
        date_range_combo.pack(anchor='w', pady=2)
        
        # Currency format
        ttk.Label(settings_frame, text="Currency format:").pack(anchor='w', pady=(10, 2))
        currency_var = tk.StringVar(value="USD ($)")
        currency_combo = ttk.Combobox(settings_frame, textvariable=currency_var, 
                                     values=["USD ($)", "EUR (€)", "GBP (£)", "CAD (C$)"], 
                                     state="readonly")
        currency_combo.pack(anchor='w', pady=2)
        
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        ttk.Button(button_frame, text="Save", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
