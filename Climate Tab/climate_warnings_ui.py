"""
Climate Warnings UI Module
Modern, visually appealing warnings subtab with clean card-based layout
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import logging

# Configure logging for climate warnings module
logger = logging.getLogger(__name__)

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
        self.create_filter_section_without_init()
        self.create_stats_summary()
        self.create_alerts_grid()
        
        # Initialize filter after all components are created
        self.set_filter("ALL")
        
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
        
        # Refresh button with improved styling
        refresh_btn = tk.Button(title_frame,
                               text="🔄 Refresh",
                               command=self.refresh_data,
                               font=('Segoe UI', 9, 'bold'),
                               bg='#28a745',
                               fg='white',
                               relief='raised',
                               bd=2,
                               padx=12,
                               pady=6,
                               cursor='hand2',
                               activebackground='#218838',
                               activeforeground='white')
        refresh_btn.pack(side='right')
        
        # Add hover effect for refresh button
        def refresh_on_enter(e):
            refresh_btn.configure(bg='#218838')
        def refresh_on_leave(e):
            refresh_btn.configure(bg='#28a745')
        
        refresh_btn.bind("<Enter>", refresh_on_enter)
        refresh_btn.bind("<Leave>", refresh_on_leave)
    
    def create_filter_section_without_init(self):
        """Create modern filter buttons without initializing"""
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
            ("ALL", "🌍 All", "#495057"),
            ("CRITICAL", "🔴 Critical", "#dc3545"),
            ("HIGH", "🟠 High", "#fd7e14"),
            ("PREDICTIVE", "⚡ Predictive", "#0d6efd"),
            ("STOCK", "📦 Stock", "#6f42c1"),
            ("WEATHER", "🌦️ Weather", "#198754")
        ]
        
        for filter_id, label, color in filters:
            btn = tk.Button(filter_frame,
                          text=label,
                          command=lambda f=filter_id: self.set_filter(f),
                          font=('Segoe UI', 10, 'bold'),
                          relief='solid',
                          bd=1,
                          padx=20,
                          pady=12,
                          cursor='hand2',
                          bg='#f8f9fa',
                          fg='#212529',
                          activebackground='#e9ecef',
                          activeforeground='#212529',
                          highlightthickness=0,
                          borderwidth=1)
            btn.pack(side='left', padx=(0, 10))
            
            # Add hover effects
            def on_enter(e, button=btn, btn_color=color):
                if button.cget('relief') != 'sunken':
                    button.configure(bg='#e9ecef', fg='#212529', bd=2)
            def on_leave(e, button=btn):
                if button.cget('relief') != 'sunken':
                    button.configure(bg='#f8f9fa', fg='#212529', bd=1)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            self.filter_buttons[filter_id] = (btn, color)
    
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
        """Create individual stat card with improved styling"""
        card_frame = tk.Frame(parent, 
                             bg='white',
                             relief='raised',
                             bd=2,
                             highlightbackground='#e3e6ea',
                             highlightthickness=1)
        card_frame.grid(row=0, column=column, padx=(0, 15) if column < 3 else 0, 
                       pady=0, sticky='ew')
        
        # Configure grid weight
        parent.grid_columnconfigure(column, weight=1)
        
        # Add hover effect for cards
        def on_enter(e):
            card_frame.configure(highlightbackground='#bdc3c7', bd=3)
        def on_leave(e):
            card_frame.configure(highlightbackground='#e3e6ea', bd=2)
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Value
        value_label = tk.Label(content_frame,
                              text=value,
                              font=('Segoe UI', 20, 'bold'),
                              fg=color,
                              bg='white')
        value_label.pack()
        
        # Label
        label_label = tk.Label(content_frame,
                              text=label,
                              font=('Segoe UI', 10, 'bold'),
                              fg='#2c3e50',
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
        
        # Initialize with no alerts message
        self.show_no_alerts_message()
    
    def set_filter(self, filter_type):
        """Set the active filter and update display"""
        self.selected_filter = filter_type
        
        # Update button styles with excellent readability
        for btn_id, (button, color) in self.filter_buttons.items():
            if btn_id == filter_type:
                # Active button styling - use the specific color for that filter with white text
                button.configure(
                    bg=color, 
                    fg='white', 
                    relief='sunken', 
                    bd=2,
                    font=('Segoe UI', 10, 'bold')
                )
            else:
                # Inactive button styling - light background with dark text for maximum readability
                button.configure(
                    bg='#f8f9fa', 
                    fg='#212529', 
                    relief='solid', 
                    bd=1,
                    font=('Segoe UI', 10, 'bold')
                )
        
        # Refresh alerts display only if alerts_container exists
        if hasattr(self, 'alerts_container'):
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
            logger.error(f"Error refreshing warnings data: {e}")
            import traceback
            traceback.print_exc()
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
        """Update the alerts display organized by raw materials"""
        # Clear existing alerts
        for widget in self.alerts_container.winfo_children():
            widget.destroy()
        
        # Filter alerts
        filtered_alerts = self.filter_alerts(self.current_alerts)
        
        if not filtered_alerts:
            # Show no alerts message
            self.show_no_alerts_message()
            return
        
        # Group alerts by material
        alerts_by_material = {}
        for alert in filtered_alerts:
            material = alert.get('material_name', 'Unknown')
            if material not in alerts_by_material:
                alerts_by_material[material] = []
            alerts_by_material[material].append(alert)
        
        # Create sections for each material
        for material_name, material_alerts in alerts_by_material.items():
            self.create_material_section(self.alerts_container, material_name, material_alerts)
    
    def filter_alerts(self, alerts):
        """Filter alerts based on selected filter"""
        if not alerts:
            return []
            
        if self.selected_filter == "ALL":
            return alerts
        elif self.selected_filter == "CRITICAL":
            filtered = [a for a in alerts if a.get('severity') == 'CRITICAL']
            return filtered
        elif self.selected_filter == "HIGH":
            filtered = [a for a in alerts if a.get('severity') == 'HIGH']
            return filtered
        elif self.selected_filter == "PREDICTIVE":
            # Look for predictive alerts by type and days_until_impact
            filtered = [a for a in alerts if (
                'PREDICTED' in a.get('alert_type', '') or 
                'LONG_TERM' in a.get('alert_type', '') or 
                a.get('days_until_impact', 0) > 0 or
                a.get('days_ahead', 0) > 0
            )]
            return filtered
        elif self.selected_filter == "STOCK":
            filtered = [a for a in alerts if (
                'STOCK' in a.get('alert_type', '') or 
                'DEPLETION' in a.get('alert_type', '') or
                'SAFETY' in a.get('alert_type', '')
            )]
            return filtered
        elif self.selected_filter == "WEATHER":
            filtered = [a for a in alerts if (
                'weather' in a.get('alert_type', '').lower() or 
                'weather' in a.get('message', '').lower() or
                'WEATHER' in a.get('alert_type', '')
            )]
            return filtered
        return alerts
    
    def create_alert_card(self, parent, alert, index):
        """Create a modern alert card with improved readability and contrast"""
        # Main card frame with improved styling
        card_frame = tk.Frame(parent,
                             bg='white',
                             relief='raised',
                             bd=2,
                             highlightbackground='#e3e6ea',
                             highlightthickness=1)
        card_frame.pack(fill='x', pady=(0, 12), padx=8)
        
        # Add hover effect
        def on_enter(e):
            card_frame.configure(relief='raised', bd=3, highlightbackground='#adb5bd')
        def on_leave(e):
            card_frame.configure(relief='raised', bd=2, highlightbackground='#e3e6ea')
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        # Card content with more padding
        content_frame = tk.Frame(card_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=18, pady=15)
        
        # Header row
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Severity indicator with better contrast
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
        
        # Severity badge with background
        severity_frame = tk.Frame(header_frame, 
                                 bg=severity_colors.get(severity, '#6c757d'),
                                 relief='raised',
                                 bd=1)
        severity_frame.pack(side='left')
        
        severity_label = tk.Label(severity_frame,
                                 text=f"{severity_icons.get(severity, '⚪')} {severity}",
                                 font=('Segoe UI', 9, 'bold'),
                                 fg='white',
                                 bg=severity_colors.get(severity, '#6c757d'),
                                 padx=8,
                                 pady=4)
        severity_label.pack()
        
        # Time info with better visibility
        time_text = self.format_time_info(alert)
        time_label = tk.Label(header_frame,
                             text=time_text,
                             font=('Segoe UI', 9, 'bold'),
                             fg='#495057',
                             bg='white')
        time_label.pack(side='right')
        
        # Alert title with better styling to show meaningful titles
        title_frame = tk.Frame(content_frame, bg='white')
        title_frame.pack(fill='x', pady=(0, 10))
        
        # Generate meaningful title from alert data
        alert_title = self.generate_alert_title(alert)
        
        title_label = tk.Label(title_frame,
                              text=alert_title,
                              font=('Segoe UI', 13, 'bold'),
                              fg='#212529',
                              bg='white',
                              anchor='w')
        title_label.pack(fill='x')
        
        # Alert description with improved readability
        description = self.generate_alert_description(alert)
        
        desc_label = tk.Label(title_frame,
                             text=description,
                             font=('Segoe UI', 10),
                             fg='#343a40',
                             bg='white',
                             anchor='w',
                             wraplength=600)
        desc_label.pack(fill='x', pady=(6, 0))
        
        # Footer with material info and action button
        footer_frame = tk.Frame(content_frame, bg='white')
        footer_frame.pack(fill='x', pady=(12, 0))
        
        # Material info with better visibility
        material_name = alert.get('material_name', 'Unknown')
        material_label = tk.Label(footer_frame,
                                 text=f"📦 {material_name}",
                                 font=('Segoe UI', 10, 'bold'),
                                 fg='#495057',
                                 bg='white')
        material_label.pack(side='left')
        
        # View details button with excellent readability
        details_btn = tk.Button(footer_frame,
                               text="View Details →",
                               command=lambda: self.show_alert_details(alert),
                               font=('Segoe UI', 9, 'bold'),
                               fg='#212529',
                               bg='#f8f9fa',
                               relief='solid',
                               bd=1,
                               cursor='hand2',
                               padx=15,
                               pady=8,
                               activebackground='#e9ecef',
                               activeforeground='#212529')
        details_btn.pack(side='right')
        
        # Add hover effect for button
        def btn_on_enter(e):
            details_btn.configure(bg='#e9ecef', bd=2)
        def btn_on_leave(e):
            details_btn.configure(bg='#f8f9fa', bd=1)
        
        details_btn.bind("<Enter>", btn_on_enter)
        details_btn.bind("<Leave>", btn_on_leave)
    
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
        """Show detailed alert information in popup with improved styling and meaningful content"""
        # Create popup window
        popup = tk.Toplevel(self.parent)
        popup.title(f"Alert Details - {alert.get('material_name', 'Unknown Material')}")
        popup.geometry("750x650")
        popup.configure(bg='#f8f9fa')
        popup.transient(self.parent)
        popup.grab_set()
        
        # Center the popup
        popup.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50))
        
        # Main content frame with better styling
        main_frame = tk.Frame(popup, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Alert title with icon
        title_frame = tk.Frame(header_frame, bg='white')
        title_frame.pack(fill='x', padx=20, pady=15)
        
        # Get severity info
        severity = alert.get('severity', 'MEDIUM')
        severity_icons = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}
        severity_colors = {'CRITICAL': '#dc3545', 'HIGH': '#fd7e14', 'MEDIUM': '#ffc107', 'LOW': '#28a745'}
        
        title_label = tk.Label(title_frame,
                              text=f"{severity_icons.get(severity, '⚪')} {alert.get('material_name', 'Unknown Material')} Alert",
                              font=('Segoe UI', 18, 'bold'),
                              fg=severity_colors.get(severity, '#6c757d'),
                              bg='white')
        title_label.pack(anchor='w')
        
        # Severity badge
        severity_badge = tk.Label(title_frame,
                                 text=f"{severity} PRIORITY",
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white',
                                 bg=severity_colors.get(severity, '#6c757d'),
                                 padx=12,
                                 pady=6)
        severity_badge.pack(anchor='w', pady=(8, 0))
        
        # Details content frame
        content_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        content_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create scrollable text area
        canvas = tk.Canvas(content_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_content = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Add content sections
        self.create_alert_content_sections(scrollable_content, alert)
        
        canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill='x')
        
        # Close button with excellent readability
        close_btn = tk.Button(button_frame,
                             text="✕ Close",
                             command=popup.destroy,
                             font=('Segoe UI', 12, 'bold'),
                             bg='#f8f9fa',
                             fg='#212529',
                             relief='solid',
                             bd=1,
                             padx=35,
                             pady=15,
                             cursor='hand2',
                             activebackground='#e9ecef',
                             activeforeground='#212529')
        close_btn.pack(side='right')
        
        # Add hover effect for close button
        def close_on_enter(e):
            close_btn.configure(bg='#e9ecef', bd=2)
        def close_on_leave(e):
            close_btn.configure(bg='#f8f9fa', bd=1)
        
        close_btn.bind("<Enter>", close_on_enter)
        close_btn.bind("<Leave>", close_on_leave)
    
    def create_alert_content_sections(self, parent, alert):
        """Create meaningful content sections for alert details"""
        # Main content container
        content_container = tk.Frame(parent, bg='white')
        content_container.pack(fill='both', expand=True, padx=25, pady=20)
        
        # Alert Summary Section
        self.create_info_section(content_container, "📋 Alert Summary", [
            ("Material", alert.get('material_name', 'Unknown')),
            ("Alert Type", self.format_alert_type(alert.get('alert_type', 'Unknown'))),
            ("Severity Level", alert.get('severity', 'Unknown')),
            ("Time to Impact", self.format_time_to_impact(alert))
        ])
        
        # Impact Analysis Section
        impact_details = self.get_impact_details(alert)
        if impact_details:
            self.create_info_section(content_container, "📊 Impact Analysis", impact_details)
        
        # Predictive Information Section
        predictive_info = self.get_predictive_info(alert)
        if predictive_info:
            self.create_info_section(content_container, "🔮 Forecast Details", predictive_info)
        
        # Recommendations Section
        recommendations = self.get_recommendations(alert)
        self.create_recommendations_section(content_container, recommendations)
        
        # Additional Metrics Section
        metrics = self.get_additional_metrics(alert)
        if metrics:
            self.create_info_section(content_container, "📈 Additional Metrics", metrics)
    
    def create_info_section(self, parent, title, info_list):
        """Create an information section with title and key-value pairs"""
        section_frame = tk.Frame(parent, bg='white')
        section_frame.pack(fill='x', pady=(0, 20))
        
        # Section title
        title_label = tk.Label(section_frame,
                              text=title,
                              font=('Segoe UI', 14, 'bold'),
                              fg='#2c3e50',
                              bg='white',
                              anchor='w')
        title_label.pack(fill='x', pady=(0, 12))
        
        # Info items
        for key, value in info_list:
            item_frame = tk.Frame(section_frame, bg='white')
            item_frame.pack(fill='x', pady=3)
            
            key_label = tk.Label(item_frame,
                                text=f"{key}:",
                                font=('Segoe UI', 11, 'bold'),
                                fg='#495057',
                                bg='white',
                                width=18,
                                anchor='w')
            key_label.pack(side='left')
            
            value_label = tk.Label(item_frame,
                                  text=str(value),
                                  font=('Segoe UI', 11),
                                  fg='#212529',
                                  bg='white',
                                  anchor='w')
            value_label.pack(side='left', fill='x', expand=True)
    
    def create_recommendations_section(self, parent, recommendations):
        """Create recommendations section with bullet points"""
        section_frame = tk.Frame(parent, bg='white')
        section_frame.pack(fill='x', pady=(0, 20))
        
        # Section title
        title_label = tk.Label(section_frame,
                              text="💡 Recommended Actions",
                              font=('Segoe UI', 14, 'bold'),
                              fg='#2c3e50',
                              bg='white',
                              anchor='w')
        title_label.pack(fill='x', pady=(0, 12))
        
        # Recommendations
        for i, rec in enumerate(recommendations, 1):
            rec_frame = tk.Frame(section_frame, bg='white')
            rec_frame.pack(fill='x', pady=3)
            
            rec_label = tk.Label(rec_frame,
                                text=f"• {rec}",
                                font=('Segoe UI', 11),
                                fg='#212529',
                                bg='white',
                                anchor='w',
                                wraplength=550,
                                justify='left')
            rec_label.pack(fill='x', padx=(15, 0))
    
    def format_alert_type(self, alert_type):
        """Format alert type for display"""
        type_mapping = {
            'PREDICTED_DELAYS': 'Production Delays',
            'PRODUCTION_DROP': 'Production Decline',
            'WEATHER_EXTREME': 'Weather Event',
            'SUPPLY_CHAIN': 'Supply Chain Risk',
            'CLIMATE_RISK': 'Climate Risk',
            'CURRENT_CRITICAL': 'Current Critical Condition'
        }
        return type_mapping.get(alert_type, alert_type.replace('_', ' ').title())
    
    def format_time_to_impact(self, alert):
        """Format time to impact for display"""
        days = alert.get('days_until_impact', alert.get('days_ahead', 0))
        if days == 0:
            return "Immediate (Current conditions)"
        elif days == 1:
            return "Tomorrow"
        elif days <= 7:
            return f"In {days} days (This week)"
        elif days <= 30:
            return f"In {days} days (This month)"
        else:
            return f"In {days} days (Long-term)"
    
    def get_impact_details(self, alert):
        """Get impact analysis details"""
        details = []
        
        if alert.get('expected_delay'):
            details.append(("Expected Delay", alert.get('expected_delay')))
        if alert.get('peak_delay'):
            details.append(("Peak Delay", alert.get('peak_delay')))
        if alert.get('production_impact'):
            details.append(("Production Impact", f"{alert.get('production_impact'):.1f}%"))
        if alert.get('duration_days'):
            details.append(("Duration", f"{alert.get('duration_days')} days"))
        if alert.get('affected_products_count'):
            details.append(("Affected Products", f"{alert.get('affected_products_count')} items"))
        
        return details
    
    def get_predictive_info(self, alert):
        """Get predictive information"""
        info = []
        
        if alert.get('message'):
            info.append(("Prediction", alert.get('message')))
        if alert.get('horizon'):
            info.append(("Time Horizon", alert.get('horizon')))
        if alert.get('expected_condition'):
            info.append(("Expected Condition", alert.get('expected_condition')))
        
        return info
    
    def get_recommendations(self, alert):
        """Get meaningful recommendations based on alert type"""
        base_rec = alert.get('recommendation', '')
        recommendations = []
        
        # Add base recommendation if available
        if base_rec:
            recommendations.append(base_rec)
        
        # Add specific recommendations based on alert type
        alert_type = alert.get('alert_type', '')
        material = alert.get('material_name', '')
        
        if 'DELAY' in alert_type:
            recommendations.extend([
                f"Consider placing {material} orders 2-3 weeks earlier than planned",
                "Identify backup suppliers for emergency procurement",
                "Review inventory levels and adjust safety stock"
            ])
        elif 'PRODUCTION' in alert_type:
            recommendations.extend([
                f"Diversify {material} sourcing to reduce dependency",
                "Explore alternative materials or substitutes",
                "Negotiate flexible contracts with current suppliers"
            ])
        elif 'WEATHER' in alert_type:
            recommendations.extend([
                "Monitor weather forecasts closely for updates",
                "Prepare contingency plans for supply disruptions",
                "Consider temporary storage solutions"
            ])
        elif 'SUPPLY_CHAIN' in alert_type:
            recommendations.extend([
                "Review and strengthen supplier relationships",
                "Implement supply chain monitoring systems",
                "Develop alternative logistics routes"
            ])
        
        # Generic recommendations if none specific
        if not recommendations:
            recommendations = [
                f"Monitor {material} situation closely",
                "Contact suppliers for status updates",
                "Review procurement strategy and timelines",
                "Consider risk mitigation measures"
            ]
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def get_additional_metrics(self, alert):
        """Get additional metrics for the alert"""
        metrics = []
        
        if alert.get('urgency_score'):
            metrics.append(("Urgency Score", f"{alert.get('urgency_score')}/100"))
        if alert.get('risk_level'):
            metrics.append(("Risk Level", alert.get('risk_level')))
        if alert.get('category'):
            metrics.append(("Category", alert.get('category')))
        
        return metrics
    
    def generate_alert_title(self, alert):
        """Generate a meaningful title for the alert"""
        material = alert.get('material_name', 'Unknown Material')
        alert_type = alert.get('alert_type', '')
        days_until = alert.get('days_until_impact', alert.get('days_ahead', 0))
        
        # Generate title based on alert type
        if 'DELAY' in alert_type:
            if days_until == 0:
                return f"{material} - Production Delays Active"
            else:
                return f"{material} - Expected Delays in {days_until} Days"
        elif 'PRODUCTION' in alert_type:
            if days_until == 0:
                return f"{material} - Production Drop Detected"
            else:
                return f"{material} - Production Drop Expected in {days_until} Days"
        elif 'STOCK' in alert_type or 'DEPLETION' in alert_type:
            if 'CRITICAL' in alert_type:
                return f"🚨 {material} - Critical Stock Alert"
            elif 'SAFETY' in alert_type:
                return f"⚠️ {material} - Safety Stock Warning"
            else:
                return f"📦 {material} - Stock Depletion Alert"
        elif 'WEATHER' in alert_type:
            if days_until == 0:
                return f"{material} - Weather Impact Active"
            else:
                return f"{material} - Weather Risk in {days_until} Days"
        elif 'SUPPLY' in alert_type:
            if days_until == 0:
                return f"{material} - Supply Chain Issues"
            else:
                return f"{material} - Supply Chain Risk in {days_until} Days"
        elif 'STOCK' in alert_type or 'RUN_OUT' in alert_type:
            return f"{material} - Stock Depletion Warning"
        else:
            # Use message if available, otherwise generate generic title
            if alert.get('message'):
                return alert.get('message')
            else:
                return f"{material} - Climate Alert"
    
    def generate_alert_description(self, alert):
        """Generate a meaningful description for the alert"""
        alert_type = alert.get('alert_type', '')
        material = alert.get('material_name', 'Unknown Material')
        days_until = alert.get('days_until_impact', alert.get('days_ahead', 0))
        
        # Generate description based on alert type
        if 'DELAY' in alert_type:
            delay_percent = alert.get('expected_delay', alert.get('delay_percent', 'unknown'))
            duration = alert.get('duration_days', 'several')
            return f"Expected {delay_percent} production delays for {duration} days. This could impact supply chain timing and delivery schedules."
        
        elif 'PRODUCTION' in alert_type:
            impact = alert.get('production_impact', 'significant')
            return f"Production output expected to decrease by {impact}. Monitor supplier capacity and consider alternative sourcing options."
        
        elif 'STOCK' in alert_type or 'DEPLETION' in alert_type:
            if 'CRITICAL' in alert_type:
                days_empty = alert.get('days_until_empty', days_until)
                current_stock = alert.get('current_stock', 'Unknown')
                daily_consumption = alert.get('daily_consumption', 'Unknown')
                return f"Critical stock alert: Only {current_stock} units remaining with {daily_consumption} daily consumption. Stock will be depleted in {days_empty} days."
            elif 'SAFETY' in alert_type:
                safety_days = alert.get('days_until_safety', days_until)
                safety_stock = alert.get('safety_stock', 'Unknown')
                return f"Stock approaching safety levels. Will reach minimum safety stock of {safety_stock} units in {safety_days} days."
            else:
                return f"{material} inventory levels need attention. Plan restocking to avoid stockouts."
        
        elif 'WEATHER' in alert_type:
            condition = alert.get('expected_condition', 'adverse weather conditions')
            return f"Weather forecast shows {condition} that may impact production and transportation. Prepare contingency plans."
        
        elif 'SUPPLY' in alert_type:
            return f"Supply chain disruptions detected that may affect {material} availability. Review supplier status and backup options."
        
        elif 'STOCK' in alert_type or 'RUN_OUT' in alert_type:
            return f"{material} inventory levels are critically low. Immediate restocking recommended to avoid stockouts."
        
        else:
            # Use existing description or message
            desc = alert.get('description', alert.get('message', ''))
            if desc:
                return desc if len(desc) <= 120 else desc[:117] + "..."
            else:
                return f"Climate-related alert for {material}. Review conditions and take appropriate action."
    
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
    
    def show_no_alerts_message(self):
        """Show no alerts message with improved styling"""
        self.no_alerts_frame = tk.Frame(self.alerts_container, bg='#f8f9fa', 
                                       relief='raised', bd=2)
        self.no_alerts_frame.pack(fill='both', expand=True, pady=50, padx=20)
        
        # Icon and message
        icon_label = tk.Label(self.no_alerts_frame,
                             text="🌅",
                             font=('Segoe UI', 48),
                             bg='#f8f9fa',
                             fg='#28a745')
        icon_label.pack(pady=(30, 10))
        
        no_alerts_label = tk.Label(self.no_alerts_frame,
                                  text="No Active Alerts",
                                  font=('Segoe UI', 16, 'bold'),
                                  foreground='#28a745',
                                  bg='#f8f9fa')
        no_alerts_label.pack()
        
        sub_label = tk.Label(self.no_alerts_frame,
                            text="All systems are running smoothly",
                            font=('Segoe UI', 12),
                            foreground='#6c757d',
                            bg='#f8f9fa')
        sub_label.pack(pady=(5, 30))
    
    def create_material_section(self, parent, material_name, material_alerts):
        """Create a section for a specific material with its alerts - improved styling"""
        # Material section container with better styling
        section_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        section_frame.pack(fill='x', pady=(0, 25))
        
        # Material header with improved contrast
        header_frame = tk.Frame(section_frame, bg='#e8f4fd', relief='raised', bd=1)
        header_frame.pack(fill='x', padx=3, pady=3)
        
        # Material name and count with better typography
        material_icon = {"Wheat": "🌾", "Rice": "🌾", "Cotton": "🌿", "Sugarcane": "🎋"}.get(material_name, "📦")
        header_label = tk.Label(header_frame,
                               text=f"{material_icon} {material_name} ({len(material_alerts)} alerts)",
                               font=('Segoe UI', 14, 'bold'),
                               bg='#e8f4fd',
                               fg='#0d6efd',
                               padx=20,
                               pady=12)
        header_label.pack(side='left')
        
        # Alert severity summary for this material with better visibility
        critical_count = len([a for a in material_alerts if a.get('severity') == 'CRITICAL'])
        high_count = len([a for a in material_alerts if a.get('severity') == 'HIGH'])
        medium_count = len([a for a in material_alerts if a.get('severity') == 'MEDIUM'])
        
        summary_parts = []
        if critical_count > 0:
            summary_parts.append(f"🔴 {critical_count} Critical")
        if high_count > 0:
            summary_parts.append(f"🟠 {high_count} High")
        if medium_count > 0:
            summary_parts.append(f"🟡 {medium_count} Medium")
        
        if summary_parts:
            summary_text = "  •  ".join(summary_parts)
            summary_label = tk.Label(header_frame,
                                   text=summary_text,
                                   font=('Segoe UI', 10, 'bold'),
                                   bg='#e8f4fd',
                                   fg='#dc3545')
            summary_label.pack(side='right', padx=20, pady=12)
        
        # Alerts container for this material with better spacing
        alerts_frame = tk.Frame(section_frame, bg='#ffffff')
        alerts_frame.pack(fill='both', expand=True, padx=15, pady=(5, 15))
        
        # Create alert cards for this material
        for i, alert in enumerate(material_alerts):
            self.create_alert_card(alerts_frame, alert, i)
