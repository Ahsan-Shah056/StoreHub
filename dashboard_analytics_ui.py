"""
Dashboard Analytics UI Module
Analytics subtab with advanced charts, data visualization, and business intelligence
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from dashboard_base import DashboardBaseUI, DashboardConstants

class AnalyticsUI(DashboardBaseUI):
    """Analytics subtab - Advanced charts and data visualization with business intelligence"""
    
    def __init__(self, parent, callbacks):
        super().__init__(parent, callbacks)
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
        
        ttk.Label(view_frame, text="Chart View Mode:", font=DashboardConstants.SUBHEADER_FONT).pack(side=tk.LEFT, padx=(0, 10))
        
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
                                       font=DashboardConstants.SMALL_FONT, foreground=DashboardConstants.INFO_COLOR)
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
                                            font=DashboardConstants.SMALL_FONT)
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
                    efficiency = float(product['revenue']) / (float(product['cost']) * float(product['units_sold']))
                    cost_efficiency = f"{efficiency:.2f}x"
                
                self.top_products_tree.insert('', 'end', values=(
                    i,
                    product['name'][:30] + "..." if len(product['name']) > 30 else product['name'],
                    self.format_number(product['units_sold']),
                    self.format_currency(product['revenue']),
                    self.format_currency(product['profit']),
                    self.format_percentage(product['profit_margin']),
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
                    self.format_number(cat['products_count']),
                    self.format_number(cat['total_stock']),
                    self.format_currency(cat['inventory_retail_value']),
                    self.format_currency(cat['total_revenue']),
                    self.format_currency(cat['total_profit']),
                    self.format_percentage(cat['profit_margin'])
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
                    self.format_number(supplier['total_orders'] or 0),
                    self.format_percentage(supplier['delivery_success_rate'] or 0),
                    self.format_currency(supplier['avg_unit_cost'] or 0),
                    self.format_number(supplier['products_supplied'] or 0),
                    f"{score_color} {self.format_percentage(performance_score)}"
                ))
            
        except Exception as e:
            print(f"Error updating supplier table: {e}")
    
    # Export methods
    def export_analytics_data(self):
        """Export analytics data to CSV"""
        try:
            self.export_status_label.config(text="Exporting analytics data...")
            # Implementation would export current analytics data to CSV
            self.show_info("Export", "Analytics data export functionality ready!\n\nWould export:\n- Top products analysis\n- Category performance\n- Supplier metrics\n- Sales trends")
            self.export_status_label.config(text="Analytics data export ready")
        except Exception as e:
            self.show_error("Export Error", f"Error exporting data: {e}")
            self.export_status_label.config(text="Export failed")
    
    def export_charts(self):
        """Export charts as images"""
        try:
            self.export_status_label.config(text="Exporting charts...")
            if self.matplotlib_available:
                self.show_info("Export", "Chart export functionality ready!\n\nWould export all charts as PNG/PDF images")
            else:
                messagebox.showwarning("Export", "Matplotlib required for chart export")
            self.export_status_label.config(text="Chart export ready")
        except Exception as e:
            self.show_error("Export Error", f"Error exporting charts: {e}")
            self.export_status_label.config(text="Export failed")
    
    def generate_analytics_report(self):
        """Generate comprehensive analytics report"""
        try:
            self.export_status_label.config(text="Generating analytics report...")
            self.show_info("Report", "Analytics report generation ready!\n\nWould generate comprehensive PDF report with:\n- All charts and visualizations\n- Detailed analytics tables\n- Business insights and recommendations")
            self.export_status_label.config(text="Report generation ready")
        except Exception as e:
            self.show_error("Report Error", f"Error generating report: {e}")
            self.export_status_label.config(text="Report generation failed")
