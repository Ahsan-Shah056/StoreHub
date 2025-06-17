"""
Dashboard Simulation UI Module
Simulation subtab with what-if analysis and scenario planning tools
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
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
        
        # Product selection
        selection_frame = ttk.Frame(control_frame)
        selection_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(selection_frame, text="Product SKU:").pack(side='left', padx=(0, 5))
        self.price_sku_var = tk.StringVar()
        self.price_sku_entry = ttk.Entry(selection_frame, textvariable=self.price_sku_var, width=15)
        self.price_sku_entry.pack(side='left', padx=(0, 10))
        
        ttk.Button(selection_frame, text="Load Product", 
                  command=self.load_product_for_price_simulation).pack(side='left', padx=(0, 20))
        
        # Price scenarios
        scenarios_frame = ttk.Frame(control_frame)
        scenarios_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(scenarios_frame, text="Price Scenarios (comma-separated):").pack(side='left', padx=(0, 5))
        self.price_scenarios_var = tk.StringVar(value="10.00, 12.50, 15.00, 17.50, 20.00")
        self.price_scenarios_entry = ttk.Entry(scenarios_frame, textvariable=self.price_scenarios_var, width=40)
        self.price_scenarios_entry.pack(side='left', padx=(0, 10))
        
        ttk.Button(scenarios_frame, text="Run Simulation", 
                  command=self.run_price_simulation).pack(side='left')
        
        # Results display
        results_frame = ttk.LabelFrame(self.price_frame, text="Simulation Results", padding="5")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results table
        table_frame = ttk.Frame(results_frame)
        table_frame.pack(fill='both', expand=True)
        
        columns = ('Price', 'Price Change %', 'Est. Quantity', 'Quantity Change %', 'Est. Revenue', 'Revenue Change', 'Est. Profit', 'Profit Change')
        self.price_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.price_tree.heading(col, text=col)
            self.price_tree.column(col, width=100)
        
        self.price_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        price_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.price_tree.yview)
        self.price_tree.configure(yscrollcommand=price_scrollbar.set)
        price_scrollbar.pack(side='right', fill='y')
        
        # Chart
        chart_frame = ttk.LabelFrame(results_frame, text="Revenue vs Price Chart", padding="5")
        chart_frame.pack(fill='x', pady=(10, 0))
        
        self.price_fig, self.price_ax = plt.subplots(figsize=(10, 3))
        self.price_canvas = FigureCanvasTkAgg(self.price_fig, chart_frame)
        self.price_canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_inventory_simulation_tab(self):
        """Create inventory simulation tab"""
        # Control panel
        control_frame = ttk.LabelFrame(self.inventory_frame, text="Inventory Simulation Controls", padding="10")
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Instructions
        ttk.Label(control_frame, 
                 text="Enter SKU and new reorder level to simulate inventory impact:",
                 font=DashboardConstants.BODY_FONT).pack(pady=(0, 10))
        
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
        self.scenarios_listbox = tk.Listbox(scenarios_frame, height=4)
        self.scenarios_listbox.pack(fill='x', pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(self.inventory_frame, text="Simulation Results", padding="5")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results table
        columns = ('SKU', 'Product', 'Current Stock', 'New Reorder', 'Days Until Stockout', 'Carrying Cost', 'Stockout Risk', 'Total Cost')
        self.inventory_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            if col in ['SKU', 'Product']:
                self.inventory_tree.column(col, width=120)
            else:
                self.inventory_tree.column(col, width=100)
        
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
        table_frame.pack(fill='x', pady=(0, 10))
        
        columns = ('Month', 'Forecasted Revenue', 'Lower Bound', 'Upper Bound', 'Confidence', 'Trend')
        self.forecast_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.forecast_tree.heading(col, text=col)
            self.forecast_tree.column(col, width=120)
        
        self.forecast_tree.pack(fill='both', expand=True)
        
        # Forecast chart
        chart_frame = ttk.LabelFrame(display_frame, text="Forecast Visualization", padding="5")
        chart_frame.pack(fill='both', expand=True)
        
        self.forecast_fig, self.forecast_ax = plt.subplots(figsize=(10, 4))
        self.forecast_canvas = FigureCanvasTkAgg(self.forecast_fig, chart_frame)
        self.forecast_canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_optimization_tab(self):
        """Create optimization analysis tab"""
        # Main container with scroll
        canvas = tk.Canvas(self.optimization_frame)
        scrollbar = ttk.Scrollbar(self.optimization_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Optimization controls
        control_frame = ttk.LabelFrame(scrollable_frame, text="Optimization Analysis", padding="10")
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Category filter
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Category Filter:").pack(side='left', padx=(0, 5))
        self.opt_category_var = tk.StringVar(value="All Categories")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.opt_category_var, 
                                     values=["All Categories", "Bread", "Buns", "Pasta"], 
                                     state="readonly", width=15)
        category_combo.pack(side='left', padx=(0, 10))
        
        ttk.Button(filter_frame, text="Analyze Pricing", 
                  command=self.run_pricing_optimization).pack(side='left')
        
        # Optimization results
        results_frame = ttk.LabelFrame(scrollable_frame, text="Pricing Optimization Results", padding="5")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results table
        columns = ('SKU', 'Product', 'Current Price', 'Recommended Price', 'Price Change %', 'Current Margin %', 'New Margin %', 'Profit Impact', 'Reason')
        self.optimization_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.optimization_tree.heading(col, text=col)
            if col in ['Product', 'Reason']:
                self.optimization_tree.column(col, width=150)
            else:
                self.optimization_tree.column(col, width=100)
        
        self.optimization_tree.pack(fill='both', expand=True)
        
        # Optimization summary
        summary_frame = ttk.LabelFrame(scrollable_frame, text="Optimization Summary", padding="10")
        summary_frame.pack(fill='x', padx=5, pady=5)
        
        self.optimization_summary = ttk.Label(summary_frame, 
                                            text="Run pricing optimization to see summary",
                                            font=DashboardConstants.BODY_FONT)
        self.optimization_summary.pack()
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_product_for_price_simulation(self):
        """Load product data for price simulation"""
        sku = self.price_sku_var.get().strip()
        if not sku:
            messagebox.showwarning("Warning", "Please enter a product SKU")
            return
        
        try:
            # Get product data (simplified check)
            products = inventory.get_all_products()
            product = next((p for p in products if p.get('SKU') == sku), None)
            
            if product:
                messagebox.showinfo("Product Loaded", 
                                  f"Product: {product.get('name', 'N/A')}\n"
                                  f"Current Price: ${product.get('price', 0):.2f}")
            else:
                messagebox.showwarning("Product Not Found", f"No product found with SKU: {sku}")
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
                
                self.update_price_chart(results)
                messagebox.showinfo("Success", f"Simulation completed for {len(results)} scenarios")
            else:
                messagebox.showinfo("No Results", "No simulation data available for this product")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid price format. Use comma-separated numbers.")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
    
    def update_price_chart(self, results):
        """Update price simulation chart"""
        self.price_ax.clear()
        
        if results:
            prices = [result['scenario_price'] for result in results]
            revenues = [result['estimated_revenue'] for result in results]
            
            self.price_ax.plot(prices, revenues, marker='o', linewidth=2, markersize=6, color='blue')
            self.price_ax.set_xlabel('Price ($)')
            self.price_ax.set_ylabel('Estimated Revenue ($)')
            self.price_ax.set_title('Revenue vs Price Analysis')
            self.price_ax.grid(True, alpha=0.3)
            
            # Highlight optimal point
            max_revenue_idx = revenues.index(max(revenues))
            self.price_ax.plot(prices[max_revenue_idx], revenues[max_revenue_idx], 
                             marker='*', markersize=12, color='red', label='Max Revenue')
            self.price_ax.legend()
        
        self.price_fig.tight_layout()
        self.price_canvas.draw()
    
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
            
            # Populate results
            if results:
                for sku, result in results.items():
                    values = (
                        sku,
                        result.get('product_name', 'N/A'),
                        f"{result.get('current_stock', 0)}",
                        f"{result.get('new_reorder_level', 0)}",
                        f"{result.get('days_until_stockout', 0):.1f}",
                        f"${result.get('estimated_carrying_cost', 0):.2f}",
                        result.get('risk_level', 'Unknown'),
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
                        f"${result.get('forecasted_revenue', 0):.2f}",
                        f"${result.get('lower_bound', 0):.2f}",
                        f"${result.get('upper_bound', 0):.2f}",
                        f"{result.get('confidence_level', 0)*100:.0f}%",
                        result.get('trend_direction', 'Unknown')
                    )
                    self.forecast_tree.insert('', 'end', values=values)
                
                self.update_forecast_chart(results)
                messagebox.showinfo("Success", f"Forecast generated for {len(results)} months")
            else:
                messagebox.showinfo("No Results", "Insufficient historical data for forecasting")
                
        except Exception as e:
            messagebox.showerror("Error", f"Forecast generation failed: {str(e)}")
    
    def update_forecast_chart(self, results):
        """Update forecast chart"""
        self.forecast_ax.clear()
        
        if results:
            months = list(range(1, len(results) + 1))
            forecasts = [result['forecasted_revenue'] for result in results]
            lower_bounds = [result['lower_bound'] for result in results]
            upper_bounds = [result['upper_bound'] for result in results]
            
            # Plot forecast line
            self.forecast_ax.plot(months, forecasts, marker='o', linewidth=2, color='blue', label='Forecast')
            
            # Plot confidence interval
            self.forecast_ax.fill_between(months, lower_bounds, upper_bounds, alpha=0.3, color='lightblue', label='Confidence Interval')
            
            self.forecast_ax.set_xlabel('Months Ahead')
            self.forecast_ax.set_ylabel('Revenue ($)')
            self.forecast_ax.set_title('Revenue Forecast')
            self.forecast_ax.legend()
            self.forecast_ax.grid(True, alpha=0.3)
        
        self.forecast_fig.tight_layout()
        self.forecast_canvas.draw()
    
    def run_pricing_optimization(self):
        """Run pricing optimization analysis"""
        try:
            category = self.opt_category_var.get()
            category_id = None if category == "All Categories" else 1  # Simplified category mapping
            
            results = dashboard.analyze_optimal_pricing(category_id)
            
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
                        result.get('product_name', 'N/A')[:20],  # Truncate name
                        f"${result.get('current_price', 0):.2f}",
                        f"${result.get('recommended_price', 0):.2f}",
                        f"{result.get('price_change_percent', 0):.1f}%",
                        f"{result.get('current_margin_percent', 0):.1f}%",
                        f"{result.get('new_margin_percent', 0):.1f}%",
                        f"${profit_impact:.2f}",
                        result.get('recommendation_reason', 'N/A')[:30]  # Truncate reason
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
            
            # Clear charts
            for ax in [self.price_ax, self.forecast_ax]:
                ax.clear()
                ax.text(0.5, 0.5, 'Run simulation to view results', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes)
            
            for canvas in [self.price_canvas, self.forecast_canvas]:
                canvas.draw()
            
            messagebox.showinfo("Success", "Simulation data refreshed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh simulation data: {str(e)}")
    
    def refresh_data(self, filters):
        """Override to refresh simulation data"""
        pass  # Simulations are run on-demand
