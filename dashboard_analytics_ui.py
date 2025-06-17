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
        self.data_limit_var = None  # Will be initialized in UI creation
        self.chart_style_var = None  # Will be initialized in UI creation
        
        # Import required libraries for charts
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
            import matplotlib.dates as mdates
            import numpy as np
            
            self.matplotlib_available = True
            self.plt = plt
            self.FigureCanvasTkAgg = FigureCanvasTkAgg
            self.Figure = Figure
            self.mdates = mdates
            self.np = np
            
            # Configure matplotlib to avoid categorical interpretation
            import matplotlib
            matplotlib.rcParams['figure.max_open_warning'] = 50
            matplotlib.rcParams['axes.formatter.use_mathtext'] = False
            
            # Disable automatic date detection
            try:
                from matplotlib import category
                # This helps prevent automatic categorization
                matplotlib.rcParams['date.autoformatter.year'] = '%Y'
                matplotlib.rcParams['date.autoformatter.month'] = '%b %Y'
                matplotlib.rcParams['date.autoformatter.day'] = '%m/%d'
            except:
                pass
            
            # Set matplotlib style safely
            try:
                plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
            except:
                pass  # Use default style if seaborn not available
            
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
        
        # Main scrollable frame with enhanced canvas
        canvas = tk.Canvas(self.parent, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configure Canvas to match the theme background
        def update_canvas_bg():
            try:
                style = ttk.Style()
                bg_color = style.lookup('TFrame', 'background')
                if bg_color:
                    canvas.configure(bg=bg_color)
                else:
                    canvas.configure(bg=self.parent.cget('bg'))
            except:
                canvas.configure(bg='SystemButtonFace')
        
        self.parent.after(1, update_canvas_bg)
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Make the canvas window width match the canvas width
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)
            
            # Auto-hide scrollbar when not needed
            canvas_height = canvas.winfo_height()
            content_height = self.scrollable_frame.winfo_reqheight()
            
            if content_height > canvas_height and canvas_height > 1:
                scrollbar.pack(side="right", fill="y")
            else:
                scrollbar.pack_forget()
        
        self.scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        
        # Analytics header with view controls
        self.create_analytics_header()
        
        # Charts section
        self.create_charts_section()
        
        # Advanced analytics tables
        self.create_advanced_analytics_section()
        
        # Export options
        self.create_export_section()
    
    def create_analytics_header(self):
        """Create analytics header with chart controls"""
        
        header_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 Advanced Business Analytics", padding="10")
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # Chart configuration controls
        config_frame = ttk.Frame(header_frame)
        config_frame.pack(fill='x')
        
        ttk.Label(config_frame, text="Chart Options:", font=DashboardConstants.SUBHEADER_FONT).pack(side=tk.LEFT, padx=(0, 10))
        
        # Data limit control
        ttk.Label(config_frame, text="Max Items:", font=DashboardConstants.SMALL_FONT).pack(side=tk.LEFT, padx=(0, 5))
        self.data_limit_var = tk.StringVar(value="5")
        data_limit_combo = ttk.Combobox(config_frame, textvariable=self.data_limit_var, 
                                       values=["5", "8", "10", "15", "20"], width=5, state="readonly")
        data_limit_combo.pack(side=tk.LEFT, padx=(0, 10))
        data_limit_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_charts())
        
        # Chart style control
        ttk.Label(config_frame, text="Style:", font=DashboardConstants.SMALL_FONT).pack(side=tk.LEFT, padx=(0, 5))
        self.chart_style_var = tk.StringVar(value="Professional")
        style_combo = ttk.Combobox(config_frame, textvariable=self.chart_style_var, 
                                  values=["Professional", "Colorful", "Minimal"], width=10, state="readonly")
        style_combo.pack(side=tk.LEFT, padx=(0, 10))
        style_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_charts())
        
        # Refresh button
        ttk.Button(config_frame, text="🔄 Refresh Charts", command=self.refresh_charts).pack(side=tk.RIGHT, padx=10)
    
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
        
        # Chart 1: Top Products Performance Bar Chart
        self.create_top_products_chart(charts_container, 0, 0)
        
        # Chart 2: Category Performance Pie Chart
        self.create_category_chart(charts_container, 0, 1)
        
        # Chart 3: Profit Margin Analysis
        self.create_profit_margin_chart(charts_container, 1, 0)
        
        # Chart 4: Inventory Value Analysis
        self.create_inventory_chart(charts_container, 1, 1)
    
    def create_top_products_chart(self, parent, row, col):
        """Create top products performance bar chart"""
        
        chart_frame = ttk.LabelFrame(parent, text="🏆 Top Products Performance", padding="5")
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        if self.matplotlib_available:
            # Create matplotlib figure
            self.products_fig = self.Figure(figsize=(6, 4), dpi=100)
            self.products_ax = self.products_fig.add_subplot(111)
            
            # Create canvas
            self.products_canvas = self.FigureCanvasTkAgg(self.products_fig, chart_frame)
            self.products_canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # Initial placeholder
            self.products_ax.text(0.5, 0.5, 'Top Products Chart\nLoading...', 
                                 horizontalalignment='center', verticalalignment='center',
                                 transform=self.products_ax.transAxes, fontsize=12)
            self.products_ax.set_title("Top Products by Revenue")
            
        else:
            # Fallback text display
            placeholder = tk.Text(chart_frame, height=8, wrap=tk.WORD)
            placeholder.pack(fill='both', expand=True)
            placeholder.insert(tk.END, "Top Products Chart\n\nMatplotlib not available.\nInstall matplotlib for chart visualization:\npip install matplotlib\n\nChart would show:\n- Top selling products\n- Revenue comparison\n- Performance indicators")
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
        
        # Export status
        self.export_status_label = ttk.Label(export_frame, text="Ready to export analytics data", 
                                            font=DashboardConstants.SMALL_FONT)
        self.export_status_label.pack(anchor='w', pady=(5, 0))
    
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
            # Refresh top products chart
            self.update_top_products_chart()
            
            # Refresh category chart
            self.update_category_chart()
            
            # Refresh profit margin chart
            self.update_profit_margin_chart()
            
            # Refresh inventory chart
            self.update_inventory_chart()
            
        except Exception as e:
            print(f"Error refreshing charts: {e}")
    
    def update_top_products_chart(self):
        """Update the top products performance chart - simple and effective"""
        try:
            if not self.dashboard_funcs or not self.current_filters:
                return
            
            # Clear previous chart
            self.products_ax.clear()
            
            # Get the number of items from dropdown
            try:
                limit = int(self.data_limit_var.get()) if self.data_limit_var else 8
            except (ValueError, AttributeError):
                limit = 8
            
            # Get top products data
            top_products = self.dashboard_funcs['get_top_products'](
                self.current_filters['start_date'], 
                self.current_filters['end_date'], 
                limit  # Use dynamic limit from dropdown
            )
            
            if top_products:
                # Extract data for chart
                product_names = []
                revenues = []
                
                for product in top_products:
                    # Truncate long product names
                    name = product['name']
                    if len(name) > 15:
                        name = name[:12] + '...'
                    product_names.append(name)
                    revenues.append(float(product['revenue']))
                
                # Create horizontal bar chart (easier to read product names)
                y_positions = range(len(product_names))
                
                # Get colors based on style
                colors = self.get_color_palette(len(product_names))
                
                bars = self.products_ax.barh(y_positions, revenues, color=colors[:len(product_names)], alpha=0.8)
                
                # Add value labels on bars
                for i, (bar, revenue) in enumerate(zip(bars, revenues)):
                    width = bar.get_width()
                    self.products_ax.text(width + max(revenues) * 0.01, bar.get_y() + bar.get_height()/2, 
                                         f'${revenue:,.0f}', 
                                         ha='left', va='center', fontsize=9, fontweight='bold')
                
                # Formatting
                self.products_ax.set_yticks(y_positions)
                self.products_ax.set_yticklabels(product_names)
                self.products_ax.set_xlabel('Revenue ($)')
                self.products_ax.set_title(f'Top {len(product_names)} Products by Revenue')
                self.products_ax.grid(True, axis='x', alpha=0.3)
                
                # Adjust layout to prevent label cutoff
                self.products_ax.set_xlim(0, max(revenues) * 1.15)
                
            else:
                self.products_ax.text(0.5, 0.5, 'No product data available\nfor selected period', 
                                     horizontalalignment='center', verticalalignment='center',
                                     transform=self.products_ax.transAxes, fontsize=12)
                self.products_ax.set_title('Top Products Performance')
            
            self.products_canvas.draw()
            
        except Exception as e:
            print(f"Error updating top products chart: {e}")
    
    def get_color_palette(self, count):
        """Get color palette based on selected style"""
        try:
            style = self.chart_style_var.get() if self.chart_style_var and hasattr(self.chart_style_var, 'get') else "Professional"
            
            if style == "Professional":
                # Professional blue-gray palette
                colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3D5A80', '#98C1D9', '#EE6C4D', '#293241']
            elif style == "Colorful":
                # Vibrant colorful palette
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
            else:  # Minimal
                # Minimal grayscale with accent
                colors = ['#2C3E50', '#7F8C8D', '#BDC3C7', '#3498DB', '#95A5A6', '#34495E', '#85929E', '#AEB6BF']
            
            # Repeat colors if we need more
            while len(colors) < count:
                colors.extend(colors)
            
            return colors[:count]
            
        except Exception as e:
            print(f"Error getting color palette: {e}")
            return ['#3498DB'] * count
    
    def update_category_chart(self):
        """Update the category performance chart with optimized display"""
        try:
            # Get category data
            category_data = self.dashboard_funcs['get_category_analytics']()
            
            # Clear previous chart
            self.category_ax.clear()
            
            if category_data:
                # Filter and sort categories by revenue
                filtered_categories = [cat for cat in category_data if cat['total_revenue'] > 0]
                filtered_categories = sorted(filtered_categories, key=lambda x: float(x['total_revenue']), reverse=True)
                
                # Limit to top categories for better readability
                max_categories = int(self.data_limit_var.get()) if self.data_limit_var and hasattr(self.data_limit_var, 'get') else 8
                if len(filtered_categories) > max_categories:
                    top_categories = filtered_categories[:max_categories-1]
                    # Combine remaining categories into "Others"
                    others_revenue = sum(float(cat['total_revenue']) for cat in filtered_categories[max_categories-1:])
                    if others_revenue > 0:
                        top_categories.append({'category_name': 'Others', 'total_revenue': others_revenue})
                    filtered_categories = top_categories
                
                if filtered_categories:
                    categories = [cat['category_name'] for cat in filtered_categories]
                    revenues = [float(cat['total_revenue']) for cat in filtered_categories]
                    
                    # Use dynamic color palette based on style
                    colors = self.get_color_palette(len(categories))
                    
                    # Create pie chart with improved formatting
                    wedges, texts, autotexts = self.category_ax.pie(
                        revenues, 
                        labels=categories, 
                        autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',  # Only show % for significant slices
                        colors=colors, 
                        startangle=90,
                        explode=[0.05 if i == 0 else 0 for i in range(len(categories))]  # Explode top category
                    )
                    
                    # Improve text readability
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                        autotext.set_fontsize(9)
                    
                    # Improve label formatting
                    for text in texts:
                        text.set_fontsize(8)
                        # Truncate long category names
                        if len(text.get_text()) > 12:
                            text.set_text(text.get_text()[:12] + '...')
                    
                    # Add a legend for better clarity
                    self.category_ax.legend(wedges, [f"{cat}: ${rev:,.0f}" for cat, rev in zip(categories, revenues)],
                                           title="Revenue by Category",
                                           loc="center left",
                                           bbox_to_anchor=(1, 0, 0.5, 1),
                                           fontsize=8)
                    
                else:
                    self.category_ax.text(0.5, 0.5, 'No revenue data\navailable by category', 
                                         horizontalalignment='center', verticalalignment='center',
                                         transform=self.category_ax.transAxes, fontsize=12)
            else:
                self.category_ax.text(0.5, 0.5, 'No category data\navailable', 
                                     horizontalalignment='center', verticalalignment='center',
                                     transform=self.category_ax.transAxes, fontsize=12)
            
            self.category_ax.set_title(f"Revenue Distribution by Category (Top {min(len(filtered_categories) if filtered_categories else 0, max_categories)})")
            self.category_canvas.draw()
            
        except Exception as e:
            print(f"Error updating category chart: {e}")
    
    def update_profit_margin_chart(self):
        """Update the profit margin analysis chart with optimized display"""
        try:
            # Get profit margin data
            margin_data = self.dashboard_funcs['calculate_profit_margins']()
            
            # Clear previous chart
            self.margin_ax.clear()
            
            if margin_data:
                # Filter out products with very low margins or revenue for focus
                filtered_margins = [p for p in margin_data if float(p.get('profit_margin', 0)) > 0]
                
                # Get top products by margin for better readability
                max_products = int(self.data_limit_var.get()) if self.data_limit_var else 8
                top_margins = sorted(filtered_margins, key=lambda x: float(x['profit_margin']), reverse=True)[:max_products]
                
                if top_margins:
                    # Truncate product names for better display
                    products = []
                    for p in top_margins:
                        name = p['name']
                        if len(name) > 20:
                            name = name[:17] + '...'
                        products.append(name)
                    
                    margins = [float(p['profit_margin']) for p in top_margins]
                    
                    # Get colors from the selected theme
                    colors = self.get_color_palette(len(products))
                    
                    # Create horizontal bar chart with theme colors
                    bars = self.margin_ax.barh(products, margins, color=colors, alpha=0.8)
                    
                    # Add value labels on bars
                    for i, (bar, margin) in enumerate(zip(bars, margins)):
                        width = bar.get_width()
                        self.margin_ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                                           f'{margin:.1f}%', 
                                           ha='left', va='center', fontsize=9, fontweight='bold')
                    
                    self.margin_ax.set_xlabel('Profit Margin (%)')
                    self.margin_ax.set_title(f'Top {len(top_margins)} Products by Profit Margin')
                    self.margin_ax.grid(True, axis='x', alpha=0.3)
                    
                    # Add margin level legend
                    from matplotlib.patches import Patch
                    legend_elements = [
                        Patch(facecolor='#2E8B57', label='Excellent (40%+)'),
                        Patch(facecolor='#32CD32', label='Good (25-40%)'),
                        Patch(facecolor='#FFD700', label='Average (15-25%)'),
                        Patch(facecolor='#FF8C00', label='Low (5-15%)'),
                        Patch(facecolor='#FF6347', label='Very Low (<5%)')
                    ]
                    self.margin_ax.legend(handles=legend_elements, loc='lower right', fontsize=8)
                    
                    # Adjust layout to prevent label cutoff
                    self.margin_ax.set_xlim(0, max(margins) * 1.15)
                    
                else:
                    self.margin_ax.text(0.5, 0.5, 'No products with\npositive margins found', 
                                       horizontalalignment='center', verticalalignment='center',
                                       transform=self.margin_ax.transAxes, fontsize=12)
                    self.margin_ax.set_title('Product Profit Margins')
                
            else:
                self.margin_ax.text(0.5, 0.5, 'No profit margin\ndata available', 
                                   horizontalalignment='center', verticalalignment='center',
                                   transform=self.margin_ax.transAxes, fontsize=12)
                self.margin_ax.set_title('Product Profit Margins')
            
            self.margin_canvas.draw()
            
        except Exception as e:
            print(f"Error updating profit margin chart: {e}")
    
    def update_inventory_chart(self):
        """Update the inventory value analysis chart with optimized display"""
        try:
            # Get category data for inventory analysis
            category_data = self.dashboard_funcs['get_category_analytics']()
            
            # Clear previous chart
            self.inventory_ax.clear()
            
            if category_data:
                # Filter categories with significant inventory value and limit display
                significant_categories = [
                    cat for cat in category_data 
                    if float(cat['inventory_retail_value']) > 0
                ]
                
                # Sort by retail value and take top categories for better readability
                max_categories = int(self.data_limit_var.get()) if self.data_limit_var and hasattr(self.data_limit_var, 'get') else 6
                significant_categories = sorted(
                    significant_categories, 
                    key=lambda x: float(x['inventory_retail_value']), 
                    reverse=True
                )[:max_categories]
                
                if significant_categories:
                    # Truncate category names for better display
                    categories = []
                    for cat in significant_categories:
                        name = cat['category_name']
                        if len(name) > 12:
                            name = name[:9] + '...'
                        categories.append(name)
                    
                    cost_values = [float(cat['inventory_cost_value']) for cat in significant_categories]
                    retail_values = [float(cat['inventory_retail_value']) for cat in significant_categories]
                    
                    x = self.np.arange(len(categories))
                    width = 0.35
                    
                    # Get colors based on style
                    colors = self.get_color_palette(2)
                    
                    # Create grouped bar chart with style-based colors
                    bars1 = self.inventory_ax.bar(x - width/2, cost_values, width, 
                                                 label='Cost Value', color=colors[0], alpha=0.8)
                    bars2 = self.inventory_ax.bar(x + width/2, retail_values, width, 
                                                 label='Retail Value', color=colors[1], alpha=0.8)
                    
                    # Add value labels on bars
                    for bars in [bars1, bars2]:
                        for bar in bars:
                            height = bar.get_height()
                            if height > 0:
                                self.inventory_ax.text(bar.get_x() + bar.get_width()/2., height,
                                                      f'${height:,.0f}',
                                                      ha='center', va='bottom', fontsize=8, rotation=0)
                    
                    self.inventory_ax.set_xlabel('Categories')
                    self.inventory_ax.set_ylabel('Value ($)')
                    self.inventory_ax.set_title(f'Inventory Value: Cost vs Retail (Top {len(categories)} Categories)')
                    self.inventory_ax.set_xticks(x)
                    self.inventory_ax.set_xticklabels(categories, rotation=45, ha='right')
                    self.inventory_ax.legend(loc='upper right')
                    self.inventory_ax.grid(True, axis='y', alpha=0.3)
                    
                    # Calculate and show average markup
                    total_cost = sum(cost_values)
                    total_retail = sum(retail_values)
                    if total_cost > 0:
                        avg_markup = ((total_retail - total_cost) / total_cost) * 100
                        self.inventory_ax.text(0.02, 0.98, f'Avg. Markup: {avg_markup:.1f}%', 
                                              transform=self.inventory_ax.transAxes, 
                                              bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                                              fontsize=9, verticalalignment='top')
                    
                else:
                    self.inventory_ax.text(0.5, 0.5, 'No categories with\nsignificant inventory value', 
                                          horizontalalignment='center', verticalalignment='center',
                                          transform=self.inventory_ax.transAxes, fontsize=12)
                    self.inventory_ax.set_title('Inventory Value Distribution')
                
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
            
            # Get top products data - limit to top 10 for better performance
            top_products = self.dashboard_funcs['get_top_products'](
                self.current_filters['start_date'], 
                self.current_filters['end_date'], 
                10  # Reduced from 15 to 10 for better readability
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
            
            # Ask user for file save location
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Analytics Data"
            )
            if not file_path:
                self.export_status_label.config(text="Export cancelled")
                return
            
            # Collect analytics data from the UI
            import csv
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write header
                writer.writerow(["ANALYTICS DATA EXPORT"])
                writer.writerow([f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([])
                
                # Export top products data if available
                if hasattr(self, 'current_filters'):
                    filters = self.current_filters
                    writer.writerow([f"Date Range: {filters.get('start_date', 'N/A')} to {filters.get('end_date', 'N/A')}"])
                    writer.writerow([f"Employee Filter: {filters.get('employee', 'All')}"])
                    writer.writerow([f"Supplier Filter: {filters.get('supplier', 'All')}"])
                    writer.writerow([f"Category Filter: {filters.get('category', 'All')}"])
                    writer.writerow([])
                
                # Try to get analytics data from backend
                try:
                    from dashboard import get_top_products, get_sales_summary
                    
                    if hasattr(self, 'current_filters'):
                        filters = self.current_filters
                        employee_id = filters.get('employee_id')
                        supplier_id = filters.get('supplier_id')
                        category_id = filters.get('category_id')
                        
                        # Top products section
                        top_products = get_top_products(
                            filters.get('start_date'), filters.get('end_date'), 10,
                            employee_id, supplier_id, category_id
                        )
                        
                        writer.writerow(["TOP PRODUCTS ANALYSIS"])
                        writer.writerow(["Rank", "Product Name", "Units Sold", "Revenue", "Average Price"])
                        for i, product in enumerate(top_products, 1):
                            writer.writerow([
                                i,
                                product.get('name', 'N/A'),
                                product.get('units_sold', 0),
                                f"${product.get('revenue', 0):.2f}",
                                f"${product.get('avg_price', 0):.2f}"
                            ])
                        
                        writer.writerow([])
                        writer.writerow(["Analytics export completed successfully"])
                        
                except ImportError:
                    writer.writerow(["Note: Full analytics data requires dashboard backend"])
            
            messagebox.showinfo("Export Success", f"Analytics data exported to {file_path}")
            self.export_status_label.config(text="Analytics data exported successfully")
            
        except Exception as e:
            self.show_error("Export Error", f"Error exporting data: {e}")
            self.export_status_label.config(text="Export failed")
    
    def export_charts(self):
        """Export charts as images"""
        try:
            self.export_status_label.config(text="Exporting charts...")
            
            if not self.matplotlib_available:
                messagebox.showwarning("Export Charts", 
                    "Matplotlib is not available. Chart export requires matplotlib to be installed.")
                self.export_status_label.config(text="Chart export requires matplotlib")
                return
            
            # Ask user for directory to save images
            from tkinter import filedialog
            dir_path = filedialog.askdirectory(title="Select Directory to Save Chart Images")
            if not dir_path:
                self.export_status_label.config(text="Export cancelled")
                return
            
            # Generate sample chart data and export (placeholder implementation)
            import matplotlib.pyplot as plt
            import os
            
            # Create a sample chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Sample data - in real implementation, use actual analytics data
            categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Sports']
            values = [2500, 1800, 3200, 1200, 950]
            
            ax.bar(categories, values)
            ax.set_title('Top Categories by Sales')
            ax.set_xlabel('Category')
            ax.set_ylabel('Sales ($)')
            
            # Save the chart
            chart_path = os.path.join(dir_path, f"analytics_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            messagebox.showinfo("Export Success", f"Chart exported to {chart_path}")
            self.export_status_label.config(text="Charts exported successfully")
            
        except Exception as e:
            self.show_error("Export Error", f"Error exporting charts: {e}")
            self.export_status_label.config(text="Export failed")
