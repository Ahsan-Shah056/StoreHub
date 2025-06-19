"""
Climate Warnings UI Module
Enhanced warnings subtab with alerts, forecasts, and notifications (no charts)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

# Import climate components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from climate_base import ClimateBaseUI, ClimateConstants, create_risk_indicator
import climate_data

class ClimateWarningsUI(ClimateBaseUI):
    """Enhanced Climate Warnings subtab"""
    
    def __init__(self, parent, callbacks):
        super().__init__(parent, callbacks)
        self.climate_manager = climate_data.climate_manager
        self.create_interface()
    
    def create_interface(self):
        """Create the enhanced warnings interface"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Header section
        self.create_header_section(main_frame)
        
        # Active alerts section
        self.create_alerts_section(main_frame)
        
        # Forecast section
        self.create_forecast_section(main_frame)
        
        # Risk timeline section
        self.create_timeline_section(main_frame)
        
        # Load initial data
        self.refresh_data()
    
    def create_header_section(self, parent):
        """Create header with warnings summary"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="🚨 Climate Warnings & Alerts",
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(side='left')
        
        # Controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        # Refresh button
        refresh_btn = ttk.Button(controls_frame,
                                text="🔄 Refresh",
                                command=self.refresh_data)
        refresh_btn.pack(side='right', padx=(5, 0))
        
        # Last updated label
        self.last_updated_label = ttk.Label(controls_frame,
                                           text="Last updated: Loading...",
                                           font=ClimateConstants.SMALL_FONT)
        self.last_updated_label.pack(side='right', padx=(0, 10))
        
        # Summary cards frame
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill='x', pady=(0, 10))
        
        # Create summary cards
        self.create_summary_cards(summary_frame)
    
    def create_summary_cards(self, parent):
        """Create warning summary cards"""
        # Critical alerts card
        self.critical_frame = ttk.LabelFrame(parent, text="🔴 Critical Alerts", padding="10")
        self.critical_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.critical_count_label = ttk.Label(self.critical_frame,
                                             text="0",
                                             font=ClimateConstants.LARGE_FONT,
                                             foreground=ClimateConstants.DANGER_COLOR)
        self.critical_count_label.pack()
        
        self.critical_desc_label = ttk.Label(self.critical_frame,
                                            text="Immediate action required",
                                            font=ClimateConstants.SMALL_FONT)
        self.critical_desc_label.pack()
        
        # High alerts card
        self.high_frame = ttk.LabelFrame(parent, text="🟡 High Alerts", padding="10")
        self.high_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.high_count_label = ttk.Label(self.high_frame,
                                         text="0",
                                         font=ClimateConstants.LARGE_FONT,
                                         foreground=ClimateConstants.WARNING_COLOR)
        self.high_count_label.pack()
        
        self.high_desc_label = ttk.Label(self.high_frame,
                                        text="Requires monitoring",
                                        font=ClimateConstants.SMALL_FONT)
        self.high_desc_label.pack()
        
        # Active forecasts card
        self.forecast_frame = ttk.LabelFrame(parent, text="📅 7-Day Forecast", padding="10")
        self.forecast_frame.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        self.forecast_count_label = ttk.Label(self.forecast_frame,
                                             text="0",
                                             font=ClimateConstants.LARGE_FONT,
                                             foreground=ClimateConstants.INFO_COLOR)
        self.forecast_count_label.pack()
        
        self.forecast_desc_label = ttk.Label(self.forecast_frame,
                                            text="Upcoming conditions",
                                            font=ClimateConstants.SMALL_FONT)
        self.forecast_desc_label.pack()
    
    def create_alerts_section(self, parent):
        """Create active alerts section"""
        alerts_container = ttk.LabelFrame(parent, text="🚨 Active Alerts", padding="10")
        alerts_container.pack(fill='x', pady=(0, 10))
        
        # Alerts treeview
        columns = ('Severity', 'Material', 'Alert Type', 'Message', 'Time', 'Action')
        self.alerts_tree = ttk.Treeview(alerts_container, columns=columns, show='headings', height=6)
        
        # Configure columns
        column_widths = {
            'Severity': 80,
            'Material': 120,
            'Alert Type': 120,
            'Message': 300,
            'Time': 120,
            'Action': 100
        }
        
        for col in columns:
            self.alerts_tree.heading(col, text=col)
            self.alerts_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbars
        alerts_scroll_y = ttk.Scrollbar(alerts_container, orient="vertical", command=self.alerts_tree.yview)
        alerts_scroll_x = ttk.Scrollbar(alerts_container, orient="horizontal", command=self.alerts_tree.xview)
        self.alerts_tree.configure(yscrollcommand=alerts_scroll_y.set, xscrollcommand=alerts_scroll_x.set)
        
        # Pack treeview and scrollbars
        self.alerts_tree.grid(row=0, column=0, sticky='nsew')
        alerts_scroll_y.grid(row=0, column=1, sticky='ns')
        alerts_scroll_x.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        alerts_container.grid_rowconfigure(0, weight=1)
        alerts_container.grid_columnconfigure(0, weight=1)
        
        # Bind double-click event
        self.alerts_tree.bind('<Double-1>', self.on_alert_details)
    
    def create_forecast_section(self, parent):
        """Create forecast section with table only (no charts)"""
        forecast_container = ttk.LabelFrame(parent, text="📊 7-Day Climate Forecast", padding="10")
        forecast_container.pack(fill='both', expand=True, pady=(0, 10))
        
        # Forecast details table
        forecast_columns = ('Date', 'Material', 'Condition', 'Risk', 'Impact')
        self.forecast_tree = ttk.Treeview(forecast_container, columns=forecast_columns, show='headings', height=10)
        
        # Configure forecast columns
        for col in forecast_columns:
            self.forecast_tree.heading(col, text=col)
            if col == 'Condition':
                self.forecast_tree.column(col, width=200)
            else:
                self.forecast_tree.column(col, width=80)
        
        # Add scrollbar for forecast
        forecast_scroll = ttk.Scrollbar(forecast_container, orient="vertical", command=self.forecast_tree.yview)
        self.forecast_tree.configure(yscrollcommand=forecast_scroll.set)
        
        # Pack forecast treeview
        self.forecast_tree.pack(side='left', fill='both', expand=True)
        forecast_scroll.pack(side='right', fill='y')
    
    def create_timeline_section(self, parent):
        """Create risk timeline summary section (no charts)"""
        timeline_container = ttk.LabelFrame(parent, text="📈 Risk Timeline Summary", padding="10")
        timeline_container.pack(fill='x', pady=(0, 5))
        
        # Timeline summary text
        timeline_label = ttk.Label(timeline_container,
                                  text="Climate risk patterns over the last 30 days:\n"
                                       "Recent trend analysis and historical risk data will be displayed here.",
                                  font=ClimateConstants.BODY_FONT,
                                  justify='left')
        timeline_label.pack(anchor='w')
    
    def refresh_data(self):
        """Refresh all warnings data"""
        try:
            # Update timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.last_updated_label.config(text=f"Last updated: {current_time}")
            
            # Get warnings data
            alerts_data = self.climate_manager.get_climate_alerts()
            forecast_data = self.climate_manager.get_climate_forecast(7)
            
            # Update summary cards
            self.update_summary_cards(alerts_data)
            
            # Update alerts table
            self.update_alerts_table(alerts_data)
            
            # Update forecast table
            self.update_forecast_data(forecast_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh warnings data: {str(e)}")
    
    def update_summary_cards(self, alerts_data):
        """Update warning summary cards"""
        # Count alerts by severity
        critical_count = len([alert for alert in alerts_data if alert.get('severity') == 'CRITICAL'])
        high_count = len([alert for alert in alerts_data if alert.get('severity') == 'HIGH'])
        
        # Update critical alerts
        self.critical_count_label.config(text=str(critical_count))
        if critical_count > 0:
            self.critical_desc_label.config(text=f"{critical_count} critical issues")
        else:
            self.critical_desc_label.config(text="No critical alerts")
        
        # Update high alerts
        self.high_count_label.config(text=str(high_count))
        if high_count > 0:
            self.high_desc_label.config(text=f"{high_count} monitoring required")
        else:
            self.high_desc_label.config(text="No high alerts")
        
        # Update forecast count (placeholder)
        self.forecast_count_label.config(text="7")
        self.forecast_desc_label.config(text="Days covered")
    
    def update_alerts_table(self, alerts_data):
        """Update active alerts table with predictive alerts"""
        # Clear existing data
        self.alerts_tree.delete(*self.alerts_tree.get_children())
        
        if not alerts_data:
            # Insert no alerts message
            self.alerts_tree.insert('', 'end', values=(
                '✅', 'All Materials', 'System', 'No active climate alerts', 
                datetime.now().strftime('%H:%M'), 'Monitor'
            ))
            return
        
        # Populate with alerts data
        for alert in alerts_data:
            # Determine severity icon
            severity = alert.get('severity', 'MEDIUM')
            if severity == 'CRITICAL':
                severity_icon = '�'
            elif severity == 'HIGH':
                severity_icon = '🟡'
            else:
                severity_icon = '🟢'
            
            # Format alert type for display
            alert_type = alert.get('alert_type', 'General')
            if alert_type.startswith('LONG_TERM_'):
                alert_type = alert_type.replace('LONG_TERM_', '').replace('_', ' ').title()
                display_type = f"📅 {alert_type}"
            elif alert_type.startswith('PREDICTED_'):
                alert_type = alert_type.replace('PREDICTED_', '').replace('_', ' ').title()
                display_type = f"⚡ {alert_type}"
            else:
                display_type = alert_type.replace('_', ' ').title()
            
            # Format time until impact
            days_until = alert.get('days_until_impact', 0)
            if days_until == 0:
                time_display = "Now"
            elif days_until == 1:
                time_display = "1 day"
            else:
                time_display = f"{days_until} days"
            
            # Get recommendation or default action
            action = alert.get('recommendation', alert.get('recommended_action', 'Review'))
            if len(action) > 40:
                action = action[:37] + "..."
            
            # Format message for display
            message = alert.get('message', 'No message')
            if len(message) > 80:
                message = message[:77] + "..."
            
            self.alerts_tree.insert('', 'end', values=(
                severity_icon,
                alert.get('material_name', 'Unknown'),
                display_type,
                message,
                time_display,
                action
            ))
    
    def update_forecast_data(self, forecast_data):
        """Update forecast table"""
        # Update forecast table
        self.forecast_tree.delete(*self.forecast_tree.get_children())
        
        for forecast in forecast_data:
            forecast_date = forecast.get('forecast_date')
            date_str = forecast_date.strftime('%m/%d') if hasattr(forecast_date, 'strftime') else str(forecast_date)
            
            self.forecast_tree.insert('', 'end', values=(
                date_str,
                forecast.get('material_name', 'Unknown'),
                forecast.get('expected_condition', 'Unknown')[:30] + "..." if len(forecast.get('expected_condition', '')) > 30 else forecast.get('expected_condition', ''),
                forecast.get('risk_level', 'LOW'),
                forecast.get('expected_impact', 'Minimal')
            ))
    
    
    def on_alert_details(self, event):
        """Handle alert details view with enhanced predictive information"""
        selection = self.alerts_tree.selection()
        if selection:
            item = self.alerts_tree.item(selection[0])
            values = item['values']
            if len(values) >= 4:
                # Get the alert data for more detailed information
                alerts_data = self.climate_manager.get_climate_alerts()
                
                # Find the matching alert based on material and message
                selected_alert = None
                for alert in alerts_data:
                    if (alert.get('material_name') == values[1] and 
                        alert.get('message', '')[:77] == values[3][:77]):
                        selected_alert = alert
                        break
                
                if selected_alert:
                    # Show detailed information for predictive alerts
                    details = f"📊 PREDICTIVE ALERT DETAILS\n\n"
                    details += f"🏷️ Material: {selected_alert['material_name']}\n"
                    details += f"⚠️ Alert Type: {selected_alert['alert_type']}\n"
                    details += f"🔥 Severity: {selected_alert['severity']}\n"
                    details += f"⏰ Impact Timeline: {selected_alert['days_until_impact']} days\n"
                    details += f"🎯 Urgency Score: {selected_alert.get('urgency_score', 0)}/100\n\n"
                    
                    details += f"📝 Description:\n{selected_alert['message']}\n\n"
                    
                    if 'recommendation' in selected_alert:
                        details += f"💡 Recommendation:\n{selected_alert['recommendation']}\n\n"
                    
                    # Add specific details based on alert type
                    if 'expected_delay' in selected_alert:
                        details += f"📉 Expected Delay: {selected_alert['expected_delay']}\n"
                    if 'peak_delay' in selected_alert:
                        details += f"📈 Peak Delay: {selected_alert['peak_delay']}\n"
                    if 'duration_days' in selected_alert:
                        details += f"⏳ Duration: {selected_alert['duration_days']} days\n"
                    if 'affected_products_count' in selected_alert:
                        details += f"📦 Affected Products: {selected_alert['affected_products_count']}\n"
                    if 'production_drop' in selected_alert:
                        details += f"📊 Production Drop: {selected_alert['production_drop']}\n"
                    if 'weather_condition' in selected_alert:
                        details += f"🌦️ Weather: {selected_alert['weather_condition']}\n"
                    
                    details += f"\n🕐 Horizon: {selected_alert.get('horizon', 'Unknown')}"
                    
                    messagebox.showinfo("Predictive Alert Details", details)
                else:
                    # Fallback to basic information
                    messagebox.showinfo("Alert Details", 
                                       f"Material: {values[1]}\n"
                                       f"Type: {values[2]}\n"
                                       f"Message: {values[3]}\n"
                                       f"Time: {values[4]}\n"
                                       f"Recommended Action: {values[5] if len(values) > 5 else 'Review'}")
