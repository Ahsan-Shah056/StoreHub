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
        """Create employee performance analysis tab"""
        # Split into left panel (rankings) and right panel (details)
        paned_window = ttk.PanedWindow(self.employee_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Employee rankings
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Employee Rankings", 
                 font=DashboardConstants.SUBHEADER_FONT).pack(pady=(0, 10))
        
        # Employee ranking treeview
        columns = ('Rank', 'Employee', 'Sales', 'Revenue', 'Profit', 'Avg Sale')
        self.employee_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.employee_tree.heading('Rank', text='Rank')
        self.employee_tree.heading('Employee', text='Employee')
        self.employee_tree.heading('Sales', text='Sales Count')
        self.employee_tree.heading('Revenue', text='Revenue')
        self.employee_tree.heading('Profit', text='Profit')
        self.employee_tree.heading('Avg Sale', text='Avg Sale')
        
        # Column widths
        self.employee_tree.column('Rank', width=50)
        self.employee_tree.column('Employee', width=120)
        self.employee_tree.column('Sales', width=80)
        self.employee_tree.column('Revenue', width=100)
        self.employee_tree.column('Profit', width=100)
        self.employee_tree.column('Avg Sale', width=80)
        
        self.employee_tree.pack(fill='both', expand=True)
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_employee_select)
        
        # Scrollbar for employee tree
        emp_scrollbar = ttk.Scrollbar(left_frame, orient='vertical', command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=emp_scrollbar.set)
        emp_scrollbar.pack(side='right', fill='y')
        
        # Right panel - Employee details and trends
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)
        
        # Employee details
        details_frame = ttk.LabelFrame(right_frame, text="Employee Performance Details", padding="10")
        details_frame.pack(fill='x', pady=(0, 10))
        
        self.employee_details = ttk.Label(details_frame, 
                                         text="Select an employee to view detailed performance metrics",
                                         font=DashboardConstants.BODY_FONT)
        self.employee_details.pack()
        
        # Performance trend chart
        chart_frame = ttk.LabelFrame(right_frame, text="Performance Trend", padding="5")
        chart_frame.pack(fill='both', expand=True)
        
        # Create matplotlib figure for employee trends
        self.emp_fig, self.emp_ax = plt.subplots(figsize=(8, 4))
        self.emp_canvas = FigureCanvasTkAgg(self.emp_fig, chart_frame)
        self.emp_canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_product_performance_tab(self):
        """Create product performance analysis tab"""
        # Product performance table
        table_frame = ttk.LabelFrame(self.product_frame, text="Product Performance Rankings", padding="10")
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Product performance treeview
        columns = ('Rank', 'SKU', 'Product', 'Units Sold', 'Revenue', 'Profit', 'Avg Price')
        self.product_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=100 if col != 'Product' else 150)
        
        self.product_tree.pack(fill='both', expand=True)
        
        # Scrollbar for product tree
        prod_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=prod_scrollbar.set)
        prod_scrollbar.pack(side='right', fill='y')
        
        # Product performance chart
        chart_frame = ttk.LabelFrame(self.product_frame, text="Top Products Chart", padding="5")
        chart_frame.pack(fill='x', padx=5, pady=5)
        
        # Create matplotlib figure for product performance
        self.prod_fig, self.prod_ax = plt.subplots(figsize=(10, 3))
        self.prod_canvas = FigureCanvasTkAgg(self.prod_fig, chart_frame)
        self.prod_canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_cost_efficiency_tab(self):
        """Create cost efficiency analysis tab"""
        # Main container with enhanced canvas
        canvas = tk.Canvas(self.efficiency_frame, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self.efficiency_frame, orient="vertical", command=canvas.yview)
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
            
            # Make the canvas window width match the canvas width
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)
            
            # Auto-hide scrollbar when not needed
            canvas_height = canvas.winfo_height()
            content_height = scrollable_frame.winfo_reqheight()
            
            if content_height > canvas_height and canvas_height > 1:
                scrollbar.pack(side="right", fill="y")
            else:
                scrollbar.pack_forget()
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Cost efficiency summary
        summary_frame = ttk.LabelFrame(scrollable_frame, text="Cost Efficiency Summary", padding="10")
        summary_frame.pack(fill='x', padx=5, pady=5)
        
        self.efficiency_summary = ttk.Label(summary_frame, 
                                           text="Loading cost efficiency metrics...",
                                           font=DashboardConstants.BODY_FONT)
        self.efficiency_summary.pack()
        
        # Efficiency table
        table_frame = ttk.LabelFrame(scrollable_frame, text="Product Cost Efficiency", padding="10")
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Cost efficiency treeview
        columns = ('SKU', 'Product', 'Cost', 'Price', 'Profit/Unit', 'Margin %', 'Category', 'Units Sold')
        self.efficiency_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        for col in columns:
            self.efficiency_tree.heading(col, text=col)
            if col == 'Product':
                self.efficiency_tree.column(col, width=150)
            elif col == 'Category':
                self.efficiency_tree.column(col, width=120)
            else:
                self.efficiency_tree.column(col, width=80)
        
        self.efficiency_tree.pack(fill='both', expand=True)
        
        # Scrollbar for efficiency tree
        eff_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.efficiency_tree.yview)
        self.efficiency_tree.configure(yscrollcommand=eff_scrollbar.set)
        eff_scrollbar.pack(side='right', fill='y')
        
        # Pack canvas (scrollbar will be packed dynamically)
        canvas.pack(side="left", fill="both", expand=True)
    
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
        """Refresh all performance data"""
        try:
            start_date, end_date = self.get_date_range()
            
            # Get employee performance data
            self.performance_data['employees'] = dashboard.get_employee_performance_ranking(start_date, end_date)
            
            # Get product performance data
            self.performance_data['products'] = dashboard.get_product_performance_analysis(start_date, end_date)
            
            # Get cost efficiency data
            self.performance_data['efficiency'] = dashboard.get_cost_efficiency_metrics()
            
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
        """Update product performance tab"""
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
        """Update cost efficiency tab"""
        # Clear existing data
        for item in self.efficiency_tree.get_children():
            self.efficiency_tree.delete(item)
        
        # Populate efficiency data
        efficiency_data = self.performance_data.get('efficiency', [])
        
        if efficiency_data:
            total_revenue = sum(float(item.get('total_revenue', 0)) for item in efficiency_data)
            total_profit = sum(float(item.get('total_profit', 0)) for item in efficiency_data)
            avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            summary_text = f"Total Products: {len(efficiency_data)} | " \
                          f"Total Revenue: ${total_revenue:,.2f} | " \
                          f"Total Profit: ${total_profit:,.2f} | " \
                          f"Avg Margin: {avg_margin:.1f}%"
            self.efficiency_summary.config(text=summary_text)
            
            for eff in efficiency_data:
                values = (
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
    
    def update_product_chart(self):
        """Update the product performance chart"""
        self.prod_ax.clear()
        
        products_data = self.performance_data.get('products', [])[:10]  # Top 10
        if products_data:
            names = [prod.get('name', 'N/A')[:20] for prod in products_data]  # Truncate names
            revenues = [float(prod.get('total_revenue', 0)) for prod in products_data]
            
            bars = self.prod_ax.bar(range(len(names)), revenues, color='steelblue', alpha=0.7)
            self.prod_ax.set_xlabel('Products')
            self.prod_ax.set_ylabel('Revenue ($)')
            self.prod_ax.set_title('Top 10 Products by Revenue')
            self.prod_ax.set_xticks(range(len(names)))
            self.prod_ax.set_xticklabels(names, rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, revenue in zip(bars, revenues):
                height = bar.get_height()
                self.prod_ax.text(bar.get_x() + bar.get_width()/2., height,
                                f'${revenue:,.0f}', ha='center', va='bottom', fontsize=8)
        
        self.prod_fig.tight_layout()
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
        """Update employee details panel"""
        if not self.selected_employee_id:
            return
        
        # Find employee data
        employees_data = self.performance_data.get('employees', [])
        emp_data = next((emp for emp in employees_data if emp.get('employee_id') == self.selected_employee_id), None)
        
        if emp_data:
            details_text = f"Employee: {emp_data.get('employee_name', 'N/A')}\n" \
                          f"Total Sales: {emp_data.get('total_sales', 0):,}\n" \
                          f"Total Revenue: ${emp_data.get('total_revenue', 0):,.2f}\n" \
                          f"Total Profit: ${emp_data.get('total_profit', 0):,.2f}\n" \
                          f"Average Sale Value: ${emp_data.get('avg_sale_value', 0):,.2f}\n" \
                          f"Items Sold: {emp_data.get('items_sold', 0):,}"
            
            self.employee_details.config(text=details_text)
    
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
                
                self.emp_ax.plot(dates, revenues, marker='o', linewidth=2, markersize=4, color='green')
                self.emp_ax.set_xlabel('Date')
                self.emp_ax.set_ylabel('Daily Revenue ($)')
                self.emp_ax.set_title(f'Daily Performance Trend - {trends_data[0].get("employee_name", "Employee")}')
                self.emp_ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                self.emp_ax.grid(True, alpha=0.3)
            else:
                self.emp_ax.text(0.5, 0.5, 'No trend data available', 
                               horizontalalignment='center', verticalalignment='center',
                               transform=self.emp_ax.transAxes)
            
            self.emp_fig.tight_layout()
            self.emp_canvas.draw()
            
        except Exception as e:
            print(f"Error updating employee chart: {e}")
    
    def refresh_data(self, filters):
        """Override to refresh performance data"""
        self.refresh_performance_data()
