"""
Main Dashboard UI Module - Orchestrator
Main dashboard controller with global filters and subtab management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import csv
import time  # Add time import for caching
import json
import logging
from PIL import Image, ImageTk
from tkcalendar import DateEntry

# Get logger instance (configured in main.py)
logger = logging.getLogger(__name__)

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
        
        # Set default date range (last 7 days for faster initial load)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Reduced from 30 to 7 days
        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
        
        # Lazy loading - track which tabs have been initialized
        self.initialized_tabs = set()
        self.subtab_uis = {}
        
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
        
        # Don't initialize subtab UIs immediately - use lazy loading
        # They will be initialized when first accessed
        
        # Bind tab change event for lazy loading
        self.subtabs_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Initialize the first tab (Overview) immediately for better UX
        self.initialize_tab("overview")
        
        # Schedule pre-warming of other tabs after initial load (for even faster switching)
        self.parent.after(2000, self.prewarm_tabs)  # 2 second delay
        
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
            logger.error(f"Error loading filter data: {e}")
    
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
                20,  # Get last 20 activities (limit)
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
                    ['Total Transactions', sales_data.get('total_orders', 0),
                     f"{filters['start_date']} to {filters['end_date']}", 
                     filters['employee'], filters['supplier'], filters['category']],
                    ['Average Transaction', f"${sales_data.get('avg_order_value', 0):.2f}",
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
                # Format datetime
                datetime_str = activity.get('sale_datetime', 'N/A')
                if hasattr(datetime_str, 'strftime'):
                    datetime_str = datetime_str.strftime('%Y-%m-%d %H:%M:%S')
                
                data['rows'].append([
                    'Activity',
                    activity.get('type', 'Sale'),
                    f"${activity.get('sale_total', 0):.2f}",
                    activity.get('employee_name', 'N/A'),
                    datetime_str,
                    filters['category']
                ])
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            # Return empty data structure
            return {
                'columns': ['Metric', 'Value', 'Period', 'Employee', 'Supplier', 'Category'],
                'rows': [['No data available', '', '', '', '', '']]
            }
    
    def refresh_dashboard(self):
        """Refresh dashboard data based on current filters - optimized for current tab only"""
        try:
            # Get current tab
            current_tab_index = self.subtabs_notebook.index(self.subtabs_notebook.select())
            current_tab_name = self.get_tab_name_from_index(current_tab_index)
            
            # Clear cache when filters change (force refresh)
            if hasattr(self, '_tab_cache'):
                self._tab_cache.clear()
            
            # Only refresh the current tab for immediate feedback
            if current_tab_name:
                self.refresh_current_tab_only(current_tab_name)
                
            # Schedule background refresh for other initialized tabs (optional)
            self.schedule_background_refresh(current_tab_name)
                
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
    
    def schedule_background_refresh(self, exclude_tab):
        """Schedule background refresh for other initialized tabs"""
        try:
            # Refresh other tabs in background with a slight delay
            filters = self.get_current_filters()
            
            for tab_name in self.initialized_tabs:
                if tab_name != exclude_tab and tab_name in self.subtab_uis:
                    # Schedule refresh after a short delay to avoid blocking UI
                    delay = 500  # 500ms delay
                    self.parent.after(delay, lambda tn=tab_name: self._background_refresh_tab(tn, filters))
                    
        except Exception as e:
            logger.error(f"Error scheduling background refresh: {e}")
    
    def _background_refresh_tab(self, tab_name, filters):
        """Background refresh for a specific tab"""
        try:
            if tab_name in self.subtab_uis:
                # Use fast refresh if available
                if hasattr(self.subtab_uis[tab_name], 'refresh_data_fast'):
                    self.subtab_uis[tab_name].refresh_data_fast(filters)
                elif hasattr(self.subtab_uis[tab_name], 'refresh_data'):
                    self.subtab_uis[tab_name].refresh_data(filters)
                    
        except Exception as e:
            logger.error(f"Error in background refresh for {tab_name}: {e}")
    
    def on_tab_changed(self, event):
        """Handle tab change events with lazy loading and optimized refresh"""
        try:
            # Get the currently selected tab index
            current_tab_index = self.subtabs_notebook.index(self.subtabs_notebook.select())
            tab_name = self.get_tab_name_from_index(current_tab_index)
            
            if tab_name:
                # Initialize the tab if it hasn't been initialized yet
                self.initialize_tab(tab_name)
                
                # Only refresh the current tab, not all tabs
                self.refresh_current_tab_only(tab_name)
        except Exception as e:
            logger.error(f"Error in tab change: {e}")
    
    def refresh_current_tab_only(self, tab_name):
        """Refresh only the currently active tab for faster switching"""
        try:
            # Enhanced caching with filter-based cache keys
            current_time = time.time()
            filters = self.get_current_filters()
            cache_key = f"{tab_name}_{hash(str(filters))}"
            
            # Initialize cache if not exists
            if not hasattr(self, '_tab_cache'):
                self._tab_cache = {}
            
            # Check if we have fresh cached data (30 seconds)
            if cache_key in self._tab_cache:
                cached_time, cached_data = self._tab_cache[cache_key]
                if current_time - cached_time < 30:  # 30-second cache
                    logger.debug(f"Using cached data for {tab_name} tab")
                    return
            
            # If no cache or cache expired, refresh the current tab
            if tab_name in self.subtab_uis:
                # Use fast refresh if available, otherwise use regular refresh
                if hasattr(self.subtab_uis[tab_name], 'refresh_data_fast'):
                    self.subtab_uis[tab_name].refresh_data_fast(filters)
                elif hasattr(self.subtab_uis[tab_name], 'refresh_data'):
                    self.subtab_uis[tab_name].refresh_data(filters)
                
                # Cache the refresh
                self._tab_cache[cache_key] = (current_time, filters)
                
                # Clean old cache entries (keep only recent ones)
                self._cleanup_cache()
            
        except Exception as e:
            logger.error(f"Error refreshing current tab {tab_name}: {e}")
    
    def _cleanup_cache(self):
        """Clean up old cache entries to prevent memory bloat"""
        try:
            if not hasattr(self, '_tab_cache'):
                return
                
            current_time = time.time()
            # Remove entries older than 5 minutes
            max_age = 300  # 5 minutes
            
            keys_to_remove = []
            for key, (cached_time, _) in self._tab_cache.items():
                if current_time - cached_time > max_age:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._tab_cache[key]
                
            if keys_to_remove:
                logger.debug(f"Cleaned up {len(keys_to_remove)} old cache entries")
                
        except Exception as e:
            logger.error(f"Error cleaning cache: {e}")
    
    
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
            
            # Export each subtab's chart (only if initialized)
            if 'overview' in self.subtab_uis and hasattr(self.subtab_uis['overview'], 'chart'):
                self.subtab_uis['overview'].chart.export_as_image(dir_path, "overview_chart", filters)
            if 'analytics' in self.subtab_uis and hasattr(self.subtab_uis['analytics'], 'chart'):
                self.subtab_uis['analytics'].chart.export_as_image(dir_path, "analytics_chart", filters)
            if 'performance' in self.subtab_uis and hasattr(self.subtab_uis['performance'], 'chart'):
                self.subtab_uis['performance'].chart.export_as_image(dir_path, "performance_chart", filters)
            if 'simulation' in self.subtab_uis and hasattr(self.subtab_uis['simulation'], 'chart'):
                self.subtab_uis['simulation'].chart.export_as_image(dir_path, "simulation_chart", filters)
            
            messagebox.showinfo("Export Charts", "Charts exported successfully as images.")
        
        except Exception as e:
            messagebox.showerror("Export Charts", f"Error exporting charts: {e}")
    
    def initialize_tab(self, tab_name):
        """Initialize a specific tab only when needed (lazy loading) with ultra-fast loading"""
        if tab_name in self.initialized_tabs:
            return  # Already initialized
        
        try:
            # Show loading indicator immediately
            self.show_tab_loading(tab_name)
            
            # Schedule the actual initialization to happen after the UI update
            self.parent.after(10, lambda: self._do_tab_initialization(tab_name))
            
        except Exception as e:
            logger.error(f"Error initializing {tab_name} tab: {e}")
    
    def show_tab_loading(self, tab_name):
        """Show a loading indicator in the tab for immediate feedback"""
        try:
            # Get the tab frame
            tab_frame = getattr(self, f"{tab_name}_tab")
            
            # Clear any existing content
            for widget in tab_frame.winfo_children():
                widget.destroy()
            
            # Add loading content
            loading_frame = ttk.Frame(tab_frame)
            loading_frame.pack(fill='both', expand=True)
            
            # Center the loading content
            center_frame = ttk.Frame(loading_frame)
            center_frame.place(relx=0.5, rely=0.5, anchor='center')
            
            ttk.Label(center_frame, text="🔄 Loading...", font=('Helvetica', 16)).pack(pady=10)
            ttk.Label(center_frame, text=f"Initializing {tab_name.title()} Tab", font=('Helvetica', 12)).pack()
            
            # Add a progress bar for visual feedback
            progress = ttk.Progressbar(center_frame, mode='indeterminate', length=200)
            progress.pack(pady=10)
            progress.start()
            
            # Store reference to stop progress later
            setattr(self, f"_{tab_name}_progress", progress)
            
        except Exception as e:
            logger.error(f"Error showing loading for {tab_name}: {e}")
    
    def _do_tab_initialization(self, tab_name):
        """Actually initialize the tab content"""
        try:
            # Stop and remove loading indicator
            if hasattr(self, f"_{tab_name}_progress"):
                progress = getattr(self, f"_{tab_name}_progress")
                progress.stop()
                delattr(self, f"_{tab_name}_progress")
            
            # Clear loading content
            tab_frame = getattr(self, f"{tab_name}_tab")
            for widget in tab_frame.winfo_children():
                widget.destroy()
            
            # Initialize the actual tab UI
            if tab_name == "overview":
                self.subtab_uis['overview'] = OverviewUI(self.overview_tab, self.callbacks)
            elif tab_name == "analytics":
                self.subtab_uis['analytics'] = AnalyticsUI(self.analytics_tab, self.callbacks)
            elif tab_name == "performance":
                self.subtab_uis['performance'] = PerformanceUI(self.performance_tab, self.callbacks)
            elif tab_name == "simulation":
                self.subtab_uis['simulation'] = SimulationUI(self.simulation_tab, self.callbacks)
            
            self.initialized_tabs.add(tab_name)
            
            # Refresh the tab with current filters
            filters = self.get_current_filters()
            if tab_name in self.subtab_uis:
                if hasattr(self.subtab_uis[tab_name], 'refresh_data_fast'):
                    self.subtab_uis[tab_name].refresh_data_fast(filters)
                elif hasattr(self.subtab_uis[tab_name], 'refresh_data'):
                    self.subtab_uis[tab_name].refresh_data(filters)
            
        except Exception as e:
            logger.error(f"Error in actual tab initialization for {tab_name}: {e}")
            # Show error message in the tab
            self.show_tab_error(tab_name, str(e))
    
    def show_tab_error(self, tab_name, error_msg):
        """Show error message in tab"""
        try:
            tab_frame = getattr(self, f"{tab_name}_tab")
            for widget in tab_frame.winfo_children():
                widget.destroy()
                
            error_frame = ttk.Frame(tab_frame)
            error_frame.place(relx=0.5, rely=0.5, anchor='center')
            
            ttk.Label(error_frame, text="❌ Error Loading Tab", font=('Helvetica', 16), foreground='red').pack(pady=10)
            ttk.Label(error_frame, text=error_msg, font=('Helvetica', 10)).pack()
            ttk.Button(error_frame, text="Retry", command=lambda: self.retry_tab_initialization(tab_name)).pack(pady=10)
        except Exception as e:
            logger.error(f"Error showing error for {tab_name}: {e}")
    
    def retry_tab_initialization(self, tab_name):
        """Retry initializing a tab"""
        if tab_name in self.initialized_tabs:
            self.initialized_tabs.remove(tab_name)
        self.initialize_tab(tab_name)
    
    def get_tab_name_from_index(self, tab_index):
        """Get tab name from notebook tab index"""
        tab_names = ["overview", "analytics", "performance", "simulation"]
        if 0 <= tab_index < len(tab_names):
            return tab_names[tab_index]
        return None
    
    def prewarm_tabs(self):
        """Pre-warm other tabs in background for faster switching"""
        try:
            # Get tabs that aren't initialized yet
            tabs_to_prewarm = ["analytics", "performance", "simulation"]
            
            for tab_name in tabs_to_prewarm:
                if tab_name not in self.initialized_tabs:
                    # Schedule initialization with staggered delays
                    delay = 1000 * (tabs_to_prewarm.index(tab_name) + 1)  # 1s, 2s, 3s delays
                    self.parent.after(delay, lambda tn=tab_name: self.initialize_tab(tn))
                    
        except Exception as e:
            logger.error(f"Error pre-warming tabs: {e}")
