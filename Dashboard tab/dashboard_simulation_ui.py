"""
Dashboard Simulation UI Module
Simulation subtab with what-if analysis and scenario planning tools
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import warnings

# Suppress matplotlib layout warnings for better user experience
warnings.filterwarnings('ignore', message='Tight layout not applied*')

from dashboard_base import DashboardBaseUI, DashboardConstants
import dashboard
import inventory

class SimulationUI(DashboardBaseUI):
    """Simulation subtab - What-if analysis tools"""
    
    def __init__(self, parent, callbacks):
        super().__init__(parent, callbacks)
        self.simulation_data = {}
        self.create_interface()
    
    def create_interface(self):
        """Create the simulation and what-if analysis interface"""
        # Configure treeview style for larger font
        style = ttk.Style()
        style.configure("Simulation.Treeview", font=DashboardConstants.SUBHEADER_FONT)
        style.configure("Simulation.Treeview.Heading", font=DashboardConstants.SUBHEADER_FONT)
        
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, 
                 text="🎲 Business Simulation & What-If Analysis", 
                 font=DashboardConstants.HEADER_FONT).pack(side='left')
        
        # Refresh button
        ttk.Button(header_frame, 
                  text="🔄 Refresh", 
                  command=self.refresh_simulation_data).pack(side='right')
        
        # Notebook for different simulation types
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Price Simulation Tab
        self.price_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.price_frame, text="💰 Price Simulation")
        
        # Inventory Simulation Tab
        self.inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_frame, text="📦 Inventory Scenarios")
        
        # Revenue Forecast Tab
        self.forecast_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forecast_frame, text="📈 Revenue Forecast")
        
        # Optimization Tab
        self.optimization_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.optimization_frame, text="⚡ Optimization")
        
        # Create content for each tab
        self.create_price_simulation_tab()
        self.create_inventory_simulation_tab()
        self.create_forecast_tab()
        self.create_optimization_tab()
    
    def create_price_simulation_tab(self):
        """Create price simulation tab"""
        # Control panel
        control_frame = ttk.LabelFrame(self.price_frame, text="Price Simulation Controls", padding="10")
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Product selection with browse button
        selection_frame = ttk.Frame(control_frame)
        selection_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(selection_frame, text="Product SKU:").pack(side='left', padx=(0, 5))
        self.price_sku_var = tk.StringVar()
        self.price_sku_entry = ttk.Entry(selection_frame, textvariable=self.price_sku_var, width=15)
        self.price_sku_entry.pack(side='left', padx=(0, 5))
        
        # Add auto-uppercase functionality for better UX
        def on_sku_change(*args):
            current_value = self.price_sku_var.get()
            if current_value != current_value.upper():
                cursor_pos = self.price_sku_entry.index(tk.INSERT)
                self.price_sku_var.set(current_value.upper())
                self.price_sku_entry.icursor(cursor_pos)
        
        self.price_sku_var.trace('w', on_sku_change)
        
        ttk.Button(selection_frame, text="Browse Products", 
                  command=self.browse_products).pack(side='left', padx=(0, 5))
        
        ttk.Button(selection_frame, text="Load Product", 
                  command=self.load_product_for_price_simulation).pack(side='left', padx=(0, 20))
        
        # Price scenarios
        scenarios_frame = ttk.Frame(control_frame)
        scenarios_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(scenarios_frame, text="Price Scenarios (comma-separated):").pack(side='left', padx=(0, 5))
        self.price_scenarios_var = tk.StringVar(value="100, 150, 200, 250, 300, 350")
        self.price_scenarios_entry = ttk.Entry(scenarios_frame, textvariable=self.price_scenarios_var, width=40)
        self.price_scenarios_entry.pack(side='left', padx=(0, 10))
        
        ttk.Button(scenarios_frame, text="Run Simulation", 
                  command=self.run_price_simulation).pack(side='left')
        
        # Results display - table only
        results_frame = ttk.LabelFrame(self.price_frame, text="Simulation Results", padding="10")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results table
        table_frame = ttk.Frame(results_frame)
        table_frame.pack(fill='both', expand=True)
        
        columns = ('Price', 'Price Change %', 'Est. Quantity', 'Quantity Change %', 'Est. Revenue', 'Revenue Change', 'Est. Profit', 'Profit Change')
        self.price_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12, style="Simulation.Treeview")
        
        for col in columns:
            self.price_tree.heading(col, text=col)
            self.price_tree.column(col, width=100)
        
        self.price_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        price_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.price_tree.yview)
        self.price_tree.configure(yscrollcommand=price_scrollbar.set)
        price_scrollbar.pack(side='right', fill='y')
    
    def create_inventory_simulation_tab(self):
        """Create inventory simulation tab"""
        # Control panel
        control_frame = ttk.LabelFrame(self.inventory_frame, text="Inventory Simulation Controls", padding="10")
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Instructions with more detail
        instruction_text = ("Enter SKU and new reorder level to simulate inventory impact.\n"
                          "Simulation calculates 60-day costs including carrying costs (25% annual rate) and stockout risks.\n"
                          "Service levels: Excellent (30+ days), Good (14-30), Adequate (7-14), Critical (<7 days)")
        ttk.Label(control_frame, 
                 text=instruction_text,
                 font=DashboardConstants.BODY_FONT,
                 justify='left').pack(pady=(0, 10))
        
        # Simulation entries
        entries_frame = ttk.Frame(control_frame)
        entries_frame.pack(fill='x')
        
        # SKU and reorder level entry
        ttk.Label(entries_frame, text="SKU:").grid(row=0, column=0, padx=(0, 5), sticky='w')
        self.inv_sku_var = tk.StringVar()
        ttk.Entry(entries_frame, textvariable=self.inv_sku_var, width=15).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(entries_frame, text="New Reorder Level:").grid(row=0, column=2, padx=(0, 5), sticky='w')
        self.inv_reorder_var = tk.StringVar()
        ttk.Entry(entries_frame, textvariable=self.inv_reorder_var, width=10).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(entries_frame, text="Add to Simulation", 
                  command=self.add_inventory_scenario).grid(row=0, column=4, padx=(10, 0))
        
        ttk.Button(entries_frame, text="Run Simulation", 
                  command=self.run_inventory_simulation).grid(row=0, column=5, padx=(10, 0))
        
        # Current scenarios display
        scenarios_frame = ttk.LabelFrame(self.inventory_frame, text="Current Scenarios", padding="5")
        scenarios_frame.pack(fill='x', padx=5, pady=5)
        
        self.inventory_scenarios = {}
        
        # Create listbox with theme-matching colors
        self.scenarios_listbox = tk.Listbox(scenarios_frame, height=4,
                                           bg='white',  # Light background
                                           fg='black',  # Dark text
                                           selectbackground=DashboardConstants.PRIMARY_COLOR,  # Selection color
                                           selectforeground='white',  # Selection text color
                                           highlightbackground='#E0E0E0',  # Border when not focused
                                           highlightcolor=DashboardConstants.PRIMARY_COLOR,  # Border when focused
                                           highlightthickness=1,
                                           borderwidth=1,
                                           relief='solid',
                                           font=DashboardConstants.SUBHEADER_FONT)
        self.scenarios_listbox.pack(fill='x', pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(self.inventory_frame, text="Simulation Results", padding="5")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results table with improved columns
        columns = ('SKU', 'Product', 'Current Stock', 'New Reorder', 'Days to Stockout', 'Daily Sales', 'Carrying Cost (60d)', 'Service Level', 'Total Cost')
        self.inventory_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10, style="Simulation.Treeview")
        
        # Configure column headers and widths
        column_config = {
            'SKU': 80,
            'Product': 150,
            'Current Stock': 90,
            'New Reorder': 90,
            'Days to Stockout': 110,
            'Daily Sales': 90,
            'Carrying Cost (60d)': 120,
            'Service Level': 110,
            'Total Cost': 90
        }
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=column_config.get(col, 100))
        
        self.inventory_tree.pack(fill='both', expand=True)
    
    def create_forecast_tab(self):
        """Create revenue forecast tab"""
        # Control panel
        control_frame = ttk.LabelFrame(self.forecast_frame, text="Forecast Controls", padding="10")
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Forecast settings
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(fill='x')
        
        ttk.Label(settings_frame, text="Months to Forecast:").pack(side='left', padx=(0, 5))
        self.forecast_months_var = tk.StringVar(value="6")
        months_spinbox = ttk.Spinbox(settings_frame, from_=1, to=12, width=5, textvariable=self.forecast_months_var)
        months_spinbox.pack(side='left', padx=(0, 20))
        
        ttk.Button(settings_frame, text="Generate Forecast", 
                  command=self.generate_forecast).pack(side='left')
        
        # Forecast display
        display_frame = ttk.LabelFrame(self.forecast_frame, text="Revenue Forecast", padding="5")
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Forecast table
        table_frame = ttk.Frame(display_frame)
        table_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Month', 'Forecasted Revenue', 'Lower Bound', 'Upper Bound', 'Confidence', 'Trend', 'Quality', 'Reliability')
        self.forecast_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Simulation.Treeview")
        
        # Configure column headers and widths
        column_widths = {'Month': 80, 'Forecasted Revenue': 130, 'Lower Bound': 120, 'Upper Bound': 120, 
                        'Confidence': 90, 'Trend': 90, 'Quality': 80, 'Reliability': 90}
        
        for col in columns:
            self.forecast_tree.heading(col, text=col)
            self.forecast_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar to forecast treeview
        forecast_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.forecast_tree.yview)
        self.forecast_tree.configure(yscrollcommand=forecast_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.forecast_tree.pack(side='left', fill='both', expand=True)
        forecast_scrollbar.pack(side='right', fill='y')
    
    def create_optimization_tab(self):
        """Create optimization analysis tab"""
        # Simplified layout without canvas scrolling for better expansion
        main_container = ttk.Frame(self.optimization_frame)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Optimization controls
        control_frame = ttk.LabelFrame(main_container, text="Optimization Analysis", padding="10")
        control_frame.pack(fill='x', pady=(0, 5))
        
        # Category filter
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Category Filter:").pack(side='left', padx=(0, 5))
        self.opt_category_var = tk.StringVar(value="All Categories")
        
        # Get all categories dynamically from database
        try:
            products = inventory.get_all_products()
            categories = sorted(list(set(p.get('category', 'Unknown') for p in products if p.get('category'))))
            category_values = ["All Categories"] + categories
        except Exception:
            category_values = ["All Categories", "Bread", "Buns", "Pasta"]  # Fallback
        
        category_combo = ttk.Combobox(filter_frame, textvariable=self.opt_category_var, 
                                     values=category_values, 
                                     state="readonly", width=20)
        category_combo.pack(side='left', padx=(0, 10))
        
        ttk.Button(filter_frame, text="Analyze Pricing", 
                  command=self.run_pricing_optimization).pack(side='left')
        
        # Optimization summary
        summary_frame = ttk.LabelFrame(main_container, text="Optimization Summary", padding="10")
        summary_frame.pack(fill='x', pady=(0, 5))
        
        self.optimization_summary = ttk.Label(summary_frame, 
                                            text="Run pricing optimization to see summary",
                                            font=("Helvetica", 14, "bold"))
        self.optimization_summary.pack()
        
        # Optimization results - expanded to full width
        results_frame = ttk.LabelFrame(main_container, text="Pricing Optimization Results", padding="5")
        results_frame.pack(fill='both', expand=True)
        
        # Create treeview container with scrollbars
        tree_container = ttk.Frame(results_frame)
        tree_container.pack(fill='both', expand=True)
        
        # Results table with enhanced column widths for full expansion
        columns = ('SKU', 'Product', 'Current Price', 'Recommended Price', 'Price Change %', 'Current Margin %', 'New Margin %', 'Profit Impact', 'Reason')
        self.optimization_tree = ttk.Treeview(tree_container, columns=columns, show='headings', style="Simulation.Treeview")
        
        # Enhanced column configuration for better width distribution
        column_widths = {
            'SKU': 80,
            'Product': 200,
            'Current Price': 110,
            'Recommended Price': 130,
            'Price Change %': 110,
            'Current Margin %': 120,
            'New Margin %': 110,
            'Profit Impact': 120,
            'Reason': 400
        }
        
        for col in columns:
            self.optimization_tree.heading(col, text=col)
            self.optimization_tree.column(col, width=column_widths[col], minwidth=80)
        
        # Add scrollbars for optimization treeview
        opt_v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.optimization_tree.yview)
        opt_h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.optimization_tree.xview)
        self.optimization_tree.configure(yscrollcommand=opt_v_scrollbar.set, xscrollcommand=opt_h_scrollbar.set)
        
        # Pack treeview and scrollbars with proper layout
        self.optimization_tree.grid(row=0, column=0, sticky='nsew')
        opt_v_scrollbar.grid(row=0, column=1, sticky='ns')
        opt_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights for proper expansion
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
    
    def load_product_for_price_simulation(self):
        """Load product data for price simulation"""
        sku = self.price_sku_var.get().strip()
        if not sku:
            messagebox.showwarning("Warning", "Please enter a product SKU")
            return
        
        try:
            # Get product data using case-insensitive search
            products = inventory.get_all_products()
            product = next((p for p in products if p.get('SKU', '').upper() == sku.upper()), None)
            
            if product:
                # Display comprehensive product information
                info_text = (f"Product: {product.get('name', 'N/A')}\n"
                           f"SKU: {product.get('SKU', 'N/A')}\n"
                           f"Current Price: ${product.get('price', 0):.2f}\n"
                           f"Cost: ${product.get('cost', 0):.2f}\n"
                           f"Stock: {product.get('stock', 0)} units\n"
                           f"Category: {product.get('category', 'N/A')}")
                messagebox.showinfo("Product Loaded", info_text)
            else:
                # Provide helpful suggestions
                similar_skus = [p['SKU'] for p in products if sku.upper() in p.get('SKU', '').upper()][:5]
                if similar_skus:
                    suggestion_text = f"No exact match found for SKU: {sku}\n\nSimilar SKUs found:\n" + "\n".join(similar_skus)
                else:
                    suggestion_text = f"No product found with SKU: {sku}\n\nTip: Use the 'Browse Products' button to find available SKUs"
                messagebox.showwarning("Product Not Found", suggestion_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product: {str(e)}")
    
    def run_price_simulation(self):
        """Run price simulation"""
        sku = self.price_sku_var.get().strip()
        scenarios_text = self.price_scenarios_var.get().strip()
        
        if not sku or not scenarios_text:
            messagebox.showwarning("Warning", "Please enter SKU and price scenarios")
            return
        
        try:
            # Parse price scenarios
            price_scenarios = [float(price.strip()) for price in scenarios_text.split(',')]
            
            # Run simulation
            results = dashboard.simulate_price_changes(sku, price_scenarios)
            
            # Clear existing results
            for item in self.price_tree.get_children():
                self.price_tree.delete(item)
            
            # Populate results
            if results:
                for result in results:
                    values = (
                        f"${result.get('scenario_price', 0):.2f}",
                        f"{result.get('price_change_percent', 0):.1f}%",
                        f"{result.get('estimated_quantity', 0):.1f}",
                        f"{result.get('quantity_change_percent', 0):.1f}%",
                        f"${result.get('estimated_revenue', 0):.2f}",
                        f"${result.get('revenue_change', 0):.2f}",
                        f"${result.get('estimated_profit', 0):.2f}",
                        f"${result.get('profit_change', 0):.2f}"
                    )
                    self.price_tree.insert('', 'end', values=values)
                
                messagebox.showinfo("Success", f"Simulation completed for {len(results)} scenarios")
            else:
                messagebox.showinfo("No Results", "No simulation data available for this product")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid price format. Use comma-separated numbers.")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
    
    def add_inventory_scenario(self):
        """Add inventory scenario to simulation"""
        sku = self.inv_sku_var.get().strip()
        reorder_level = self.inv_reorder_var.get().strip()
        
        if not sku or not reorder_level:
            messagebox.showwarning("Warning", "Please enter both SKU and reorder level")
            return
        
        try:
            reorder_int = int(reorder_level)
            self.inventory_scenarios[sku] = reorder_int
            
            # Update scenarios listbox
            self.scenarios_listbox.delete(0, tk.END)
            for sku_key, level in self.inventory_scenarios.items():
                self.scenarios_listbox.insert(tk.END, f"{sku_key}: {level} units")
            
            # Clear entries
            self.inv_sku_var.set("")
            self.inv_reorder_var.set("")
            
        except ValueError:
            messagebox.showerror("Error", "Reorder level must be a number")
    
    def run_inventory_simulation(self):
        """Run inventory simulation"""
        if not self.inventory_scenarios:
            messagebox.showwarning("Warning", "Please add at least one scenario")
            return
        
        try:
            results = dashboard.simulate_inventory_scenarios(self.inventory_scenarios)
            
            # Clear existing results
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
            
            # Populate results with improved formatting
            if results:
                for sku, result in results.items():
                    # Format values for better readability
                    days_to_stockout = result.get('days_until_stockout', 0)
                    if days_to_stockout == float('inf'):
                        days_display = "∞"
                    else:
                        days_display = f"{days_to_stockout:.1f}"
                    
                    daily_sales = result.get('avg_daily_sales', 0)
                    service_level = result.get('service_level', result.get('risk_level', 'Unknown'))
                    
                    values = (
                        sku,
                        result.get('product_name', 'N/A')[:20] + ('...' if len(result.get('product_name', '')) > 20 else ''),
                        f"{result.get('current_stock', 0):,}",
                        f"{result.get('new_reorder_level', 0):,}",
                        days_display,
                        f"{daily_sales:.2f}",
                        f"${result.get('estimated_carrying_cost', 0):.2f}",
                        service_level,
                        f"${result.get('total_estimated_cost', 0):.2f}"
                    )
                    self.inventory_tree.insert('', 'end', values=values)
                
                messagebox.showinfo("Success", f"Simulation completed for {len(results)} products")
            else:
                messagebox.showinfo("No Results", "No simulation data available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Inventory simulation failed: {str(e)}")
    
    def generate_forecast(self):
        """Generate revenue forecast"""
        try:
            months = int(self.forecast_months_var.get())
            results = dashboard.forecast_revenue(months)
            
            # Clear existing results
            for item in self.forecast_tree.get_children():
                self.forecast_tree.delete(item)
            
            # Populate results
            if results:
                for i, result in enumerate(results, 1):
                    values = (
                        f"Month +{i}",
                        f"${result.get('forecasted_revenue', 0):,.0f}",
                        f"${result.get('lower_bound', 0):,.0f}",
                        f"${result.get('upper_bound', 0):,.0f}",
                        f"{result.get('confidence_level', 0)*100:.0f}%",
                        result.get('trend_direction', 'Unknown'),
                        result.get('model_quality', 'N/A'),
                        result.get('data_reliability', 'N/A')
                    )
                    self.forecast_tree.insert('', 'end', values=values)
                
                messagebox.showinfo("Success", f"Forecast generated for {len(results)} months")
            else:
                messagebox.showinfo("No Results", "Insufficient historical data for forecasting")
                
        except Exception as e:
            messagebox.showerror("Error", f"Forecast generation failed: {str(e)}")
    
    def run_pricing_optimization(self):
        """Run pricing optimization analysis"""
        try:
            category = self.opt_category_var.get()
            
            # Get all results first, then filter by category name if needed
            results = dashboard.analyze_optimal_pricing(None)  # Get all categories
            
            # Filter results by category name if not "All Categories"
            if category != "All Categories":
                # Filter results based on the category name from the products
                filtered_results = []
                products = inventory.get_all_products()
                category_skus = {p.get('SKU') for p in products if p.get('category') == category}
                filtered_results = [r for r in results if r.get('sku') in category_skus]
                results = filtered_results
            
            # Clear existing results
            for item in self.optimization_tree.get_children():
                self.optimization_tree.delete(item)
            
            # Populate results
            if results:
                total_profit_impact = 0
                improvements = 0
                
                for result in results:
                    profit_impact = result.get('profit_impact', 0)
                    total_profit_impact += profit_impact
                    if profit_impact > 0:
                        improvements += 1
                    
                    values = (
                        result.get('sku', 'N/A'),
                        result.get('product_name', 'N/A')[:25],  # Allow more space for product name
                        f"${result.get('current_price', 0):.2f}",
                        f"${result.get('recommended_price', 0):.2f}",
                        f"{result.get('price_change_percent', 0):.1f}%",
                        f"{result.get('current_margin_percent', 0):.1f}%",
                        f"{result.get('new_margin_percent', 0):.1f}%",
                        f"${profit_impact:.2f}",
                        result.get('recommendation_reason', 'N/A')  # Show full reason
                    )
                    self.optimization_tree.insert('', 'end', values=values)
                
                # Update summary
                summary_text = f"Analyzed: {len(results)} products | " \
                              f"Potential Improvements: {improvements} | " \
                              f"Total Profit Impact: ${total_profit_impact:.2f}"
                self.optimization_summary.config(text=summary_text)
                
                messagebox.showinfo("Success", f"Optimization analysis completed for {len(results)} products")
            else:
                messagebox.showinfo("No Results", "No optimization data available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Optimization analysis failed: {str(e)}")
    
    def refresh_simulation_data(self):
        """Refresh simulation data"""
        try:
            # Clear all simulation data
            self.simulation_data.clear()
            self.inventory_scenarios.clear()
            
            # Clear all tables
            for tree in [self.price_tree, self.inventory_tree, self.forecast_tree, self.optimization_tree]:
                for item in tree.get_children():
                    tree.delete(item)
            
            # Clear scenarios listbox
            self.scenarios_listbox.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Simulation data refreshed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh simulation data: {str(e)}")
    
    def refresh_data(self, filters):
        """Override to refresh simulation data"""
        pass  # Simulations are run on-demand
    
    def browse_products(self):
        """Open a product browser window"""
        try:
            # Create a new window for product selection
            browse_window = tk.Toplevel(self.parent)
            browse_window.title("Select Product")
            browse_window.geometry("600x400")
            browse_window.transient(self.parent)
            browse_window.grab_set()
            
            # Search frame
            search_frame = ttk.Frame(browse_window)
            search_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Label(search_frame, text="Search:").pack(side='left', padx=(0, 5))
            search_var = tk.StringVar()
            search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
            search_entry.pack(side='left', padx=(0, 10))
            
            def filter_products():
                """Filter products based on search text"""
                search_text = search_var.get().lower()
                for item in product_tree.get_children():
                    product_tree.delete(item)
                
                try:
                    products = inventory.get_all_products()
                    filtered_products = [p for p in products 
                                       if search_text in p.get('name', '').lower() 
                                       or search_text in p.get('SKU', '').lower()
                                       or search_text in p.get('category', '').lower()]
                    
                    for product in filtered_products[:50]:  # Limit to 50 results
                        product_tree.insert('', 'end', values=(
                            product.get('SKU', ''),
                            product.get('name', ''),
                            product.get('category', ''),
                            f"${product.get('price', 0):.2f}",
                            product.get('stock', 0)
                        ))
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load products: {str(e)}")
            
            ttk.Button(search_frame, text="Search", command=filter_products).pack(side='left')
            
            # Products table
            table_frame = ttk.Frame(browse_window)
            table_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            columns = ('SKU', 'Name', 'Category', 'Price', 'Stock')
            product_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15, style="Simulation.Treeview")
            
            for col in columns:
                product_tree.heading(col, text=col)
                if col == 'Name':
                    product_tree.column(col, width=200)
                elif col in ['Category']:
                    product_tree.column(col, width=120)
                else:
                    product_tree.column(col, width=80)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=product_tree.yview)
            h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=product_tree.xview)
            product_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            product_tree.pack(side='left', fill='both', expand=True)
            v_scrollbar.pack(side='right', fill='y')
            h_scrollbar.pack(side='bottom', fill='x')
            
            # Buttons
            button_frame = ttk.Frame(browse_window)
            button_frame.pack(fill='x', padx=10, pady=5)
            
            def select_product():
                """Select the highlighted product"""
                selection = product_tree.selection()
                if selection:
                    item = product_tree.item(selection[0])
                    sku = item['values'][0]
                    self.price_sku_var.set(sku)
                    browse_window.destroy()
                else:
                    messagebox.showwarning("No Selection", "Please select a product")
            
            ttk.Button(button_frame, text="Select", command=select_product).pack(side='right', padx=(5, 0))
            ttk.Button(button_frame, text="Cancel", command=browse_window.destroy).pack(side='right')
            
            # Load initial products
            filter_products()
            
            # Center the window
            browse_window.update_idletasks()
            x = (browse_window.winfo_screenwidth() // 2) - (browse_window.winfo_width() // 2)
            y = (browse_window.winfo_screenheight() // 2) - (browse_window.winfo_height() // 2)
            browse_window.geometry(f"+{x}+{y}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open product browser: {str(e)}")
