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
        
        # Alert settings button (placeholder)
        settings_btn = ttk.Button(controls_frame,
                                 text="⚙️ Settings",
                                 command=self.open_alert_settings)
        settings_btn.pack(side='right', padx=(5, 0))
        
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
        """Update active alerts table"""
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
            severity_icon = '🔴' if alert.get('severity') == 'CRITICAL' else '🟡'
            
            self.alerts_tree.insert('', 'end', values=(
                severity_icon,
                alert.get('material_name', 'Unknown'),
                alert.get('alert_type', 'General'),
                alert.get('message', 'No message')[:60] + "..." if len(alert.get('message', '')) > 60 else alert.get('message', ''),
                alert.get('created_at', datetime.now()).strftime('%H:%M') if hasattr(alert.get('created_at'), 'strftime') else str(alert.get('created_at', '')),
                alert.get('recommended_action', 'Review')
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
        """Handle alert details view"""
        selection = self.alerts_tree.selection()
        if selection:
            item = self.alerts_tree.item(selection[0])
            values = item['values']
            if len(values) >= 4:
                messagebox.showinfo("Alert Details", 
                                   f"Material: {values[1]}\n"
                                   f"Type: {values[2]}\n"
                                   f"Message: {values[3]}\n"
                                   f"Time: {values[4]}\n"
                                   f"Recommended Action: {values[5] if len(values) > 5 else 'Review'}")
    
    def open_alert_settings(self):
        """Open alert settings configuration dialog"""
        settings_window = tk.Toplevel(self.parent)
        settings_window.title("Climate Alert Settings")
        settings_window.geometry("600x500")
        settings_window.resizable(True, True)
        
        # Make window modal
        settings_window.transient(self.parent)
        settings_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🔧 Climate Alert Settings", 
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(pady=(0, 15))
        
        # Create notebook for different setting categories
        settings_notebook = ttk.Notebook(main_frame)
        settings_notebook.pack(fill='both', expand=True, pady=(0, 15))
        
        # Thresholds tab
        thresholds_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(thresholds_tab, text="⚠️ Thresholds")
        self.create_thresholds_settings(thresholds_tab)
        
        # Notifications tab
        notifications_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(notifications_tab, text="📢 Notifications")
        self.create_notifications_settings(notifications_tab)
        
        # Alert rules tab
        rules_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(rules_tab, text="📋 Rules")
        self.create_rules_settings(rules_tab)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        def save_settings():
            """Save alert settings"""
            # Here you would save settings to a configuration file or database
            messagebox.showinfo("Success", "Alert settings saved successfully!")
            settings_window.destroy()
            
        def reset_defaults():
            """Reset to default settings"""
            if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
                # Reset logic here
                messagebox.showinfo("Reset", "Settings reset to defaults")
                
        def cancel_settings():
            """Cancel without saving"""
            settings_window.destroy()
            
        ttk.Button(buttons_frame, text="💾 Save Settings", 
                  command=save_settings).pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="🔄 Reset Defaults", 
                  command=reset_defaults).pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="❌ Cancel", 
                  command=cancel_settings).pack(side='left')
                  
    def create_thresholds_settings(self, parent):
        """Create threshold settings interface"""
        container = ttk.Frame(parent, padding="10")
        container.pack(fill='both', expand=True)
        
        # Risk level thresholds
        ttk.Label(container, text="Risk Level Thresholds", 
                 font=ClimateConstants.BODY_FONT).pack(anchor='w', pady=(0, 10))
        
        # Material-specific thresholds
        materials = ["Cotton", "Rice", "Wheat", "Sugarcane"]
        self.threshold_vars = {}
        
        for material in materials:
            material_frame = ttk.LabelFrame(container, text=f"{material} Thresholds", padding="10")
            material_frame.pack(fill='x', pady=(0, 10))
            
            # Create threshold sliders for each risk level
            levels = ["Low", "Medium", "High", "Critical"]
            self.threshold_vars[material] = {}
            
            for i, level in enumerate(levels):
                level_frame = ttk.Frame(material_frame)
                level_frame.pack(fill='x', pady=2)
                
                ttk.Label(level_frame, text=f"{level}:", width=10).pack(side='left')
                
                threshold_var = tk.DoubleVar(value=25 + i * 25)  # Default values
                self.threshold_vars[material][level] = threshold_var
                
                threshold_scale = ttk.Scale(level_frame, from_=0, to=100, 
                                          variable=threshold_var, orient='horizontal')
                threshold_scale.pack(side='left', fill='x', expand=True, padx=(5, 5))
                
                value_label = ttk.Label(level_frame, text="25%", width=5)
                value_label.pack(side='right')
                
                # Update label when scale changes
                def update_label(val, label=value_label, var=threshold_var):
                    label.config(text=f"{int(var.get())}%")
                
                threshold_scale.config(command=update_label)
                
    def create_notifications_settings(self, parent):
        """Create notification settings interface"""
        container = ttk.Frame(parent, padding="10")
        container.pack(fill='both', expand=True)
        
        # Notification methods
        ttk.Label(container, text="Notification Methods", 
                 font=ClimateConstants.BODY_FONT).pack(anchor='w', pady=(0, 10))
        
        methods_frame = ttk.LabelFrame(container, text="Enable Notifications", padding="10")
        methods_frame.pack(fill='x', pady=(0, 10))
        
        # Notification options
        self.notify_app = tk.BooleanVar(value=True)
        self.notify_email = tk.BooleanVar(value=False)
        self.notify_sms = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(methods_frame, text="In-App Notifications", 
                       variable=self.notify_app).pack(anchor='w')
        ttk.Checkbutton(methods_frame, text="Email Notifications", 
                       variable=self.notify_email).pack(anchor='w')
        ttk.Checkbutton(methods_frame, text="SMS Notifications", 
                       variable=self.notify_sms).pack(anchor='w')
        
        # Email settings
        email_frame = ttk.LabelFrame(container, text="Email Settings", padding="10")
        email_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(email_frame, text="Email Address:").pack(anchor='w')
        self.email_var = tk.StringVar(value="admin@company.com")
        ttk.Entry(email_frame, textvariable=self.email_var).pack(fill='x', pady=(0, 5))
        
        ttk.Label(email_frame, text="Alert Frequency:").pack(anchor='w')
        self.frequency_var = tk.StringVar(value="Immediate")
        frequency_combo = ttk.Combobox(email_frame, textvariable=self.frequency_var,
                                     values=["Immediate", "Hourly", "Daily", "Weekly"],
                                     state="readonly")
        frequency_combo.pack(fill='x')
        
        # Sound settings
        sound_frame = ttk.LabelFrame(container, text="Sound Alerts", padding="10")
        sound_frame.pack(fill='x')
        
        self.sound_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(sound_frame, text="Enable Sound Alerts", 
                       variable=self.sound_enabled).pack(anchor='w')
        
        ttk.Label(sound_frame, text="Alert Volume:").pack(anchor='w')
        self.volume_var = tk.DoubleVar(value=75)
        volume_scale = ttk.Scale(sound_frame, from_=0, to=100, 
                               variable=self.volume_var, orient='horizontal')
        volume_scale.pack(fill='x')
        
    def create_rules_settings(self, parent):
        """Create alert rules settings interface"""
        container = ttk.Frame(parent, padding="10")
        container.pack(fill='both', expand=True)
        
        # Rules list
        ttk.Label(container, text="Alert Rules", 
                 font=ClimateConstants.BODY_FONT).pack(anchor='w', pady=(0, 10))
        
        # Rules management frame
        rules_frame = ttk.Frame(container)
        rules_frame.pack(fill='both', expand=True)
        
        # Rules list
        columns = ('Rule Name', 'Condition', 'Action', 'Enabled')
        self.rules_tree = ttk.Treeview(rules_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.rules_tree.heading(col, text=col)
            self.rules_tree.column(col, width=150)
        
        # Add some sample rules
        sample_rules = [
            ("High Risk Cotton", "Cotton risk > 75%", "Send Alert", "Yes"),
            ("Weather Warning", "Storm forecast", "Create Action", "Yes"),
            ("Price Volatility", "Price change > 10%", "Lock Prices", "No")
        ]
        
        for rule in sample_rules:
            self.rules_tree.insert('', 'end', values=rule)
            
        # Scrollbar for rules
        rules_scrollbar = ttk.Scrollbar(rules_frame, orient="vertical", command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=rules_scrollbar.set)
        
        # Pack rules tree
        self.rules_tree.pack(side='left', fill='both', expand=True)
        rules_scrollbar.pack(side='right', fill='y')
        
        # Rules buttons
        rules_buttons_frame = ttk.Frame(container)
        rules_buttons_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(rules_buttons_frame, text="➕ Add Rule", 
                  command=self.add_alert_rule).pack(side='left', padx=(0, 5))
        ttk.Button(rules_buttons_frame, text="✏️ Edit Rule", 
                  command=self.edit_alert_rule).pack(side='left', padx=(0, 5))
        ttk.Button(rules_buttons_frame, text="🗑️ Delete Rule", 
                  command=self.delete_alert_rule).pack(side='left')
                  
    def add_alert_rule(self):
        """Add new alert rule"""
        messagebox.showinfo("Add Rule", "Rule creation dialog would open here")
        
    def edit_alert_rule(self):
        """Edit selected alert rule"""
        messagebox.showinfo("Edit Rule", "Rule editing dialog would open here")
        
    def delete_alert_rule(self):
        """Delete selected alert rule"""
        selection = self.rules_tree.selection()
        if selection:
            if messagebox.askyesno("Delete Rule", "Delete selected rule?"):
                self.rules_tree.delete(selection[0])
        else:
            messagebox.showwarning("Warning", "Please select a rule to delete")
