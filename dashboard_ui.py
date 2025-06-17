"""
Main Dashboard UI Module - Orchestrator
Main dashboard controller with global filters and subtab management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
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
        self.load_filter_data()
        
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
            # Load employees
            if 'get_employees_callback' in self.callbacks and self.callbacks['get_employees_callback']:
                employees = self.callbacks['get_employees_callback']()
                employee_names = ["All Employees"] + [emp['name'] for emp in employees if emp['name']]
                self.employee_combobox['values'] = employee_names
                self.employee_combobox.set("All Employees")
            
            # Load suppliers
            if 'get_suppliers_callback' in self.callbacks and self.callbacks['get_suppliers_callback']:
                suppliers = self.callbacks['get_suppliers_callback']()
                supplier_names = ["All Suppliers"] + [sup['name'] for sup in suppliers if sup['name']]
                self.supplier_combobox['values'] = supplier_names
                self.supplier_combobox.set("All Suppliers")
            
            # Load categories (placeholder for now)
            categories = ["All Categories", "Bread", "Buns", "Pasta", "Doughnuts", "Noodles", "Clothing", "Beverages"]
            self.category_combobox['values'] = categories
            self.category_combobox.set("All Categories")
            
        except Exception as e:
            print(f"Error loading filter data: {e}")
    
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
        """Get current filter values"""
        return {
            'start_date': self.start_date_var.get(),
            'end_date': self.end_date_var.get(),
            'employee': self.employee_filter_var.get(),
            'supplier': self.supplier_filter_var.get(),
            'category': self.category_filter_var.get()
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
        print(f"Switched to {tab_text} tab")
        
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
        
        ttk.Button(export_frame, text="📄 Export to CSV", width=20).pack(pady=5)
        ttk.Button(export_frame, text="📊 Export to Excel", width=20).pack(pady=5)
        ttk.Button(export_frame, text="📑 Generate PDF Report", width=20).pack(pady=5)
        ttk.Button(export_frame, text="📈 Export Charts", width=20).pack(pady=5)
        
        ttk.Button(export_window, text="Close", command=export_window.destroy).pack(pady=10)
    
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
