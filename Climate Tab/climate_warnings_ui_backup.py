"""
Climate Warnings UI Module
Modern, visually appealing warnings subtab with clean card-based layout
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
    """Modern Climate Warnings subtab with enhanced visual design"""
    
    def __init__(self, parent, callbacks):
        super().__init__(parent, callbacks)
        self.climate_manager = climate_data.climate_manager
        self.selected_filter = "ALL"
        self.current_alerts = []
        self.create_interface()
    
    def create_interface(self):
        """Create the modern, clean warnings interface"""
        # Main container
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill='both', expand=True)
        
        # Create scrollable canvas
        self.canvas = tk.Canvas(main_container, highlightthickness=0, bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def configure_canvas(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind('<Configure>', configure_canvas)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create interface sections
        self.create_header()
        self.create_filter_section()
        self.create_stats_summary()
        self.create_alerts_grid()
        
        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Load initial data
        self.refresh_data()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_header(self):
        """Create modern header section"""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill='x', padx=25, pady=(20, 15))
        
        # Title and refresh
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill='x')
        
        # Title
        title_label = ttk.Label(title_frame, 
                               text="⚠️ Climate Alerts & Warnings",
                               font=('Segoe UI', 16, 'bold'),
                               foreground='#2c3e50')
        title_label.pack(side='left')
        
        # Last updated info
        self.last_updated_label = ttk.Label(title_frame,
                                           text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
                                           font=('Segoe UI', 9),
                                           foreground='#6c757d')
        self.last_updated_label.pack(side='right', padx=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(title_frame,
                                text="🔄 Refresh",
                                command=self.refresh_data)
        refresh_btn.pack(side='right')
    
    def create_filter_section(self):
        """Create modern filter buttons"""
        filter_frame = ttk.Frame(self.scrollable_frame)
        filter_frame.pack(fill='x', padx=25, pady=(0, 20))
        
        # Filter label
        filter_label = ttk.Label(filter_frame,
                                text="Filter by:",
                                font=('Segoe UI', 10, 'bold'))
        filter_label.pack(side='left', padx=(0, 15))
        
        # Filter buttons
        self.filter_buttons = {}
        filters = [
            ("ALL", "🌍 All", "#6c757d"),
            ("CRITICAL", "🔴 Critical", "#dc3545"),
            ("HIGH", "🟠 High", "#fd7e14"),
            ("PREDICTIVE", "⚡ Predictive", "#0d6efd"),
            ("WEATHER", "🌦️ Weather", "#198754")
        ]
        
        for filter_id, label, color in filters:
            btn = tk.Button(filter_frame,
                          text=label,
                          command=lambda f=filter_id: self.set_filter(f),
                          font=('Segoe UI', 9),
                          relief='flat',
                          bd=0,
                          padx=15,
                          pady=8,
                          cursor='hand2')
            btn.pack(side='left', padx=(0, 8))
            self.filter_buttons[filter_id] = (btn, color)
        
        # Set initial filter
        self.set_filter("ALL")
    
    def create_stats_summary(self):
        """Create summary statistics cards"""
        stats_frame = ttk.Frame(self.scrollable_frame)
        stats_frame.pack(fill='x', padx=25, pady=(0, 25))
        
        # Stats cards container
        cards_container = ttk.Frame(stats_frame)
        cards_container.pack(fill='x')
        
        # Create stat cards
        self.stats_cards = {}
        stats = [
            ("total", "📊 Total Alerts", "0", "#6c757d"),
            ("critical", "🔴 Critical", "0", "#dc3545"),
            ("high", "🟠 High Priority", "0", "#fd7e14"),
            ("active", "⚡ Active Risks", "0", "#0d6efd")
        ]
        
        for i, (stat_id, label, value, color) in enumerate(stats):
            card = self.create_stat_card(cards_container, label, value, color, i)
            self.stats_cards[stat_id] = card
    
    def create_stat_card(self, parent, label, value, color, column):
        """Create individual stat card"""
        card_frame = tk.Frame(parent, 
                             bg='white',
                             relief='solid',
                             bd=1)
        card_frame.grid(row=0, column=column, padx=(0, 15) if column < 3 else 0, 
                       pady=0, sticky='ew')
        
        # Configure grid weight
        parent.grid_columnconfigure(column, weight=1)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Value
        value_label = tk.Label(content_frame,
                              text=value,
                              font=('Segoe UI', 18, 'bold'),
                              fg=color,
                              bg='white')
        value_label.pack()
        
        # Label
        label_label = tk.Label(content_frame,
                              text=label,
                              font=('Segoe UI', 9),
                              fg='#6c757d',
                              bg='white')
        label_label.pack()
        
        return {"frame": card_frame, "value": value_label, "label": label_label}
    
    def create_alerts_grid(self):
        """Create modern alerts grid with cards"""
        alerts_frame = ttk.Frame(self.scrollable_frame)
        alerts_frame.pack(fill='both', expand=True, padx=25, pady=(0, 25))
        
        # Alerts header
        header_frame = ttk.Frame(alerts_frame)
        header_frame.pack(fill='x', pady=(0, 15))
        
        alerts_title = ttk.Label(header_frame,
                                text="🚨 Active Alerts",
                                font=('Segoe UI', 14, 'bold'),
                                foreground='#2c3e50')
        alerts_title.pack(side='left')
        
        # Alerts container for cards
        self.alerts_container = ttk.Frame(alerts_frame)
        self.alerts_container.pack(fill='both', expand=True)
        
        # No alerts placeholder
        self.no_alerts_frame = ttk.Frame(self.alerts_container)
        no_alerts_label = ttk.Label(self.no_alerts_frame,
                                   text="🌅 No active alerts\nSystem is running smoothly",
                                   font=('Segoe UI', 12),
                                   foreground='#6c757d',
                                   justify='center')
        no_alerts_label.pack(expand=True)
    
    def set_filter(self, filter_type):
        """Set the active filter and update display"""
        self.selected_filter = filter_type
        
        # Update button styles
        for btn_id, (button, color) in self.filter_buttons.items():
            if btn_id == filter_type:
                button.configure(bg=color, fg='white')
            else:
                button.configure(bg='#e9ecef', fg='#6c757d')
        
        # Refresh alerts display
        self.update_alerts_display()
    
    def refresh_data(self):
        """Refresh all data"""
        try:
            # Get fresh data
            self.current_alerts = self.climate_manager.get_climate_alerts()
            
            # Update timestamp
            self.last_updated_label.config(
                text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            # Update statistics
            self.update_statistics()
            
            # Update alerts display
            self.update_alerts_display()
            
        except Exception as e:
            print(f"Error refreshing warnings data: {e}")
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")
    
    def update_statistics(self):
        """Update summary statistics"""
        if not self.current_alerts:
            stats = {"total": 0, "critical": 0, "high": 0, "active": 0}
        else:
            total = len(self.current_alerts)
            critical = len([a for a in self.current_alerts if a.get('severity') == 'CRITICAL'])
            high = len([a for a in self.current_alerts if a.get('severity') == 'HIGH'])
            active = len([a for a in self.current_alerts if a.get('type') == 'predictive'])
            
            stats = {
                "total": total,
                "critical": critical, 
                "high": high,
                "active": active
            }
        
        # Update card values
        for stat_id, value in stats.items():
            if stat_id in self.stats_cards:
                self.stats_cards[stat_id]["value"].config(text=str(value))
    
    def update_alerts_display(self):
        """Update the alerts display based on current filter"""
        # Clear existing alerts
        for widget in self.alerts_container.winfo_children():
            widget.destroy()
        
        # Filter alerts
        filtered_alerts = self.filter_alerts(self.current_alerts)
        
        if not filtered_alerts:
            # Show no alerts message
            self.no_alerts_frame = ttk.Frame(self.alerts_container)
            self.no_alerts_frame.pack(fill='both', expand=True, pady=50)
            
            no_alerts_label = ttk.Label(self.no_alerts_frame,
                                       text="🌅 No alerts match your filter\nTry selecting a different filter",
                                       font=('Segoe UI', 12),
                                       foreground='#6c757d',
                                       justify='center')
            no_alerts_label.pack(expand=True)
            return
        
        # Create alert cards
        for i, alert in enumerate(filtered_alerts):
            self.create_alert_card(self.alerts_container, alert, i)
    
    def filter_alerts(self, alerts):
        """Filter alerts based on selected filter"""
        if self.selected_filter == "ALL":
            return alerts
        elif self.selected_filter == "CRITICAL":
            return [a for a in alerts if a.get('severity') == 'CRITICAL']
        elif self.selected_filter == "HIGH":
            return [a for a in alerts if a.get('severity') == 'HIGH']
        elif self.selected_filter == "PREDICTIVE":
            return [a for a in alerts if a.get('type') == 'predictive']
        elif self.selected_filter == "WEATHER":
            return [a for a in alerts if 'weather' in a.get('title', '').lower() or 
                   'weather' in a.get('description', '').lower()]
        return alerts
    
    def create_alert_card(self, parent, alert, index):
        """Create a modern alert card"""
        # Main card frame
        card_frame = tk.Frame(parent,
                             bg='white',
                             relief='solid',
                             bd=1)
        card_frame.pack(fill='x', pady=(0, 12))
        
        # Add hover effect
        def on_enter(e):
            card_frame.configure(relief='solid', bd=2)
        def on_leave(e):
            card_frame.configure(relief='solid', bd=1)
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Header row
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 8))
        
        # Severity indicator
        severity = alert.get('severity', 'MEDIUM')
        severity_colors = {
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14', 
            'MEDIUM': '#ffc107',
            'LOW': '#28a745'
        }
        severity_icons = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡', 
            'LOW': '🟢'
        }
        
        severity_label = tk.Label(header_frame,
                                 text=f"{severity_icons.get(severity, '⚪')} {severity}",
                                 font=('Segoe UI', 9, 'bold'),
                                 fg=severity_colors.get(severity, '#6c757d'),
                                 bg='white')
        severity_label.pack(side='left')
        
        # Time info
        time_text = self.format_time_info(alert)
        time_label = tk.Label(header_frame,
                             text=time_text,
                             font=('Segoe UI', 9),
                             fg='#6c757d',
                             bg='white')
        time_label.pack(side='right')
        
        # Alert title
        title_frame = tk.Frame(content_frame, bg='white')
        title_frame.pack(fill='x', pady=(0, 8))
        
        title_label = tk.Label(title_frame,
                              text=alert.get('title', 'Climate Alert'),
                              font=('Segoe UI', 12, 'bold'),
                              fg='#2c3e50',
                              bg='white',
                              anchor='w')
        title_label.pack(fill='x')
        
        # Alert description
        description = alert.get('description', 'No description available')
        if len(description) > 120:
            description = description[:117] + "..."
        
        desc_label = tk.Label(title_frame,
                             text=description,
                             font=('Segoe UI', 10),
                             fg='#495057',
                             bg='white',
                             anchor='w',
                             wraplength=600)
        desc_label.pack(fill='x', pady=(4, 0))
        
        # Footer with material info and action button
        footer_frame = tk.Frame(content_frame, bg='white')
        footer_frame.pack(fill='x', pady=(8, 0))
        
        # Material info
        material_name = alert.get('material_name', 'Unknown')
        material_label = tk.Label(footer_frame,
                                 text=f"📦 {material_name}",
                                 font=('Segoe UI', 9),
                                 fg='#6c757d',
                                 bg='white')
        material_label.pack(side='left')
        
        # View details button
        details_btn = tk.Button(footer_frame,
                               text="View Details →",
                               command=lambda: self.show_alert_details(alert),
                               font=('Segoe UI', 9),
                               fg='#0d6efd',
                               bg='white',
                               relief='flat',
                               bd=0,
                               cursor='hand2')
        details_btn.pack(side='right')
    
    def format_time_info(self, alert):
        """Format time information for alert"""
        if alert.get('type') == 'predictive':
            days_ahead = alert.get('days_ahead', 0)
            if days_ahead == 0:
                return "📅 Today"
            elif days_ahead == 1:
                return "📅 Tomorrow"
            else:
                return f"📅 In {days_ahead} days"
        else:
            return "📅 Current condition"
    
    def show_alert_details(self, alert):
        """Show detailed alert information in popup"""
        # Create popup window
        popup = tk.Toplevel(self.parent)
        popup.title(f"Alert Details - {alert.get('title', 'Alert')}")
        popup.geometry("500x400")
        popup.configure(bg='white')
        popup.transient(self.parent)
        popup.grab_set()
        
        # Center the popup
        popup.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50))
        
        # Main content frame
        main_frame = tk.Frame(popup, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame,
                              text=alert.get('title', 'Alert Details'),
                              font=('Segoe UI', 14, 'bold'),
                              fg='#2c3e50',
                              bg='white')
        title_label.pack(anchor='w', pady=(0, 15))
        
        # Details text area
        details_frame = tk.Frame(main_frame, bg='white')
        details_frame.pack(fill='both', expand=True)
        
        details_text = tk.Text(details_frame,
                              font=('Segoe UI', 10),
                              wrap='word',
                              bg='#f8f9fa',
                              relief='flat',
                              padx=15,
                              pady=15)
        
        # Build details content
        details_content = self.build_alert_details(alert)
        details_text.insert('1.0', details_content)
        details_text.configure(state='disabled')
        
        # Scrollbar for details
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        details_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        close_btn = tk.Button(main_frame,
                             text="Close",
                             command=popup.destroy,
                             font=('Segoe UI', 10),
                             bg='#0d6efd',
                             fg='white',
                             relief='flat',
                             padx=20,
                             pady=8,
                             cursor='hand2')
        close_btn.pack(pady=(15, 0))
    
    def build_alert_details(self, alert):
        """Build detailed alert information text"""
        details = []
        
        # Basic information
        details.append("📋 ALERT INFORMATION")
        details.append("="*50)
        details.append(f"Severity: {alert.get('severity', 'Unknown')}")
        details.append(f"Type: {alert.get('type', 'Unknown').title()}")
        details.append(f"Material: {alert.get('material_name', 'Unknown')}")
        details.append(f"Status: {alert.get('status', 'Active')}")
        details.append("")
        
        # Description
        details.append("📝 DESCRIPTION")
        details.append("="*50)
        details.append(alert.get('description', 'No description available'))
        details.append("")
        
        # Recommendations
        if alert.get('recommendations'):
            details.append("💡 RECOMMENDATIONS")
            details.append("="*50)
            recommendations = alert.get('recommendations', [])
            if isinstance(recommendations, list):
                for i, rec in enumerate(recommendations, 1):
                    details.append(f"{i}. {rec}")
            else:
                details.append(str(recommendations))
            details.append("")
        
        # Timing information
        details.append("⏰ TIMING")
        details.append("="*50)
        if alert.get('type') == 'predictive':
            days_ahead = alert.get('days_ahead', 0)
            details.append(f"Expected in: {days_ahead} days")
            target_date = datetime.now() + timedelta(days=days_ahead)
            details.append(f"Target date: {target_date.strftime('%Y-%m-%d')}")
        else:
            details.append("Status: Current condition")
            details.append(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        details.append("")
        
        # Additional metrics
        if alert.get('delay_percent'):
            details.append("📊 METRICS")
            details.append("="*50)
            details.append(f"Delay percentage: {alert.get('delay_percent', 0):.1f}%")
            if alert.get('production_impact'):
                details.append(f"Production impact: {alert.get('production_impact', 0):.1f}")
        
        return "\n".join(details)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create sections
        self.create_header_section()
        self.create_filter_section()
        self.create_stats_cards()
        self.create_alerts_grid()
        
        # Load initial data
        self.refresh_data()
    
    def create_header_section(self):
        """Create modern header with title and controls"""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Left side - Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left', fill='x', expand=True)
        
        title_label = ttk.Label(title_frame,
                               text="🚨 Climate Alerts & Warnings",
                               font=('Arial', 18, 'bold'))
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(title_frame,
                                  text="Real-time climate monitoring and predictive alerts",
                                  font=('Arial', 10))
        subtitle_label.pack(anchor='w', pady=(2, 0))
        
        # Right side - Controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        # Last updated
        self.last_updated_label = ttk.Label(controls_frame,
                                           text="Last updated: Loading...",
                                           font=('Arial', 9),
                                           foreground='#6c757d')
        self.last_updated_label.pack(anchor='e')
        
        # Refresh button
        refresh_btn = ttk.Button(controls_frame,
                                text="🔄 Refresh",
                                command=self.refresh_data,
                                style="Accent.TButton")
        refresh_btn.pack(anchor='e', pady=(5, 0))
    
    def create_filter_section(self):
        """Create filter tabs for different alert types"""
        filter_frame = ttk.Frame(self.scrollable_frame)
        filter_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # Filter buttons
        filters = [
            ("ALL", "🌍 All Alerts"),
            ("CRITICAL", "🔴 Critical"),
            ("PREDICTIVE", "⚡ Predictive"),
            ("SUPPLY", "📦 Supply Chain"),
            ("WEATHER", "🌦️ Weather")
        ]
        
        for filter_id, label in filters:
            btn = ttk.Button(filter_frame,
                           text=label,
                           command=lambda f=filter_id: self.set_filter(f),
                           style="Outline.TButton")
            btn.pack(side='left', padx=(0, 8))
            
            # Store button reference for styling
            if filter_id == "ALL":
                btn.configure(style="Accent.TButton")
    
    def create_stats_cards(self):
        """Create modern statistics cards"""
        stats_container = ttk.Frame(self.scrollable_frame)
        stats_container.pack(fill='x', padx=20, pady=(0, 20))
        
        # Create a frame for the cards row
        cards_row = ttk.Frame(stats_container)
        cards_row.pack(fill='x')
        
        # Critical alerts card
        self.critical_card = self.create_stat_card(
            cards_row, "🔴", "Critical Alerts", "0", "#dc3545", 0)
        
        # High priority card
        self.high_card = self.create_stat_card(
            cards_row, "🟡", "High Priority", "0", "#ffc107", 1)
        
        # Active forecasts card
        self.forecast_card = self.create_stat_card(
            cards_row, "📅", "7-Day Forecast", "0", "#17a2b8", 2)
        
        # Materials affected card
        self.materials_card = self.create_stat_card(
            cards_row, "🏭", "Materials Affected", "0", "#28a745", 3)
    
    def create_stat_card(self, parent, icon, title, value, color, position):
        """Create a modern statistics card"""
        # Card frame with border effect
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.grid(row=0, column=position, sticky='ew', padx=(0, 15))
        parent.grid_columnconfigure(position, weight=1)
        
        # Inner padding frame
        inner_frame = tk.Frame(card_frame, bg='white')
        inner_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Icon and value row
        top_row = tk.Frame(inner_frame, bg='white')
        top_row.pack(fill='x')
        
        # Icon
        icon_label = tk.Label(top_row, text=icon, font=('Arial', 20), bg='white')
        icon_label.pack(side='left')
        
        # Value
        value_label = tk.Label(top_row, text=value, font=('Arial', 24, 'bold'), 
                              fg=color, bg='white')
        value_label.pack(side='right')
        
        # Title
        title_label = tk.Label(inner_frame, text=title, font=('Arial', 11), 
                              fg='#6c757d', bg='white')
        title_label.pack(anchor='w', pady=(8, 0))
        
        # Store references for updating
        card_data = {
            'frame': card_frame,
            'value_label': value_label,
            'title_label': title_label
        }
        
        return card_data
    
    def create_alerts_grid(self):
        """Create modern alerts grid with cards instead of treeview"""
        alerts_container = ttk.Frame(self.scrollable_frame)
        alerts_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Section header
        header_frame = ttk.Frame(alerts_container)
        header_frame.pack(fill='x', pady=(0, 15))
        
        alerts_title = ttk.Label(header_frame,
                                text="Active Alerts",
                                font=('Arial', 14, 'bold'))
        alerts_title.pack(side='left')
        
        # Alerts grid container
        self.alerts_grid_frame = ttk.Frame(alerts_container)
        self.alerts_grid_frame.pack(fill='both', expand=True)
        
        # Configure grid for responsive layout
        self.alerts_grid_frame.grid_columnconfigure(0, weight=1)
        self.alerts_grid_frame.grid_columnconfigure(1, weight=1)
    
    def create_alert_card(self, parent, alert_data, row, col):
        """Create an individual alert card"""
        # Determine card colors based on severity
        severity = alert_data.get('severity', 'MEDIUM')
        if severity == 'CRITICAL':
            border_color = '#dc3545'
            bg_color = '#fff5f5'
            icon = '🔴'
        elif severity == 'HIGH':
            border_color = '#ffc107'
            bg_color = '#fffbf0'
            icon = '🟡'
        else:
            border_color = '#28a745'
            bg_color = '#f8fff8'
            icon = '🟢'
        
        # Main card frame
        card_frame = tk.Frame(parent, bg=bg_color, relief='solid', bd=2, 
                             highlightbackground=border_color, highlightthickness=1)
        card_frame.grid(row=row, column=col, sticky='ew', padx=(0, 15), pady=(0, 15))
        
        # Inner content frame
        content_frame = tk.Frame(card_frame, bg=bg_color)
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header row with icon and severity
        header_row = tk.Frame(content_frame, bg=bg_color)
        header_row.pack(fill='x')
        
        severity_label = tk.Label(header_row, text=f"{icon} {severity}", 
                                 font=('Arial', 12, 'bold'), fg=border_color, bg=bg_color)
        severity_label.pack(side='left')
        
        # Time until impact
        days_until = alert_data.get('days_until_impact', 0)
        if days_until == 0:
            time_text = "⚡ Immediate"
        elif days_until == 1:
            time_text = "📅 1 day"
        else:
            time_text = f"📅 {days_until} days"
        
        time_label = tk.Label(header_row, text=time_text, font=('Arial', 10), 
                             fg='#6c757d', bg=bg_color)
        time_label.pack(side='right')
        
        # Material name
        material_label = tk.Label(content_frame, 
                                 text=f"🏭 {alert_data.get('material_name', 'Unknown')}", 
                                 font=('Arial', 13, 'bold'), bg=bg_color)
        material_label.pack(anchor='w', pady=(8, 4))
        
        # Alert type
        alert_type = alert_data.get('alert_type', 'General')
        if 'PREDICTED' in alert_type:
            type_display = f"⚡ {alert_type.replace('PREDICTED_', '').replace('_', ' ').title()}"
        elif 'SUPPLY' in alert_type:
            type_display = f"📦 {alert_type.replace('_', ' ').title()}"
        else:
            type_display = alert_type.replace('_', ' ').title()
        
        type_label = tk.Label(content_frame, text=type_display, 
                             font=('Arial', 11), fg='#495057', bg=bg_color)
        type_label.pack(anchor='w', pady=(0, 8))
        
        # Message
        message = alert_data.get('message', 'No message available')
        if len(message) > 120:
            message = message[:117] + "..."
        
        message_label = tk.Label(content_frame, text=message, font=('Arial', 10), 
                                fg='#212529', bg=bg_color, wraplength=280, justify='left')
        message_label.pack(anchor='w', pady=(0, 10))
        
        # Action button
        action_frame = tk.Frame(content_frame, bg=bg_color)
        action_frame.pack(fill='x')
        
        details_btn = tk.Button(action_frame, text="� View Details", 
                               font=('Arial', 9), bg=border_color, fg='white', 
                               border=0, padx=15, pady=5,
                               command=lambda: self.show_alert_details(alert_data))
        details_btn.pack(side='right')
        
        # Urgency score if available
        if 'urgency_score' in alert_data:
            urgency_text = f"🎯 Urgency: {alert_data['urgency_score']}/100"
            urgency_label = tk.Label(action_frame, text=urgency_text, 
                                   font=('Arial', 9), fg='#6c757d', bg=bg_color)
            urgency_label.pack(side='left')
        
        return card_frame
        
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
