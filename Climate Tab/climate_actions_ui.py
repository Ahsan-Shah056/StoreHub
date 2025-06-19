"""
Climate Actions UI Module - Simplified Version
Streamlined Actions subtab with essential climate management features
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json

from climate_base import ClimateBaseUI, ClimateConstants
import climate_data

class ClimateActionsUI(ClimateBaseUI):
    """Simplified Actions UI with essential climate management functionality"""
    
    def __init__(self, parent_frame, callbacks=None):
        super().__init__(parent_frame, callbacks)
        self.climate_manager = climate_data.climate_manager
        
        # Action tracking
        self.pending_actions = []
        self.completed_actions = []
        self.last_hover_item = None  # For hover effects
        
        self.create_actions_layout()
        self.load_initial_data()
        
    def create_actions_layout(self):
        """Create the simplified actions layout"""
        # Main container with padding
        self.main_container = ttk.Frame(self.parent, padding="20")
        self.main_container.pack(fill='both', expand=True)
        
        # Header section
        self.create_header_section()
        
        # Main content area
        self.create_content_area()
        
    def create_header_section(self):
        """Create the header with title and essential controls"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="🎯 Climate Action Center",
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(side='left')
        
        # Essential controls only
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        # Refresh button
        refresh_btn = ttk.Button(controls_frame,
                                text="🔄 Refresh",
                                command=self.refresh_data)
        refresh_btn.pack(side='right', padx=(5, 0))
        
        # New action button
        new_action_btn = ttk.Button(controls_frame,
                                   text="➕ New Action",
                                   command=self.show_new_action_form)
        new_action_btn.pack(side='right', padx=(5, 0))
        
    def create_content_area(self):
        """Create the main content with simplified layout"""
        # Create notebook for action views
        self.action_notebook = ttk.Notebook(self.main_container)
        self.action_notebook.pack(fill='both', expand=True)
        
        # Quick actions tab
        self.quick_tab = ttk.Frame(self.action_notebook)
        self.action_notebook.add(self.quick_tab, text="⚡ Quick Actions")
        
        # Pending actions tab
        self.pending_tab = ttk.Frame(self.action_notebook)
        self.action_notebook.add(self.pending_tab, text="📋 Action List")
        
        # Create content for each tab
        self.create_quick_actions_tab()
        self.create_action_list_tab()
        
    def create_quick_actions_tab(self):
        """Create simplified quick actions"""
        container = ttk.Frame(self.quick_tab, padding="15")
        container.pack(fill='both', expand=True)
        
        # Essential quick actions only
        actions_frame = ttk.LabelFrame(container, text="🚨 Essential Actions", padding="15")
        actions_frame.pack(fill='x', pady=(0, 20))
        
        # Quick action buttons in a clean grid
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack(fill='x')
        
        # Essential actions only
        quick_actions = [
            ("🌧️ Weather Alert", self.create_weather_alert),
            ("📦 Secure Inventory", self.secure_inventory_action),
            ("📞 Contact Suppliers", self.notify_suppliers_action),
            ("📊 Generate Report", self.generate_risk_report)
        ]
        
        # Create action buttons in 2x2 grid
        for i, (text, command) in enumerate(quick_actions):
            row, col = i // 2, i % 2
            btn = ttk.Button(actions_grid, text=text, command=command, width=22)
            btn.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
        
        # Configure grid weights
        actions_grid.grid_columnconfigure(0, weight=1)
        actions_grid.grid_columnconfigure(1, weight=1)
        
        # Recent actions summary - show actual actions in a mini treeview
        log_frame = ttk.LabelFrame(container, text="📋 Recent Actions Summary", padding="10")
        log_frame.pack(fill='both', expand=True)
        
        # Create a mini treeview for recent actions
        recent_columns = ('Time', 'Priority', 'Action', 'Material')
        self.recent_tree = ttk.Treeview(log_frame, columns=recent_columns, show='headings', height=8)
        
        # Configure columns for the recent actions treeview
        self.recent_tree.heading('Time', text='⏰ Time')
        self.recent_tree.heading('Priority', text='🎯 Priority')
        self.recent_tree.heading('Action', text='📋 Action')
        self.recent_tree.heading('Material', text='🌾 Material')
        
        # Set column widths for recent actions
        self.recent_tree.column('Time', width=80, minwidth=60)
        self.recent_tree.column('Priority', width=80, minwidth=60)
        self.recent_tree.column('Action', width=200, minwidth=150)
        self.recent_tree.column('Material', width=120, minwidth=80)
        
        # Style the recent actions treeview
        style = ttk.Style()
        style.configure("Recent.Treeview", font=('Segoe UI', 11, 'bold'))
        style.configure("Recent.Treeview.Heading", font=('Segoe UI', 14, 'bold'))
        self.recent_tree.configure(style="Recent.Treeview")
        
        # Add scrollbar for recent actions
        recent_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=recent_scrollbar.set)
        
        self.recent_tree.pack(side='left', fill='both', expand=True, padx=(0, 5))
        recent_scrollbar.pack(side='right', fill='y')
        
        # Add some initial placeholder data
        self.add_recent_action_summary("System initialized", "Info", "📊 Ready to manage climate actions", "All Materials")
        
    def create_action_list_tab(self):
        """Create simplified action list with improved treeview"""
        container = ttk.Frame(self.pending_tab, padding="15")
        container.pack(fill='both', expand=True)
        
        # Action controls
        controls_frame = ttk.Frame(container)
        controls_frame.pack(fill='x', pady=(0, 15))
        
        # Essential controls only
        ttk.Button(controls_frame, text="✅ Complete Selected", 
                  command=self.complete_selected_action).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="✏️ Edit Selected", 
                  command=self.edit_selected_action).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="🗑️ Delete Selected", 
                  command=self.delete_selected_action).pack(side='left')
        
        # Create container frame for treeview first
        tree_container = ttk.Frame(container, relief='solid', borderwidth=1)
        tree_container.pack(fill='both', expand=True, pady=(5, 0))
        
        # Enhanced treeview with professional styling - created in the container
        columns = ('Priority', 'Action', 'Material', 'Due Date', 'Status')
        self.actions_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=16)
        
        # Configure columns with optimized widths and alignment
        column_config = {
            'Priority': {'width': 110, 'anchor': 'center', 'minwidth': 90},
            'Action': {'width': 220, 'anchor': 'w', 'minwidth': 150},
            'Material': {'width': 130, 'anchor': 'center', 'minwidth': 100},
            'Due Date': {'width': 130, 'anchor': 'center', 'minwidth': 100},
            'Status': {'width': 120, 'anchor': 'center', 'minwidth': 90}
        }
        
        for col in columns:
            config = column_config[col]
            self.actions_tree.heading(col, text=col, anchor='center')
            self.actions_tree.column(col, width=config['width'], anchor=config['anchor'], 
                                   minwidth=config['minwidth'], stretch=True)
        
        # Enhanced professional styling for treeview
        style = ttk.Style()
        
        # Header styling with gradient-like appearance
        style.configure("ActionsTree.Treeview.Heading", 
                       font=('Segoe UI', 12, 'bold'),
                       background='#2c3e50',
                       foreground='#ecf0f1',
                       relief='flat',
                       borderwidth=0)
        
        # Main treeview styling with improved readability
        style.configure("ActionsTree.Treeview", 
                       font=('Segoe UI', 11),
                       background='#ffffff',
                       foreground='#2c3e50',
                       fieldbackground='#ffffff',
                       borderwidth=1,
                       relief='solid',
                       rowheight=32,
                       selectbackground='#3498db',
                       selectforeground='white')
        
        # Enhanced selection and hover effects
        style.map("ActionsTree.Treeview",
                 background=[('selected', '#3498db'), ('focus', '#3498db')],
                 foreground=[('selected', 'white'), ('focus', 'white')],
                 relief=[('selected', 'flat'), ('focus', 'flat')])
        
        # Apply the custom style
        self.actions_tree.configure(style="ActionsTree.Treeview")
        
        # Configure row tags for priority-based styling
        self.actions_tree.tag_configure('high_priority', 
                                       background='#fdf2f2', 
                                       foreground='#721c24')
        self.actions_tree.tag_configure('medium_priority', 
                                       background='#fffbeb', 
                                       foreground='#92400e')
        self.actions_tree.tag_configure('low_priority', 
                                       background='#f0fdf4', 
                                       foreground='#166534')
        self.actions_tree.tag_configure('alternating', 
                                       background='#f8fafc')
        self.actions_tree.tag_configure('hover', 
                                       background='#e3f2fd', 
                                       foreground='#1565c0')
        
        # Create scrollbar in the same container
        tree_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.actions_tree.yview)
        self.actions_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack treeview and scrollbar properly
        self.actions_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Bind events
        self.actions_tree.bind('<Double-1>', self.on_action_double_click)
        self.actions_tree.bind('<Button-1>', self.on_action_select)
        self.actions_tree.bind('<Motion>', self.on_tree_motion)
        self.actions_tree.bind('<Leave>', self.on_tree_leave)
        
        # Add some sample data for demonstration
        self.populate_sample_actions()
        
    def populate_sample_actions(self):
        """Add sample actions with enhanced priority-based styling"""
        sample_actions = [
            ('🔴 High', 'Monitor Cotton Supply', 'Cotton', '2025-06-20', '⏳ Pending', 'high'),
            ('🟡 Medium', 'Review Rice Inventory', 'Rice', '2025-06-22', '⏳ Pending', 'medium'),
            ('🔴 High', 'Contact Wheat Suppliers', 'Wheat', '2025-06-21', '⏳ Pending', 'high'),
            ('🟢 Low', 'Update Forecasts', 'All Materials', '2025-06-25', '⏳ Pending', 'low'),
            ('🟡 Medium', 'Secure Transportation', 'Sugarcane', '2025-06-23', '⏳ Pending', 'medium'),
            ('🔴 High', 'Emergency Stock Check', 'Cotton', '2025-06-20', '⏳ Pending', 'high'),
            ('🟢 Low', 'Monthly Climate Review', 'All Materials', '2025-06-30', '⏳ Pending', 'low')
        ]
        
        for i, action_data in enumerate(sample_actions):
            priority_level = action_data[5]  # Get priority level for styling
            item_values = action_data[:5]    # Get the display values
            
            # Determine tag for row styling
            if 'High' in item_values[0]:
                tag = 'high_priority'
            elif 'Medium' in item_values[0]:
                tag = 'medium_priority'
            elif 'Low' in item_values[0]:
                tag = 'low_priority'
            else:
                tag = 'alternating' if i % 2 == 0 else ''
            
            # Insert with appropriate styling tag
            item_id = self.actions_tree.insert('', 'end', values=item_values, tags=(tag,))
    
    # Essential action methods with real functionality
    def create_weather_alert(self):
        """Create real weather alert action with data"""
        try:
            # Get current climate data to create meaningful alert
            status_data = self.climate_manager.get_current_climate_status()
            
            # Create a real weather alert entry in the action list
            if status_data:
                # Find materials with weather risks
                risk_materials = []
                
                # Handle both list and dict formats
                if isinstance(status_data, list):
                    risk_materials = [item for item in status_data 
                                    if isinstance(item, dict) and 
                                    item.get('risk_level', '').upper() in ['HIGH', 'CRITICAL']]
                elif isinstance(status_data, dict):
                    # If it's a dict, it might contain a list under a key
                    materials_list = status_data.get('materials', []) or status_data.get('data', [])
                    if materials_list:
                        risk_materials = [item for item in materials_list 
                                        if isinstance(item, dict) and 
                                        item.get('risk_level', '').upper() in ['HIGH', 'CRITICAL']]
                
                if risk_materials:
                    for material in risk_materials[:2]:  # Limit to 2 most critical
                        material_name = material.get('material_name', material.get('name', 'Unknown Material'))
                        alert_values = (
                            '🔴 High', 
                            f'Weather Alert - {material_name}',
                            material_name,
                            datetime.now().strftime('%Y-%m-%d'),
                            '⏳ Pending'
                        )
                        self.actions_tree.insert('', 0, values=alert_values, tags=('high_priority',))
                        # Also add to recent actions summary
                        self.add_recent_action_summary("Weather Alert", "High", f"Weather alert for {material_name}", material_name)
                        
                    self.log_action(f"🌧️ Created weather alerts for {len(risk_materials)} high-risk materials")
                    messagebox.showinfo("Weather Alert Created", 
                                      f"Weather alerts created for {len(risk_materials)} materials with high climate risk!")
                else:
                    # Create general monitoring alert
                    alert_values = (
                        '🟡 Medium', 
                        'Weather Monitoring - All Materials',
                        'All Materials',
                        datetime.now().strftime('%Y-%m-%d'),
                        '⏳ Pending'
                    )
                    self.actions_tree.insert('', 0, values=alert_values, tags=('medium_priority',))
                    self.log_action("🌧️ General weather monitoring alert activated")
                    messagebox.showinfo("Weather Alert", "General weather monitoring alert has been activated!")
            else:
                # Fallback alert
                alert_values = (
                    '🟡 Medium', 
                    'Weather Alert - Monitor Conditions',
                    'All Materials',
                    datetime.now().strftime('%Y-%m-%d'),
                    '⏳ Pending'
                )
                self.actions_tree.insert('', 0, values=alert_values, tags=('medium_priority',))
                self.log_action("🌧️ Weather alert created - monitor all conditions")
                
        except Exception as e:
            self.log_action(f"❌ Error creating weather alert: {str(e)}")
            messagebox.showerror("Error", f"Failed to create weather alert: {str(e)}")
        
    def secure_inventory_action(self):
        """Create real inventory security action"""
        try:
            # Get climate alerts to identify materials needing security
            alerts = self.climate_manager.get_climate_alerts()
            
            # Handle both dictionary and list formats
            current_alerts = []
            stock_alerts = []
            
            if isinstance(alerts, dict):
                current_alerts = alerts.get('current', [])
                stock_alerts = alerts.get('stock', [])
            elif isinstance(alerts, list):
                # If alerts is a list, treat it as current alerts
                current_alerts = alerts
            
            if current_alerts or stock_alerts:
                affected_materials = set()
                
                # Process current alerts
                for alert in current_alerts:
                    if isinstance(alert, dict):
                        material = alert.get('material_name', 'Unknown')
                        affected_materials.add(material)
                    elif isinstance(alert, str):
                        affected_materials.add(alert)
                
                # Process stock alerts  
                for alert in stock_alerts:
                    if isinstance(alert, dict):
                        material = alert.get('material_name', 'Unknown')
                        affected_materials.add(material)
                    elif isinstance(alert, str):
                        affected_materials.add(alert)
                
                # Create security actions for affected materials
                for material in list(affected_materials)[:3]:  # Limit to 3 most critical
                    security_values = (
                        '🔴 High',
                        f'Secure {material} Inventory',
                        material,
                        datetime.now().strftime('%Y-%m-%d'),
                        '⏳ Pending'
                    )
                    self.actions_tree.insert('', 0, values=security_values, tags=('high_priority',))
                    # Also add to recent actions summary
                    self.add_recent_action_summary("Security", "High", f"Secure {material} inventory", material)
                
                self.log_action(f"📦 Created inventory security actions for {len(affected_materials)} materials")
                messagebox.showinfo("Inventory Security", 
                                  f"Security protocols activated for {len(affected_materials)} materials at risk!")
            else:
                # General security check
                security_values = (
                    '🟡 Medium',
                    'General Inventory Security Check',
                    'All Materials',
                    datetime.now().strftime('%Y-%m-%d'),
                    '⏳ Pending'
                )
                self.actions_tree.insert('', 0, values=security_values, tags=('medium_priority',))
                self.log_action("📦 General inventory security check initiated")
                messagebox.showinfo("Inventory Security", "General inventory security protocols activated!")
                
        except Exception as e:
            self.log_action(f"❌ Error creating security action: {str(e)}")
            messagebox.showerror("Error", f"Failed to create security action: {str(e)}")
        
    def notify_suppliers_action(self):
        """Create real supplier notification actions"""
        try:
            # Get current climate status to identify suppliers to contact
            status_data = self.climate_manager.get_current_climate_status()
            
            if status_data:
                high_risk_materials = []
                
                # Handle both list and dict formats
                if isinstance(status_data, list):
                    high_risk_materials = [item for item in status_data 
                                         if isinstance(item, dict) and 
                                         item.get('risk_level', '').upper() in ['HIGH', 'CRITICAL']]
                elif isinstance(status_data, dict):
                    # If it's a dict, it might contain a list under a key
                    materials_list = status_data.get('materials', []) or status_data.get('data', [])
                    if materials_list:
                        high_risk_materials = [item for item in materials_list 
                                             if isinstance(item, dict) and 
                                             item.get('risk_level', '').upper() in ['HIGH', 'CRITICAL']]
                
                if high_risk_materials:
                    for material in high_risk_materials[:3]:  # Limit to 3 most critical
                        material_name = material.get('material_name', material.get('name', 'Unknown Material'))
                        supplier_values = (
                            '🔴 High',
                            f'Contact {material_name} Suppliers',
                            material_name,
                            datetime.now().strftime('%Y-%m-%d'),
                            '⏳ Pending'
                        )
                        self.actions_tree.insert('', 0, values=supplier_values, tags=('high_priority',))
                        # Also add to recent actions summary
                        self.add_recent_action_summary("Supplier", "High", f"Contact {material_name} suppliers", material_name)
                    
                    self.log_action(f"📞 Created supplier contact actions for {len(high_risk_materials)} high-risk materials")
                    messagebox.showinfo("Supplier Notifications", 
                                      f"Contact actions created for suppliers of {len(high_risk_materials)} high-risk materials!")
                else:
                    # General supplier check
                    supplier_values = (
                        '🟡 Medium',
                        'Routine Supplier Check-in',
                        'All Materials',
                        datetime.now().strftime('%Y-%m-%d'),
                        '⏳ Pending'
                    )
                    self.actions_tree.insert('', 0, values=supplier_values, tags=('medium_priority',))
                    self.log_action("📞 Routine supplier check-in scheduled")
                    messagebox.showinfo("Supplier Contact", "Routine supplier check-in has been scheduled!")
            else:
                # Fallback supplier contact
                supplier_values = (
                    '🟡 Medium',
                    'General Supplier Communications',
                    'All Materials',
                    datetime.now().strftime('%Y-%m-%d'),
                    '⏳ Pending'
                )
                self.actions_tree.insert('', 0, values=supplier_values, tags=('medium_priority',))
                self.log_action("📞 General supplier communication initiated")
                
        except Exception as e:
            self.log_action(f"❌ Error creating supplier notification: {str(e)}")
            messagebox.showerror("Error", f"Failed to create supplier notification: {str(e)}")
        
    def generate_risk_report(self):
        """Generate a comprehensive risk assessment PDF report and email it to the manager"""
        try:
            # Show progress indication
            progress_dialog = tk.Toplevel(self.parent)
            progress_dialog.title("Generating Report")
            progress_dialog.geometry("300x100")
            progress_dialog.transient(self.parent)
            progress_dialog.grab_set()
            
            # Center the progress dialog
            progress_dialog.update_idletasks()
            x = (progress_dialog.winfo_screenwidth() // 2) - (150)
            y = (progress_dialog.winfo_screenheight() // 2) - (50)
            progress_dialog.geometry(f"300x100+{x}+{y}")
            
            progress_label = ttk.Label(progress_dialog, text="Generating PDF report...", font=('Segoe UI', 10))
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_dialog, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill='x')
            progress_bar.start()
            
            # Force update to show the dialog
            progress_dialog.update()
            
            # Get current climate data and alerts
            current_alerts = self.climate_manager.get_climate_alerts()
            status_data = self.climate_manager.get_current_climate_status()
            
            # Update progress
            progress_label.config(text="Collecting climate data...")
            progress_dialog.update()
            
            # Generate PDF report
            progress_label.config(text="Creating PDF document...")
            progress_dialog.update()
            
            pdf_path = self._generate_pdf_report(current_alerts, status_data)
            
            # Update progress
            progress_label.config(text="Sending email...")
            progress_dialog.update()
            
            # Send email with PDF attachment
            self._send_report_email(pdf_path)
            
            # Clean up the PDF file after sending
            import os
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            
            # Close progress dialog
            progress_dialog.destroy()
            
            # Show success message
            messagebox.showinfo("Report Generated", 
                              "Climate risk assessment report has been generated and emailed to the manager successfully!")
            
            # Add success action to the actions tree
            summary_action = (
                '� Low',
                'Report Generated',
                'All Materials',
                datetime.now().strftime('%Y-%m-%d'),
                '✅ Complete'
            )
            
            self.actions_tree.insert('', 0, values=summary_action, tags=('completed',))
            
            # Add to recent actions summary
            risk_summary = self._get_risk_summary(current_alerts, status_data)
            self.add_recent_action_summary("Report", "Medium", f"📊 Report emailed: {risk_summary}", "All Materials")
            
            self.log_action(f"📊 Climate risk report PDF generated and emailed successfully")
                
        except Exception as e:
            # Close progress dialog if it exists
            try:
                progress_dialog.destroy()
            except:
                pass
                
            error_msg = f"Failed to generate or send risk report: {str(e)}"
            self.log_action(f"❌ Error generating/sending risk report: {str(e)}")
            messagebox.showerror("Error", error_msg)
    
    def _generate_detailed_report_content(self, current_alerts, status_data):
        """Generate detailed report content with comprehensive analysis"""
        report_lines = []
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        # Professional Header
        report_lines.extend([
            "╔══════════════════════════════════════════════════════════════════════════════╗",
            "║                       🌍 CLIMATE RISK ASSESSMENT REPORT                      ║",
            "╚══════════════════════════════════════════════════════════════════════════════╝",
            "",
            f"📅 Generated: {timestamp}",
            f"🏢 System: DigiClimate Store Hub",
            f"📊 Report Type: Comprehensive Climate Analysis",
            "",
            "═" * 80,
            "",
        ])
        
        # Executive Summary with better formatting
        report_lines.extend([
            "📋 EXECUTIVE SUMMARY",
            "─" * 80,
        ])
        
        # Process alerts data
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        affected_materials = set()
        alert_details = []
        
        if isinstance(current_alerts, list):
            for alert in current_alerts:
                if isinstance(alert, dict):
                    severity = alert.get('severity', 'UNKNOWN').upper()
                    material = alert.get('material_name', alert.get('material', 'Unknown'))
                    alert_type = alert.get('alert_type', alert.get('type', 'General'))
                    
                    affected_materials.add(material)
                    alert_details.append({
                        'material': material,
                        'severity': severity,
                        'type': alert_type,
                        'description': alert.get('description', alert.get('message', 'No description'))
                    })
                    
                    if severity in ['HIGH', 'CRITICAL']:
                        high_risk_count += 1
                    elif severity == 'MEDIUM':
                        medium_risk_count += 1
                    else:
                        low_risk_count += 1
         # Overall risk assessment with visual indicators
        total_alerts = high_risk_count + medium_risk_count + low_risk_count
        risk_level = "CRITICAL" if high_risk_count > 3 else "HIGH" if high_risk_count > 0 else "MEDIUM" if medium_risk_count > 0 else "LOW"
        
        # Summary section
        report_lines.extend([
            f"🚨 Overall Risk Level: {risk_level}",
            f"📊 Total Alerts: {total_alerts} ({high_risk_count} High, {medium_risk_count} Medium, {low_risk_count} Low)",
            f"🏭 Affected Materials: {len(affected_materials)} types",
            "",
            "═" * 80,
            ""
        ])
        
        # Alert details
        if alert_details:
            report_lines.extend([
                "🔍 DETAILED ALERT ANALYSIS",
                "─" * 80,
            ])
            
            for detail in alert_details:
                material = detail['material']
                severity = detail['severity']
                alert_type = detail['type']
                description = detail['description']
            
            report_lines.append(f"• Material: {material}")
            report_lines.append(f"  Severity: {severity}")
            report_lines.append(f"  Type: {alert_type}")
            report_lines.append(f"  Description: {description}")
            report_lines.append("")  # Spacer
    
        # Recommendations section
        report_lines.extend([
            "💡 RECOMMENDATIONS",
            "─" * 80,
            "1. Review high-risk materials and take immediate action.",
            "2. Monitor medium-risk materials closely.",
            "3. Ensure all inventory is secured against potential climate impacts.",
            "4. Maintain regular communication with suppliers, especially for high-risk materials.",
            "5. Consider diversifying suppliers and materials to mitigate risks.",
            "",
            "For detailed recommendations, refer to the full climate risk management plan.",
            ""
        ])
        
        # Professional closing
        report_lines.append("═" * 80)
        report_lines.append("Thank you for using the DigiClimate Store Hub.")
        report_lines.append("Together, we can make a difference!")
        report_lines.append("═" * 80)
        
        return "\n".join(report_lines)
    
    def _generate_pdf_report(self, current_alerts, status_data):
        """Generate PDF report with detailed climate risk information using ReportLab"""
        import os
        
        try:
            # Try using ReportLab for professional PDF generation
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            # Output file path
            file_path = f"climate_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1  # Center alignment
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkgreen
            )
            
            # Title
            story.append(Paragraph("Climate Risk Assessment Report", title_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
            story.append(Paragraph("DigiClimate Store Hub", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Get detailed content and format for PDF
            detailed_content = self._generate_detailed_report_content(current_alerts, status_data)
            
            # Split content into sections and format appropriately
            lines = detailed_content.split('\n')
            current_section = []
            
            for line in lines:
                if line.startswith('📋') or line.startswith('🔍') or line.startswith('💡'):
                    # This is a section header
                    if current_section:
                        # Add previous section content
                        story.append(Paragraph('<br/>'.join(current_section), styles['Normal']))
                        story.append(Spacer(1, 0.2*inch))
                        current_section = []
                    
                    # Add section header
                    story.append(Paragraph(line, heading_style))
                elif line.startswith('─') or line.startswith('═'):
                    # Skip decorative lines
                    continue
                elif line.strip():
                    # Regular content line
                    current_section.append(line)
                else:
                    # Empty line - add spacing
                    if current_section:
                        story.append(Paragraph('<br/>'.join(current_section), styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                        current_section = []
            
            # Add any remaining content
            if current_section:
                story.append(Paragraph('<br/>'.join(current_section), styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            return file_path
            
        except ImportError:
            # Fallback to FPDF if ReportLab is not available
            from fpdf import FPDF
            
            # Create PDF document
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Set title
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Climate Risk Assessment Report", ln=True, align='C')
            
            # Add generated date
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%B %d, %Y')}", ln=True, align='C')
            pdf.cell(0, 10, "DigiClimate Store Hub", ln=True, align='C')
            
            # Add a line break
            pdf.ln(10)
            
            # Set font for body
            pdf.set_font("Arial", '', 10)
            
            # Add detailed report content
            detailed_content = self._generate_detailed_report_content(current_alerts, status_data)
            for line in detailed_content.split('\n'):
                if line.strip():  # Skip empty lines
                    # Clean line of special characters that might cause issues
                    clean_line = line.encode('latin-1', 'replace').decode('latin-1')
                    pdf.cell(0, 6, clean_line, ln=True)
            
            # Output file path
            file_path = f"climate_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(file_path)
            
            return file_path
    
    def _send_report_email(self, pdf_path):
        """Send the generated report via email using credentials from credentials.json"""
        import smtplib
        import json
        import os
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        
        try:
            # Load email credentials from credentials.json
            credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
            with open(credentials_path, 'r') as f:
                credentials = json.load(f)
            
            # Extract email configuration
            smtp_user = credentials.get('email')
            smtp_password = credentials.get('password')
            
            if not smtp_user or not smtp_password:
                raise ValueError("Email credentials not found in credentials.json")
            
            # Find manager email from users
            manager_emails = []
            for user in credentials.get('users', []):
                if user.get('role') == 'manager':
                    manager_emails.append(user.get('email'))
            
            if not manager_emails:
                # Fallback to sending to the primary email
                manager_emails = [smtp_user]
            
            # Gmail SMTP configuration (assuming Gmail based on the app password format)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            
            # Email content
            subject = "Climate Risk Assessment Report - DigiClimate Store Hub"
            body = f"""\
Dear Manager,

Please find attached the latest Climate Risk Assessment Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}.

This comprehensive report includes:
- Current climate alerts and risk assessments
- Detailed analysis of affected materials
- Recommended actions for risk mitigation

Please review the attached PDF for complete details.

Best regards,
DigiClimate Store Hub System
            """
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ", ".join(manager_emails)
            msg['Subject'] = subject
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF report
            with open(pdf_path, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name=os.path.basename(pdf_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            raise e
    
    def _get_risk_summary(self, current_alerts, status_data):
        """Generate a concise risk summary for the report"""
        high_count = 0
        medium_count = 0
        low_count = 0
        
        if isinstance(current_alerts, list):
            for alert in current_alerts:
                if isinstance(alert, dict):
                    severity = alert.get('severity', '').upper()
                    
                    if severity == 'HIGH':
                        high_count += 1
                    elif severity == 'MEDIUM':
                        medium_count += 1
                    elif severity == 'LOW':
                        low_count += 1
        
        return f"{high_count}H/{medium_count}M risks"
        
    def complete_selected_action(self):
        """Mark selected action as complete"""
        selection = self.actions_tree.selection()
        if selection:
            item = selection[0]
            values = list(self.actions_tree.item(item, 'values'))
            if len(values) >= 5:
                values[4] = '✅ Complete'
                self.actions_tree.item(item, values=values)
                
                # Add to recent actions summary with more details
                action_name = values[1] if len(values) > 1 else "Unknown action"
                material_name = values[2] if len(values) > 2 else "Unknown material"
                self.add_recent_action_summary("Completed", "Low", f"✅ {action_name[:20]}", material_name)
                
                self.log_action(f"✅ Completed: {values[1]}")
        else:
            messagebox.showwarning("No Selection", "Please select an action to complete.")
            
    def edit_selected_action(self):
        """Edit selected action"""
        selection = self.actions_tree.selection()
        if selection:
            self.show_edit_dialog()
        else:
            messagebox.showwarning("No Selection", "Please select an action to edit.")
            
    def delete_selected_action(self):
        """Delete selected action"""
        selection = self.actions_tree.selection()
        if selection:
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this action?"):
                item = selection[0]
                values = self.actions_tree.item(item, 'values')
                
                # Add to recent actions summary with more details
                action_name = values[1] if len(values) > 1 else "Unknown action"
                material_name = values[2] if len(values) > 2 else "Unknown material"
                self.add_recent_action_summary("Deleted", "Info", f"🗑️ {action_name[:20]}", material_name)
                
                self.actions_tree.delete(item)
                self.log_action(f"🗑️ Deleted: {values[1] if values else 'Unknown action'}")
        else:
            messagebox.showwarning("No Selection", "Please select an action to delete.")
    
    def show_new_action_form(self):
        """Show simplified new action form"""
        self.show_action_dialog()
        
    def show_action_dialog(self, edit_mode=False):
        """Show simplified action creation/edit dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("New Action" if not edit_mode else "Edit Action")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Form fields
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Action type
        ttk.Label(main_frame, text="Action Type:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        action_var = tk.StringVar()
        action_combo = ttk.Combobox(main_frame, textvariable=action_var,
                                   values=["Weather Alert", "Inventory Check", "Supplier Contact", 
                                          "Risk Assessment", "Price Monitor"], state="readonly")
        action_combo.pack(fill='x', pady=(0, 15))
        
        # Material
        ttk.Label(main_frame, text="Material:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        material_var = tk.StringVar()
        material_combo = ttk.Combobox(main_frame, textvariable=material_var,
                                     values=["Cotton", "Rice", "Wheat", "Sugarcane", "All Materials"],
                                     state="readonly")
        material_combo.pack(fill='x', pady=(0, 15))
        
        # Priority
        ttk.Label(main_frame, text="Priority:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(main_frame, textvariable=priority_var,
                                     values=["Low", "Medium", "High"], state="readonly")
        priority_combo.pack(fill='x', pady=(0, 15))
        
        # Due date
        ttk.Label(main_frame, text="Due Date:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        due_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        due_entry = ttk.Entry(main_frame, textvariable=due_var)
        due_entry.pack(fill='x', pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        def save_action():
            if action_var.get() and material_var.get():
                priority_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}
                priority_display = f"{priority_emoji.get(priority_var.get(), '🟡')} {priority_var.get()}"
                
                new_values = (priority_display, action_var.get(), material_var.get(), 
                             due_var.get(), '⏳ Pending')
                
                # Determine styling tag based on priority
                priority_level = priority_var.get()
                if priority_level == 'High':
                    tag = 'high_priority'
                elif priority_level == 'Medium':
                    tag = 'medium_priority'
                elif priority_level == 'Low':
                    tag = 'low_priority'
                else:
                    tag = 'alternating'
                
                # Insert with appropriate styling
                self.actions_tree.insert('', 'end', values=new_values, tags=(tag,))
                self.log_action(f"➕ Added: {action_var.get()} for {material_var.get()}")
                dialog.destroy()
            else:
                messagebox.showwarning("Missing Information", "Please fill in all required fields.")
        
        ttk.Button(button_frame, text="💾 Save", command=save_action).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", command=dialog.destroy).pack(side='left')
    
    def show_edit_dialog(self):
        """Show edit dialog for selected action"""
        self.show_action_dialog(edit_mode=True)
    
    def on_action_double_click(self, event):
        """Handle double-click on action"""
        self.show_edit_dialog()
        
    def on_action_select(self, event):
        """Handle action selection"""
        selection = self.actions_tree.selection()
        if selection:
            values = self.actions_tree.item(selection[0], 'values')
            if values:
                self.log_action(f"📋 Selected: {values[1]}")
    
    def on_tree_motion(self, event):
        """Handle mouse motion over treeview for hover effect"""
        region = self.actions_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.actions_tree.identify_row(event.y)
            if item != self.last_hover_item:
                # Reset previous hover item to its original tags
                if self.last_hover_item:
                    self.restore_item_tags(self.last_hover_item)
                
                # Apply hover effect while preserving priority styling
                if item:
                    current_tags = self.actions_tree.item(item, 'tags')
                    hover_tags = list(current_tags) + ['hover'] if current_tags else ['hover']
                    self.actions_tree.item(item, tags=hover_tags)
                    self.last_hover_item = item
        elif self.last_hover_item:
            self.restore_item_tags(self.last_hover_item)
            self.last_hover_item = None
    
    def on_tree_leave(self, event):
        """Handle mouse leave treeview"""
        if self.last_hover_item:
            self.restore_item_tags(self.last_hover_item)
            self.last_hover_item = None
    
    def restore_item_tags(self, item):
        """Restore original tags for an item (remove hover effect)"""
        current_tags = self.actions_tree.item(item, 'tags')
        if current_tags and 'hover' in current_tags:
            original_tags = [tag for tag in current_tags if tag != 'hover']
            self.actions_tree.item(item, tags=original_tags)
    
    def add_recent_action_summary(self, action_type, priority, description, material):
        """Add an entry to the recent actions summary treeview"""
        timestamp = datetime.now().strftime('%H:%M')
        
        # Priority display mapping
        priority_display = {
            'High': '🔴 High',
            'Medium': '🟡 Medium', 
            'Low': '🟢 Low',
            'Info': 'ℹ️ Info'
        }
        
        priority_text = priority_display.get(priority, priority)
        
        # Truncate long descriptions
        if len(description) > 30:
            description = description[:27] + "..."
        
        # Add to recent actions treeview
        item_id = self.recent_tree.insert('', 0, values=(timestamp, priority_text, description, material))
        
        # Keep only the last 20 entries
        children = self.recent_tree.get_children()
        if len(children) > 20:
            # Remove the oldest entries
            for old_item in children[20:]:
                self.recent_tree.delete(old_item)
                
        # Scroll to show the newest entry
        self.recent_tree.see(item_id)
    
    def log_action(self, message):
        """Log action - now updates the recent actions summary instead of text log"""
        # Extract useful information from the message for the summary
        if "Created weather alerts" in message:
            self.add_recent_action_summary("Weather Alert", "High", "Weather alerts created", "Multiple Materials")
        elif "security actions" in message:
            self.add_recent_action_summary("Security", "High", "Inventory security activated", "At Risk Materials")
        elif "supplier contact" in message:
            self.add_recent_action_summary("Supplier", "Medium", "Supplier notifications sent", "High Risk Materials")
        elif "Risk assessment" in message or "PDF generated" in message:
            self.add_recent_action_summary("Report", "Medium", "PDF report generated & emailed", "All Materials")
        elif "Completed:" in message:
            action_name = message.split("Completed: ")[1] if "Completed: " in message else "Unknown"
            self.add_recent_action_summary("Completed", "Low", f"Completed: {action_name[:20]}", "Various")
        elif "Deleted:" in message:
            action_name = message.split("Deleted: ")[1] if "Deleted: " in message else "Unknown"
            self.add_recent_action_summary("Deleted", "Info", f"Deleted: {action_name[:20]}", "Various")
        elif "Added:" in message:
            self.add_recent_action_summary("Added", "Info", "New action added", "Specified Material")
        elif "Error" in message:
            self.add_recent_action_summary("Error", "High", "Action failed - check logs", "System")
        else:
            # Generic system messages
            self.add_recent_action_summary("System", "Info", message[:30], "System")
    
    def refresh_data(self):
        """Refresh action data"""
        self.log_action("🔄 Data refreshed")
        
    def load_initial_data(self):
        """Load initial action data"""
        self.log_action("🚀 Climate Action Center initialized")
