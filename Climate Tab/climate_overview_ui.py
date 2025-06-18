"""
Climate Overview UI Module
Enhanced overview subtab with detailed material status and metrics (no charts)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

# Import climate components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from climate_base import ClimateBaseUI, ClimateConstants, create_material_status_card, create_risk_indicator
import climate_data

class ClimateOverviewUI(ClimateBaseUI):
    """Enhanced Climate Overview subtab"""
    
    def __init__(self, parent, callbacks):
        super().__init__(parent, callbacks)
        self.climate_manager = climate_data.climate_manager
        self.create_interface()
    
    def create_interface(self):
        """Create the enhanced overview interface with improved layout"""
        # Create main scrollable frame without separate canvas/scrollbar to prevent white space
        # Use a simpler approach that fills the entire parent
        
        # Main content frame that fills the parent
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True)
        
        # Create scrollable text widget for main content (better than canvas approach)
        # This eliminates the white space issue entirely
        self.main_container = tk.Frame(main_frame, bg='white')
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header section with better styling
        self.create_enhanced_header_section(self.main_container)
        
        # Quick stats dashboard
        self.create_quick_stats_dashboard(self.main_container)
        
        # Material status cards with improved design
        self.create_enhanced_status_cards_section(self.main_container)
        
        # Detailed information with collapsible design (remove analytics)
        self.create_collapsible_details_section(self.main_container)
        
        # Load initial data
        self.refresh_data()
        
        # Make sure the main container updates its size properly
        self.main_container.update_idletasks()

    def create_enhanced_header_section(self, parent):
        """Create an enhanced header with modern styling and key metrics"""
        # Main header frame with modern styling
        header_frame = ttk.LabelFrame(parent, text="🌍 Climate Risk Dashboard", padding="15")
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Top row - Overall status and last update
        top_row = ttk.Frame(header_frame)
        top_row.pack(fill='x', pady=(0, 15))
        
        # Overall risk indicator
        risk_frame = ttk.Frame(top_row)
        risk_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(risk_frame, text="Overall Risk Level:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w')
        self.overall_risk_label = ttk.Label(risk_frame, text="LOADING...", 
                                          font=('Arial', 14, 'bold'),
                                          foreground='blue')
        self.overall_risk_label.pack(anchor='w', pady=(2, 0))
        
        # Last update time
        update_frame = ttk.Frame(top_row)
        update_frame.pack(side='right')
        
        ttk.Label(update_frame, text="Last Updated:", 
                 font=('Arial', 9)).pack(anchor='e')
        self.last_update_label = ttk.Label(update_frame, 
                                         text=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                         font=('Arial', 9, 'bold'))
        self.last_update_label.pack(anchor='e')
        
        # Separator
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.pack(fill='x', pady=(0, 15))
        
        # Bottom row - Key metrics in a grid
        metrics_frame = ttk.Frame(header_frame)
        metrics_frame.pack(fill='x')
        
        # Configure grid weights
        for i in range(4):
            metrics_frame.columnconfigure(i, weight=1)
        
        # Create metric cards
        self.create_metric_card(metrics_frame, "Materials Monitored", "0", "📊", 0, 0)
        self.create_metric_card(metrics_frame, "High Risk Materials", "0", "⚠️", 0, 1)
        self.create_metric_card(metrics_frame, "Average Delay", "0%", "⏱️", 0, 2)
        self.create_metric_card(metrics_frame, "Production Impact", "0", "📉", 0, 3)

    def create_metric_card(self, parent, title, value, icon, row, col):
        """Create a metric card with icon and value"""
        card_frame = ttk.LabelFrame(parent, text="", padding="12")
        card_frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew', ipadx=8, ipady=8)
        
        # Icon and title row with better styling
        title_frame = ttk.Frame(card_frame)
        title_frame.pack(fill='x')
        
        # Large icon
        icon_label = ttk.Label(title_frame, text=icon, font=('Arial', 18))
        icon_label.pack(side='left')
        
        # Title with better formatting
        title_label = ttk.Label(title_frame, text=title, font=('Arial', 9, 'bold'), 
                               foreground='#666666')
        title_label.pack(side='left', padx=(8, 0))
        
        # Value with enhanced styling
        value_label = ttk.Label(card_frame, text=value, font=('Arial', 16, 'bold'),
                               foreground='#2c3e50')
        value_label.pack(pady=(8, 0))
        
        # Store reference for updates
        setattr(self, f"{title.lower().replace(' ', '_')}_value_label", value_label)

    def create_quick_stats_dashboard(self, parent):
        """Create a quick stats dashboard with visual indicators"""
        stats_frame = ttk.LabelFrame(parent, text="📈 Quick Statistics", padding="15")
        stats_frame.pack(fill='x', pady=(0, 15))
        
        # Create a grid for stats
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        # Configure grid
        for i in range(3):
            stats_grid.columnconfigure(i, weight=1)
        
        # Production Status
        self.create_status_indicator(stats_grid, "Production Status", "🏭", 0, 0)
        
        # Weather Conditions
        self.create_status_indicator(stats_grid, "Weather Conditions", "🌤️", 0, 1)
        
        # Supply Chain Health
        self.create_status_indicator(stats_grid, "Supply Chain Health", "🚛", 0, 2)

    def create_status_indicator(self, parent, title, icon, row, col):
        """Create a status indicator with traffic light system"""
        indicator_frame = ttk.LabelFrame(parent, text=f"{icon} {title}", padding="12")
        indicator_frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
        
        # Status circle container
        status_frame = ttk.Frame(indicator_frame)
        status_frame.pack(pady=(5, 0))
        
        # Create colored canvas for status indicator with better size
        status_canvas = tk.Canvas(status_frame, width=40, height=40, highlightthickness=0, 
                                 bg='white', relief='flat')
        status_canvas.pack()
        
        # Store reference for updates
        setattr(self, f"{title.lower().replace(' ', '_')}_canvas", status_canvas)
        
        # Status text with better styling
        status_label = ttk.Label(indicator_frame, text="Checking...", 
                               font=('Arial', 10, 'bold'), foreground='#34495e')
        status_label.pack(pady=(8, 0))
        
        # Store reference for updates
        setattr(self, f"{title.lower().replace(' ', '_')}_label", status_label)

    def create_enhanced_status_cards_section(self, parent):
        """Create enhanced material status cards with better design"""
        cards_frame = ttk.LabelFrame(parent, text="🎯 Material Status Overview", padding="15")
        cards_frame.pack(fill='x', pady=(0, 15))
        
        # Cards container with responsive grid
        self.cards_container = ttk.Frame(cards_frame)
        self.cards_container.pack(fill='x')
        
        # Configure grid to be responsive
        for i in range(2):  # 2 columns for better layout
            self.cards_container.columnconfigure(i, weight=1)

    def create_collapsible_details_section(self, parent):
        """Create a collapsible detailed information section"""
        # Details frame with expand/collapse functionality
        self.details_main_frame = ttk.LabelFrame(parent, text="📋 Detailed Climate Data", padding="15")
        self.details_main_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Header with expand/collapse button
        details_header = ttk.Frame(self.details_main_frame)
        details_header.pack(fill='x', pady=(0, 15))
        
        # Expand/collapse state
        self.details_expanded = tk.BooleanVar(value=True)
        self.expand_btn = ttk.Button(details_header, text="▼ Hide Details", 
                                   command=self.toggle_details_section,
                                   style="Accent.TButton")
        self.expand_btn.pack(side='right')
        
        # Description label
        ttk.Label(details_header, text="Complete material data with real-time updates",
                 font=('Arial', 10, 'italic'), foreground='#7f8c8d').pack(side='left')
        
        # Details content frame with better organization
        self.details_content_frame = ttk.Frame(self.details_main_frame)
        self.details_content_frame.pack(fill='both', expand=True)
        
        # Enhanced treeview with modern styling
        columns = ('Material', 'Status', 'Condition', 'Category', 'Impact', 'Risk', 'Updated')
        self.details_tree = ttk.Treeview(self.details_content_frame, columns=columns, 
                                       show='headings', height=10, style="Treeview")
        
        # Configure columns with appropriate widths and modern headings
        column_config = {
            'Material': (100, 'Material Name'),
            'Status': (70, 'Status'),
            'Condition': (250, 'Current Condition'),
            'Category': (120, 'Category'),
            'Impact': (90, 'Impact (Units)'),
            'Risk': (80, 'Risk Level'),
            'Updated': (130, 'Last Updated')
        }
        
        for col, (width, heading) in column_config.items():
            self.details_tree.heading(col, text=heading, anchor='w')
            self.details_tree.column(col, width=width, minwidth=60, anchor='w')
        
        # Configure alternating row colors and risk-based styling
        self.details_tree.tag_configure('critical', background='#fdf2f2', foreground='#721c24')
        self.details_tree.tag_configure('high', background='#fef7ec', foreground='#92400e')
        self.details_tree.tag_configure('medium', background='#fffbeb', foreground='#a16207')
        self.details_tree.tag_configure('low', background='#f0fdf4', foreground='#166534')
        self.details_tree.tag_configure('evenrow', background='#f8fafc')
        
        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(self.details_content_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Create scrollbars
        tree_v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", 
                                    command=self.details_tree.yview)
        tree_h_scroll = ttk.Scrollbar(self.details_content_frame, orient="horizontal",
                                    command=self.details_tree.xview)
        
        # Configure treeview scrolling
        self.details_tree.configure(yscrollcommand=tree_v_scroll.set,
                                  xscrollcommand=tree_h_scroll.set)
        
        # Pack treeview and scrollbars using pack instead of grid
        self.details_tree.pack(side='left', fill='both', expand=True)
        tree_v_scroll.pack(side='right', fill='y')
        
        # Horizontal scrollbar in a separate frame
        h_scroll_frame = ttk.Frame(self.details_content_frame)
        h_scroll_frame.pack(fill='x')
        tree_h_scroll.pack(fill='x')
        
        # Add summary stats below the tree
        summary_frame = ttk.Frame(self.details_content_frame)
        summary_frame.pack(fill='x', pady=(10, 0))
        
        # Summary statistics
        self.summary_stats_label = ttk.Label(summary_frame, 
                                           text="Loading summary statistics...",
                                           font=('Arial', 9, 'italic'),
                                           foreground='#6c757d')
        self.summary_stats_label.pack(anchor='w')

    def toggle_details_section(self):
        """Toggle the visibility of the details section"""
        if self.details_expanded.get():
            self.details_content_frame.pack_forget()
            self.expand_btn.config(text="▶ Show Details")
            self.details_expanded.set(False)
        else:
            self.details_content_frame.pack(fill='both', expand=True)
            self.expand_btn.config(text="▼ Hide Details")
            self.details_expanded.set(True)

    def refresh_data(self):
        """Refresh all overview data with enhanced visual updates"""
        try:
            # Update timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.last_update_label.config(text=current_time)
            
            # Get climate data
            status_data = self.climate_manager.get_current_climate_status()
            risk_data = self.climate_manager.get_overall_climate_risk()
            
            # Update only the essential components (remove analytics tabs)
            self.update_header_metrics(status_data, risk_data)
            self.update_quick_stats(status_data)
            self.update_material_cards(status_data)
            self.update_details_table(status_data)
            
        except Exception as e:
            print(f"Error refreshing overview data: {e}")
            messagebox.showerror("Error", f"Failed to refresh overview data: {str(e)}")
    
    def update_header_metrics(self, status_data, risk_data):
        """Update header metrics with enhanced styling"""
        try:
            # Overall risk level
            risk_level = risk_data['risk_level']
            risk_colors = {'CRITICAL': 'red', 'HIGH': 'orange', 'MEDIUM': 'gold', 'LOW': 'green'}
            color = risk_colors.get(risk_level, 'blue')
            
            self.overall_risk_label.config(text=risk_level, foreground=color)
            
            # Materials monitored
            total_materials = len(status_data)
            self.materials_monitored_value_label.config(text=str(total_materials))
            
            # High risk materials
            high_risk_count = len([m for m in status_data if m['risk_level'] in ['CRITICAL', 'HIGH']])
            self.high_risk_materials_value_label.config(text=str(high_risk_count))
            
            # Average delay
            if status_data:
                avg_delay = sum(m['delay_percent'] for m in status_data) / len(status_data)
                self.average_delay_value_label.config(text=f"{avg_delay:.1f}%")
            else:
                self.average_delay_value_label.config(text="0%")
            
            # Production impact
            if status_data:
                total_impact = sum(abs(m['production_impact']) for m in status_data)
                self.production_impact_value_label.config(text=f"{total_impact:.0f}")
            else:
                self.production_impact_value_label.config(text="0")
                
        except Exception as e:
            print(f"Error updating header metrics: {e}")

    def update_quick_stats(self, status_data):
        """Update quick stats indicators with enhanced visuals"""
        try:
            # Production Status
            critical_materials = [m for m in status_data if m['risk_level'] == 'CRITICAL']
            high_risk_materials = [m for m in status_data if m['risk_level'] == 'HIGH']
            
            # Clear and redraw production status
            self.production_status_canvas.delete("all")
            if critical_materials:
                # Draw critical status with pulsing effect
                self.production_status_canvas.create_oval(8, 8, 32, 32, fill='#e74c3c', outline='#c0392b', width=2)
                self.production_status_canvas.create_oval(12, 12, 28, 28, fill='#ffffff', outline='')
                self.production_status_label.config(text="Critical Issues", foreground='#e74c3c')
            elif high_risk_materials:
                self.production_status_canvas.create_oval(8, 8, 32, 32, fill='#f39c12', outline='#e67e22', width=2)
                self.production_status_canvas.create_oval(14, 14, 26, 26, fill='#ffffff', outline='')
                self.production_status_label.config(text="High Risk", foreground='#f39c12')
            else:
                self.production_status_canvas.create_oval(8, 8, 32, 32, fill='#27ae60', outline='#229954', width=2)
                self.production_status_canvas.create_oval(16, 16, 24, 24, fill='#ffffff', outline='')
                self.production_status_label.config(text="Normal", foreground='#27ae60')
            
            # Weather Conditions
            extreme_weather = [m for m in status_data if 'Extreme' in m.get('category', '') or 'Severe' in m.get('current_condition', '')]
            
            self.weather_conditions_canvas.delete("all")
            if extreme_weather:
                self.weather_conditions_canvas.create_oval(8, 8, 32, 32, fill='#e74c3c', outline='#c0392b', width=2)
                self.weather_conditions_canvas.create_text(20, 20, text="⚠", fill='white', font=('Arial', 12, 'bold'))
                self.weather_conditions_label.config(text="Severe Weather", foreground='#e74c3c')
            else:
                self.weather_conditions_canvas.create_oval(8, 8, 32, 32, fill='#27ae60', outline='#229954', width=2)
                self.weather_conditions_canvas.create_text(20, 20, text="☀", fill='white', font=('Arial', 12))
                self.weather_conditions_label.config(text="Favorable", foreground='#27ae60')
            
            # Supply Chain Health
            if status_data:
                avg_delay = sum(m['delay_percent'] for m in status_data) / len(status_data)
            else:
                avg_delay = 0
            
            self.supply_chain_health_canvas.delete("all")
            if avg_delay > 20:
                self.supply_chain_health_canvas.create_oval(8, 8, 32, 32, fill='#e74c3c', outline='#c0392b', width=2)
                self.supply_chain_health_canvas.create_text(20, 20, text="🚫", fill='white', font=('Arial', 10))
                self.supply_chain_health_label.config(text="Disrupted", foreground='#e74c3c')
            elif avg_delay > 10:
                self.supply_chain_health_canvas.create_oval(8, 8, 32, 32, fill='#f39c12', outline='#e67e22', width=2)
                self.supply_chain_health_canvas.create_text(20, 20, text="⏳", fill='white', font=('Arial', 10))
                self.supply_chain_health_label.config(text="Delayed", foreground='#f39c12')
            else:
                self.supply_chain_health_canvas.create_oval(8, 8, 32, 32, fill='#27ae60', outline='#229954', width=2)
                self.supply_chain_health_canvas.create_text(20, 20, text="✓", fill='white', font=('Arial', 12, 'bold'))
                self.supply_chain_health_label.config(text="Healthy", foreground='#27ae60')
                
        except Exception as e:
            print(f"Error updating quick stats: {e}")
            # Set default "error" state for all indicators
            for indicator_type in ['production_status', 'weather_conditions', 'supply_chain_health']:
                canvas = getattr(self, f"{indicator_type}_canvas", None)
                label = getattr(self, f"{indicator_type}_label", None)
                if canvas and label:
                    canvas.delete("all")
                    canvas.create_oval(8, 8, 32, 32, fill='#95a5a6', outline='#7f8c8d', width=2)
                    canvas.create_text(20, 20, text="?", fill='white', font=('Arial', 12, 'bold'))
                    label.config(text="Unknown", foreground='#95a5a6')

    def update_material_cards(self, status_data):
        """Update material status cards with enhanced visual design"""
        try:
            # Clear existing cards
            for widget in self.cards_container.winfo_children():
                widget.destroy()
            
            if not status_data:
                # Show "no data" message
                no_data_frame = ttk.Frame(self.cards_container)
                no_data_frame.grid(row=0, column=0, columnspan=2, pady=20)
                ttk.Label(no_data_frame, text="📭 No climate data available", 
                         font=('Arial', 12), foreground='#7f8c8d').pack()
                return
            
            # Create enhanced cards for each material
            for i, material in enumerate(status_data):
                row = i // 2
                col = i % 2
                
                # Create main card frame with better styling
                card_frame = ttk.LabelFrame(self.cards_container, padding="15")
                card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew', ipadx=5, ipady=5)
                
                # Material header with icon and name
                header_frame = ttk.Frame(card_frame)
                header_frame.pack(fill='x', pady=(0, 10))
                
                # Material icon based on type
                material_icons = {
                    'Wheat': '🌾', 'Cotton': '🌱', 'Rice': '🌾', 
                    'Sugarcane': '🎋', 'Corn': '🌽'
                }
                icon = material_icons.get(material['material_name'], '📦')
                
                ttk.Label(header_frame, text=f"{icon} {material['material_name']}", 
                         font=('Arial', 12, 'bold'), foreground='#2c3e50').pack(side='left')
                
                # Risk level badge
                risk_colors = {'CRITICAL': '#e74c3c', 'HIGH': '#f39c12', 'MEDIUM': '#f1c40f', 'LOW': '#27ae60'}
                risk_color = risk_colors.get(material['risk_level'], '#95a5a6')
                
                risk_badge = tk.Label(header_frame, text=material['risk_level'], 
                                    font=('Arial', 8, 'bold'), fg='white', bg=risk_color,
                                    padx=8, pady=2)
                risk_badge.pack(side='right')
                
                # Separator line
                separator = ttk.Separator(card_frame, orient='horizontal')
                separator.pack(fill='x', pady=(0, 10))
                
                # Card content in a grid
                content_frame = ttk.Frame(card_frame)
                content_frame.pack(fill='x')
                
                # Delay information
                delay_frame = ttk.Frame(content_frame)
                delay_frame.pack(fill='x', pady=2)
                
                ttk.Label(delay_frame, text="⏱️ Delay:", font=('Arial', 9, 'bold')).pack(side='left')
                delay_color = '#e74c3c' if material['delay_percent'] > 15 else '#f39c12' if material['delay_percent'] > 5 else '#27ae60'
                ttk.Label(delay_frame, text=f"{material['delay_percent']:.1f}%", 
                         font=('Arial', 9), foreground=delay_color).pack(side='right')
                
                # Impact information
                impact_frame = ttk.Frame(content_frame)
                impact_frame.pack(fill='x', pady=2)
                
                ttk.Label(impact_frame, text="📊 Impact:", font=('Arial', 9, 'bold')).pack(side='left')
                impact_color = '#e74c3c' if abs(material['production_impact']) > 100 else '#f39c12' if abs(material['production_impact']) > 50 else '#27ae60'
                ttk.Label(impact_frame, text=f"{material['production_impact']:+.0f} units", 
                         font=('Arial', 9), foreground=impact_color).pack(side='right')
                
                # Condition preview
                condition_frame = ttk.Frame(content_frame)
                condition_frame.pack(fill='x', pady=(5, 0))
                
                ttk.Label(condition_frame, text="📋 Condition:", font=('Arial', 9, 'bold')).pack(anchor='w')
                condition_text = material['current_condition']
                if len(condition_text) > 60:
                    condition_text = condition_text[:57] + "..."
                ttk.Label(condition_frame, text=condition_text, font=('Arial', 8), 
                         foreground='#7f8c8d', wraplength=200).pack(anchor='w', pady=(2, 0))
                
        except Exception as e:
            print(f"Error updating material cards: {e}")
            # Show error message
            error_frame = ttk.Frame(self.cards_container)
            error_frame.grid(row=0, column=0, columnspan=2, pady=20)
            ttk.Label(error_frame, text=f"❌ Error loading data: {str(e)}", 
                     font=('Arial', 10), foreground='#e74c3c').pack()

    def update_production_impact_tab(self, status_data):
        """Update production impact tab"""
        try:
            # Update impact metric cards
            total_impact = sum(abs(m['production_impact']) for m in status_data)
            self.impact_total_impact_label.config(text=f"{total_impact:.0f} units")
            
            # Material-specific impacts
            material_impacts = {m['material_name']: m['production_impact'] for m in status_data}
            
            if hasattr(self, 'impact_wheat_impact_label'):
                wheat_impact = material_impacts.get('Wheat', 0)
                self.impact_wheat_impact_label.config(text=f"{abs(wheat_impact):.0f} units")
            
            if hasattr(self, 'impact_cotton_impact_label'):
                cotton_impact = material_impacts.get('Cotton', 0)
                self.impact_cotton_impact_label.config(text=f"{abs(cotton_impact):.0f} units")
            
            if hasattr(self, 'impact_rice_impact_label'):
                rice_impact = material_impacts.get('Rice', 0)
                self.impact_rice_impact_label.config(text=f"{abs(rice_impact):.0f} units")
            
            # Update details text
            self.impact_details_text.config(state=tk.NORMAL)
            self.impact_details_text.delete('1.0', tk.END)
            
            self.impact_details_text.insert(tk.END, "PRODUCTION IMPACT ANALYSIS\n", 'header')
            self.impact_details_text.insert(tk.END, "=" * 40 + "\n\n")
            
            for material in status_data:
                impact = material['production_impact']
                impact_type = "Loss" if impact < 0 else "Gain"
                
                self.impact_details_text.insert(tk.END, f"{material['material_name']}:\n", 'material')
                self.impact_details_text.insert(tk.END, f"  • {impact_type}: {abs(impact):.1f} units\n")
                self.impact_details_text.insert(tk.END, f"  • Delay: {material['delay_percent']:.1f}%\n")
                self.impact_details_text.insert(tk.END, f"  • Risk Level: {material['risk_level']}\n")
                self.impact_details_text.insert(tk.END, f"  • Condition: {material['current_condition']}\n\n")
            
            self.impact_details_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error updating production impact tab: {e}")

    def update_risk_analysis_tab(self, status_data):
        """Update risk analysis tab"""
        try:
            # Count materials by risk level
            risk_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
            for material in status_data:
                risk_level = material['risk_level'].title()
                if risk_level in risk_counts:
                    risk_counts[risk_level] += 1
            
            # Update risk level cards
            for level, count in risk_counts.items():
                label = getattr(self, f"risk_{level.lower()}_count_label", None)
                if label:
                    label.config(text=str(count))
            
            # Update risk analysis text
            self.risk_analysis_text.config(state=tk.NORMAL)
            self.risk_analysis_text.delete('1.0', tk.END)
            
            self.risk_analysis_text.insert(tk.END, "RISK ANALYSIS REPORT\n", 'header')
            self.risk_analysis_text.insert(tk.END, "=" * 40 + "\n\n")
            
            total_materials = len(status_data)
            high_risk_materials = risk_counts['Critical'] + risk_counts['High']
            
            self.risk_analysis_text.insert(tk.END, f"Total Materials Monitored: {total_materials}\n")
            self.risk_analysis_text.insert(tk.END, f"High Risk Materials: {high_risk_materials}\n")
            self.risk_analysis_text.insert(tk.END, f"Risk Percentage: {(high_risk_materials/total_materials*100):.1f}%\n\n")
            
            for material in status_data:
                if material['risk_level'] in ['CRITICAL', 'HIGH']:
                    self.risk_analysis_text.insert(tk.END, f"⚠️ {material['material_name']}\n", 'material')
                    self.risk_analysis_text.insert(tk.END, f"   Risk: {material['risk_level']}\n")
                    self.risk_analysis_text.insert(tk.END, f"   Delay: {material['delay_percent']:.1f}%\n")
                    self.risk_analysis_text.insert(tk.END, f"   Category: {material.get('category', 'Unknown')}\n\n")
            
            self.risk_analysis_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error updating risk analysis tab: {e}")

    def update_trends_tab(self):
        """Update trends and forecasts tab"""
        try:
            # Update trends summary
            self.trends_summary_text.config(state=tk.NORMAL)
            self.trends_summary_text.delete('1.0', tk.END)
            
            self.trends_summary_text.insert(tk.END, "📈 Recent trends show climate volatility affecting production schedules. ")
            self.trends_summary_text.insert(tk.END, "Monitoring indicates increased risk in wheat and sugarcane sectors. ")
            self.trends_summary_text.insert(tk.END, "Cotton and rice markets remain relatively stable with minor fluctuations.")
            
            self.trends_summary_text.config(state=tk.DISABLED)
            
            # Update forecast
            forecast_data = self.climate_manager.get_climate_forecast(7)
            
            self.forecast_text.config(state=tk.NORMAL)
            self.forecast_text.delete('1.0', tk.END)
            
            self.forecast_text.insert(tk.END, "7-DAY CLIMATE FORECAST\n", 'header')
            self.forecast_text.insert(tk.END, "=" * 30 + "\n\n")
            
            if forecast_data:
                current_date = datetime.now()
                for i, forecast in enumerate(forecast_data[:7]):
                    forecast_date = current_date + timedelta(days=i)
                    
                    self.forecast_text.insert(tk.END, f"Day {i+1} ({forecast_date.strftime('%m/%d')}):\n", 'date')
                    self.forecast_text.insert(tk.END, f"  Condition: {forecast.get('expected_condition', 'Unknown')}\n")
                    self.forecast_text.insert(tk.END, f"  Category: {forecast.get('category', 'Normal')}\n")
                    self.forecast_text.insert(tk.END, f"  Risk Level: {forecast.get('risk_level', 'Low')}\n\n")
            else:
                self.forecast_text.insert(tk.END, "No forecast data available.\n")
            
            self.forecast_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error updating trends tab: {e}")

    def update_details_table(self, status_data):
        """Update the detailed information table with enhanced data"""
        try:
            # Clear existing items
            for item in self.details_tree.get_children():
                self.details_tree.delete(item)
            
            if not status_data:
                # Insert "no data" row
                self.details_tree.insert('', 'end', values=(
                    "No Data", "📭", "No climate data available", 
                    "System", "0", "N/A", "N/A"
                ))
                self.summary_stats_label.config(text="No data available for analysis")
                return
            
            # Add data with enhanced styling and formatting
            for i, material in enumerate(status_data):
                # Determine status icon based on risk level
                status_icons = {
                    'CRITICAL': '🔴', 'HIGH': '🟠', 
                    'MEDIUM': '🟡', 'LOW': '🟢'
                }
                status_icon = status_icons.get(material['risk_level'], '⚪')
                
                # Format condition text (smart truncation)
                condition = material['current_condition']
                if len(condition) > 35:
                    # Find last space before 32 characters
                    truncate_pos = condition.rfind(' ', 0, 32)
                    if truncate_pos > 20:  # If we found a good break point
                        condition = condition[:truncate_pos] + "..."
                    else:
                        condition = condition[:32] + "..."
                
                # Format impact with better visualization
                impact_value = material['production_impact']
                if impact_value > 0:
                    impact_text = f"+{impact_value:.0f}"
                elif impact_value < 0:
                    impact_text = f"{impact_value:.0f}"
                else:
                    impact_text = "0"
                
                # Format update time
                try:
                    if hasattr(material['last_updated'], 'strftime'):
                        last_updated = material['last_updated'].strftime('%m/%d %H:%M')
                    else:
                        last_updated = str(material['last_updated'])[:16]
                except:
                    last_updated = "Unknown"
                
                # Insert item with appropriate styling
                risk_level = material['risk_level'].lower()
                tags = [risk_level]
                if i % 2 == 0:
                    tags.append('evenrow')
                
                self.details_tree.insert('', 'end', 
                                       values=(
                                           material['material_name'],
                                           status_icon,
                                           condition,
                                           material.get('category', 'Unknown'),
                                           impact_text,
                                           material['risk_level'],
                                           last_updated
                                       ),
                                       tags=tuple(tags))
            
            # Update summary statistics
            self.update_summary_statistics(status_data)
                                       
        except Exception as e:
            print(f"Error updating details table: {e}")
            # Insert error row
            self.details_tree.insert('', 'end', values=(
                "Error", "❌", f"Failed to load data: {str(e)}", 
                "System", "0", "ERROR", "N/A"
            ))
            self.summary_stats_label.config(text="Error loading summary statistics")

    def update_summary_statistics(self, status_data):
        """Update summary statistics below the details table"""
        try:
            if not status_data:
                self.summary_stats_label.config(text="No data available for analysis")
                return
            
            # Calculate statistics
            total_materials = len(status_data)
            total_impact = sum(abs(m['production_impact']) for m in status_data)
            avg_delay = sum(m['delay_percent'] for m in status_data) / total_materials
            
            # Risk distribution
            risk_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for material in status_data:
                risk_level = material['risk_level']
                if risk_level in risk_counts:
                    risk_counts[risk_level] += 1
            
            # Create summary text
            summary_parts = [
                f"📊 Total Materials: {total_materials}",
                f"📈 Total Impact: {total_impact:.0f} units",
                f"⏱️ Avg Delay: {avg_delay:.1f}%"
            ]
            
            # Add risk distribution
            risk_summary = []
            for level, count in risk_counts.items():
                if count > 0:
                    risk_summary.append(f"{level}: {count}")
            
            if risk_summary:
                summary_parts.append(f"⚠️ Risk Distribution: {', '.join(risk_summary)}")
            
            # Update label
            summary_text = " | ".join(summary_parts)
            self.summary_stats_label.config(text=summary_text)
            
        except Exception as e:
            self.summary_stats_label.config(text=f"Error calculating statistics: {str(e)}")
    
    def update_status_cards(self, status_data):
        """Update material status cards"""
        # Clear existing cards
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        
        # Create enhanced status cards
        for i, material_data in enumerate(status_data):
            card = self.create_enhanced_status_card(self.cards_container, material_data)
            card.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
    
    def create_enhanced_status_card(self, parent, material_data):
        """Create an enhanced status card with more details"""
        material_info = ClimateConstants.MATERIALS.get(material_data['material_id'], {})
        icon = material_info.get('icon', '📦')
        
        # Main card frame
        card_frame = ttk.LabelFrame(parent, text=f"{icon} {material_data['material_name']}", padding="8")
        
        # Current condition (truncated)
        condition_text = material_data['current_condition']
        if len(condition_text) > 35:
            condition_text = condition_text[:32] + "..."
        
        condition_label = ttk.Label(card_frame, 
                                   text=condition_text,
                                   font=ClimateConstants.SMALL_FONT,
                                   wraplength=160)
        condition_label.pack(pady=(0, 3))
        
        # Production metrics frame
        metrics_frame = ttk.Frame(card_frame)
        metrics_frame.pack(fill='x', pady=(0, 3))
        
        # Original vs Expected production
        original = material_data['original_production']
        expected = material_data['expected_production']
        impact = expected - original
        
        ttk.Label(metrics_frame, 
                 text=f"Original: {original:,.0f}",
                 font=ClimateConstants.SMALL_FONT).pack()
        
        ttk.Label(metrics_frame, 
                 text=f"Expected: {expected:,.0f}",
                 font=ClimateConstants.SMALL_FONT).pack()
        
        # Impact with color coding
        impact_color = ClimateConstants.SUCCESS_COLOR if impact >= 0 else ClimateConstants.DANGER_COLOR
        impact_symbol = "+" if impact >= 0 else ""
        
        impact_label = ttk.Label(metrics_frame, 
                                text=f"Impact: {impact_symbol}{impact:,.0f}",
                                font=ClimateConstants.BODY_FONT)
        impact_label.pack()
        
        # Delay percentage
        delay_percent = material_data['delay_percent']
        delay_label = ttk.Label(metrics_frame,
                               text=f"Delay: {delay_percent:.1f}%",
                               font=ClimateConstants.SMALL_FONT)
        delay_label.pack()
        
        # Risk level indicator
        risk_frame = create_risk_indicator(card_frame, material_data['risk_level'], size="normal")
        risk_frame.pack(pady=(3, 0))
        
        # Category badge
        category = material_data['category']
        category_info = ClimateConstants.CLIMATE_CATEGORIES.get(category, {})
        category_icon = category_info.get('icon', '🌍')
        
        category_label = ttk.Label(card_frame,
                                  text=f"{category_icon} {category}",
                                  font=ClimateConstants.SMALL_FONT)
        category_label.pack(pady=(2, 0))
        
        return card_frame
    
    def update_summaries(self, status_data, risk_data):
        """Update all summary sections with current data"""
        self.update_production_impact_summary(status_data)
        self.update_risk_distribution_summary(status_data)
    
    def update_production_impact_summary(self, status_data):
        """Update production impact summary text"""
        if not hasattr(self, 'impact_summary_text'):
            return
            
        summary_text = "Production Impact Analysis:\n\n"
        
        if not status_data:
            summary_text += "No data available for production impact analysis."
        else:
            # Sort by impact
            sorted_data = sorted(status_data, key=lambda x: x['production_impact'], reverse=True)
            
            summary_text += "Materials ranked by production impact:\n\n"
            for i, data in enumerate(sorted_data, 1):
                impact = data['production_impact']
                impact_symbol = "+" if impact >= 0 else ""
                risk_color = "🔴" if data['risk_level'] == 'CRITICAL' else \
                           "🟡" if data['risk_level'] == 'HIGH' else \
                           "🟠" if data['risk_level'] == 'MEDIUM' else "🟢"
                
                summary_text += f"{i}. {data['material_name']}: {impact_symbol}{impact:,.0f} units {risk_color}\n"
                summary_text += f"   Risk Level: {data['risk_level']}\n"
                summary_text += f"   Delay: {data['delay_percent']:.1f}%\n\n"
        
        # Update text widget
        self.impact_summary_text.config(state=tk.NORMAL)
        self.impact_summary_text.delete('1.0', tk.END)
        self.impact_summary_text.insert('1.0', summary_text)
        self.impact_summary_text.config(state=tk.DISABLED)
    
    def update_risk_distribution_summary(self, status_data):
        """Update risk distribution summary"""
        # Clear existing content
        for widget in self.risk_summary_frame_content.winfo_children():
            widget.destroy()
        
        if not status_data:
            no_data_label = ttk.Label(self.risk_summary_frame_content,
                                     text="No data available for risk analysis.",
                                     font=ClimateConstants.BODY_FONT)
            no_data_label.pack()
            return
        
        # Count risk levels
        risk_counts = {}
        total_materials = len(status_data)
        for data in status_data:
            risk_level = data['risk_level']
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # Create risk level summary
        summary_label = ttk.Label(self.risk_summary_frame_content,
                                 text=f"Risk Distribution Summary ({total_materials} materials):",
                                 font=ClimateConstants.BODY_FONT)
        summary_label.pack(anchor='w', pady=(0, 10))
        
        # Risk level breakdown
        for risk_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = risk_counts.get(risk_level, 0)
            percentage = (count / total_materials) * 100 if total_materials > 0 else 0
            
            if count > 0:
                color_indicator = "🔴" if risk_level == 'CRITICAL' else \
                                "🟡" if risk_level == 'HIGH' else \
                                "🟠" if risk_level == 'MEDIUM' else "🟢"
                
                risk_frame = ttk.Frame(self.risk_summary_frame_content)
                risk_frame.pack(fill='x', pady=2)
                
                risk_info = ttk.Label(risk_frame,
                                     text=f"{color_indicator} {risk_level}: {count} materials ({percentage:.1f}%)",
                                     font=ClimateConstants.BODY_FONT)
                risk_info.pack(anchor='w')
    
    def update_details_table(self, status_data):
        """Update the detailed information table"""
        # Clear existing data
        self.details_tree.delete(*self.details_tree.get_children())
        
        # Populate with current data
        for data in status_data:
            # Format production impact
            impact = data['production_impact']
            impact_text = f"{impact:+,.0f}"
            
            # Format last updated
            last_updated = data['last_updated']
            if hasattr(last_updated, 'strftime'):
                updated_text = last_updated.strftime('%Y-%m-%d %H:%M')
            else:
                updated_text = str(last_updated)
            
            # Insert row
            self.details_tree.insert('', 'end', values=(
                data['material_name'],
                data['current_condition'][:40] + "..." if len(data['current_condition']) > 40 else data['current_condition'],
                data['category'],
                impact_text,
                data['risk_level'],
                updated_text
            ))
        
        # Apply alternating row colors using tags instead of set()
        for i, item in enumerate(self.details_tree.get_children()):
            if i % 2 == 0:
                self.details_tree.item(item, tags=('evenrow',))
        
        # Configure tag for alternating colors
        self.details_tree.tag_configure('evenrow', background='#f8f9fa')

    def refresh_recommendations(self):
        """Refresh the smart recommendations"""
        try:
            recommendations = self.climate_manager.get_smart_recommendations()
            
            self.recommendations_text.config(state=tk.NORMAL)
            self.recommendations_text.delete('1.0', tk.END)
            
            if recommendations:
                self.recommendations_text.insert(tk.END, "🎯 SMART RECOMMENDATIONS\n", 'header')
                self.recommendations_text.insert(tk.END, "=" * 50 + "\n\n", 'separator')
                
                for i, rec in enumerate(recommendations, 1):
                    self.recommendations_text.insert(tk.END, f"{i}. {rec['material_name']}\n", 'material')
                    self.recommendations_text.insert(tk.END, f"   Risk Level: {rec['current_risk_level']}\n")
                    self.recommendations_text.insert(tk.END, f"   Urgency Score: {rec['urgency_score']:.1f}/100\n")
                    self.recommendations_text.insert(tk.END, f"   \n")
                    
                    # Top 3 recommendations
                    for j, action in enumerate(rec['recommendations'][:3], 1):
                        self.recommendations_text.insert(tk.END, f"   • {action}\n", 'action')
                    
                    if len(rec['recommendations']) > 3:
                        self.recommendations_text.insert(tk.END, f"   ... and {len(rec['recommendations'])-3} more actions\n")
                    
                    self.recommendations_text.insert(tk.END, f"\n")
            else:
                self.recommendations_text.insert(tk.END, "✅ No urgent recommendations at this time.\n")
                self.recommendations_text.insert(tk.END, "All materials are within acceptable risk levels.")
            
            # Configure text tags for styling
            self.recommendations_text.tag_config('header', font=('Arial', 11, 'bold'))
            self.recommendations_text.tag_config('material', font=('Arial', 10, 'bold'), foreground='navy')
            self.recommendations_text.tag_config('action', foreground='darkgreen')
            
            self.recommendations_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.recommendations_text.config(state=tk.NORMAL)
            self.recommendations_text.delete('1.0', tk.END)
            self.recommendations_text.insert(tk.END, f"Error loading recommendations: {e}")
            self.recommendations_text.config(state=tk.DISABLED)
