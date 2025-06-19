"""
Main Climate UI Module - Controller
Main climate tab controller with subtab management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os

# Import modular climate components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from climate_base import ClimateBaseUI, ClimateConstants
from climate_overview_ui import ClimateOverviewUI
from climate_warnings_ui import ClimateWarningsUI
from climate_actions_ui import ClimateActionsUI
import climate_data

class ClimateUI:
    """Main Climate UI class with 3 subtabs: Overview, Warnings, Actions"""
    
    def __init__(self, parent_frame, **callbacks):
        self.parent = parent_frame
        self.callbacks = callbacks
        
        # Initialize data manager
        self.climate_manager = climate_data.climate_manager
        
        # Create main climate layout
        self.create_climate_layout()
        
    def create_climate_layout(self):
        """Create the main climate structure with subtabs"""
        
        # Main climate frame
        self.main_frame = ttk.Frame(self.parent, padding="10")
        self.main_frame.pack(fill='both', expand=True)
        
        # Header section
        self.create_header()
        
        # Main content area with subtabs
        self.create_subtabs()
        
        # Load initial data
        self.refresh_all_data()
        
    def create_header(self):
        """Create the header section with title and global controls"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Title with icon
        title_label = ttk.Label(header_frame, 
                               text="🌍 Climate Management Dashboard",
                               font=ClimateConstants.HEADER_FONT)
        title_label.pack(side='left')
        
        # Global controls frame
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        # Refresh button
        refresh_btn = ttk.Button(controls_frame, 
                                text="🔄 Refresh All",
                                command=self.refresh_all_data)
        refresh_btn.pack(side='right', padx=(5, 0))
        
        # Last updated label
        self.last_updated_label = ttk.Label(controls_frame,
                                           text="Last updated: Loading...",
                                           font=ClimateConstants.SMALL_FONT)
        self.last_updated_label.pack(side='right', padx=(0, 10))
        
    def create_subtabs(self):
        """Create the subtabs notebook"""
        # Subtabs notebook
        self.subtabs_notebook = ttk.Notebook(self.main_frame)
        self.subtabs_notebook.pack(fill='both', expand=True)
        
        # Create subtab frames
        self.overview_tab = ttk.Frame(self.subtabs_notebook)
        self.warnings_tab = ttk.Frame(self.subtabs_notebook)
        self.actions_tab = ttk.Frame(self.subtabs_notebook)
        
        # Add subtabs to notebook
        self.subtabs_notebook.add(self.overview_tab, text="📊 Overview")
        self.subtabs_notebook.add(self.warnings_tab, text="⚠️ Warnings")
        self.subtabs_notebook.add(self.actions_tab, text="🎯 Actions")
        
        # Initialize subtab content
        self.create_overview_content()
        self.create_warnings_content()
        self.create_actions_content()
        
        # Bind tab change event
        self.subtabs_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def create_overview_content(self):
        """Create enhanced overview content using ClimateOverviewUI"""
        try:
            # Initialize the enhanced overview UI
            self.overview_ui = ClimateOverviewUI(self.overview_tab, self.callbacks)
        except Exception as e:
            # Fallback to placeholder if enhanced UI fails
            self.create_overview_placeholder()
    
    def create_warnings_content(self):
        """Create enhanced warnings content using ClimateWarningsUI"""
        try:
            # Initialize the enhanced warnings UI
            self.warnings_ui = ClimateWarningsUI(self.warnings_tab, self.callbacks)
        except Exception as e:
            # Fallback to placeholder if enhanced UI fails
            self.create_warnings_placeholder()
    
    def create_actions_content(self):
        """Create enhanced actions content using ClimateActionsUI"""
        try:
            # Initialize the enhanced actions UI
            self.actions_ui = ClimateActionsUI(self.actions_tab, self.callbacks)
        except Exception as e:
            # Fallback to placeholder if enhanced UI fails
            self.create_actions_placeholder()
        
    def create_overview_placeholder(self):
        """Create placeholder content for overview tab"""
        # Overview content frame
        overview_frame = ttk.Frame(self.overview_tab, padding="10")
        overview_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(overview_frame,
                               text="Climate Overview",
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Material status cards frame
        self.status_cards_frame = ttk.Frame(overview_frame)
        self.status_cards_frame.pack(fill='x', pady=(0, 15))
        
        # Overall risk section
        risk_frame = ttk.LabelFrame(overview_frame, text="Overall Climate Risk", padding="10")
        risk_frame.pack(fill='x', pady=(0, 15))
        
        self.overall_risk_label = ttk.Label(risk_frame,
                                           text="Loading climate risk assessment...",
                                           font=ClimateConstants.BODY_FONT)
        self.overall_risk_label.pack()
        
        # Recent updates section
        updates_frame = ttk.LabelFrame(overview_frame, text="Recent Climate Updates", padding="10")
        updates_frame.pack(fill='both', expand=True)
        
        # Create treeview for recent updates
        columns = ('Material', 'Condition', 'Risk Level', 'Last Updated')
        self.updates_tree = ttk.Treeview(updates_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        for col in columns:
            self.updates_tree.heading(col, text=col)
            if col == 'Condition':
                self.updates_tree.column(col, width=300)
            elif col == 'Material':
                self.updates_tree.column(col, width=100)
            elif col == 'Risk Level':
                self.updates_tree.column(col, width=100)
            else:
                self.updates_tree.column(col, width=150)
        
        # Add scrollbar
        updates_scrollbar = ttk.Scrollbar(updates_frame, orient="vertical", command=self.updates_tree.yview)
        self.updates_tree.configure(yscrollcommand=updates_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.updates_tree.pack(side='left', fill='both', expand=True)
        updates_scrollbar.pack(side='right', fill='y')
        
    def create_warnings_placeholder(self):
        """Create placeholder content for warnings tab"""
        warnings_frame = ttk.Frame(self.warnings_tab, padding="10")
        warnings_frame.pack(fill='both', expand=True)
        
        title_label = ttk.Label(warnings_frame,
                               text="Climate Warnings & Alerts",
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Alerts frame
        self.alerts_frame = ttk.LabelFrame(warnings_frame, text="Active Alerts", padding="10")
        self.alerts_frame.pack(fill='x', pady=(0, 15))
        
        self.alerts_label = ttk.Label(self.alerts_frame,
                                     text="Loading climate alerts...",
                                     font=ClimateConstants.BODY_FONT)
        self.alerts_label.pack()
        
        # Forecast frame
        forecast_frame = ttk.LabelFrame(warnings_frame, text="7-Day Climate Forecast", padding="10")
        forecast_frame.pack(fill='both', expand=True)
        
        # Create treeview for forecast
        forecast_columns = ('Material', 'Date', 'Condition', 'Risk', 'Days Away')
        self.forecast_tree = ttk.Treeview(forecast_frame, columns=forecast_columns, show='headings', height=10)
        
        # Configure forecast columns
        for col in forecast_columns:
            self.forecast_tree.heading(col, text=col)
            if col == 'Condition':
                self.forecast_tree.column(col, width=250)
            else:
                self.forecast_tree.column(col, width=100)
        
        # Add scrollbar for forecast
        forecast_scrollbar = ttk.Scrollbar(forecast_frame, orient="vertical", command=self.forecast_tree.yview)
        self.forecast_tree.configure(yscrollcommand=forecast_scrollbar.set)
        
        # Pack forecast treeview
        self.forecast_tree.pack(side='left', fill='both', expand=True)
        forecast_scrollbar.pack(side='right', fill='y')
        
    def create_actions_placeholder(self):
        """Create placeholder content for actions tab"""
        actions_frame = ttk.Frame(self.actions_tab, padding="10")
        actions_frame.pack(fill='both', expand=True)
        
        title_label = ttk.Label(actions_frame,
                               text="Climate Action Center",
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(anchor='w', pady=(0, 10))
        
        placeholder_label = ttk.Label(actions_frame,
                                     text="Action center features will be implemented in Phase 5",
                                     font=ClimateConstants.BODY_FONT)
        placeholder_label.pack(expand=True)
        
    def refresh_all_data(self):
        """Refresh all climate data"""
        try:
            # Update last updated timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.last_updated_label.config(text=f"Last updated: {current_time}")
            
            # Refresh overview data
            self.refresh_overview_data()
            
            # Refresh warnings data
            self.refresh_warnings_data()
            
            # Refresh actions data
            self.refresh_actions_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh climate data: {str(e)}")
    
    def refresh_overview_data(self):
        """Refresh data for overview tab"""
        try:
            # Try to refresh enhanced overview first
            if hasattr(self, 'overview_ui') and self.overview_ui:
                self.overview_ui.refresh_data()
                return
            
            # Fallback to placeholder data refresh if enhanced UI not available
            if not hasattr(self, 'status_cards_frame'):
                return
                
            # Clear existing status cards
            for widget in self.status_cards_frame.winfo_children():
                widget.destroy()
            
            # Get current climate status
            status_data = self.climate_manager.get_current_climate_status()
            
            # Create status cards for each material
            for i, material_data in enumerate(status_data):
                from climate_base import create_material_status_card
                card = create_material_status_card(self.status_cards_frame, material_data)
                card.grid(row=0, column=i, padx=5, sticky='ew')
            
            # Configure grid weights
            for i in range(len(status_data)):
                self.status_cards_frame.grid_columnconfigure(i, weight=1)
            
            # Update overall risk
            risk_data = self.climate_manager.get_overall_climate_risk()
            risk_text = f"Overall Risk Score: {risk_data['risk_score']}% ({risk_data['risk_level']}) | " \
                       f"Materials at Risk: {risk_data['materials_at_risk']}/{risk_data['total_materials']}"
            self.overall_risk_label.config(text=risk_text)
            
            # Update recent updates treeview
            self.updates_tree.delete(*self.updates_tree.get_children())
            for material_data in status_data:
                self.updates_tree.insert('', 'end', values=(
                    material_data['material_name'],
                    material_data['current_condition'][:50] + "..." if len(material_data['current_condition']) > 50 else material_data['current_condition'],
                    material_data['risk_level'],
                    material_data['last_updated'].strftime('%Y-%m-%d %H:%M') if hasattr(material_data['last_updated'], 'strftime') else str(material_data['last_updated'])
                ))
                
        except Exception as e:
            if hasattr(self, 'overall_risk_label'):
                self.overall_risk_label.config(text=f"Error loading overview data: {str(e)}")
    
    def refresh_warnings_data(self):
        """Refresh data for warnings tab"""
        try:
            # Try to refresh enhanced warnings first
            if hasattr(self, 'warnings_ui') and self.warnings_ui:
                self.warnings_ui.refresh_data()
                return
            
            # Fallback to placeholder data refresh if enhanced UI not available
            if not hasattr(self, 'alerts_label'):
                return
                
            # Get alerts
            alerts = self.climate_manager.get_climate_alerts()
            
            if alerts:
                alert_text = f"🚨 {len(alerts)} Active Alerts:\n"
                for alert in alerts[:3]:  # Show top 3 alerts
                    alert_text += f"• {alert['material_name']}: {alert['message']}\n"
                self.alerts_label.config(text=alert_text)
            else:
                self.alerts_label.config(text="✅ No active climate alerts")
            
            # Get forecast data
            forecast_data = self.climate_manager.get_climate_forecast(7)
            
            # Update forecast treeview
            self.forecast_tree.delete(*self.forecast_tree.get_children())
            for forecast in forecast_data:
                self.forecast_tree.insert('', 'end', values=(
                    forecast['material_name'],
                    forecast['forecast_date'].strftime('%Y-%m-%d') if hasattr(forecast['forecast_date'], 'strftime') else str(forecast['forecast_date']),
                    forecast['expected_condition'][:40] + "..." if len(forecast['expected_condition']) > 40 else forecast['expected_condition'],
                    forecast['risk_level'],
                    f"{forecast['days_from_now']} days"
                ))
                
        except Exception as e:
            if hasattr(self, 'alerts_label'):
                self.alerts_label.config(text=f"Error loading warnings data: {str(e)}")
    
    def refresh_actions_data(self):
        """Refresh data for actions tab"""
        try:
            # Try to refresh enhanced actions first
            if hasattr(self, 'actions_ui') and self.actions_ui:
                self.actions_ui.refresh_data()
        except Exception as e:
            pass  # Silently fail for actions refresh
    
    def on_tab_changed(self, event):
        """Handle tab change events"""
        selected_tab = event.widget.tab('current')['text']
        
        # Refresh data when switching to specific tabs
        if '📊 Overview' in selected_tab:
            self.refresh_overview_data()
        elif '⚠️ Warnings' in selected_tab:
            self.refresh_warnings_data()
        elif '🎯 Actions' in selected_tab:
            self.refresh_actions_data()
    
    def get_current_tab(self):
        """Get currently selected tab"""
        return self.subtabs_notebook.tab('current')['text']
