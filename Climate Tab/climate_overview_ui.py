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
        """Create the enhanced overview interface"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Header section
        self.create_header_section(main_frame)
        
        # Material status cards section
        self.create_status_cards_section(main_frame)
        
        # Summary information section
        self.create_summary_section(main_frame)
        
        # Detailed information section
        self.create_details_section(main_frame)
        
        # Load initial data
        self.refresh_data()
    
    def create_header_section(self, parent):
        """Create header with overall risk metrics"""
        header_frame = ttk.LabelFrame(parent, text="🌍 Climate Overview", padding="10")
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Overall risk gauge container
        gauge_frame = ttk.Frame(header_frame)
        gauge_frame.pack(side='left', fill='both', expand=True)
        
        self.overall_risk_label = ttk.Label(gauge_frame,
                                           text="Loading overall risk...",
                                           font=ClimateConstants.LARGE_FONT)
        self.overall_risk_label.pack()
        
        self.risk_description_label = ttk.Label(gauge_frame,
                                               text="",
                                               font=ClimateConstants.BODY_FONT)
        self.risk_description_label.pack()
        
        # Quick stats container
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side='right', padx=(20, 0))
        
        # Materials at risk
        self.materials_risk_label = ttk.Label(stats_frame,
                                             text="Materials at Risk: --",
                                             font=ClimateConstants.SUBHEADER_FONT)
        self.materials_risk_label.pack()
        
        # Last updated
        self.last_updated_label = ttk.Label(stats_frame,
                                           text="Last updated: --",
                                           font=ClimateConstants.SMALL_FONT)
        self.last_updated_label.pack()
        
        # Refresh button
        refresh_btn = ttk.Button(stats_frame,
                                text="🔄 Refresh",
                                command=self.refresh_data)
        refresh_btn.pack(pady=(5, 0))
    
    def create_status_cards_section(self, parent):
        """Create enhanced material status cards"""
        cards_frame = ttk.LabelFrame(parent, text="📊 Material Status", padding="10")
        cards_frame.pack(fill='x', pady=(0, 10))
        
        # Cards container
        self.cards_container = ttk.Frame(cards_frame)
        self.cards_container.pack(fill='x')
        
        # Configure grid weights for responsive design
        for i in range(4):  # 4 materials
            self.cards_container.grid_columnconfigure(i, weight=1)
    
    def create_summary_section(self, parent):
        """Create summary information section (replacing charts)"""
        summary_frame = ttk.LabelFrame(parent, text="� Climate Summary", padding="10")
        summary_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create notebook for different summary views
        self.summary_notebook = ttk.Notebook(summary_frame)
        self.summary_notebook.pack(fill='both', expand=True)
        
        # Production impact summary tab
        self.impact_summary_frame = ttk.Frame(self.summary_notebook)
        self.summary_notebook.add(self.impact_summary_frame, text="Production Impact")
        
        # Risk distribution summary tab
        self.risk_summary_frame = ttk.Frame(self.summary_notebook)
        self.summary_notebook.add(self.risk_summary_frame, text="Risk Distribution")
        
        # Trend summary tab
        self.trend_summary_frame = ttk.Frame(self.summary_notebook)
        self.summary_notebook.add(self.trend_summary_frame, text="Trends")
        
        # Create summary content
        self.create_production_impact_summary()
        self.create_risk_distribution_summary()
        self.create_trend_summary()
    
    def create_details_section(self, parent):
        """Create detailed information section"""
        details_frame = ttk.LabelFrame(parent, text="📋 Detailed Climate Information", padding="10")
        details_frame.pack(fill='x')
        
        # Create treeview for detailed data
        columns = ('Material', 'Current Condition', 'Category', 'Production Impact', 'Risk Level', 'Last Updated')
        self.details_tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=6)
        
        # Configure columns
        column_widths = {
            'Material': 100,
            'Current Condition': 250,
            'Category': 120,
            'Production Impact': 130,
            'Risk Level': 100,
            'Last Updated': 130
        }
        
        for col in columns:
            self.details_tree.heading(col, text=col)
            self.details_tree.column(col, width=column_widths[col], minwidth=80)
        
        # Add scrollbar
        details_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_tree.yview)
        self.details_tree.configure(yscrollcommand=details_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.details_tree.pack(side='left', fill='both', expand=True)
        details_scrollbar.pack(side='right', fill='y')
    
    def create_production_impact_summary(self):
        """Create production impact summary (text-based)"""
        summary_frame = ttk.Frame(self.impact_summary_frame, padding="10")
        summary_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(summary_frame, 
                               text="Production Impact Summary",
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Summary text widget
        self.impact_summary_text = tk.Text(summary_frame, height=8, width=50,
                                          font=ClimateConstants.BODY_FONT,
                                          wrap=tk.WORD, state=tk.DISABLED)
        self.impact_summary_text.pack(fill='both', expand=True)
        
        # Scrollbar
        impact_scroll = ttk.Scrollbar(summary_frame, orient="vertical", 
                                     command=self.impact_summary_text.yview)
        self.impact_summary_text.configure(yscrollcommand=impact_scroll.set)
        impact_scroll.pack(side='right', fill='y')
    
    def create_risk_distribution_summary(self):
        """Create risk distribution summary (text-based)"""
        summary_frame = ttk.Frame(self.risk_summary_frame, padding="10")
        summary_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(summary_frame,
                               text="Risk Distribution Summary", 
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Risk summary frame
        self.risk_summary_frame_content = ttk.Frame(summary_frame)
        self.risk_summary_frame_content.pack(fill='both', expand=True)
        
        # Will be populated with risk information
    
    def create_trend_summary(self):
        """Create trend summary (text-based)"""
        summary_frame = ttk.Frame(self.trend_summary_frame, padding="10")
        summary_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(summary_frame,
                               text="Climate Trends Summary",
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Trend information
        trend_label = ttk.Label(summary_frame,
                               text="Trend analysis will show historical patterns\nand forecasted climate conditions.",
                               font=ClimateConstants.BODY_FONT,
                               justify='left')
        trend_label.pack(anchor='w')
    
    def refresh_data(self):
        """Refresh all overview data"""
        try:
            # Update timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.last_updated_label.config(text=f"Last updated: {current_time}")
            
            # Get climate data
            status_data = self.climate_manager.get_current_climate_status()
            risk_data = self.climate_manager.get_overall_climate_risk()
            
            # Update header metrics
            self.update_header_metrics(risk_data, status_data)
            
            # Update status cards
            self.update_status_cards(status_data)
            
            # Update charts
            self.update_summaries(status_data, risk_data)
            
            # Update details table
            self.update_details_table(status_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh overview data: {str(e)}")
    
    def update_header_metrics(self, risk_data, status_data):
        """Update header risk metrics"""
        risk_score = risk_data['risk_score']
        risk_level = risk_data['risk_level']
        materials_at_risk = risk_data['materials_at_risk']
        total_materials = risk_data['total_materials']
        
        # Update overall risk display
        risk_color = ClimateConstants.RISK_COLORS.get(risk_level, ClimateConstants.INFO_COLOR)
        self.overall_risk_label.config(
            text=f"Overall Risk: {risk_score}% ({risk_level})",
            foreground=risk_color
        )
        
        # Update description
        if risk_level == "CRITICAL":
            description = "Immediate action required for multiple materials"
        elif risk_level == "HIGH":
            description = "Several materials showing concerning patterns"
        elif risk_level == "MEDIUM":
            description = "Some materials require monitoring"
        else:
            description = "Climate conditions are generally stable"
        
        self.risk_description_label.config(text=description)
        
        # Update materials at risk
        self.materials_risk_label.config(
            text=f"Materials at Risk: {materials_at_risk}/{total_materials}",
            foreground=risk_color if materials_at_risk > 0 else ClimateConstants.SUCCESS_COLOR
        )
    
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
