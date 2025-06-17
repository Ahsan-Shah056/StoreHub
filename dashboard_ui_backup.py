"""
Dashboard UI Components for Storecore POS & Inventory System
Provides comprehensive business intelligence interface with advanced filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
from PIL import Image, ImageTk
from tkcalendar import DateEntry

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
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Current time display
        self.time_label = ttk.Label(
            header_frame, 
            text=f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
            font=("Helvetica", 10)
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
        ttk.Label(date_row, text="Date Range:", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
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
        ttk.Label(entity_row, text="Employee:", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.employee_combobox = ttk.Combobox(
            entity_row, 
            textvariable=self.employee_filter_var, 
            width=15, 
            state="readonly"
        )
        self.employee_combobox.pack(side=tk.LEFT, padx=(0, 15))
        
        # Supplier filter
        ttk.Label(entity_row, text="Supplier:", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.supplier_combobox = ttk.Combobox(
            entity_row, 
            textvariable=self.supplier_filter_var, 
            width=15, 
            state="readonly"
        )
        self.supplier_combobox.pack(side=tk.LEFT, padx=(0, 15))
        
        # Category filter
        ttk.Label(entity_row, text="Category:", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
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
        ttk.Label(export_window, text="Export Options", font=("Helvetica", 14, "bold")).pack(pady=10)
        
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
        
        ttk.Label(settings_window, text="Dashboard Settings", font=("Helvetica", 14, "bold")).pack(pady=10)
        
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


# Placeholder classes for the 4 subtabs (to be implemented in upcoming phases)
class OverviewUI:
    """Overview subtab - Enhanced Key metrics and quick insights with live data"""
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.current_filters = {}
        
        # Import dashboard functions
        try:
            from dashboard import (
                get_sales_summary, get_inventory_value, calculate_profit_margins,
                get_top_products, get_low_stock_analytics, get_recent_activities,
                get_supplier_performance
            )
            self.dashboard_funcs = {
                'get_sales_summary': get_sales_summary,
                'get_inventory_value': get_inventory_value,
                'calculate_profit_margins': calculate_profit_margins,
                'get_top_products': get_top_products,
                'get_low_stock_analytics': get_low_stock_analytics,
                'get_recent_activities': get_recent_activities,
                'get_supplier_performance': get_supplier_performance
            }
        except ImportError as e:
            print(f"Error importing dashboard functions: {e}")
            self.dashboard_funcs = {}
        
        self.create_overview_ui()
        
        # Load initial data
        default_filters = {
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'employee': 'All Employees',
            'supplier': 'All Suppliers',
            'category': 'All Categories'
        }
        self.refresh_data(default_filters)
    
    def create_overview_ui(self):
        """Create the comprehensive overview interface"""
        
        # Main scrollable frame
        canvas = tk.Canvas(self.parent)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Overview header
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        ttk.Label(
            header_frame, 
            text="📈 Business Overview Dashboard", 
            font=("Helvetica", 18, "bold")
        ).pack(side=tk.LEFT)
        
        self.last_updated_label = ttk.Label(
            header_frame, 
            text="Last Updated: --", 
            font=("Helvetica", 9)
        )
        self.last_updated_label.pack(side=tk.RIGHT)
        
        # Key metrics cards section
        self.create_metrics_cards()
        
        # Quick stats panel
        self.create_quick_stats_panel()
        
        # Quick actions buttons
        self.create_quick_actions()
        
        # Recent activity feed
        self.create_recent_activity_feed()
        
        # Top products and alerts
        self.create_insights_section()
    
    def create_metrics_cards(self):
        """Create 6 main metrics cards with enhanced styling"""
        
        metrics_label_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 Key Performance Metrics", padding="10")
        metrics_label_frame.pack(fill='x', padx=10, pady=5)
        
        # Cards container with grid layout
        cards_frame = ttk.Frame(metrics_label_frame)
        cards_frame.pack(fill='x')
        
        # Configure grid weights for responsive design
        for i in range(3):
            cards_frame.columnconfigure(i, weight=1)
        
        # Card styling configuration
        card_style = {
            'relief': 'raised',
            'borderwidth': 2,
            'padding': '15'
        }
        
        # Row 1: Primary business metrics
        # Card 1: Total Sales
        self.sales_card = ttk.LabelFrame(cards_frame, text="💰 Total Sales", **card_style)
        self.sales_card.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        self.sales_value_label = ttk.Label(self.sales_card, text="$0.00", font=("Helvetica", 16, "bold"))
        self.sales_value_label.pack()
        self.sales_change_label = ttk.Label(self.sales_card, text="-- % change", font=("Helvetica", 9))
        self.sales_change_label.pack()
        
        # Card 2: Total Orders
        self.orders_card = ttk.LabelFrame(cards_frame, text="📦 Total Orders", **card_style)
        self.orders_card.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        self.orders_value_label = ttk.Label(self.orders_card, text="0", font=("Helvetica", 16, "bold"))
        self.orders_value_label.pack()
        self.orders_change_label = ttk.Label(self.orders_card, text="-- % change", font=("Helvetica", 9))
        self.orders_change_label.pack()
        
        # Card 3: Total Profit
        self.profit_card = ttk.LabelFrame(cards_frame, text="💎 Total Profit", **card_style)
        self.profit_card.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        
        self.profit_value_label = ttk.Label(self.profit_card, text="$0.00", font=("Helvetica", 16, "bold"))
        self.profit_value_label.pack()
        self.profit_margin_label = ttk.Label(self.profit_card, text="-- % margin", font=("Helvetica", 9))
        self.profit_margin_label.pack()
        
        # Row 2: Operational metrics
        # Card 4: Inventory Value
        self.inventory_card = ttk.LabelFrame(cards_frame, text="📚 Inventory Value", **card_style)
        self.inventory_card.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        self.inventory_value_label = ttk.Label(self.inventory_card, text="$0.00", font=("Helvetica", 16, "bold"))
        self.inventory_value_label.pack()
        self.inventory_count_label = ttk.Label(self.inventory_card, text="-- products", font=("Helvetica", 9))
        self.inventory_count_label.pack()
        
        # Card 5: Top Product
        self.top_product_card = ttk.LabelFrame(cards_frame, text="🏆 Top Product", **card_style)
        self.top_product_card.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        self.top_product_name_label = ttk.Label(self.top_product_card, text="--", font=("Helvetica", 12, "bold"))
        self.top_product_name_label.pack()
        self.top_product_sales_label = ttk.Label(self.top_product_card, text="-- units sold", font=("Helvetica", 9))
        self.top_product_sales_label.pack()
        
        # Card 6: Average Profit Margin
        self.avg_margin_card = ttk.LabelFrame(cards_frame, text="📈 Avg Profit Margin", **card_style)
        self.avg_margin_card.grid(row=1, column=2, padx=5, pady=5, sticky='ew')
        
        self.avg_margin_value_label = ttk.Label(self.avg_margin_card, text="0.00%", font=("Helvetica", 16, "bold"))
        self.avg_margin_value_label.pack()
        self.margin_trend_label = ttk.Label(self.avg_margin_card, text="-- trend", font=("Helvetica", 9))
        self.margin_trend_label.pack()
    
    def create_quick_stats_panel(self):
        """Create enhanced quick stats panel"""
        
        stats_label_frame = ttk.LabelFrame(self.scrollable_frame, text="⚡ Quick Statistics", padding="10")
        stats_label_frame.pack(fill='x', padx=10, pady=5)
        
        # Two-column layout for stats
        stats_frame = ttk.Frame(stats_label_frame)
        stats_frame.pack(fill='x')
        
        # Column 1
        col1_frame = ttk.Frame(stats_frame)
        col1_frame.pack(side=tk.LEFT, fill='both', expand=True)
        
        self.avg_order_value_label = ttk.Label(col1_frame, text="Average Order Value: $--", font=("Helvetica", 10))
        self.avg_order_value_label.pack(anchor='w', pady=2)
        
        self.items_sold_today_label = ttk.Label(col1_frame, text="Items Sold Today: --", font=("Helvetica", 10))
        self.items_sold_today_label.pack(anchor='w', pady=2)
        
        self.new_customers_label = ttk.Label(col1_frame, text="New Customers: --", font=("Helvetica", 10))
        self.new_customers_label.pack(anchor='w', pady=2)
        
        # Column 2
        col2_frame = ttk.Frame(stats_frame)
        col2_frame.pack(side=tk.LEFT, fill='both', expand=True)
        
        self.low_stock_count_label = ttk.Label(col2_frame, text="Low Stock Items: --", font=("Helvetica", 10))
        self.low_stock_count_label.pack(anchor='w', pady=2)
        
        self.supplier_performance_label = ttk.Label(col2_frame, text="Supplier Performance: --%", font=("Helvetica", 10))
        self.supplier_performance_label.pack(anchor='w', pady=2)
        
        self.cost_savings_label = ttk.Label(col2_frame, text="Cost Savings Potential: $--", font=("Helvetica", 10))
        self.cost_savings_label.pack(anchor='w', pady=2)
    
    def create_quick_actions(self):
        """Create quick action buttons"""
        
        actions_label_frame = ttk.LabelFrame(self.scrollable_frame, text="🚀 Quick Actions", padding="10")
        actions_label_frame.pack(fill='x', padx=10, pady=5)
        
        actions_frame = ttk.Frame(actions_label_frame)
        actions_frame.pack(fill='x')
        
        # Action buttons
        ttk.Button(actions_frame, text="🛒 New Sale", width=12, command=self.open_new_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="📦 Add Product", width=12, command=self.open_add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="📊 View Reports", width=12, command=self.open_reports).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="⚠️ Low Stock Alert", width=12, command=self.show_low_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="🤝 Supplier Analysis", width=15, command=self.show_supplier_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="💰 Cost Review", width=12, command=self.show_cost_review).pack(side=tk.LEFT, padx=5)
    
    def create_recent_activity_feed(self):
        """Create recent activity feed with profit information"""
        
        activity_label_frame = ttk.LabelFrame(self.scrollable_frame, text="📋 Recent Activity Feed", padding="10")
        activity_label_frame.pack(fill='x', padx=10, pady=5)
        
        # Activity list with scrollbar
        activity_frame = ttk.Frame(activity_label_frame)
        activity_frame.pack(fill='both', expand=True)
        
        # Treeview for activities
        columns = ('Time', 'Type', 'Amount', 'Employee', 'Profit', 'Margin')
        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show='headings', height=6)
        
        # Configure column headings
        self.activity_tree.heading('Time', text='Time')
        self.activity_tree.heading('Type', text='Type')
        self.activity_tree.heading('Amount', text='Amount')
        self.activity_tree.heading('Employee', text='Employee')
        self.activity_tree.heading('Profit', text='Profit')
        self.activity_tree.heading('Margin', text='Margin %')
        
        # Configure column widths
        self.activity_tree.column('Time', width=120)
        self.activity_tree.column('Type', width=80)
        self.activity_tree.column('Amount', width=80)
        self.activity_tree.column('Employee', width=100)
        self.activity_tree.column('Profit', width=80)
        self.activity_tree.column('Margin', width=70)
        
        # Scrollbar for activity tree
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient="vertical", command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=activity_scrollbar.set)
        
        self.activity_tree.pack(side="left", fill="both", expand=True)
        activity_scrollbar.pack(side="right", fill="y")
    
    def create_insights_section(self):
        """Create insights and alerts section"""
        
        insights_label_frame = ttk.LabelFrame(self.scrollable_frame, text="💡 Business Insights & Alerts", padding="10")
        insights_label_frame.pack(fill='x', padx=10, pady=5)
        
        insights_frame = ttk.Frame(insights_label_frame)
        insights_frame.pack(fill='both', expand=True)
        
        # Top products column
        top_products_frame = ttk.LabelFrame(insights_frame, text="🏆 Top Products", padding="5")
        top_products_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 5))
        
        self.top_products_text = tk.Text(top_products_frame, height=8, width=30)
        self.top_products_text.pack(fill='both', expand=True)
        
        # Alerts column
        alerts_frame = ttk.LabelFrame(insights_frame, text="⚠️ Alerts & Notifications", padding="5")
        alerts_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=(5, 0))
        
        self.alerts_text = tk.Text(alerts_frame, height=8, width=30)
        self.alerts_text.pack(fill='both', expand=True)
    
    def refresh_data(self, filters):
        """Refresh all overview data based on current filters"""
        try:
            self.current_filters = filters
            
            # Update last updated timestamp
            self.last_updated_label.config(text=f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
            
            # Refresh all data sections
            self.update_metrics_cards(filters)
            self.update_quick_stats(filters)
            self.update_recent_activities(filters)
            self.update_insights_section(filters)
            
        except Exception as e:
            print(f"Error refreshing overview data: {e}")
    
    def update_metrics_cards(self, filters):
        """Update the 6 main metrics cards"""
        try:
            if not self.dashboard_funcs:
                return
            
            # Get sales summary
            sales_summary = self.dashboard_funcs['get_sales_summary'](
                filters['start_date'], filters['end_date']
            )
            
            # Update sales card
            self.sales_value_label.config(text=f"${sales_summary['total_sales']:,.2f}")
            change_color = "green" if sales_summary['sales_change'] >= 0 else "red"
            self.sales_change_label.config(
                text=f"{sales_summary['sales_change']:+.1f}% vs previous period",
                foreground=change_color
            )
            
            # Update orders card
            self.orders_value_label.config(text=f"{sales_summary['total_orders']:,}")
            change_color = "green" if sales_summary['orders_change'] >= 0 else "red"
            self.orders_change_label.config(
                text=f"{sales_summary['orders_change']:+.1f}% vs previous period",
                foreground=change_color
            )
            
            # Update profit card
            self.profit_value_label.config(text=f"${sales_summary['total_profit']:,.2f}")
            self.profit_margin_label.config(text=f"{sales_summary['profit_margin']:.1f}% margin")
            
            # Get inventory value
            inventory_data = self.dashboard_funcs['get_inventory_value']()
            
            # Update inventory card
            self.inventory_value_label.config(text=f"${inventory_data['total_retail_value']:,.2f}")
            self.inventory_count_label.config(text=f"{inventory_data['total_products']:,} products")
            
            # Get top product
            top_products = self.dashboard_funcs['get_top_products'](
                filters['start_date'], filters['end_date'], 1
            )
            
            # Update top product card
            if top_products:
                top_product = top_products[0]
                self.top_product_name_label.config(text=top_product['name'][:20] + "..." if len(top_product['name']) > 20 else top_product['name'])
                self.top_product_sales_label.config(text=f"{top_product['units_sold']} units sold")
            else:
                self.top_product_name_label.config(text="No sales data")
                self.top_product_sales_label.config(text="-- units sold")
            
            # Calculate average profit margin
            profit_margins = self.dashboard_funcs['calculate_profit_margins']()
            if profit_margins:
                avg_margin = sum(p['profit_margin'] for p in profit_margins) / len(profit_margins)
                self.avg_margin_value_label.config(text=f"{avg_margin:.1f}%")
                
                # Determine trend (simplified)
                if avg_margin > 25:
                    trend = "Excellent"
                    trend_color = "green"
                elif avg_margin > 15:
                    trend = "Good"
                    trend_color = "blue"
                else:
                    trend = "Needs attention"
                    trend_color = "orange"
                
                self.margin_trend_label.config(text=trend, foreground=trend_color)
            else:
                self.avg_margin_value_label.config(text="0.0%")
                self.margin_trend_label.config(text="No data")
            
        except Exception as e:
            print(f"Error updating metrics cards: {e}")
    
    def update_quick_stats(self, filters):
        """Update quick statistics panel"""
        try:
            if not self.dashboard_funcs:
                return
            
            # Get sales summary for additional stats
            sales_summary = self.dashboard_funcs['get_sales_summary'](
                filters['start_date'], filters['end_date']
            )
            
            # Update average order value
            self.avg_order_value_label.config(text=f"Average Order Value: ${sales_summary['avg_order_value']:.2f}")
            
            # Update items sold today
            today = datetime.now().strftime('%Y-%m-%d')
            today_summary = self.dashboard_funcs['get_sales_summary'](today, today)
            self.items_sold_today_label.config(text=f"Items Sold Today: {today_summary['total_items_sold']:,}")
            
            # Mock new customers (would need actual customer tracking)
            self.new_customers_label.config(text="New Customers: --")
            
            # Get low stock count
            low_stock_items = self.dashboard_funcs['get_low_stock_analytics']()
            low_stock_value = sum(item['reorder_cost'] for item in low_stock_items) if low_stock_items else 0
            self.low_stock_count_label.config(text=f"Low Stock Items: {len(low_stock_items)} (${low_stock_value:,.0f})")
            
            # Get supplier performance
            supplier_performance = self.dashboard_funcs['get_supplier_performance']()
            if supplier_performance:
                avg_delivery_rate = sum(s['delivery_success_rate'] for s in supplier_performance) / len(supplier_performance)
                self.supplier_performance_label.config(text=f"Supplier Performance: {avg_delivery_rate:.1f}%")
            else:
                self.supplier_performance_label.config(text="Supplier Performance: --%")
            
            # Calculate cost savings potential (simplified)
            inventory_data = self.dashboard_funcs['get_inventory_value']()
            potential_savings = float(inventory_data['potential_profit']) * 0.1  # 10% optimization potential
            self.cost_savings_label.config(text=f"Cost Savings Potential: ${potential_savings:,.0f}")
            
        except Exception as e:
            print(f"Error updating quick stats: {e}")
    
    def update_recent_activities(self, filters):
        """Update recent activities feed"""
        try:
            if not self.dashboard_funcs:
                return
            
            # Clear existing items
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            # Get recent activities
            activities = self.dashboard_funcs['get_recent_activities'](10)
            
            for activity in activities:
                # Format the data
                time_str = activity['sale_datetime'].strftime('%m/%d %H:%M') if hasattr(activity['sale_datetime'], 'strftime') else str(activity['sale_datetime'])[:16]
                amount_str = f"${activity['sale_total']:.2f}"
                profit_str = f"${activity['transaction_profit']:.2f}" if activity['transaction_profit'] else "$0.00"
                margin_str = f"{activity['profit_margin']:.1f}%" if activity['profit_margin'] else "0.0%"
                
                self.activity_tree.insert('', 'end', values=(
                    time_str,
                    'Sale',
                    amount_str,
                    activity['employee_name'],
                    profit_str,
                    margin_str
                ))
            
        except Exception as e:
            print(f"Error updating recent activities: {e}")
    
    def update_insights_section(self, filters):
        """Update insights and alerts section"""
        try:
            if not self.dashboard_funcs:
                return
            
            # Update top products
            self.top_products_text.delete(1.0, tk.END)
            top_products = self.dashboard_funcs['get_top_products'](
                filters['start_date'], filters['end_date'], 5
            )
            
            if top_products:
                self.top_products_text.insert(tk.END, "🏆 TOP PERFORMERS:\n\n")
                for i, product in enumerate(top_products, 1):
                    self.top_products_text.insert(tk.END, 
                        f"{i}. {product['name']}\n"
                        f"   Units: {product['units_sold']}\n"
                        f"   Revenue: ${product['revenue']:,.2f}\n"
                        f"   Profit: ${product['profit']:,.2f}\n\n"
                    )
            else:
                self.top_products_text.insert(tk.END, "No sales data available for selected period.")
            
            # Update alerts
            self.alerts_text.delete(1.0, tk.END)
            alerts_count = 0
            
            # Low stock alerts
            low_stock_items = self.dashboard_funcs['get_low_stock_analytics']()
            if low_stock_items:
                self.alerts_text.insert(tk.END, f"⚠️ LOW STOCK ALERTS:\n")
                for item in low_stock_items[:3]:  # Show top 3
                    self.alerts_text.insert(tk.END, 
                        f"• {item['name']}: {item['stock']} units\n"
                    )
                if len(low_stock_items) > 3:
                    self.alerts_text.insert(tk.END, f"• ... and {len(low_stock_items) - 3} more\n")
                self.alerts_text.insert(tk.END, "\n")
                alerts_count += len(low_stock_items)
            
            # Performance alerts (simplified)
            profit_margins = self.dashboard_funcs['calculate_profit_margins']()
            low_margin_products = [p for p in profit_margins if p['profit_margin'] < 10]
            if low_margin_products:
                self.alerts_text.insert(tk.END, f"📉 LOW MARGIN PRODUCTS:\n")
                for product in low_margin_products[:3]:
                    self.alerts_text.insert(tk.END, 
                        f"• {product['name']}: {product['profit_margin']:.1f}%\n"
                    )
                if len(low_margin_products) > 3:
                    self.alerts_text.insert(tk.END, f"• ... and {len(low_margin_products) - 3} more\n")
                self.alerts_text.insert(tk.END, "\n")
                alerts_count += len(low_margin_products)
            
            if alerts_count == 0:
                self.alerts_text.insert(tk.END, "✅ All systems operating normally!\n\nNo critical alerts at this time.")
            
        except Exception as e:
            print(f"Error updating insights section: {e}")
    
    # Quick action methods
    def open_new_sale(self):
        """Open new sale interface"""
        messagebox.showinfo("Quick Action", "New Sale - This would open the Sales tab")
    
    def open_add_product(self):
        """Open add product interface"""
        messagebox.showinfo("Quick Action", "Add Product - This would open the Inventory tab")
    
    def open_reports(self):
        """Open reports interface"""
        messagebox.showinfo("Quick Action", "Reports - This would open the Reports tab")
    
    def show_low_stock(self):
        """Show low stock alert details"""
        if not self.dashboard_funcs:
            messagebox.showinfo("Low Stock", "Dashboard functions not available")
            return
        
        try:
            low_stock_items = self.dashboard_funcs['get_low_stock_analytics']()
            if low_stock_items:
                alert_window = tk.Toplevel(self.parent)
                alert_window.title("Low Stock Alert")
                alert_window.geometry("600x400")
                
                ttk.Label(alert_window, text="⚠️ Low Stock Items", font=("Helvetica", 14, "bold")).pack(pady=10)
                
                # Create treeview for low stock items
                columns = ('Product', 'Current Stock', 'Threshold', 'Reorder Cost')
                tree = ttk.Treeview(alert_window, columns=columns, show='headings')
                
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=120)
                
                for item in low_stock_items:
                    tree.insert('', 'end', values=(
                        item['name'],
                        item['stock'],
                        item['low_stock_threshold'],
                        f"${item['reorder_cost']:.2f}"
                    ))
                
                tree.pack(fill='both', expand=True, padx=10, pady=5)
                ttk.Button(alert_window, text="Close", command=alert_window.destroy).pack(pady=10)
            else:
                messagebox.showinfo("Low Stock", "No items are currently below their stock thresholds!")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading low stock data: {e}")
    
    def show_supplier_analysis(self):
        """Show supplier performance analysis"""
        messagebox.showinfo("Quick Action", "Supplier Analysis - Advanced supplier metrics would be displayed here")
    
    def show_cost_review(self):
        """Show cost review analysis"""
        messagebox.showinfo("Quick Action", "Cost Review - Cost optimization opportunities would be shown here")


class AnalyticsUI:
    """Analytics subtab - Advanced charts and data visualization with business intelligence"""
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.current_filters = {}
        self.chart_view_mode = "Daily"  # Daily, Weekly, Monthly
        
        # Import required libraries for charts
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
            import numpy as np
            
            self.matplotlib_available = True
            self.plt = plt
            self.FigureCanvasTkAgg = FigureCanvasTkAgg
            self.Figure = Figure
            self.np = np
            
            # Set matplotlib style
            plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
            
        except ImportError:
            self.matplotlib_available = False
            print("Matplotlib not available - charts will show placeholders")
        
        # Import dashboard functions
        try:
            from dashboard import (
                get_daily_sales_data, get_top_products, get_category_analytics,
                get_sales_summary, calculate_profit_margins, get_supplier_performance,
                get_inventory_value
            )
            self.dashboard_funcs = {
                'get_daily_sales_data': get_daily_sales_data,
                'get_top_products': get_top_products,
                'get_category_analytics': get_category_analytics,
                'get_sales_summary': get_sales_summary,
                'calculate_profit_margins': calculate_profit_margins,
                'get_supplier_performance': get_supplier_performance,
                'get_inventory_value': get_inventory_value
            }
        except ImportError as e:
            print(f"Error importing dashboard functions: {e}")
            self.dashboard_funcs = {}
        
        self.create_analytics_ui()
        
        # Load initial data
        default_filters = {
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'employee': 'All Employees',
            'supplier': 'All Suppliers',
            'category': 'All Categories'
        }
        self.refresh_data(default_filters)
    
    def create_analytics_ui(self):
        """Create comprehensive analytics interface with charts and visualizations"""
        
        # Main scrollable frame
        canvas = tk.Canvas(self.parent)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Analytics header with view controls
        self.create_analytics_header()
        
        # Charts section
        self.create_charts_section()
        
        # Advanced analytics tables
        self.create_advanced_analytics_section()
        
        # Export options
        self.create_export_section()
    
    def create_analytics_header(self):
        """Create analytics header with view controls"""
        
        header_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 Advanced Business Analytics", padding="10")
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # View mode controls
        view_frame = ttk.Frame(header_frame)
        view_frame.pack(fill='x')
        
        ttk.Label(view_frame, text="Chart View Mode:", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        # View mode buttons
        self.daily_btn = ttk.Button(view_frame, text="📅 Daily View", command=lambda: self.set_view_mode("Daily"))
        self.daily_btn.pack(side=tk.LEFT, padx=2)
        
        self.weekly_btn = ttk.Button(view_frame, text="📊 Weekly View", command=lambda: self.set_view_mode("Weekly"))
        self.weekly_btn.pack(side=tk.LEFT, padx=2)
        
        self.monthly_btn = ttk.Button(view_frame, text="📈 Monthly View", command=lambda: self.set_view_mode("Monthly"))
        self.monthly_btn.pack(side=tk.LEFT, padx=2)
        
        # Refresh button
        ttk.Button(view_frame, text="🔄 Refresh Charts", command=self.refresh_charts).pack(side=tk.RIGHT, padx=10)
        
        # Current view indicator
        self.view_indicator = ttk.Label(header_frame, text=f"Current View: {self.chart_view_mode}", 
                                       font=("Helvetica", 9), foreground="blue")
        self.view_indicator.pack(anchor='w', pady=(5, 0))
    
    def create_charts_section(self):
        """Create the main charts section"""
        
        charts_frame = ttk.LabelFrame(self.scrollable_frame, text="📈 Sales & Profitability Charts", padding="10")
        charts_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Charts container with 2x2 grid
        charts_container = ttk.Frame(charts_frame)
        charts_container.pack(fill='both', expand=True)
        
        # Configure grid weights
        charts_container.columnconfigure(0, weight=1)
        charts_container.columnconfigure(1, weight=1)
        charts_container.rowconfigure(0, weight=1)
        charts_container.rowconfigure(1, weight=1)
        
        # Chart 1: Sales Trend with Profit Overlay
        self.create_sales_trend_chart(charts_container, 0, 0)
        
        # Chart 2: Category Performance Pie Chart
        self.create_category_chart(charts_container, 0, 1)
        
        # Chart 3: Profit Margin Analysis
        self.create_profit_margin_chart(charts_container, 1, 0)
        
        # Chart 4: Inventory Value Analysis
        self.create_inventory_chart(charts_container, 1, 1)
    
    def create_sales_trend_chart(self, parent, row, col):
        """Create sales trend line chart with profit overlay"""
        
        chart_frame = ttk.LabelFrame(parent, text="💰 Sales Trend with Profit Analysis", padding="5")
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        if self.matplotlib_available:
            # Create matplotlib figure
            self.sales_fig = self.Figure(figsize=(6, 4), dpi=100)
            self.sales_ax1 = self.sales_fig.add_subplot(111)
            
            # Create canvas
            self.sales_canvas = self.FigureCanvasTkAgg(self.sales_fig, chart_frame)
            self.sales_canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # Initial placeholder
            self.sales_ax1.text(0.5, 0.5, 'Sales Trend Chart\nLoading...', 
                               horizontalalignment='center', verticalalignment='center',
                               transform=self.sales_ax1.transAxes, fontsize=12)
            self.sales_ax1.set_title(f"Sales Trend - {self.chart_view_mode} View")
            
        else:
            # Fallback text display
            placeholder = tk.Text(chart_frame, height=8, wrap=tk.WORD)
            placeholder.pack(fill='both', expand=True)
            placeholder.insert(tk.END, "Sales Trend Chart\n\nMatplotlib not available.\nInstall matplotlib for chart visualization:\npip install matplotlib\n\nChart would show:\n- Daily/Weekly/Monthly sales\n- Profit overlay\n- Trend analysis")
            placeholder.config(state='disabled')
    
    def create_category_chart(self, parent, row, col):
        """Create category performance pie chart"""
        
        chart_frame = ttk.LabelFrame(parent, text="🎯 Revenue by Category", padding="5")
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        if self.matplotlib_available:
            # Create matplotlib figure
            self.category_fig = self.Figure(figsize=(6, 4), dpi=100)
            self.category_ax = self.category_fig.add_subplot(111)
            
            # Create canvas
            self.category_canvas = self.FigureCanvasTkAgg(self.category_fig, chart_frame)
            self.category_canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # Initial placeholder
            self.category_ax.text(0.5, 0.5, 'Category Performance\nLoading...', 
                                 horizontalalignment='center', verticalalignment='center',
                                 transform=self.category_ax.transAxes, fontsize=12)
            self.category_ax.set_title("Revenue Distribution by Category")
            
        else:
            # Fallback text display
            placeholder = tk.Text(chart_frame, height=8, wrap=tk.WORD)
            placeholder.pack(fill='both', expand=True)
            placeholder.insert(tk.END, "Category Performance Chart\n\nChart would show:\n- Revenue by category\n- Profit margins\n- Category comparison\n- Performance trends")
            placeholder.config(state='disabled')
    
    def create_profit_margin_chart(self, parent, row, col):
        """Create profit margin analysis chart"""
        
        chart_frame = ttk.LabelFrame(parent, text="📊 Profit Margin Analysis", padding="5")
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        if self.matplotlib_available:
            # Create matplotlib figure
            self.margin_fig = self.Figure(figsize=(6, 4), dpi=100)
            self.margin_ax = self.margin_fig.add_subplot(111)
            
            # Create canvas
            self.margin_canvas = self.FigureCanvasTkAgg(self.margin_fig, chart_frame)
            self.margin_canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # Initial placeholder
            self.margin_ax.text(0.5, 0.5, 'Profit Margin Analysis\nLoading...', 
                               horizontalalignment='center', verticalalignment='center',
                               transform=self.margin_ax.transAxes, fontsize=12)
            self.margin_ax.set_title("Product Profit Margins")
            
        else:
            # Fallback text display
            placeholder = tk.Text(chart_frame, height=8, wrap=tk.WORD)
            placeholder.pack(fill='both', expand=True)
            placeholder.insert(tk.END, "Profit Margin Chart\n\nChart would show:\n- Product margins\n- Cost vs revenue\n- Margin trends\n- Optimization opportunities")
            placeholder.config(state='disabled')
    
    def create_inventory_chart(self, parent, row, col):
        """Create inventory value analysis chart"""
        
        chart_frame = ttk.LabelFrame(parent, text="📚 Inventory Value Analysis", padding="5")
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        if self.matplotlib_available:
            # Create matplotlib figure
            self.inventory_fig = self.Figure(figsize=(6, 4), dpi=100)
            self.inventory_ax = self.inventory_fig.add_subplot(111)
            
            # Create canvas
            self.inventory_canvas = self.FigureCanvasTkAgg(self.inventory_fig, chart_frame)
            self.inventory_canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # Initial placeholder
            self.inventory_ax.text(0.5, 0.5, 'Inventory Analysis\nLoading...', 
                                  horizontalalignment='center', verticalalignment='center',
                                  transform=self.inventory_ax.transAxes, fontsize=12)
            self.inventory_ax.set_title("Inventory Value Distribution")
            
        else:
            # Fallback text display
            placeholder = tk.Text(chart_frame, height=8, wrap=tk.WORD)
            placeholder.pack(fill='both', expand=True)
            placeholder.insert(tk.END, "Inventory Analysis Chart\n\nChart would show:\n- Stock value by category\n- Cost vs retail value\n- Turnover analysis\n- Investment optimization")
            placeholder.config(state='disabled')
    
    def create_advanced_analytics_section(self):
        """Create advanced analytics tables and metrics"""
        
        analytics_frame = ttk.LabelFrame(self.scrollable_frame, text="📋 Advanced Product Analytics", padding="10")
        analytics_frame.pack(fill='x', padx=10, pady=5)
        
        # Analytics notebook for different views
        analytics_notebook = ttk.Notebook(analytics_frame)
        analytics_notebook.pack(fill='both', expand=True)
        
        # Top Products tab
        self.create_top_products_tab(analytics_notebook)
        
        # Category Performance tab
        self.create_category_performance_tab(analytics_notebook)
        
        # Supplier Performance tab
        self.create_supplier_performance_tab(analytics_notebook)
    
    def create_top_products_tab(self, notebook):
        """Create top products analysis tab"""
        
        top_products_frame = ttk.Frame(notebook)
        notebook.add(top_products_frame, text="🏆 Top Products")
        
        # Top products table
        columns = ('Rank', 'Product', 'Units Sold', 'Revenue', 'Profit', 'Margin %', 'Cost Efficiency')
        self.top_products_tree = ttk.Treeview(top_products_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.top_products_tree.heading('Rank', text='#')
        self.top_products_tree.heading('Product', text='Product Name')
        self.top_products_tree.heading('Units Sold', text='Units Sold')
        self.top_products_tree.heading('Revenue', text='Revenue')
        self.top_products_tree.heading('Profit', text='Profit')
        self.top_products_tree.heading('Margin %', text='Margin %')
        self.top_products_tree.heading('Cost Efficiency', text='Cost Efficiency')
        
        # Set column widths
        self.top_products_tree.column('Rank', width=40)
        self.top_products_tree.column('Product', width=150)
        self.top_products_tree.column('Units Sold', width=80)
        self.top_products_tree.column('Revenue', width=80)
        self.top_products_tree.column('Profit', width=80)
        self.top_products_tree.column('Margin %', width=70)
        self.top_products_tree.column('Cost Efficiency', width=100)
        
        # Scrollbar
        products_scrollbar = ttk.Scrollbar(top_products_frame, orient="vertical", command=self.top_products_tree.yview)
        self.top_products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        self.top_products_tree.pack(side="left", fill="both", expand=True)
        products_scrollbar.pack(side="right", fill="y")
    
    def create_category_performance_tab(self, notebook):
        """Create category performance analysis tab"""
        
        category_frame = ttk.Frame(notebook)
        notebook.add(category_frame, text="📊 Category Analysis")
        
        # Category performance table
        columns = ('Category', 'Products', 'Total Stock', 'Inventory Value', 'Revenue', 'Profit', 'Margin %')
        self.category_tree = ttk.Treeview(category_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        for col in columns:
            self.category_tree.heading(col, text=col)
            self.category_tree.column(col, width=100)
        
        # Scrollbar
        category_scrollbar = ttk.Scrollbar(category_frame, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=category_scrollbar.set)
        
        self.category_tree.pack(side="left", fill="both", expand=True)
        category_scrollbar.pack(side="right", fill="y")
    
    def create_supplier_performance_tab(self, notebook):
        """Create supplier performance analysis tab"""
        
        supplier_frame = ttk.Frame(notebook)
        notebook.add(supplier_frame, text="🤝 Supplier Performance")
        
        # Supplier performance table
        columns = ('Supplier', 'Total Orders', 'Delivery Rate', 'Avg Cost', 'Products', 'Performance Score')
        self.supplier_tree = ttk.Treeview(supplier_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        for col in columns:
            self.supplier_tree.heading(col, text=col)
            self.supplier_tree.column(col, width=100)
        
        # Scrollbar
        supplier_scrollbar = ttk.Scrollbar(supplier_frame, orient="vertical", command=self.supplier_tree.yview)
        self.supplier_tree.configure(yscrollcommand=supplier_scrollbar.set)
        
        self.supplier_tree.pack(side="left", fill="both", expand=True)
        supplier_scrollbar.pack(side="right", fill="y")
    
    def create_export_section(self):
        """Create enhanced export options"""
        
        export_frame = ttk.LabelFrame(self.scrollable_frame, text="📤 Export Analytics", padding="10")
        export_frame.pack(fill='x', padx=10, pady=5)
        
        # Export buttons
        export_buttons_frame = ttk.Frame(export_frame)
        export_buttons_frame.pack(fill='x')
        
        ttk.Button(export_buttons_frame, text="📊 Export Analytics Data", 
                  command=self.export_analytics_data).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_buttons_frame, text="📈 Export Charts as Images", 
                  command=self.export_charts).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_buttons_frame, text="📑 Generate Analytics Report", 
                  command=self.generate_analytics_report).pack(side=tk.LEFT, padx=5)
        
        # Export status
        self.export_status_label = ttk.Label(export_frame, text="Ready to export analytics data", 
                                            font=("Helvetica", 9))
        self.export_status_label.pack(anchor='w', pady=(5, 0))
    
    def set_view_mode(self, mode):
        """Set the chart view mode (Daily, Weekly, Monthly)"""
        self.chart_view_mode = mode
        self.view_indicator.config(text=f"Current View: {mode}")
        
        # Update button states
        self.daily_btn.config(state='normal')
        self.weekly_btn.config(state='normal')
        self.monthly_btn.config(state='normal')
        
        if mode == "Daily":
            self.daily_btn.config(state='disabled')
        elif mode == "Weekly":
            self.weekly_btn.config(state='disabled')
        elif mode == "Monthly":
            self.monthly_btn.config(state='disabled')
        
        # Refresh charts with new view mode
        self.refresh_charts()
    
    def refresh_data(self, filters):
        """Refresh all analytics data based on current filters"""
        try:
            self.current_filters = filters
            
            # Refresh charts
            self.refresh_charts()
            
            # Refresh analytics tables
            self.refresh_analytics_tables()
            
        except Exception as e:
            print(f"Error refreshing analytics data: {e}")
    
    def refresh_charts(self):
        """Refresh all charts with current data"""
        if not self.matplotlib_available or not self.dashboard_funcs:
            return
        
        try:
            # Refresh sales trend chart
            self.update_sales_trend_chart()
            
            # Refresh category chart
            self.update_category_chart()
            
            # Refresh profit margin chart
            self.update_profit_margin_chart()
            
            # Refresh inventory chart
            self.update_inventory_chart()
            
        except Exception as e:
            print(f"Error refreshing charts: {e}")
    
    def update_sales_trend_chart(self):
        """Update the sales trend chart"""
        try:
            if not self.current_filters:
                return
            
            # Get sales data
            daily_sales = self.dashboard_funcs['get_daily_sales_data'](
                self.current_filters['start_date'], 
                self.current_filters['end_date']
            )
            
            # Clear previous chart
            self.sales_ax1.clear()
            
            if daily_sales:
                dates = [data['sale_date'] for data in daily_sales]
                revenues = [float(data['daily_revenue'] or 0) for data in daily_sales]
                profits = [float(data['daily_profit'] or 0) for data in daily_sales]
                
                # Create dual-axis chart
                self.sales_ax2 = self.sales_ax1.twinx()
                
                # Plot revenue
                line1 = self.sales_ax1.plot(dates, revenues, 'b-', label='Revenue', linewidth=2, marker='o')
                self.sales_ax1.set_ylabel('Revenue ($)', color='b')
                self.sales_ax1.tick_params(axis='y', labelcolor='b')
                
                # Plot profit
                line2 = self.sales_ax2.plot(dates, profits, 'g-', label='Profit', linewidth=2, marker='s')
                self.sales_ax2.set_ylabel('Profit ($)', color='g')
                self.sales_ax2.tick_params(axis='y', labelcolor='g')
                
                # Formatting
                self.sales_ax1.set_title(f"Sales & Profit Trend - {self.chart_view_mode} View")
                self.sales_ax1.grid(True, alpha=0.3)
                
                # Rotate x-axis labels for better readability
                self.sales_fig.autofmt_xdate()
                
            else:
                self.sales_ax1.text(0.5, 0.5, 'No sales data available\nfor selected period', 
                                   horizontalalignment='center', verticalalignment='center',
                                   transform=self.sales_ax1.transAxes, fontsize=12)
                self.sales_ax1.set_title(f"Sales Trend - {self.chart_view_mode} View")
            
            self.sales_canvas.draw()
            
        except Exception as e:
            print(f"Error updating sales trend chart: {e}")
    
    def update_category_chart(self):
        """Update the category performance chart"""
        try:
            # Get category data
            category_data = self.dashboard_funcs['get_category_analytics']()
            
            # Clear previous chart
            self.category_ax.clear()
            
            if category_data:
                categories = [cat['category_name'] for cat in category_data if cat['total_revenue'] > 0]
                revenues = [float(cat['total_revenue']) for cat in category_data if cat['total_revenue'] > 0]
                
                if categories and revenues:
                    # Create pie chart
                    colors = self.plt.cm.Set3(self.np.linspace(0, 1, len(categories)))
                    wedges, texts, autotexts = self.category_ax.pie(revenues, labels=categories, autopct='%1.1f%%', 
                                                                   colors=colors, startangle=90)
                    
                    # Improve text readability
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                    
                else:
                    self.category_ax.text(0.5, 0.5, 'No revenue data\navailable by category', 
                                         horizontalalignment='center', verticalalignment='center',
                                         transform=self.category_ax.transAxes, fontsize=12)
            else:
                self.category_ax.text(0.5, 0.5, 'No category data\navailable', 
                                     horizontalalignment='center', verticalalignment='center',
                                     transform=self.category_ax.transAxes, fontsize=12)
            
            self.category_ax.set_title("Revenue Distribution by Category")
            self.category_canvas.draw()
            
        except Exception as e:
            print(f"Error updating category chart: {e}")
    
    def update_profit_margin_chart(self):
        """Update the profit margin analysis chart"""
        try:
            # Get profit margin data
            margin_data = self.dashboard_funcs['calculate_profit_margins']()
            
            # Clear previous chart
            self.margin_ax.clear()
            
            if margin_data:
                # Get top 10 products by margin
                top_margins = sorted(margin_data, key=lambda x: x['profit_margin'], reverse=True)[:10]
                
                products = [p['name'][:15] + '...' if len(p['name']) > 15 else p['name'] for p in top_margins]
                margins = [float(p['profit_margin']) for p in top_margins]
                
                # Create horizontal bar chart
                bars = self.margin_ax.barh(products, margins, color='skyblue')
                
                # Color bars based on margin levels
                for i, bar in enumerate(bars):
                    if margins[i] >= 30:
                        bar.set_color('green')
                    elif margins[i] >= 20:
                        bar.set_color('orange')
                    else:
                        bar.set_color('red')
                
                self.margin_ax.set_xlabel('Profit Margin (%)')
                self.margin_ax.set_title('Top 10 Products by Profit Margin')
                self.margin_ax.grid(True, axis='x', alpha=0.3)
                
            else:
                self.margin_ax.text(0.5, 0.5, 'No profit margin\ndata available', 
                                   horizontalalignment='center', verticalalignment='center',
                                   transform=self.margin_ax.transAxes, fontsize=12)
                self.margin_ax.set_title('Product Profit Margins')
            
            self.margin_canvas.draw()
            
        except Exception as e:
            print(f"Error updating profit margin chart: {e}")
    
    def update_inventory_chart(self):
        """Update the inventory value analysis chart"""
        try:
            # Get category data for inventory analysis
            category_data = self.dashboard_funcs['get_category_analytics']()
            
            # Clear previous chart
            self.inventory_ax.clear()
            
            if category_data:
                categories = [cat['category_name'] for cat in category_data]
                cost_values = [float(cat['inventory_cost_value']) for cat in category_data]
                retail_values = [float(cat['inventory_retail_value']) for cat in category_data]
                
                x = self.np.arange(len(categories))
                width = 0.35
                
                # Create grouped bar chart
                bars1 = self.inventory_ax.bar(x - width/2, cost_values, width, label='Cost Value', color='lightcoral')
                bars2 = self.inventory_ax.bar(x + width/2, retail_values, width, label='Retail Value', color='skyblue')
                
                self.inventory_ax.set_xlabel('Categories')
                self.inventory_ax.set_ylabel('Value ($)')
                self.inventory_ax.set_title('Inventory Value: Cost vs Retail by Category')
                self.inventory_ax.set_xticks(x)
                self.inventory_ax.set_xticklabels(categories, rotation=45, ha='right')
                self.inventory_ax.legend()
                self.inventory_ax.grid(True, axis='y', alpha=0.3)
                
            else:
                self.inventory_ax.text(0.5, 0.5, 'No inventory data\navailable', 
                                      horizontalalignment='center', verticalalignment='center',
                                      transform=self.inventory_ax.transAxes, fontsize=12)
                self.inventory_ax.set_title('Inventory Value Distribution')
            
            self.inventory_canvas.draw()
            
        except Exception as e:
            print(f"Error updating inventory chart: {e}")
    
    def refresh_analytics_tables(self):
        """Refresh all analytics tables"""
        try:
            # Refresh top products table
            self.update_top_products_table()
            
            # Refresh category performance table
            self.update_category_table()
            
            # Refresh supplier performance table
            self.update_supplier_table()
            
        except Exception as e:
            print(f"Error refreshing analytics tables: {e}")
    
    def update_top_products_table(self):
        """Update top products table"""
        try:
            if not self.dashboard_funcs or not self.current_filters:
                return
            
            # Clear existing items
            for item in self.top_products_tree.get_children():
                self.top_products_tree.delete(item)
            
            # Get top products data
            top_products = self.dashboard_funcs['get_top_products'](
                self.current_filters['start_date'], 
                self.current_filters['end_date'], 
                15  # Top 15 products
            )
            
            for i, product in enumerate(top_products, 1):
                # Calculate cost efficiency (revenue per unit cost)
                cost_efficiency = "N/A"
                if product.get('cost') and product['cost'] > 0:
                    efficiency = float(product['revenue']) / (float(product['cost']) * product['units_sold'])
                    cost_efficiency = f"{efficiency:.2f}x"
                
                self.top_products_tree.insert('', 'end', values=(
                    i,
                    product['name'][:30] + "..." if len(product['name']) > 30 else product['name'],
                    f"{product['units_sold']:,}",
                    f"${product['revenue']:,.2f}",
                    f"${product['profit']:,.2f}",
                    f"{product['profit_margin']:.1f}%",
                    cost_efficiency
                ))
            
        except Exception as e:
            print(f"Error updating top products table: {e}")
    
    def update_category_table(self):
        """Update category performance table"""
        try:
            if not self.dashboard_funcs:
                return
            
            # Clear existing items
            for item in self.category_tree.get_children():
                self.category_tree.delete(item)
            
            # Get category data
            category_data = self.dashboard_funcs['get_category_analytics']()
            
            for cat in category_data:
                self.category_tree.insert('', 'end', values=(
                    cat['category_name'],
                    f"{cat['products_count']:,}",
                    f"{cat['total_stock']:,}",
                    f"${cat['inventory_retail_value']:,.2f}",
                    f"${cat['total_revenue']:,.2f}",
                    f"${cat['total_profit']:,.2f}",
                    f"{cat['profit_margin']:.1f}%"
                ))
            
        except Exception as e:
            print(f"Error updating category table: {e}")
    
    def update_supplier_table(self):
        """Update supplier performance table"""
        try:
            if not self.dashboard_funcs:
                return
            
            # Clear existing items
            for item in self.supplier_tree.get_children():
                self.supplier_tree.delete(item)
            
            # Get supplier data
            supplier_data = self.dashboard_funcs['get_supplier_performance']()
            
            for supplier in supplier_data:
                # Calculate performance score (simplified)
                performance_score = supplier['delivery_success_rate'] or 0
                score_color = "🟢" if performance_score >= 90 else "🟡" if performance_score >= 70 else "🔴"
                
                self.supplier_tree.insert('', 'end', values=(
                    supplier['supplier_name'],
                    f"{supplier['total_orders'] or 0:,}",
                    f"{supplier['delivery_success_rate'] or 0:.1f}%",
                    f"${supplier['avg_unit_cost'] or 0:.2f}",
                    f"{supplier['products_supplied'] or 0:,}",
                    f"{score_color} {performance_score:.1f}%"
                ))
            
        except Exception as e:
            print(f"Error updating supplier table: {e}")
    
    # Export methods
    def export_analytics_data(self):
        """Export analytics data to CSV"""
        try:
            self.export_status_label.config(text="Exporting analytics data...")
            # Implementation would export current analytics data to CSV
            messagebox.showinfo("Export", "Analytics data export functionality ready!\n\nWould export:\n- Top products analysis\n- Category performance\n- Supplier metrics\n- Sales trends")
            self.export_status_label.config(text="Analytics data export ready")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {e}")
            self.export_status_label.config(text="Export failed")
    
    def export_charts(self):
        """Export charts as images"""
        try:
            self.export_status_label.config(text="Exporting charts...")
            if self.matplotlib_available:
                messagebox.showinfo("Export", "Chart export functionality ready!\n\nWould export all charts as PNG/PDF images")
            else:
                messagebox.showwarning("Export", "Matplotlib required for chart export")
            self.export_status_label.config(text="Chart export ready")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting charts: {e}")
            self.export_status_label.config(text="Export failed")
    
    def generate_analytics_report(self):
        """Generate comprehensive analytics report"""
        try:
            self.export_status_label.config(text="Generating analytics report...")
            messagebox.showinfo("Report", "Analytics report generation ready!\n\nWould generate comprehensive PDF report with:\n- All charts and visualizations\n- Detailed analytics tables\n- Business insights and recommendations")
            self.export_status_label.config(text="Report generation ready")
        except Exception as e:
            messagebox.showerror("Report Error", f"Error generating report: {e}")
            self.export_status_label.config(text="Report generation failed")


class PerformanceUI:
    """Performance subtab - Employee and product performance"""
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.create_placeholder()
    
    def create_placeholder(self):
        placeholder_frame = ttk.Frame(self.parent, padding="20")
        placeholder_frame.pack(fill='both', expand=True)
        
        ttk.Label(placeholder_frame, 
                 text="👤 Performance Subtab", 
                 font=("Helvetica", 16, "bold")).pack(pady=10)
        
        ttk.Label(placeholder_frame, 
                 text="Employee and product performance metrics will be displayed here.\n\nComing in Phase 5A!", 
                 font=("Helvetica", 12)).pack()
    
    def refresh_data(self, filters):
        pass


class SimulationUI:
    """Simulation subtab - What-if analysis tools"""
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.create_placeholder()
    
    def create_placeholder(self):
        placeholder_frame = ttk.Frame(self.parent, padding="20")
        placeholder_frame.pack(fill='both', expand=True)
        
        ttk.Label(placeholder_frame, 
                 text="🎲 Simulation Subtab", 
                 font=("Helvetica", 16, "bold")).pack(pady=10)
        
        ttk.Label(placeholder_frame, 
                 text="What-if analysis and simulation tools will be displayed here.\n\nComing in Phase 5B!", 
                 font=("Helvetica", 12)).pack()
    
    def refresh_data(self, filters):
        pass
