"""
Dashboard Overview UI Module
Overview subtab with key metrics, quick insights, and live data integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import logging
from dashboard_base import DashboardBaseUI, DashboardConstants, create_metric_card, create_status_indicator

# Get logger instance
logger = logging.getLogger(__name__)

class OverviewUI(DashboardBaseUI):
    """Overview subtab - Enhanced Key metrics and quick insights with live data"""
    
    def __init__(self, parent, callbacks):
        super().__init__(parent, callbacks)
        
        # Import dashboard functions
        try:
            from dashboard import (
                get_sales_summary, get_inventory_value, calculate_profit_margins,
                get_top_products, get_low_stock_analytics, get_recent_activities,
                get_supplier_performance, get_dashboard_summary_fast, 
                get_top_products_fast, get_recent_sales_fast
            )
            self.dashboard_funcs = {
                'get_sales_summary': get_sales_summary,
                'get_inventory_value': get_inventory_value,
                'calculate_profit_margins': calculate_profit_margins,
                'get_top_products': get_top_products,
                'get_low_stock_analytics': get_low_stock_analytics,
                'get_recent_activities': get_recent_activities,
                'get_supplier_performance': get_supplier_performance,
                'get_dashboard_summary_fast': get_dashboard_summary_fast,
                'get_top_products_fast': get_top_products_fast,
                'get_recent_sales_fast': get_recent_sales_fast
            }
        except ImportError as e:
            logger.error(f"Error importing dashboard functions: {e}")
            self.dashboard_funcs = {}
        
        self.create_overview_ui()
        
        # Load initial data with fast functions for quick startup
        default_filters = {
            'start_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),  # Reduced to 7 days for faster initial load
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'employee': 'All Employees',
            'supplier': 'All Suppliers',
            'category': 'All Categories'
        }
        self.refresh_data_fast(default_filters)  # Use fast initial load
    
    def create_overview_ui(self):
        """Create the comprehensive overview interface"""
        
        # Create a main frame container 
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True)
        
        # Main scrollable frame with smart scrollbar that blends with UI
        self.canvas = tk.Canvas(main_frame, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure Canvas to match the theme background
        def update_canvas_bg():
            # Get the background color from the parent frame
            try:
                # Check if canvas still exists and is valid
                if not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
                    return
                    
                # For TTK themes, get the background color
                style = ttk.Style()
                bg_color = style.lookup('TFrame', 'background')
                if bg_color:
                    self.canvas.configure(bg=bg_color)
                else:
                    # Fallback to system default
                    self.canvas.configure(bg=main_frame.cget('bg'))
            except (tk.TclError, AttributeError):
                # Canvas may have been destroyed, ignore silently
                pass
            except Exception as e:
                # Other errors, log but continue
                logger.warning(f"Error updating canvas background: {e}")
                try:
                    self.canvas.configure(bg='SystemButtonFace')
                except:
                    pass
        
        # Update background initially and when theme might change
        try:
            self.parent.after(1, update_canvas_bg)
        except:
            pass
        
        # Configure scrolling with auto-hide scrollbar
        def configure_scroll_region(event=None):
            try:
                # Check if canvas still exists and is valid
                if not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
                    return
                    
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
                # Make the canvas window width match the canvas width
                canvas_width = self.canvas.winfo_width()
                if canvas_width > 1:
                    self.canvas.itemconfig(self.canvas_window, width=canvas_width)
                
                # Auto-hide scrollbar when not needed
                canvas_height = self.canvas.winfo_height()
                content_height = self.scrollable_frame.winfo_reqheight()
                
                if content_height > canvas_height and canvas_height > 1:
                    # Show scrollbar when content exceeds canvas height
                    self.scrollbar.pack(side="right", fill="y")
                else:
                    # Hide scrollbar when content fits
                    self.scrollbar.pack_forget()
            except (tk.TclError, AttributeError):
                # Canvas may have been destroyed, ignore silently
                pass
            except Exception as e:
                # Other errors, log but continue
                logger.warning(f"Error configuring scroll region: {e}")
        
        self.scrollable_frame.bind("<Configure>", configure_scroll_region)
        self.canvas.bind("<Configure>", configure_scroll_region)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas (scrollbar will be packed dynamically)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel to canvas for smooth scrolling
        def _on_mousewheel(event):
            try:
                if hasattr(self, 'scrollbar') and self.scrollbar.winfo_viewable():
                    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except (tk.TclError, AttributeError):
                pass
        
        def _bind_mousewheel(event):
            try:
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
                self.canvas.bind_all("<Button-4>", lambda e: _on_mousewheel(e) if hasattr(self, 'scrollbar') and self.scrollbar.winfo_viewable() else None)
                self.canvas.bind_all("<Button-5>", lambda e: _on_mousewheel(e) if hasattr(self, 'scrollbar') and self.scrollbar.winfo_viewable() else None)
            except (tk.TclError, AttributeError):
                pass
        
        def _unbind_mousewheel(event):
            try:
                self.canvas.unbind_all("<MouseWheel>")
                self.canvas.unbind_all("<Button-4>")
                self.canvas.unbind_all("<Button-5>")
            except (tk.TclError, AttributeError):
                pass
        
        try:
            self.canvas.bind('<Enter>', _bind_mousewheel)
            self.canvas.bind('<Leave>', _unbind_mousewheel)
        except (tk.TclError, AttributeError):
            pass
        
        # Overview header
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        ttk.Label(
            header_frame, 
            text="📈 Business Overview Dashboard", 
            font=DashboardConstants.HEADER_FONT
        ).pack(side=tk.LEFT)
        
        self.last_updated_label = ttk.Label(
            header_frame, 
            text="Last Updated: --", 
            font=DashboardConstants.SMALL_FONT
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
        self.sales_change_label = ttk.Label(self.sales_card, text="-- % change", font=DashboardConstants.SMALL_FONT)
        self.sales_change_label.pack()
        
        # Card 2: Total Orders
        self.orders_card = ttk.LabelFrame(cards_frame, text="📦 Total Orders", **card_style)
        self.orders_card.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        self.orders_value_label = ttk.Label(self.orders_card, text="0", font=("Helvetica", 16, "bold"))
        self.orders_value_label.pack()
        self.orders_change_label = ttk.Label(self.orders_card, text="-- % change", font=DashboardConstants.SMALL_FONT)
        self.orders_change_label.pack()
        
        # Card 3: Total Profit
        self.profit_card = ttk.LabelFrame(cards_frame, text="💎 Total Profit", **card_style)
        self.profit_card.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        
        self.profit_value_label = ttk.Label(self.profit_card, text="$0.00", font=("Helvetica", 16, "bold"))
        self.profit_value_label.pack()
        self.profit_margin_label = ttk.Label(self.profit_card, text="-- % margin", font=DashboardConstants.SMALL_FONT)
        self.profit_margin_label.pack()
        
        # Row 2: Operational metrics
        # Card 4: Inventory Value
        self.inventory_card = ttk.LabelFrame(cards_frame, text="📚 Inventory Value", **card_style)
        self.inventory_card.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        self.inventory_value_label = ttk.Label(self.inventory_card, text="$0.00", font=("Helvetica", 16, "bold"))
        self.inventory_value_label.pack()
        self.inventory_count_label = ttk.Label(self.inventory_card, text="-- products", font=DashboardConstants.SMALL_FONT)
        self.inventory_count_label.pack()
        
        # Card 5: Top Product
        self.top_product_card = ttk.LabelFrame(cards_frame, text="🏆 Top Product", **card_style)
        self.top_product_card.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        self.top_product_name_label = ttk.Label(self.top_product_card, text="--", font=DashboardConstants.SUBHEADER_FONT)
        self.top_product_name_label.pack()
        self.top_product_sales_label = ttk.Label(self.top_product_card, text="-- units sold", font=DashboardConstants.SMALL_FONT)
        self.top_product_sales_label.pack()
        
        # Card 6: Average Profit Margin
        self.avg_margin_card = ttk.LabelFrame(cards_frame, text="📈 Avg Profit Margin", **card_style)
        self.avg_margin_card.grid(row=1, column=2, padx=5, pady=5, sticky='ew')
        
        self.avg_margin_value_label = ttk.Label(self.avg_margin_card, text="0.00%", font=("Helvetica", 16, "bold"))
        self.avg_margin_value_label.pack()
        self.margin_trend_label = ttk.Label(self.avg_margin_card, text="-- trend", font=DashboardConstants.SMALL_FONT)
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
        
        self.avg_order_value_label = ttk.Label(col1_frame, text="Average Order Value: $--", font=DashboardConstants.BODY_FONT)
        self.avg_order_value_label.pack(anchor='w', pady=2)
        
        self.items_sold_today_label = ttk.Label(col1_frame, text="Items Sold Today: --", font=DashboardConstants.BODY_FONT)
        self.items_sold_today_label.pack(anchor='w', pady=2)
        
        self.new_customers_label = ttk.Label(col1_frame, text="New Customers: --", font=DashboardConstants.BODY_FONT)
        self.new_customers_label.pack(anchor='w', pady=2)
        
        # Column 2
        col2_frame = ttk.Frame(stats_frame)
        col2_frame.pack(side=tk.LEFT, fill='both', expand=True)
        
        self.low_stock_count_label = ttk.Label(col2_frame, text="Low Stock Items: --", font=DashboardConstants.BODY_FONT)
        self.low_stock_count_label.pack(anchor='w', pady=2)
        
        self.supplier_performance_label = ttk.Label(col2_frame, text="Supplier Performance: --%", font=DashboardConstants.BODY_FONT)
        self.supplier_performance_label.pack(anchor='w', pady=2)
        
        self.cost_savings_label = ttk.Label(col2_frame, text="Cost Savings Potential: $--", font=DashboardConstants.BODY_FONT)
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
        ttk.Button(actions_frame, text="📤 Export Data", width=12, command=self.export_activities_to_csv).pack(side=tk.LEFT, padx=5)
    
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
            
            # Check if widgets still exist before updating
            if not hasattr(self, 'last_updated_label') or not self.last_updated_label.winfo_exists():
                return
            
            # Update last updated timestamp
            self.last_updated_label.config(text=f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
            
            # Refresh all data sections with error handling
            try:
                self.update_metrics_cards(filters)
            except (tk.TclError, AttributeError) as e:
                logger.warning(f"Metrics cards update skipped - widget may be destroyed: {e}")
            
            try:
                self.update_quick_stats(filters)
            except (tk.TclError, AttributeError) as e:
                logger.warning(f"Quick stats update skipped - widget may be destroyed: {e}")
            
            try:
                self.update_recent_activities(filters)
            except (tk.TclError, AttributeError) as e:
                logger.warning(f"Recent activities update skipped - widget may be destroyed: {e}")
            
            try:
                self.update_insights_section(filters)
            except (tk.TclError, AttributeError) as e:
                logger.warning(f"Insights section update skipped - widget may be destroyed: {e}")
            
        except Exception as e:
            logger.error(f"Error refreshing overview data: {e}")
    
    def export_activities_to_csv(self):
        """Export recent activities tree data to CSV"""
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from automation.data_exporting import export_treeview_to_csv
            export_treeview_to_csv(self.activity_tree, self.parent)
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting activities: {e}")
    
    def refresh_data_fast(self, filters):
        """Fast refresh for initial load using optimized dashboard functions"""
        try:
            self.current_filters = filters
            
            # Check if widgets still exist before updating
            if not hasattr(self, 'last_updated_label') or not self.last_updated_label.winfo_exists():
                return
            
            # Update last updated timestamp
            self.last_updated_label.config(text=f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
            
            # Use fast functions for initial load with error handling
            try:
                self.update_metrics_cards_fast(filters)
            except (tk.TclError, AttributeError) as e:
                logger.warning(f"Fast metrics update skipped - widget may be destroyed: {e}")
            
            try:
                self.update_recent_activities_fast(filters)
            except (tk.TclError, AttributeError) as e:
                logger.warning(f"Fast activities update skipped - widget may be destroyed: {e}")
            
            try:
                self.update_insights_section_fast(filters)
            except (tk.TclError, AttributeError) as e:
                logger.warning(f"Fast insights update skipped - widget may be destroyed: {e}")
            
            # Schedule a complete refresh after 2 seconds to fill in any remaining data
            try:
                self.parent.after(2000, lambda: self.refresh_data(filters))
            except (tk.TclError, AttributeError):
                pass  # Widget may be destroyed, ignore
            
        except Exception as e:
            logger.error(f"Error in fast refresh: {e}")
            # Fallback to regular refresh if fast fails
            try:
                self.refresh_data(filters)
            except:
                pass  # Don't cascade errors
    
    def update_metrics_cards(self, filters):
        """Update the 6 main metrics cards"""
        try:
            if not self.dashboard_funcs:
                return
            
            # Get filter IDs
            employee_id = filters.get('employee_id')
            supplier_id = filters.get('supplier_id')
            category_id = filters.get('category_id')
            
            # Get sales summary with all filters
            sales_summary = self.dashboard_funcs['get_sales_summary'](
                filters['start_date'], filters['end_date'], employee_id, supplier_id, category_id
            )
            
            # Update sales card
            self.sales_value_label.config(text=self.format_currency(sales_summary['total_sales']))
            change_color = DashboardConstants.SUCCESS_COLOR if sales_summary['sales_change'] >= 0 else DashboardConstants.DANGER_COLOR
            self.sales_change_label.config(
                text=f"{sales_summary['sales_change']:+.1f}% vs previous period",
                foreground=change_color
            )
            
            # Update orders card
            self.orders_value_label.config(text=self.format_number(sales_summary['total_orders']))
            change_color = DashboardConstants.SUCCESS_COLOR if sales_summary['orders_change'] >= 0 else DashboardConstants.DANGER_COLOR
            self.orders_change_label.config(
                text=f"{sales_summary['orders_change']:+.1f}% vs previous period",
                foreground=change_color
            )
            
            # Update profit card
            self.profit_value_label.config(text=self.format_currency(sales_summary['total_profit']))
            self.profit_margin_label.config(text=f"{sales_summary['profit_margin']:.1f}% margin")
            
            # Get inventory value
            inventory_data = self.dashboard_funcs['get_inventory_value']()
            
            # Update inventory card
            self.inventory_value_label.config(text=self.format_currency(inventory_data['total_retail_value']))
            self.inventory_count_label.config(text=f"{self.format_number(inventory_data['total_products'])} products")
            
            # Get top product with all filters
            top_products = self.dashboard_funcs['get_top_products'](
                filters['start_date'], filters['end_date'], 1, employee_id, supplier_id, category_id
            )
            
            # Update top product card
            if top_products:
                top_product = top_products[0]
                product_name = top_product['name']
                if len(product_name) > 20:
                    product_name = product_name[:20] + "..."
                self.top_product_name_label.config(text=product_name)
                self.top_product_sales_label.config(text=f"{self.format_number(top_product['units_sold'])} units sold")
            else:
                self.top_product_name_label.config(text="No sales data")
                self.top_product_sales_label.config(text="-- units sold")
            
            # Calculate average profit margin
            profit_margins = self.dashboard_funcs['calculate_profit_margins']()
            if profit_margins:
                avg_margin = sum(p['profit_margin'] for p in profit_margins) / len(profit_margins)
                self.avg_margin_value_label.config(text=self.format_percentage(avg_margin))
                
                # Determine trend
                if avg_margin > 25:
                    trend = "Excellent"
                    trend_color = DashboardConstants.SUCCESS_COLOR
                elif avg_margin > 15:
                    trend = "Good"
                    trend_color = DashboardConstants.INFO_COLOR
                else:
                    trend = "Needs attention"
                    trend_color = DashboardConstants.WARNING_COLOR
                
                self.margin_trend_label.config(text=trend, foreground=trend_color)
            else:
                self.avg_margin_value_label.config(text="0.0%")
                self.margin_trend_label.config(text="No data")
            
        except Exception as e:
            logger.error(f"Error updating metrics cards: {e}")
    
    def update_metrics_cards_fast(self, filters):
        """Update metrics cards using fast dashboard functions"""
        try:
            if not self.dashboard_funcs or 'get_dashboard_summary_fast' not in self.dashboard_funcs:
                # Fallback to regular update if fast functions not available
                self.update_metrics_cards(filters)
                return
            
            # Get fast summary data
            summary = self.dashboard_funcs['get_dashboard_summary_fast'](
                filters['start_date'], filters['end_date']
            )
            
            # Update sales card
            self.sales_value_label.config(text=self.format_currency(summary.get('total_sales', 0)))
            
            # Calculate sales trend (simplified)
            try:
                sales_change = summary.get('sales_change', 0)
                if sales_change > 0:
                    trend_text = f"↗️ +{sales_change:.1f}% vs last period"
                    trend_color = DashboardConstants.SUCCESS_COLOR
                elif sales_change < 0:
                    trend_text = f"↘️ {sales_change:.1f}% vs last period"
                    trend_color = DashboardConstants.DANGER_COLOR
                else:
                    trend_text = "→ No change vs last period"
                    trend_color = DashboardConstants.TEXT_COLOR
                    
                self.sales_change_label.config(text=trend_text, foreground=trend_color)
            except:
                self.sales_change_label.config(text="→ Trend data unavailable", foreground=DashboardConstants.TEXT_COLOR)
            
            # Update orders card
            self.orders_value_label.config(text=self.format_number(summary.get('total_orders', 0)))
            
            # Calculate orders trend (simplified)
            try:
                orders_change = summary.get('orders_change', 0)
                if orders_change > 0:
                    trend_text = f"↗️ +{orders_change:.1f}% vs last period"
                    trend_color = DashboardConstants.SUCCESS_COLOR
                elif orders_change < 0:
                    trend_text = f"↘️ {orders_change:.1f}% vs last period"
                    trend_color = DashboardConstants.DANGER_COLOR
                else:
                    trend_text = "→ No change vs last period"
                    trend_color = DashboardConstants.TEXT_COLOR
                    
                self.orders_change_label.config(text=trend_text, foreground=trend_color)
            except:
                self.orders_change_label.config(text="→ Trend data unavailable", foreground=DashboardConstants.TEXT_COLOR)
            
            # Update profit card - calculate actual profit
            try:
                profit_data = self.dashboard_funcs['calculate_profit_margins']()
                if profit_data:
                    total_profit = sum(float(p.get('profit', 0)) for p in profit_data)
                    avg_margin = sum(float(p.get('profit_margin', 0)) for p in profit_data) / len(profit_data) if profit_data else 0
                    
                    self.profit_value_label.config(text=self.format_currency(total_profit))
                    self.profit_margin_label.config(text=f"Avg: {avg_margin:.1f}%")
                else:
                    self.profit_value_label.config(text="$0.00")
                    self.profit_margin_label.config(text="Avg: 0.0%")
            except Exception as e:
                logger.error(f"Error calculating profit: {e}")
                self.profit_value_label.config(text="$0.00")
                self.profit_margin_label.config(text="No data")
            
            # Get inventory value (this is already fast)
            inventory_data = self.dashboard_funcs['get_inventory_value']()
            
            # Update inventory card
            self.inventory_value_label.config(text=self.format_currency(inventory_data['total_retail_value']))
            self.inventory_count_label.config(text=f"{self.format_number(inventory_data['total_products'])} products")
            
            # Get top product using fast function
            top_products = self.dashboard_funcs['get_top_products_fast'](
                filters['start_date'], filters['end_date'], 1
            )
            
            # Update top product card
            if top_products:
                top_product = top_products[0]
                product_name = top_product['name']
                if len(product_name) > 20:
                    product_name = product_name[:20] + "..."
                self.top_product_name_label.config(text=product_name)
                self.top_product_sales_label.config(text=f"{self.format_number(top_product['units_sold'])} units sold")
            else:
                self.top_product_name_label.config(text="No sales data")
                self.top_product_sales_label.config(text="-- units sold")
            
            # Calculate actual average margin and trend
            try:
                profit_data = self.dashboard_funcs['calculate_profit_margins']()
                if profit_data:
                    avg_margin = sum(float(p.get('profit_margin', 0)) for p in profit_data) / len(profit_data) if profit_data else 0
                    
                    # Calculate trend (simplified - compare to historical data)
                    trend_indicator = "↗️" if avg_margin > 10 else "↘️" if avg_margin < 5 else "→"
                    trend_color = DashboardConstants.SUCCESS_COLOR if avg_margin > 10 else DashboardConstants.DANGER_COLOR if avg_margin < 5 else DashboardConstants.TEXT_COLOR
                    
                    self.avg_margin_value_label.config(text=f"{avg_margin:.1f}%")
                    self.margin_trend_label.config(text=f"{trend_indicator} Margin trend", foreground=trend_color)
                else:
                    self.avg_margin_value_label.config(text="0.0%")
                    self.margin_trend_label.config(text="→ No data", foreground=DashboardConstants.TEXT_COLOR)
            except Exception as e:
                logger.error(f"Error calculating margin: {e}")
                self.avg_margin_value_label.config(text="0.0%")
                self.margin_trend_label.config(text="→ No data", foreground=DashboardConstants.TEXT_COLOR)
            
        except Exception as e:
            logger.error(f"Error updating metrics cards fast: {e}")
            # Fallback to regular update
            self.update_metrics_cards(filters)
    
    def update_quick_stats(self, filters):
        """Update quick statistics panel"""
        try:
            if not self.dashboard_funcs:
                return
            
            # Get filter IDs
            employee_id = filters.get('employee_id')
            supplier_id = filters.get('supplier_id')
            category_id = filters.get('category_id')
            
            # Get sales summary for additional stats with all filters
            sales_summary = self.dashboard_funcs['get_sales_summary'](
                filters['start_date'], filters['end_date'], employee_id, supplier_id, category_id
            )
            
            # Update average order value
            self.avg_order_value_label.config(text=f"Average Order Value: {self.format_currency(sales_summary['avg_order_value'])}")
            
            # Update items sold today
            today = datetime.now().strftime('%Y-%m-%d')
            today_summary = self.dashboard_funcs['get_sales_summary'](today, today)
            self.items_sold_today_label.config(text=f"Items Sold Today: {self.format_number(today_summary['total_items_sold'])}")
            
            # Mock new customers (would need actual customer tracking)
            self.new_customers_label.config(text="New Customers: --")
            
            # Get low stock count
            low_stock_items = self.dashboard_funcs['get_low_stock_analytics']()
            low_stock_value = sum(item['reorder_cost'] for item in low_stock_items) if low_stock_items else 0
            self.low_stock_count_label.config(text=f"Low Stock Items: {len(low_stock_items)} ({self.format_currency(low_stock_value)})")
            
            # Get supplier performance
            supplier_performance = self.dashboard_funcs['get_supplier_performance']()
            if supplier_performance:
                avg_delivery_rate = sum(s['delivery_success_rate'] for s in supplier_performance) / len(supplier_performance)
                self.supplier_performance_label.config(text=f"Supplier Performance: {self.format_percentage(avg_delivery_rate)}")
            else:
                self.supplier_performance_label.config(text="Supplier Performance: --%")
            
            # Calculate cost savings potential (simplified)
            inventory_data = self.dashboard_funcs['get_inventory_value']()
            potential_savings = float(inventory_data['potential_profit']) * 0.1  # 10% optimization potential
            self.cost_savings_label.config(text=f"Cost Savings Potential: {self.format_currency(potential_savings)}")
            
        except Exception as e:
            logger.error(f"Error updating quick stats: {e}")
    
    def update_recent_activities(self, filters):
        """Update recent activities feed"""
        try:
            if not self.dashboard_funcs:
                return
            
            # Clear existing items
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            # Get filter IDs
            employee_id = filters.get('employee_id')
            supplier_id = filters.get('supplier_id')
            category_id = filters.get('category_id')
            
            # Get recent activities with all filters
            activities = self.dashboard_funcs['get_recent_activities'](10, employee_id, supplier_id, category_id)
            
            for activity in activities:
                # Format the data
                time_str = activity['sale_datetime'].strftime('%m/%d %H:%M') if hasattr(activity['sale_datetime'], 'strftime') else str(activity['sale_datetime'])[:16]
                amount_str = self.format_currency(activity['sale_total'])
                profit_str = self.format_currency(activity['transaction_profit']) if activity['transaction_profit'] else "$0.00"
                margin_str = self.format_percentage(activity['profit_margin']) if activity['profit_margin'] else "0.0%"
                
                self.activity_tree.insert('', 'end', values=(
                    time_str,
                    'Sale',
                    amount_str,
                    activity['employee_name'],
                    profit_str,
                    margin_str
                ))
            
        except Exception as e:
            logger.error(f"Error updating recent activities: {e}")
    
    def update_recent_activities_fast(self, filters):
        """Update recent activities using fast function"""
        try:
            if not self.dashboard_funcs or 'get_recent_sales_fast' not in self.dashboard_funcs:
                # Fallback to regular update if fast functions not available
                self.update_recent_activities(filters)
                return
            
            # Clear existing items
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            # Get recent sales using fast function
            activities = self.dashboard_funcs['get_recent_sales_fast'](10)
            
            for activity in activities:
                # Format the data
                time_str = activity['sale_datetime'].strftime('%m/%d %H:%M') if hasattr(activity['sale_datetime'], 'strftime') else str(activity['sale_datetime'])[:16]
                amount_str = self.format_currency(activity['total'])
                
                # Calculate profit and margin if data is available
                try:
                    profit = float(activity.get('profit', 0))
                    margin = float(activity.get('profit_margin', 0))
                    profit_str = self.format_currency(profit) if profit > 0 else "$0.00"
                    margin_str = f"{margin:.1f}%" if margin > 0 else "0.0%"
                except (ValueError, TypeError):
                    profit_str = "$0.00"
                    margin_str = "0.0%"
                
                self.activity_tree.insert('', 'end', values=(
                    time_str,
                    'Sale',
                    amount_str,
                    activity['employee_name'],
                    profit_str,
                    margin_str
                ))
            
        except Exception as e:
            logger.error(f"Error updating recent activities fast: {e}")
            # Fallback to regular update
            self.update_recent_activities(filters)
    
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
                        f"   Units: {self.format_number(product['units_sold'])}\n"
                        f"   Revenue: {self.format_currency(product['revenue'])}\n"
                        f"   Profit: {self.format_currency(product['profit'])}\n\n"
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
                        f"• {product['name']}: {self.format_percentage(product['profit_margin'])}\n"
                    )
                if len(low_margin_products) > 3:
                    self.alerts_text.insert(tk.END, f"• ... and {len(low_margin_products) - 3} more\n")
                self.alerts_text.insert(tk.END, "\n")
                alerts_count += len(low_margin_products)
            
            if alerts_count == 0:
                self.alerts_text.insert(tk.END, "✅ All systems operating normally!\n\nNo critical alerts at this time.")
            
        except Exception as e:
            logger.error(f"Error updating insights section: {e}")
    
    def update_insights_section_fast(self, filters):
        """Update insights using fast functions"""
        try:
            if not self.dashboard_funcs or 'get_top_products_fast' not in self.dashboard_funcs:
                # Fallback to regular update if fast functions not available
                self.update_insights_section(filters)
                return
            
            # Update top products
            self.top_products_text.delete(1.0, tk.END)
            top_products = self.dashboard_funcs['get_top_products_fast'](
                filters['start_date'], filters['end_date'], 5
            )
            
            if top_products:
                self.top_products_text.insert(tk.END, "🏆 TOP PERFORMERS:\n\n")
                for i, product in enumerate(top_products, 1):
                    self.top_products_text.insert(tk.END, 
                        f"{i}. {product['name']}\n"
                        f"   Units: {self.format_number(product['units_sold'])}\n"
                        f"   Revenue: {self.format_currency(product['revenue'])}\n\n"
                    )
            else:
                self.top_products_text.insert(tk.END, "No sales data for selected period.")
            
            # Update alerts with actual low stock data
            self.alerts_text.delete(1.0, tk.END)
            
            try:
                # Get low stock alerts
                low_stock_data = self.dashboard_funcs['get_low_stock_analytics']()
                
                if low_stock_data:
                    self.alerts_text.insert(tk.END, "⚠️ STOCK ALERTS:\n\n")
                    
                    alert_count = 0
                    for item in low_stock_data:
                        if alert_count >= 5:  # Limit to 5 alerts for display
                            break
                        
                        stock_level = item.get('stock_quantity', 0)
                        min_stock = item.get('min_stock_level', 0)
                        
                        if stock_level <= min_stock:
                            self.alerts_text.insert(tk.END, 
                                f"🔴 {item.get('name', 'Unknown Product')}\n"
                                f"   Stock: {stock_level} (Min: {min_stock})\n"
                                f"   Action: Reorder needed\n\n"
                            )
                            alert_count += 1
                    
                    if alert_count == 0:
                        self.alerts_text.insert(tk.END, "✅ All items are adequately stocked!\n\n")
                        
                        # Show performance insights instead
                        try:
                            profit_data = self.dashboard_funcs['calculate_profit_margins']()
                            if profit_data:
                                avg_margin = sum(float(p.get('profit_margin', 0)) for p in profit_data) / len(profit_data)
                                self.alerts_text.insert(tk.END, f"📈 INSIGHTS:\n\n")
                                self.alerts_text.insert(tk.END, f"• Average profit margin: {avg_margin:.1f}%\n")
                                
                                # Find best performing product
                                best_product = max(profit_data, key=lambda x: float(x.get('profit_margin', 0)))
                                self.alerts_text.insert(tk.END, f"• Best margin: {best_product.get('name', 'N/A')[:20]} ({float(best_product.get('profit_margin', 0)):.1f}%)\n")
                        except:
                            pass
                            
                else:
                    self.alerts_text.insert(tk.END, "📊 SYSTEM STATUS:\n\n")
                    self.alerts_text.insert(tk.END, "✅ Dashboard operational\n")
                    self.alerts_text.insert(tk.END, "✅ Data connection active\n")
                    self.alerts_text.insert(tk.END, "✅ All systems normal\n")
                    
            except Exception as e:
                logger.error(f"Error getting alerts: {e}")
                self.alerts_text.insert(tk.END, "📊 SYSTEM STATUS:\n\n")
                self.alerts_text.insert(tk.END, "✅ Dashboard operational\n")
                self.alerts_text.insert(tk.END, "ℹ️ Loading stock data...\n")
            
        except Exception as e:
            logger.error(f"Error updating insights section fast: {e}")
            # Fallback to regular update
            self.update_insights_section(filters)

    # Quick action methods
    def open_new_sale(self):
        """Open new sale interface"""
        if 'navigate_to_sales' in self.callbacks:
            self.callbacks['navigate_to_sales']()
        else:
            self.show_info("Quick Action", "Sales navigation not available")
    
    def open_add_product(self):
        """Open add product interface"""
        if 'navigate_to_inventory' in self.callbacks:
            self.callbacks['navigate_to_inventory']()
        else:
            self.show_info("Quick Action", "Inventory navigation not available")
    
    def open_reports(self):
        """Open reports interface"""
        if 'navigate_to_reports' in self.callbacks:
            self.callbacks['navigate_to_reports']()
        else:
            self.show_info("Quick Action", "Reports navigation not available")
    
    def show_low_stock(self):
        """Show low stock alert details"""
        if not self.dashboard_funcs:
            self.show_info("Low Stock", "Dashboard functions not available")
            return
        
        try:
            low_stock_items = self.dashboard_funcs['get_low_stock_analytics']()
            if low_stock_items:
                alert_window = tk.Toplevel(self.parent)
                alert_window.title("Low Stock Alert")
                alert_window.geometry("600x400")
                
                ttk.Label(alert_window, text="⚠️ Low Stock Items", font=DashboardConstants.HEADER_FONT).pack(pady=10)
                
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
                        self.format_currency(item['reorder_cost'])
                    ))
                
                tree.pack(fill='both', expand=True, padx=10, pady=5)
                ttk.Button(alert_window, text="Close", command=alert_window.destroy).pack(pady=10)
            else:
                self.show_info("Low Stock", "No items are currently below their stock thresholds!")
        except Exception as e:
            self.show_error("Error", f"Error loading low stock data: {e}")
    
    def show_supplier_analysis(self):
        """Show supplier performance analysis"""
        if 'navigate_to_suppliers' in self.callbacks:
            self.callbacks['navigate_to_suppliers']()
        else:
            # Show actual supplier analysis instead of placeholder
            try:
                supplier_data = self.dashboard_funcs['get_supplier_performance']()
                if supplier_data:
                    analysis_text = "📊 SUPPLIER PERFORMANCE:\n\n"
                    for i, supplier in enumerate(supplier_data[:5], 1):
                        analysis_text += f"{i}. {supplier.get('supplier_name', 'N/A')}\n"
                        analysis_text += f"   Delivery Rate: {self.format_percentage(supplier.get('delivery_success_rate', 0))}\n"
                        analysis_text += f"   Products: {supplier.get('products_supplied', 0)}\n\n"
                    
                    self.show_info("Supplier Analysis", analysis_text)
                else:
                    self.show_info("Supplier Analysis", "No supplier performance data available")
            except Exception as e:
                self.show_info("Supplier Analysis", f"Error loading supplier data: {e}")
    
    def show_cost_review(self):
        """Show cost review analysis"""
        if 'navigate_to_inventory' in self.callbacks:
            self.callbacks['navigate_to_inventory']()
        else:
            # Show actual cost analysis instead of placeholder
            try:
                inventory_data = self.dashboard_funcs['get_inventory_value']()
                profit_data = self.dashboard_funcs['calculate_profit_margins']()
                
                analysis_text = "💰 COST ANALYSIS:\n\n"
                analysis_text += f"Total Inventory Value: {self.format_currency(inventory_data.get('total_retail_value', 0))}\n"
                analysis_text += f"Total Cost Value: {self.format_currency(inventory_data.get('total_cost_value', 0))}\n\n"
                
                if profit_data:
                    # Find products with low margins
                    low_margin_products = [p for p in profit_data if float(p.get('profit_margin', 0)) < 15]
                    if low_margin_products:
                        analysis_text += "⚠️ LOW MARGIN PRODUCTS:\n"
                        for product in low_margin_products[:3]:
                            analysis_text += f"• {product.get('name', 'N/A')[:25]}: {self.format_percentage(product.get('profit_margin', 0))}\n"
                        
                        if len(low_margin_products) > 3:
                            analysis_text += f"• ... and {len(low_margin_products) - 3} more\n"
                    else:
                        analysis_text += "✅ All products have healthy margins!\n"
                
                self.show_info("Cost Review", analysis_text)
            except Exception as e:
                self.show_info("Cost Review", f"Error loading cost data: {e}")
