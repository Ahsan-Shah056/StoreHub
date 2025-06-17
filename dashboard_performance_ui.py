"""
Dashboard Performance UI Module
Performance subtab with employee and product performance metrics
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from dashboard_base import DashboardBaseUI, DashboardConstants
import dashboard
import employees

class PerformanceUI(DashboardBaseUI):
    """Performance subtab - Employee and product performance"""
    
    def __init__(self, parent, callbacks):
        super().__init__(parent, callbacks)
        self.performance_data = {}
        self.selected_employee_id = None
        self.create_interface()
        self.refresh_data({})
    
    def create_interface(self):
        """Create the performance analysis interface"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, 
                 text="📊 Performance Analysis", 
                 font=DashboardConstants.HEADER_FONT).pack(side='left')
        
        # Refresh button
        ttk.Button(header_frame, 
                  text="🔄 Refresh", 
                  command=self.refresh_performance_data).pack(side='right')
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Date range selection
        ttk.Label(control_frame, text="Analysis Period:").pack(side='left', padx=(0, 5))
        
        self.period_var = tk.StringVar(value="Last 30 Days")
        period_combo = ttk.Combobox(control_frame, 
                                   textvariable=self.period_var,
                                   values=["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months"],
                                   state="readonly", width=15)
        period_combo.pack(side='left', padx=(0, 10))
        period_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_performance_data())
        
        # Notebook for different performance views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Employee Performance Tab
        self.employee_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.employee_frame, text="👤 Employee Performance")
        
        # Product Performance Tab
        self.product_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.product_frame, text="📦 Product Performance")
        
        # Cost Efficiency Tab
        self.efficiency_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.efficiency_frame, text="💰 Cost Efficiency")
        
        # Create content for each tab
        self.create_employee_performance_tab()
        self.create_product_performance_tab()
        self.create_cost_efficiency_tab()
    
    def create_employee_performance_tab(self):
        """Create employee performance analysis tab with vertical layout"""
        
        # Main scrollable canvas setup
        canvas = tk.Canvas(self.employee_frame, highlightthickness=0, bd=0)
        v_scrollbar = ttk.Scrollbar(self.employee_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure Canvas to match the theme background
        def update_canvas_bg():
            try:
                style = ttk.Style()
                bg_color = style.lookup('TFrame', 'background')
                if bg_color:
                    canvas.configure(bg=bg_color)
                else:
                    canvas.configure(bg=self.employee_frame.cget('bg'))
            except:
                canvas.configure(bg='SystemButtonFace')
        
        self.employee_frame.after(1, update_canvas_bg)
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            if scrollable_frame.winfo_reqwidth() < canvas_width:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        def on_canvas_configure(event):
            configure_scroll_region()
        
        def show_scrollbars():
            v_scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
        
        def hide_scrollbars():
            v_scrollbar.pack_forget()
            canvas.pack(side="left", fill="both", expand=True)
        
        def check_scrollbars():
            canvas.update_idletasks()
            scrollable_frame.update_idletasks()
            
            canvas_height = canvas.winfo_height()
            content_height = scrollable_frame.winfo_reqheight()
            
            if content_height > canvas_height:
                show_scrollbars()
            else:
                hide_scrollbars()
        
        scrollable_frame.bind("<Configure>", lambda e: (configure_scroll_region(), canvas.after(10, check_scrollbars)))
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Initially pack canvas and check for scrollbars
        canvas.pack(side="left", fill="both", expand=True)
        canvas.after(100, check_scrollbars)
        
        # 1. Employee Rankings Table (Top)
        rankings_frame = ttk.LabelFrame(scrollable_frame, text="👤 Employee Performance Rankings", padding="15")
        rankings_frame.pack(fill='both', expand=False, padx=10, pady=(10, 5))
        
        # Employee ranking treeview with proper container
        tree_container = ttk.Frame(rankings_frame)
        tree_container.pack(fill='both', expand=True)
        
        columns = ('Rank', 'Employee', 'Sales', 'Revenue', 'Profit', 'Avg Sale')
        self.employee_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=10)
        
        # Configure columns with better widths
        self.employee_tree.heading('Rank', text='Rank')
        self.employee_tree.heading('Employee', text='Employee Name')
        self.employee_tree.heading('Sales', text='Total Sales')
        self.employee_tree.heading('Revenue', text='Revenue')
        self.employee_tree.heading('Profit', text='Profit')
        self.employee_tree.heading('Avg Sale', text='Avg Sale')
        
        # Better column widths for readability
        self.employee_tree.column('Rank', width=70, minwidth=60)
        self.employee_tree.column('Employee', width=180, minwidth=150)
        self.employee_tree.column('Sales', width=100, minwidth=90)
        self.employee_tree.column('Revenue', width=120, minwidth=100)
        self.employee_tree.column('Profit', width=120, minwidth=100)
        self.employee_tree.column('Avg Sale', width=100, minwidth=90)
        
        # Pack treeview and scrollbar properly
        emp_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.employee_tree.yview)
        emp_scrollbar.pack(side='right', fill='y')
        self.employee_tree.configure(yscrollcommand=emp_scrollbar.set)
        self.employee_tree.pack(side='left', fill='both', expand=True)
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_employee_select)
        
        # 2. Employee Details (Middle)
        details_frame = ttk.LabelFrame(scrollable_frame, text="📊 Selected Employee Details", padding="15")
        details_frame.pack(fill='x', padx=10, pady=5)
        
        self.employee_details = ttk.Label(details_frame, 
                                         text="Select an employee from the rankings above to view detailed performance metrics",
                                         font=DashboardConstants.BODY_FONT,
                                         justify='left',
                                         anchor='w')
        self.employee_details.pack(fill='x', pady=10)
        
        # 3. Performance Chart (Bottom) - Smaller size to fit properly
        chart_frame = ttk.LabelFrame(scrollable_frame, text="📈 Performance Trend Chart", padding="10")
        chart_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        # Create matplotlib figure with smaller, more appropriate size
        self.emp_fig, self.emp_ax = plt.subplots(figsize=(8, 3), dpi=80)
        self.emp_canvas = FigureCanvasTkAgg(self.emp_fig, chart_frame)
        self.emp_canvas.get_tk_widget().pack(fill='x', expand=False, padx=5, pady=5)
        
        # Initialize with placeholder chart
        self.emp_ax.text(0.5, 0.5, 'Select an employee to view performance trends', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.emp_ax.transAxes, fontsize=10)
        self.emp_ax.set_title('Employee Performance Trend')
        self.emp_canvas.draw()
    
    def create_product_performance_tab(self):
        """Create product performance analysis tab with improved layout"""
        
        # Main scrollable canvas setup
        canvas = tk.Canvas(self.product_frame, highlightthickness=0, bd=0)
        v_scrollbar = ttk.Scrollbar(self.product_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure Canvas to match the theme background
        def update_canvas_bg():
            try:
                style = ttk.Style()
                bg_color = style.lookup('TFrame', 'background')
                if bg_color:
                    canvas.configure(bg=bg_color)
                else:
                    canvas.configure(bg=self.product_frame.cget('bg'))
            except:
                canvas.configure(bg='SystemButtonFace')
        
        self.product_frame.after(1, update_canvas_bg)
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            if scrollable_frame.winfo_reqwidth() < canvas_width:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        def on_canvas_configure(event):
            configure_scroll_region()
        
        def show_scrollbars():
            v_scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
        
        def hide_scrollbars():
            v_scrollbar.pack_forget()
            canvas.pack(side="left", fill="both", expand=True)
        
        def check_scrollbars():
            canvas.update_idletasks()
            scrollable_frame.update_idletasks()
            
            canvas_height = canvas.winfo_height()
            content_height = scrollable_frame.winfo_reqheight()
            
            if content_height > canvas_height:
                show_scrollbars()
            else:
                hide_scrollbars()
        
        scrollable_frame.bind("<Configure>", lambda e: (configure_scroll_region(), canvas.after(10, check_scrollbars)))
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Initially pack canvas and check for scrollbars
        canvas.pack(side="left", fill="both", expand=True)
        canvas.after(100, check_scrollbars)
        
        # 1. Product Performance Rankings Table (Top)
        table_frame = ttk.LabelFrame(scrollable_frame, text="🏆 Product Performance Rankings", padding="15")
        table_frame.pack(fill='both', expand=False, padx=10, pady=(10, 5))
        
        # Product performance treeview with proper container
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill='both', expand=True)
        
        columns = ('Rank', 'SKU', 'Product', 'Units Sold', 'Revenue', 'Profit', 'Avg Price')
        self.product_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=12)
        
        # Configure columns with better sizing
        self.product_tree.heading('Rank', text='Rank')
        self.product_tree.heading('SKU', text='SKU')
        self.product_tree.heading('Product', text='Product Name')
        self.product_tree.heading('Units Sold', text='Units Sold')
        self.product_tree.heading('Revenue', text='Revenue')
        self.product_tree.heading('Profit', text='Profit')
        self.product_tree.heading('Avg Price', text='Avg Price')
        
        # Better column widths for readability
        self.product_tree.column('Rank', width=70, minwidth=60)
        self.product_tree.column('SKU', width=100, minwidth=80)
        self.product_tree.column('Product', width=200, minwidth=150)
        self.product_tree.column('Units Sold', width=100, minwidth=90)
        self.product_tree.column('Revenue', width=120, minwidth=100)
        self.product_tree.column('Profit', width=120, minwidth=100)
        self.product_tree.column('Avg Price', width=100, minwidth=90)
        
        # Pack treeview and scrollbar properly
        prod_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.product_tree.yview)
        prod_scrollbar.pack(side='right', fill='y')
        self.product_tree.configure(yscrollcommand=prod_scrollbar.set)
        self.product_tree.pack(side='left', fill='both', expand=True)
        
        # 2. Product Performance Chart (Bottom)
        chart_frame = ttk.LabelFrame(scrollable_frame, text="📊 Top Products Performance Chart", padding="10")
        chart_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        # Create matplotlib figure with appropriate size
        self.prod_fig, self.prod_ax = plt.subplots(figsize=(8, 3), dpi=80)
        self.prod_canvas = FigureCanvasTkAgg(self.prod_fig, chart_frame)
        self.prod_canvas.get_tk_widget().pack(fill='x', expand=False, padx=5, pady=5)
        
        # Initialize with placeholder chart
        self.prod_ax.text(0.5, 0.5, 'Product performance chart will appear here', 
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.prod_ax.transAxes, fontsize=10)
        self.prod_ax.set_title('Top Products Performance')
        self.prod_canvas.draw()
    
    def create_cost_efficiency_tab(self):
        """Create cost efficiency analysis tab with improved layout"""
        
        # Main scrollable canvas setup
        canvas = tk.Canvas(self.efficiency_frame, highlightthickness=0, bd=0)
        v_scrollbar = ttk.Scrollbar(self.efficiency_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure Canvas to match the theme background
        def update_canvas_bg():
            try:
                style = ttk.Style()
                bg_color = style.lookup('TFrame', 'background')
                if bg_color:
                    canvas.configure(bg=bg_color)
                else:
                    canvas.configure(bg=self.efficiency_frame.cget('bg'))
            except:
                canvas.configure(bg='SystemButtonFace')
        
        self.efficiency_frame.after(1, update_canvas_bg)
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            if scrollable_frame.winfo_reqwidth() < canvas_width:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        def on_canvas_configure(event):
            configure_scroll_region()
        
        def show_scrollbars():
            v_scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
        
        def hide_scrollbars():
            v_scrollbar.pack_forget()
            canvas.pack(side="left", fill="both", expand=True)
        
        def check_scrollbars():
            canvas.update_idletasks()
            scrollable_frame.update_idletasks()
            
            canvas_height = canvas.winfo_height()
            content_height = scrollable_frame.winfo_reqheight()
            
            if content_height > canvas_height:
                show_scrollbars()
            else:
                hide_scrollbars()
        
        scrollable_frame.bind("<Configure>", lambda e: (configure_scroll_region(), canvas.after(10, check_scrollbars)))
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Initially pack canvas and check for scrollbars
        canvas.pack(side="left", fill="both", expand=True)
        canvas.after(100, check_scrollbars)
        
        # 1. Cost Efficiency Summary (Top)
        summary_frame = ttk.LabelFrame(scrollable_frame, text="💰 Cost Efficiency Summary", padding="15")
        summary_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        self.efficiency_summary = ttk.Label(summary_frame, 
                                           text="Loading cost efficiency metrics...",
                                           font=DashboardConstants.BODY_FONT,
                                           justify='left',
                                           anchor='w')
        self.efficiency_summary.pack(fill='x', pady=5)
        
        # 2. Efficiency Rankings Table (Bottom)
        table_frame = ttk.LabelFrame(scrollable_frame, text="📊 Product Cost Efficiency Rankings", padding="15")
        table_frame.pack(fill='both', expand=False, padx=10, pady=(5, 10))
        
        # Cost efficiency treeview with proper container
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill='both', expand=True)
        
        columns = ('Rank', 'SKU', 'Product', 'Cost', 'Price', 'Profit/Unit', 'Margin %', 'Category', 'Units Sold')
        self.efficiency_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=12)
        
        # Configure columns with better sizing
        self.efficiency_tree.heading('Rank', text='Rank')
        self.efficiency_tree.heading('SKU', text='SKU')
        self.efficiency_tree.heading('Product', text='Product Name')
        self.efficiency_tree.heading('Cost', text='Cost')
        self.efficiency_tree.heading('Price', text='Price')
        self.efficiency_tree.heading('Profit/Unit', text='Profit/Unit')
        self.efficiency_tree.heading('Margin %', text='Margin %')
        self.efficiency_tree.heading('Category', text='Category')
        self.efficiency_tree.heading('Units Sold', text='Units Sold')
        
        # Better column widths for readability
        self.efficiency_tree.column('Rank', width=60, minwidth=50)
        self.efficiency_tree.column('SKU', width=100, minwidth=80)
        self.efficiency_tree.column('Product', width=180, minwidth=150)
        self.efficiency_tree.column('Cost', width=90, minwidth=80)
        self.efficiency_tree.column('Price', width=90, minwidth=80)
        self.efficiency_tree.column('Profit/Unit', width=100, minwidth=90)
        self.efficiency_tree.column('Margin %', width=90, minwidth=80)
        self.efficiency_tree.column('Category', width=120, minwidth=100)
        self.efficiency_tree.column('Units Sold', width=100, minwidth=90)
        
        # Pack treeview and scrollbar properly
        eff_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.efficiency_tree.yview)
        eff_scrollbar.pack(side='right', fill='y')
        self.efficiency_tree.configure(yscrollcommand=eff_scrollbar.set)
        self.efficiency_tree.pack(side='left', fill='both', expand=True)
    
    def get_date_range(self):
        """Get start and end dates based on selected period"""
        end_date = datetime.now()
        
        period = self.period_var.get()
        if period == "Last 7 Days":
            start_date = end_date - timedelta(days=7)
        elif period == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif period == "Last 90 Days":
            start_date = end_date - timedelta(days=90)
        elif period == "Last 6 Months":
            start_date = end_date - timedelta(days=180)
        else:
            start_date = end_date - timedelta(days=30)
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def refresh_performance_data(self):
        """Refresh all performance data with selected date range"""
        try:
            start_date, end_date = self.get_date_range()
            
            # Get employee performance data
            self.performance_data['employees'] = dashboard.get_employee_performance_ranking(start_date, end_date)
            
            # Get product performance data
            self.performance_data['products'] = dashboard.get_product_performance_analysis(start_date, end_date)
            
            # Get cost efficiency data with date range
            self.performance_data['efficiency'] = dashboard.get_cost_efficiency_metrics(start_date, end_date)
            
            # Update all tabs
            self.update_employee_performance()
            self.update_product_performance()
            self.update_cost_efficiency()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh performance data: {str(e)}")
    
    def update_employee_performance(self):
        """Update employee performance tab"""
        # Clear existing data
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        # Populate employee rankings
        employees_data = self.performance_data.get('employees', [])
        for i, emp in enumerate(employees_data, 1):
            # Add rank to employee data for later use
            emp['rank'] = i
            values = (
                i,  # Rank
                emp.get('employee_name', 'N/A'),
                f"{emp.get('total_sales', 0):,}",
                f"${emp.get('total_revenue', 0):,.2f}",
                f"${emp.get('total_profit', 0):,.2f}",
                f"${emp.get('avg_sale_value', 0):,.2f}"
            )
            self.employee_tree.insert('', 'end', values=values, tags=(emp.get('employee_id'),))
    
    def update_product_performance(self):
        """Update product performance tab with rankings"""
        # Clear existing data
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Populate product rankings
        products_data = self.performance_data.get('products', [])
        for i, prod in enumerate(products_data, 1):
            values = (
                i,  # Rank
                prod.get('SKU', 'N/A'),
                prod.get('name', 'N/A'),
                f"{prod.get('total_units_sold', 0):,}",
                f"${prod.get('total_revenue', 0):,.2f}",
                f"${prod.get('total_profit', 0):,.2f}",
                f"${prod.get('avg_selling_price', 0):,.2f}"
            )
            self.product_tree.insert('', 'end', values=values)
        
        # Update product chart
        self.update_product_chart()
    
    def update_cost_efficiency(self):
        """Update cost efficiency tab with rankings and period indicator"""
        # Clear existing data
        for item in self.efficiency_tree.get_children():
            self.efficiency_tree.delete(item)
        
        # Populate efficiency data
        efficiency_data = self.performance_data.get('efficiency', [])
        
        if efficiency_data:
            total_revenue = sum(float(item.get('total_revenue', 0)) for item in efficiency_data)
            total_profit = sum(float(item.get('total_profit', 0)) for item in efficiency_data)
            avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Include the analysis period in the summary
            period = self.period_var.get() if hasattr(self, 'period_var') else "Unknown Period"
            summary_text = f"📊 Analysis Period: {period}  |  Products: {len(efficiency_data)}  |  💰 Revenue: ${total_revenue:,.2f}  |  📈 Profit: ${total_profit:,.2f}  |  📊 Avg Margin: {avg_margin:.1f}%"
            self.efficiency_summary.config(text=summary_text)
            
            # Sort by profit margin for ranking
            sorted_efficiency = sorted(efficiency_data, key=lambda x: float(x.get('profit_margin', 0)), reverse=True)
            
            for i, eff in enumerate(sorted_efficiency, 1):
                values = (
                    i,  # Rank
                    eff.get('SKU', 'N/A'),
                    eff.get('name', 'N/A'),
                    f"${eff.get('cost', 0):,.2f}",
                    f"${eff.get('price', 0):,.2f}",
                    f"${eff.get('profit_per_unit', 0):,.2f}",
                    f"{eff.get('profit_margin', 0):,.1f}%",
                    eff.get('category_name', 'N/A'),
                    f"{eff.get('total_units_sold', 0):,}"
                )
                self.efficiency_tree.insert('', 'end', values=values)
        else:
            period = self.period_var.get() if hasattr(self, 'period_var') else "selected period"
            self.efficiency_summary.config(text=f"No cost efficiency data available for {period} - Please refresh the data")
    
    def update_product_chart(self):
        """Update the product performance chart with better formatting"""
        self.prod_ax.clear()
        
        products_data = self.performance_data.get('products', [])[:8]  # Top 8 for better visibility
        if products_data:
            # Truncate names for better readability
            names = []
            for prod in products_data:
                name = prod.get('name', 'N/A')
                if len(name) > 15:
                    name = name[:12] + '...'
                names.append(name)
            
            revenues = [float(prod.get('total_revenue', 0)) for prod in products_data]
            
            bars = self.prod_ax.bar(range(len(names)), revenues, color='#2E86AB', alpha=0.8)
            self.prod_ax.set_xlabel('Products', fontsize=9)
            self.prod_ax.set_ylabel('Revenue ($)', fontsize=9)
            self.prod_ax.set_title('Top Products by Revenue', fontsize=10)
            self.prod_ax.set_xticks(range(len(names)))
            self.prod_ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
            
            # Add value labels on bars
            for bar, revenue in zip(bars, revenues):
                height = bar.get_height()
                self.prod_ax.text(bar.get_x() + bar.get_width()/2., height,
                                f'${revenue:,.0f}', ha='center', va='bottom', fontsize=7)
            
            # Adjust tick label sizes for smaller chart
            self.prod_ax.tick_params(axis='both', which='major', labelsize=8)
        else:
            self.prod_ax.text(0.5, 0.5, 'No product data available', 
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.prod_ax.transAxes, fontsize=9)
            self.prod_ax.set_title('Product Performance Chart', fontsize=10)
        
        # Use tight layout with padding to fit smaller space
        self.prod_fig.tight_layout(pad=1.0)
        self.prod_canvas.draw()
    
    def on_employee_select(self, event):
        """Handle employee selection in the ranking table"""
        selected_items = self.employee_tree.selection()
        if selected_items:
            item = selected_items[0]
            tags = self.employee_tree.item(item, 'tags')
            if tags:
                self.selected_employee_id = int(tags[0])
                self.update_employee_details()
                self.update_employee_chart()
    
    def update_employee_details(self):
        """Update employee details panel with improved formatting for vertical layout"""
        if not self.selected_employee_id:
            self.employee_details.config(text="Select an employee from the rankings above to view detailed performance metrics")
            return
        
        # Find employee data
        employees_data = self.performance_data.get('employees', [])
        emp_data = next((emp for emp in employees_data if emp.get('employee_id') == self.selected_employee_id), None)
        
        if emp_data:
            # Create a more readable, formatted display for horizontal layout
            emp_name = emp_data.get('employee_name', 'N/A')
            total_sales = emp_data.get('total_sales', 0)
            total_revenue = emp_data.get('total_revenue', 0)
            total_profit = emp_data.get('total_profit', 0)
            avg_sale = emp_data.get('avg_sale_value', 0)
            items_sold = emp_data.get('items_sold', 0)
            rank = emp_data.get('rank', 'N/A')
            
            # Calculate additional metrics
            profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Create horizontal layout text for better readability
            details_text = f"""📊 {emp_name} (Rank #{rank})     💰 Revenue: ${total_revenue:,.2f}  |  Profit: ${total_profit:,.2f} ({profit_margin:.1f}%)     � Sales: {total_sales:,} transactions  |  Items: {items_sold:,}  |  Avg Sale: ${avg_sale:,.2f}"""
            
            self.employee_details.config(text=details_text, justify='left', anchor='w')
        else:
            self.employee_details.config(text="Employee data not found - Please refresh the data", justify='center')
    
    def update_employee_chart(self):
        """Update employee productivity trend chart"""
        if not self.selected_employee_id:
            return
        
        try:
            start_date, end_date = self.get_date_range()
            trends_data = dashboard.get_employee_productivity_trends(self.selected_employee_id, start_date, end_date)
            
            self.emp_ax.clear()
            
            if trends_data:
                dates = [datetime.strptime(item['sale_date'].strftime('%Y-%m-%d'), '%Y-%m-%d') 
                        for item in trends_data]
                revenues = [float(item.get('daily_revenue', 0)) for item in trends_data]
                
                self.emp_ax.plot(dates, revenues, marker='o', linewidth=1.5, markersize=3, color='#2E86AB')
                self.emp_ax.set_xlabel('Date', fontsize=9)
                self.emp_ax.set_ylabel('Daily Revenue ($)', fontsize=9)
                self.emp_ax.set_title(f'Daily Performance - {trends_data[0].get("employee_name", "Employee")}', fontsize=10)
                self.emp_ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                self.emp_ax.grid(True, alpha=0.3)
                
                # Adjust tick label sizes for smaller chart
                self.emp_ax.tick_params(axis='both', which='major', labelsize=8)
                
            else:
                self.emp_ax.text(0.5, 0.5, 'No trend data available', 
                               horizontalalignment='center', verticalalignment='center',
                               transform=self.emp_ax.transAxes, fontsize=9)
                self.emp_ax.set_title('Employee Performance Trend', fontsize=10)
            
            # Use tight layout with padding to fit smaller space
            self.emp_fig.tight_layout(pad=1.0)
            self.emp_canvas.draw()
            
        except Exception as e:
            print(f"Error updating employee chart: {e}")
            # Show error message in chart
            self.emp_ax.clear()
            self.emp_ax.text(0.5, 0.5, f'Error loading chart:\n{str(e)}', 
                           horizontalalignment='center', verticalalignment='center',
                           transform=self.emp_ax.transAxes, fontsize=9)
            self.emp_ax.set_title('Employee Performance Trend', fontsize=10)
            self.emp_canvas.draw()
    
    def refresh_data(self, filters):
        """Override to refresh performance data"""
        self.refresh_performance_data()
