"""
Climate Actions UI Module - Phase 3
Enhanced Actions subtab with actionable climate management features
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime, timedelta
import json
import os
import logging

from climate_base import ClimateBaseUI, ClimateConstants
import climate_data

# Set up logging
logger = logging.getLogger(__name__)

class ClimateActionsUI(ClimateBaseUI):
    """Enhanced Actions UI with real climate management functionality"""
    
    def __init__(self, parent_frame, callbacks=None):
        super().__init__(parent_frame, callbacks)
        self.climate_manager = climate_data.climate_manager
        
        # Action tracking
        self.pending_actions = []
        self.completed_actions = []
        
        self.create_actions_layout()
        self.load_initial_data()
        
    def create_actions_layout(self):
        """Create the main actions layout"""
        # Main container with padding
        self.main_container = ttk.Frame(self.parent, padding="15")
        self.main_container.pack(fill='both', expand=True)
        
        # Header section
        self.create_header_section()
        
        # Main content area with paned window
        self.create_content_panes()
        
    def create_header_section(self):
        """Create the header with title and action controls"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="🎯 Climate Action Center",
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(side='left')
        
        # Action controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        # New action button
        new_action_btn = ttk.Button(controls_frame,
                                   text="➕ New Action",
                                   command=self.show_new_action_form)
        new_action_btn.pack(side='right', padx=(5, 0))
        
        # Export actions button
        export_actions_btn = ttk.Button(controls_frame,
                                       text="📤 Export Actions",
                                       command=self.export_actions)
        export_actions_btn.pack(side='right', padx=(5, 0))
        
        # Refresh button
        refresh_btn = ttk.Button(controls_frame,
                                text="🔄 Refresh",
                                command=self.refresh_data)
        refresh_btn.pack(side='right', padx=(5, 0))
        
    def create_content_panes(self):
        """Create the main content with paned window layout"""
        # Create paned window for resizable layout
        self.paned_window = ttk.PanedWindow(self.main_container, orient='horizontal')
        self.paned_window.pack(fill='both', expand=True)
        
        # Left pane - Action center
        self.left_pane = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_pane, weight=2)
        
        # Right pane - Action details
        self.right_pane = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_pane, weight=1)
        
        # Create content for each pane
        self.create_action_center()
        self.create_action_details()
        
    def create_action_center(self):
        """Create the main action center interface"""
        # Action center notebook for different action views
        self.action_notebook = ttk.Notebook(self.left_pane)
        self.action_notebook.pack(fill='both', expand=True)
        
        # Quick actions tab
        self.quick_tab = ttk.Frame(self.action_notebook)
        self.action_notebook.add(self.quick_tab, text="⚡ Quick Actions")
        
        # Pending actions tab
        self.pending_tab = ttk.Frame(self.action_notebook)
        self.action_notebook.add(self.pending_tab, text="⏳ Pending")
        
        # Completed actions tab
        self.completed_tab = ttk.Frame(self.action_notebook)
        self.action_notebook.add(self.completed_tab, text="✅ Completed")
        
        # Create content for each tab
        self.create_quick_actions_tab()
        self.create_pending_actions_tab()
        self.create_completed_actions_tab()
        
    def create_quick_actions_tab(self):
        """Create quick actions for immediate climate response"""
        container = ttk.Frame(self.quick_tab, padding="10")
        container.pack(fill='both', expand=True)
        
        # Risk response section
        risk_frame = ttk.LabelFrame(container, text="🚨 Risk Response Actions", padding="10")
        risk_frame.pack(fill='x', pady=(0, 10))
        
        # Quick action buttons grid
        actions_grid = ttk.Frame(risk_frame)
        actions_grid.pack(fill='x')
        
        # Define quick actions
        quick_actions = [
            ("🌧️ Weather Alert", self.create_weather_alert),
            ("📦 Secure Inventory", self.secure_inventory_action),
            ("🚚 Emergency Transport", self.emergency_transport_action),
            ("📞 Notify Suppliers", self.notify_suppliers_action),
            ("🔒 Lock Prices", self.lock_prices_action),
            ("📊 Generate Report", self.generate_risk_report)
        ]
        
        # Create action buttons in 2x3 grid
        for i, (text, command) in enumerate(quick_actions):
            row, col = i // 2, i % 2
            btn = ttk.Button(actions_grid, text=text, command=command, width=20)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Configure grid weights
        actions_grid.grid_columnconfigure(0, weight=1)
        actions_grid.grid_columnconfigure(1, weight=1)
        
        # Climate monitoring section
        monitoring_frame = ttk.LabelFrame(container, text="📡 Monitoring Actions", padding="10")
        monitoring_frame.pack(fill='x', pady=(0, 10))
        
        # Monitoring controls
        monitoring_controls = ttk.Frame(monitoring_frame)
        monitoring_controls.pack(fill='x')
        
        ttk.Button(monitoring_controls, text="🔍 Check All Materials", 
                  command=self.check_all_materials).pack(side='left', padx=(0, 10))
        ttk.Button(monitoring_controls, text="⚠️ Review Alerts", 
                  command=self.review_alerts).pack(side='left', padx=(0, 10))
        ttk.Button(monitoring_controls, text="📈 Update Forecasts", 
                  command=self.update_forecasts).pack(side='left', padx=(0, 10))
        ttk.Button(monitoring_controls, text="🤖 Smart Suggestions", 
                  command=self.show_smart_suggestions).pack(side='left', padx=(0, 10))
        ttk.Button(monitoring_controls, text="⚙️ Email Settings", 
                  command=self.show_email_settings).pack(side='left')
        
        # Smart suggestions section
        suggestions_frame = ttk.LabelFrame(container, text="🤖 Rule-Based Recommendations", padding="5")
        suggestions_frame.pack(fill='x', pady=(0, 10))
        
        # Suggestions display
        self.suggestions_text = tk.Text(suggestions_frame, height=6, font=ClimateConstants.SMALL_FONT)
        suggestions_scrollbar = ttk.Scrollbar(suggestions_frame, orient="vertical", command=self.suggestions_text.yview)
        self.suggestions_text.configure(yscrollcommand=suggestions_scrollbar.set)
        self.suggestions_text.pack(side='left', fill='both', expand=True)
        suggestions_scrollbar.pack(side='right', fill='y')
        
        # Auto-refresh suggestions
        self.refresh_smart_suggestions()
        
        # Action log section
        log_frame = ttk.LabelFrame(container, text="📋 Recent Actions", padding="5")
        log_frame.pack(fill='both', expand=True)
        
        # Action log text widget
        self.action_log = tk.Text(log_frame, height=8, font=ClimateConstants.SMALL_FONT)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.action_log.yview)
        self.action_log.configure(yscrollcommand=log_scrollbar.set)
        
        self.action_log.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
    def create_pending_actions_tab(self):
        """Create pending actions management interface"""
        container = ttk.Frame(self.pending_tab, padding="10")
        container.pack(fill='both', expand=True)
        
        # Bulk actions toolbar
        bulk_frame = ttk.Frame(container)
        bulk_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(bulk_frame, text="Bulk Actions:").pack(side='left')
        
        ttk.Button(bulk_frame, text="✅ Complete Selected", 
                  command=self.bulk_complete_actions).pack(side='left', padx=(10, 5))
        ttk.Button(bulk_frame, text="🗑️ Delete Selected", 
                  command=self.bulk_delete_actions).pack(side='left', padx=(0, 5))
        ttk.Button(bulk_frame, text="📝 Edit Priority", 
                  command=self.bulk_edit_priority).pack(side='left', padx=(0, 5))
        ttk.Button(bulk_frame, text="📅 Edit Due Date", 
                  command=self.bulk_edit_due_date).pack(side='left')
        
        # Pending actions list
        columns = ('ID', 'Action Type', 'Material', 'Priority', 'Due Date', 'Status')
        self.pending_tree = ttk.Treeview(container, columns=columns, show='headings', height=12)
        
        # Configure columns
        column_widths = {'ID': 60, 'Action Type': 150, 'Material': 100, 
                        'Priority': 80, 'Due Date': 100, 'Status': 100}
        
        for col in columns:
            self.pending_tree.heading(col, text=col)
            self.pending_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        pending_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.pending_tree.yview)
        self.pending_tree.configure(yscrollcommand=pending_scrollbar.set)
        
        # Pack treeview
        self.pending_tree.pack(side='left', fill='both', expand=True)
        pending_scrollbar.pack(side='right', fill='y')
        
        # Bind double-click event
        self.pending_tree.bind('<Double-1>', self.on_pending_action_select)
        
        # Context menu for pending actions
        self.create_pending_context_menu()
        
        # Bulk actions frame
        self.create_bulk_actions_frame()
        
    def create_completed_actions_tab(self):
        """Create completed actions history interface"""
        container = ttk.Frame(self.completed_tab, padding="10")
        container.pack(fill='both', expand=True)
        
        # Filter frame
        filter_frame = ttk.Frame(container)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by:").pack(side='left')
        
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=["All", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
                                   state="readonly", width=15)
        filter_combo.pack(side='left', padx=(5, 0))
        filter_combo.bind('<<ComboboxSelected>>', self.filter_completed_actions)
        
        # Completed actions list
        columns = ('Date', 'Action Type', 'Material', 'Result', 'Duration')
        self.completed_tree = ttk.Treeview(container, columns=columns, show='headings', height=12)
        
        # Configure columns
        column_widths = {'Date': 100, 'Action Type': 150, 'Material': 100, 
                        'Result': 150, 'Duration': 80}
        
        for col in columns:
            self.completed_tree.heading(col, text=col)
            self.completed_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        completed_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.completed_tree.yview)
        self.completed_tree.configure(yscrollcommand=completed_scrollbar.set)
        
        # Pack treeview
        self.completed_tree.pack(side='left', fill='both', expand=True)
        completed_scrollbar.pack(side='right', fill='y')
        
    def create_action_details(self):
        """Create action details panel"""
        # Details notebook
        self.details_notebook = ttk.Notebook(self.right_pane)
        self.details_notebook.pack(fill='both', expand=True)
        
        # Action details tab
        self.details_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.details_tab, text="📋 Details")
        
        # Action form tab
        self.form_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.form_tab, text="➕ New Action")
        
        # Create content for detail tabs
        self.create_details_view()
        self.create_action_form()
        
    def create_details_view(self):
        """Create action details view"""
        container = ttk.Frame(self.details_tab, padding="10")
        container.pack(fill='both', expand=True)
        
        # Selected action details
        self.details_text = tk.Text(container, wrap=tk.WORD, font=ClimateConstants.SMALL_FONT,
                                   state='disabled', height=15)
        details_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side='left', fill='both', expand=True)
        details_scrollbar.pack(side='right', fill='y')
        
        # Action buttons frame
        buttons_frame = ttk.Frame(container)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        self.complete_btn = ttk.Button(buttons_frame, text="✅ Mark Complete",
                                      command=self.complete_selected_action,
                                      state='disabled')
        self.complete_btn.pack(side='left', padx=(0, 5))
        
        self.edit_btn = ttk.Button(buttons_frame, text="✏️ Edit Action",
                                  command=self.edit_selected_action,
                                  state='disabled')
        self.edit_btn.pack(side='left', padx=(0, 5))
        
        self.delete_btn = ttk.Button(buttons_frame, text="🗑️ Delete",
                                    command=self.delete_selected_action,
                                    state='disabled')
        self.delete_btn.pack(side='left')
        
    def create_action_form(self):
        """Create new action form"""
        container = ttk.Frame(self.form_tab, padding="10")
        container.pack(fill='both', expand=True)
        
        # Form fields
        ttk.Label(container, text="Action Type:").pack(anchor='w')
        self.action_type_var = tk.StringVar()
        action_type_combo = ttk.Combobox(container, textvariable=self.action_type_var,
                                        values=["Weather Alert", "Inventory Secure", "Price Lock",
                                               "Supplier Contact", "Transport Plan", "Risk Assessment"],
                                        state="readonly")
        action_type_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(container, text="Material:").pack(anchor='w')
        self.material_var = tk.StringVar()
        material_combo = ttk.Combobox(container, textvariable=self.material_var,
                                     values=["Cotton", "Rice", "Wheat", "Sugarcane", "All Materials"],
                                     state="readonly")
        material_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(container, text="Priority:").pack(anchor='w')
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(container, textvariable=self.priority_var,
                                     values=["Low", "Medium", "High", "Critical"],
                                     state="readonly")
        priority_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(container, text="Due Date:").pack(anchor='w')
        self.due_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        due_date_entry = ttk.Entry(container, textvariable=self.due_date_var)
        due_date_entry.pack(fill='x', pady=(0, 10))
        
        ttk.Label(container, text="Description:").pack(anchor='w')
        self.description_text = tk.Text(container, height=5, font=ClimateConstants.SMALL_FONT)
        self.description_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Form buttons
        form_buttons = ttk.Frame(container)
        form_buttons.pack(fill='x')
        
        ttk.Button(form_buttons, text="💾 Save Action",
                  command=self.save_new_action).pack(side='left', padx=(0, 5))
        ttk.Button(form_buttons, text="🗑️ Clear Form",
                  command=self.clear_action_form).pack(side='left')
        
    def create_pending_context_menu(self):
        """Create context menu for pending actions"""
        self.pending_menu = tk.Menu(self.pending_tree, tearoff=0)
        self.pending_menu.add_command(label="✅ Mark Complete", command=self.complete_selected_action)
        self.pending_menu.add_command(label="✏️ Edit", command=self.edit_selected_action)
        self.pending_menu.add_separator()
        self.pending_menu.add_command(label="🗑️ Delete", command=self.delete_selected_action)
        
        # Bind right-click
        self.pending_tree.bind("<Button-3>", self.show_pending_context_menu)
        
    def create_bulk_actions_frame(self):
        """Create bulk actions toolbar"""
        bulk_frame = ttk.Frame(self.pending_tab)
        bulk_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        ttk.Label(bulk_frame, text="Bulk Actions:").pack(side='left')
        
        ttk.Button(bulk_frame, text="✅ Complete Selected", 
                  command=self.bulk_complete_actions).pack(side='left', padx=(10, 5))
        ttk.Button(bulk_frame, text="🗑️ Delete Selected", 
                  command=self.bulk_delete_actions).pack(side='left', padx=(0, 5))
        ttk.Button(bulk_frame, text="📝 Bulk Edit Priority", 
                  command=self.bulk_edit_priority).pack(side='left', padx=(0, 5))
        ttk.Button(bulk_frame, text="📅 Bulk Edit Due Date", 
                  command=self.bulk_edit_due_date).pack(side='left')
    
    # Quick Action Methods
    def create_weather_alert(self):
        """Create weather alert action"""
        self.log_action("Created weather alert for all materials")
        self.create_action_item("Weather Alert", "All Materials", "High", 
                               "Monitor weather conditions and prepare for potential impacts")
        
    def secure_inventory_action(self):
        """Create secure inventory action"""
        self.log_action("Initiated inventory security protocols")
        self.create_action_item("Inventory Secure", "All Materials", "High",
                               "Secure physical inventory against weather threats")
        
    def emergency_transport_action(self):
        """Create emergency transport action"""
        self.log_action("Emergency transport protocols activated")
        self.create_action_item("Transport Plan", "All Materials", "Critical",
                               "Arrange emergency transportation for at-risk inventory")
        
    def notify_suppliers_action(self):
        """Create notify suppliers action"""
        self.log_action("Supplier notification system activated")
        self.create_action_item("Supplier Contact", "All Materials", "Medium",
                               "Notify suppliers of potential climate risks and delays")
        
    def lock_prices_action(self):
        """Create price lock action"""
        self.log_action("Price locking mechanism activated")
        self.create_action_item("Price Lock", "All Materials", "High",
                               "Lock current prices to protect against climate-driven volatility")
        
    def generate_risk_report(self):
        """Generate comprehensive risk report"""
        self.log_action("Generating comprehensive climate risk report")
        messagebox.showinfo("Report Generation", "Climate risk report generation initiated. Report will be available in 5-10 minutes.")
        
    def check_all_materials(self):
        """Check status of all materials"""
        self.log_action("Checking status of all climate-sensitive materials")
        status_data = self.climate_manager.get_current_climate_status()
        self.log_action(f"Status check complete: {len(status_data)} materials reviewed")
        
    def review_alerts(self):
        """Review all climate alerts"""
        alerts = self.climate_manager.get_climate_alerts()
        self.log_action(f"Reviewing {len(alerts)} active climate alerts")
        if alerts:
            alert_summary = "Active alerts:\n" + "\n".join([f"• {alert['material_name']}: {alert['message']}" for alert in alerts[:5]])
            messagebox.showinfo("Climate Alerts", alert_summary)
        else:
            messagebox.showinfo("Climate Alerts", "No active climate alerts at this time.")
        
    def update_forecasts(self):
        """Update climate forecasts"""
        self.log_action("Updating 7-day climate forecasts for all materials")
        messagebox.showinfo("Forecast Update", "Climate forecasts updated successfully.")
        
    # Action Management Methods
    def create_action_item(self, action_type, material, priority, description):
        """Create a new action item"""
        action_id = f"ACT{len(self.pending_actions) + 1:04d}"
        due_date = datetime.now() + timedelta(days=1)
        
        action = {
            'id': action_id,
            'type': action_type,
            'material': material,
            'priority': priority,
            'description': description,
            'due_date': due_date,
            'created_date': datetime.now(),
            'status': 'Pending'
        }
        
        self.pending_actions.append(action)
        self.refresh_pending_actions()
        
    def save_new_action(self):
        """Save new action from form"""
        if not self.action_type_var.get() or not self.material_var.get():
            messagebox.showerror("Error", "Please fill in all required fields")
            return
            
        try:
            due_date = datetime.strptime(self.due_date_var.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return
            
        description = self.description_text.get(1.0, tk.END).strip()
        
        action_id = f"ACT{len(self.pending_actions) + 1:04d}"
        
        action = {
            'id': action_id,
            'type': self.action_type_var.get(),
            'material': self.material_var.get(),
            'priority': self.priority_var.get(),
            'description': description,
            'due_date': due_date,
            'created_date': datetime.now(),
            'status': 'Pending'
        }
        
        self.pending_actions.append(action)
        self.refresh_pending_actions()
        self.clear_action_form()
        self.log_action(f"Created new action: {action['type']} for {action['material']}")
        messagebox.showinfo("Success", "Action created successfully!")
        
    def clear_action_form(self):
        """Clear the action form"""
        self.action_type_var.set("")
        self.material_var.set("")
        self.priority_var.set("Medium")
        self.due_date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.description_text.delete(1.0, tk.END)
        
    def complete_selected_action(self):
        """Mark selected action as complete"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an action to complete")
            return
            
        item = self.pending_tree.item(selection[0])
        action_id = item['values'][0]
        
        # Find and move action to completed
        for i, action in enumerate(self.pending_actions):
            if action['id'] == action_id:
                action['status'] = 'Completed'
                action['completed_date'] = datetime.now()
                self.completed_actions.append(action)
                self.pending_actions.pop(i)
                break
                
        self.refresh_pending_actions()
        self.refresh_completed_actions()
        self.log_action(f"Completed action: {action_id}")
        
    def edit_selected_action(self):
        """Edit selected action"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an action to edit")
            return
            
        item = self.pending_tree.item(selection[0])
        action_id = item['values'][0]
        
        # Find the action to edit
        action_to_edit = None
        for action in self.pending_actions:
            if action['id'] == action_id:
                action_to_edit = action
                break
                
        if action_to_edit:
            self.open_edit_dialog(action_to_edit)
        else:
            messagebox.showerror("Error", "Action not found")
            
    def open_edit_dialog(self, action):
        """Open edit dialog for action"""
        edit_window = tk.Toplevel(self.parent)
        edit_window.title(f"Edit Action - {action['id']}")
        edit_window.geometry("500x400")
        edit_window.resizable(True, True)
        
        # Make window modal
        edit_window.transient(self.parent)
        edit_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(edit_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text=f"Edit Action: {action['id']}", 
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(pady=(0, 15))
        
        # Form fields
        ttk.Label(main_frame, text="Action Type:").pack(anchor='w')
        edit_action_type_var = tk.StringVar(value=action['type'])
        action_type_combo = ttk.Combobox(main_frame, textvariable=edit_action_type_var,
                                        values=["Weather Alert", "Inventory Secure", "Price Lock",
                                               "Supplier Contact", "Transport Plan", "Risk Assessment"],
                                        state="readonly")
        action_type_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(main_frame, text="Material:").pack(anchor='w')
        edit_material_var = tk.StringVar(value=action['material'])
        material_combo = ttk.Combobox(main_frame, textvariable=edit_material_var,
                                     values=["Cotton", "Rice", "Wheat", "Sugarcane", "All Materials"],
                                     state="readonly")
        material_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(main_frame, text="Priority:").pack(anchor='w')
        edit_priority_var = tk.StringVar(value=action['priority'])
        priority_combo = ttk.Combobox(main_frame, textvariable=edit_priority_var,
                                     values=["Low", "Medium", "High", "Critical"],
                                     state="readonly")
        priority_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(main_frame, text="Due Date:").pack(anchor='w')
        edit_due_date_var = tk.StringVar(value=action['due_date'].strftime('%Y-%m-%d'))
        due_date_entry = ttk.Entry(main_frame, textvariable=edit_due_date_var)
        due_date_entry.pack(fill='x', pady=(0, 10))
        
        ttk.Label(main_frame, text="Description:").pack(anchor='w')
        edit_description_text = tk.Text(main_frame, height=8, font=ClimateConstants.SMALL_FONT)
        edit_description_text.insert(1.0, action['description'])
        edit_description_text.pack(fill='both', expand=True, pady=(0, 15))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        def save_changes():
            """Save the edited action"""
            try:
                new_due_date = datetime.strptime(edit_due_date_var.get(), '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
                
            # Update action
            action['type'] = edit_action_type_var.get()
            action['material'] = edit_material_var.get()
            action['priority'] = edit_priority_var.get()
            action['due_date'] = new_due_date
            action['description'] = edit_description_text.get(1.0, tk.END).strip()
            action['modified_date'] = datetime.now()
            
            # Refresh display
            self.refresh_pending_actions()
            self.log_action(f"Updated action: {action['id']}")
            
            edit_window.destroy()
            messagebox.showinfo("Success", "Action updated successfully!")
            
        def cancel_edit():
            """Cancel editing"""
            edit_window.destroy()
            
        ttk.Button(buttons_frame, text="💾 Save Changes", 
                  command=save_changes).pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="❌ Cancel", 
                  command=cancel_edit).pack(side='left')
        
    def delete_selected_action(self):
        """Delete selected action"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an action to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this action?"):
            item = self.pending_tree.item(selection[0])
            action_id = item['values'][0]
            
            # Remove from pending actions
            self.pending_actions = [a for a in self.pending_actions if a['id'] != action_id]
            self.refresh_pending_actions()
            self.log_action(f"Deleted action: {action_id}")
            
    def export_actions(self):
        """Export actions with multiple format options"""
        export_window = tk.Toplevel(self.parent)
        export_window.title("Export Climate Actions")
        export_window.geometry("400x300")
        export_window.resizable(False, False)
        
        # Make window modal
        export_window.transient(self.parent)
        export_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(export_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="Export Climate Actions", 
                               font=ClimateConstants.SUBHEADER_FONT)
        title_label.pack(pady=(0, 15))
        
        # Export format selection
        ttk.Label(main_frame, text="Export Format:").pack(anchor='w')
        format_var = tk.StringVar(value="JSON")
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Radiobutton(format_frame, text="JSON", variable=format_var, 
                       value="JSON").pack(anchor='w')
        ttk.Radiobutton(format_frame, text="CSV", variable=format_var, 
                       value="CSV").pack(anchor='w')
        ttk.Radiobutton(format_frame, text="Text Report", variable=format_var, 
                       value="TXT").pack(anchor='w')
        
        # Data selection
        ttk.Label(main_frame, text="Data to Export:").pack(anchor='w')
        data_frame = ttk.Frame(main_frame)
        data_frame.pack(fill='x', pady=(0, 15))
        
        pending_var = tk.BooleanVar(value=True)
        completed_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(data_frame, text="Pending Actions", 
                       variable=pending_var).pack(anchor='w')
        ttk.Checkbutton(data_frame, text="Completed Actions", 
                       variable=completed_var).pack(anchor='w')
        
        # Date range option
        ttk.Label(main_frame, text="Date Range:").pack(anchor='w')
        date_range_var = tk.StringVar(value="All")
        date_combo = ttk.Combobox(main_frame, textvariable=date_range_var,
                                 values=["All", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
                                 state="readonly")
        date_combo.pack(fill='x', pady=(0, 15))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        def perform_export():
            """Perform the export based on selections"""
            if not pending_var.get() and not completed_var.get():
                messagebox.showerror("Error", "Please select at least one data type to export")
                return
                
            # Determine file extension
            extensions = {"JSON": ".json", "CSV": ".csv", "TXT": ".txt"}
            filetypes = {
                "JSON": [("JSON files", "*.json"), ("All files", "*.*")],
                "CSV": [("CSV files", "*.csv"), ("All files", "*.*")],
                "TXT": [("Text files", "*.txt"), ("All files", "*.*")]
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=extensions[format_var.get()],
                filetypes=filetypes[format_var.get()],
                title="Export Climate Actions"
            )
            
            if filename:
                try:
                    self.export_to_file(filename, format_var.get(), 
                                      pending_var.get(), completed_var.get(),
                                      date_range_var.get())
                    export_window.destroy()
                    messagebox.showinfo("Success", f"Actions exported to {filename}")
                    self.log_action(f"Exported actions to {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export actions: {str(e)}")
        
        def cancel_export():
            """Cancel export"""
            export_window.destroy()
            
        ttk.Button(buttons_frame, text="📤 Export", 
                  command=perform_export).pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="❌ Cancel", 
                  command=cancel_export).pack(side='left')
                  
    def export_to_file(self, filename, format_type, include_pending, include_completed, date_range):
        """Export actions to file in specified format"""
        # Filter data based on date range
        def filter_by_date(actions):
            if date_range == "All":
                return actions
            
            cutoff_date = None
            if date_range == "Last 7 Days":
                cutoff_date = datetime.now() - timedelta(days=7)
            elif date_range == "Last 30 Days":
                cutoff_date = datetime.now() - timedelta(days=30)
            elif date_range == "Last 90 Days":
                cutoff_date = datetime.now() - timedelta(days=90)
                
            if cutoff_date:
                return [a for a in actions if a['created_date'] >= cutoff_date]
            return actions
        
        # Prepare data
        export_data = {}
        
        if include_pending:
            export_data['pending_actions'] = filter_by_date(self.pending_actions)
            
        if include_completed:
            export_data['completed_actions'] = filter_by_date(self.completed_actions)
            
        export_data['export_info'] = {
            'export_date': datetime.now().isoformat(),
            'date_range': date_range,
            'total_pending': len(export_data.get('pending_actions', [])),
            'total_completed': len(export_data.get('completed_actions', []))
        }
        
        # Export based on format
        if format_type == "JSON":
            self.export_json(filename, export_data)
        elif format_type == "CSV":
            self.export_csv(filename, export_data)
        elif format_type == "TXT":
            self.export_txt(filename, export_data)
            
    def export_json(self, filename, data):
        """Export to JSON format"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
            
    def export_csv(self, filename, data):
        """Export to CSV format"""
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Type', 'ID', 'Action Type', 'Material', 'Priority', 
                           'Status', 'Created Date', 'Due Date', 'Description'])
            
            # Write pending actions
            for action in data.get('pending_actions', []):
                writer.writerow([
                    'Pending', action['id'], action['type'], action['material'],
                    action['priority'], action['status'], 
                    action['created_date'].strftime('%Y-%m-%d %H:%M'),
                    action['due_date'].strftime('%Y-%m-%d'),
                    action['description']
                ])
                
            # Write completed actions
            for action in data.get('completed_actions', []):
                completed_date = action.get('completed_date', action['created_date'])
                writer.writerow([
                    'Completed', action['id'], action['type'], action['material'],
                    action['priority'], action['status'],
                    action['created_date'].strftime('%Y-%m-%d %H:%M'),
                    action['due_date'].strftime('%Y-%m-%d'),
                    action['description']
                ])
                
    def export_txt(self, filename, data):
        """Export to text report format"""
        with open(filename, 'w') as f:
            f.write("CLIMATE ACTIONS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Export info
            info = data['export_info']
            f.write(f"Export Date: {info['export_date']}\n")
            f.write(f"Date Range: {info['date_range']}\n")
            f.write(f"Total Pending Actions: {info['total_pending']}\n")
            f.write(f"Total Completed Actions: {info['total_completed']}\n\n")
            
            # Pending actions
            if 'pending_actions' in data:
                f.write("PENDING ACTIONS\n")
                f.write("-" * 30 + "\n\n")
                
                for action in data['pending_actions']:
                    f.write(f"ID: {action['id']}\n")
                    f.write(f"Type: {action['type']}\n")
                    f.write(f"Material: {action['material']}\n")
                    f.write(f"Priority: {action['priority']}\n")
                    f.write(f"Due Date: {action['due_date'].strftime('%Y-%m-%d')}\n")
                    f.write(f"Created: {action['created_date'].strftime('%Y-%m-%d %H:%M')}\n")
                    f.write(f"Description: {action['description']}\n")
                    f.write("-" * 50 + "\n\n")
                    
            # Completed actions
            if 'completed_actions' in data:
                f.write("COMPLETED ACTIONS\n")
                f.write("-" * 30 + "\n\n")
                
                for action in data['completed_actions']:
                    completed_date = action.get('completed_date', action['created_date'])
                    f.write(f"ID: {action['id']}\n")
                    f.write(f"Type: {action['type']}\n")
                    f.write(f"Material: {action['material']}\n")
                    f.write(f"Priority: {action['priority']}\n")
                    f.write(f"Completed: {completed_date.strftime('%Y-%m-%d %H:%M')}\n")
                    f.write(f"Description: {action['description']}\n")
                    f.write("-" * 50 + "\n\n")
                
    # UI Event Methods
    def on_pending_action_select(self, event):
        """Handle pending action selection"""
        selection = self.pending_tree.selection()
        if selection:
            item = self.pending_tree.item(selection[0])
            action_id = item['values'][0]
            
            # Find action details
            action = next((a for a in self.pending_actions if a['id'] == action_id), None)
            if action:
                self.show_action_details(action)
                
    def show_pending_context_menu(self, event):
        """Show context menu for pending actions"""
        selection = self.pending_tree.selection()
        if selection:
            self.pending_menu.post(event.x_root, event.y_root)
            
    def filter_completed_actions(self, event=None):
        """Filter completed actions by date range"""
        self.refresh_completed_actions()
        
    def show_action_details(self, action):
        """Show action details in the details panel"""
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        
        details = f"""Action Details
{'=' * 40}

ID: {action['id']}
Type: {action['type']}
Material: {action['material']}
Priority: {action['priority']}
Status: {action['status']}

Created: {action['created_date'].strftime('%Y-%m-%d %H:%M')}
Due Date: {action['due_date'].strftime('%Y-%m-%d')}

Description:
{action['description']}
"""
        
        self.details_text.insert(1.0, details)
        self.details_text.config(state='disabled')
        
        # Enable action buttons
        self.complete_btn.config(state='normal')
        self.edit_btn.config(state='normal')
        self.delete_btn.config(state='normal')
        
    # Data Management Methods
    def refresh_pending_actions(self):
        """Refresh pending actions list"""
        self.pending_tree.delete(*self.pending_tree.get_children())
        
        for action in self.pending_actions:
            self.pending_tree.insert('', 'end', values=(
                action['id'],
                action['type'],
                action['material'],
                action['priority'],
                action['due_date'].strftime('%Y-%m-%d'),
                action['status']
            ))
            
    def refresh_completed_actions(self):
        """Refresh completed actions list"""
        self.completed_tree.delete(*self.completed_tree.get_children())
        
        # Apply date filter
        filter_value = self.filter_var.get()
        cutoff_date = None
        
        if filter_value == "Last 7 Days":
            cutoff_date = datetime.now() - timedelta(days=7)
        elif filter_value == "Last 30 Days":
            cutoff_date = datetime.now() - timedelta(days=30)
        elif filter_value == "Last 90 Days":
            cutoff_date = datetime.now() - timedelta(days=90)
            
        for action in self.completed_actions:
            completed_date = action.get('completed_date', action['created_date'])
            
            if cutoff_date and completed_date < cutoff_date:
                continue
                
            duration = "N/A"
            if 'completed_date' in action:
                duration_delta = action['completed_date'] - action['created_date']
                duration = f"{duration_delta.days}d {duration_delta.seconds//3600}h"
                
            self.completed_tree.insert('', 'end', values=(
                completed_date.strftime('%Y-%m-%d'),
                action['type'],
                action['material'],
                "Success",  # Default result
                duration
            ))
            
    def log_action(self, message):
        """Log action to the action log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.action_log.config(state='normal')
        self.action_log.insert(tk.END, log_entry)
        self.action_log.see(tk.END)
        self.action_log.config(state='disabled')
        
    def load_initial_data(self):
        """Load initial action data"""
        # Add some sample actions for demonstration
        sample_actions = [
            {
                'id': 'ACT0001',
                'type': 'Weather Alert',
                'material': 'Cotton',
                'priority': 'High',
                'description': 'Monitor incoming storm system that may affect cotton storage facilities',
                'due_date': datetime.now() + timedelta(days=1),
                'created_date': datetime.now() - timedelta(hours=2),
                'status': 'Pending'
            },
            {
                'id': 'ACT0002',
                'type': 'Price Lock',
                'material': 'Wheat',
                'priority': 'Medium',
                'description': 'Lock wheat prices due to predicted drought conditions',
                'due_date': datetime.now() + timedelta(days=3),
                'created_date': datetime.now() - timedelta(hours=1),
                'status': 'Pending'
            }
        ]
        
        self.pending_actions.extend(sample_actions)
        self.refresh_pending_actions()
        
        self.log_action("Climate Actions UI initialized")
        self.log_action(f"Loaded {len(sample_actions)} pending actions")
        
    def refresh_data(self):
        """Refresh all action data"""
        self.refresh_pending_actions()
        self.refresh_completed_actions()
        self.log_action("Action data refreshed")
        
    def show_new_action_form(self):
        """Switch to new action form tab"""
        self.details_notebook.select(self.form_tab)
        
    def bulk_complete_actions(self):
        """Mark multiple selected actions as complete"""
        selections = self.pending_tree.selection()
        if not selections:
            messagebox.showwarning("Warning", "Please select actions to complete")
            return
            
        if messagebox.askyesno("Bulk Complete", f"Mark {len(selections)} actions as complete?"):
            completed_count = 0
            for selection in selections:
                item = self.pending_tree.item(selection)
                action_id = item['values'][0]
                
                # Find and move action to completed
                for i, action in enumerate(self.pending_actions):
                    if action['id'] == action_id:
                        action['status'] = 'Completed'
                        action['completed_date'] = datetime.now()
                        self.completed_actions.append(action)
                        self.pending_actions.pop(i)
                        completed_count += 1
                        break
            
            self.refresh_pending_actions()
            self.refresh_completed_actions()
            self.log_action(f"Bulk completed {completed_count} actions")
            messagebox.showinfo("Success", f"Completed {completed_count} actions")
    
    def bulk_delete_actions(self):
        """Delete multiple selected actions"""
        selections = self.pending_tree.selection()
        if not selections:
            messagebox.showwarning("Warning", "Please select actions to delete")
            return
            
        if messagebox.askyesno("Bulk Delete", f"Delete {len(selections)} actions permanently?"):
            deleted_count = 0
            action_ids = []
            
            for selection in selections:
                item = self.pending_tree.item(selection)
                action_ids.append(item['values'][0])
            
            # Remove actions
            self.pending_actions = [a for a in self.pending_actions if a['id'] not in action_ids]
            deleted_count = len(action_ids)
            
            self.refresh_pending_actions()
            self.log_action(f"Bulk deleted {deleted_count} actions")
            messagebox.showinfo("Success", f"Deleted {deleted_count} actions")
    
    def bulk_edit_priority(self):
        """Edit priority for multiple selected actions"""
        selections = self.pending_tree.selection()
        if not selections:
            messagebox.showwarning("Warning", "Please select actions to edit")
            return
            
        # Create priority selection dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Bulk Edit Priority")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text=f"Set priority for {len(selections)} selected actions:").pack(pady=(0, 10))
        
        priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(main_frame, textvariable=priority_var,
                                     values=["Low", "Medium", "High", "Critical"],
                                     state="readonly")
        priority_combo.pack(fill='x', pady=(0, 15))
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        def apply_priority():
            new_priority = priority_var.get()
            updated_count = 0
            
            for selection in selections:
                item = self.pending_tree.item(selection)
                action_id = item['values'][0]
                
                # Find and update action
                for action in self.pending_actions:
                    if action['id'] == action_id:
                        action['priority'] = new_priority
                        action['modified_date'] = datetime.now()
                        updated_count += 1
                        break
            
            self.refresh_pending_actions()
            self.log_action(f"Bulk updated priority for {updated_count} actions to {new_priority}")
            dialog.destroy()
            messagebox.showinfo("Success", f"Updated priority for {updated_count} actions")
        
        ttk.Button(buttons_frame, text="Apply", command=apply_priority).pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side='left')
    
    def bulk_edit_due_date(self):
        """Edit due date for multiple selected actions"""
        selections = self.pending_tree.selection()
        if not selections:
            messagebox.showwarning("Warning", "Please select actions to edit")
            return
            
        # Create due date selection dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Bulk Edit Due Date")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text=f"Set due date for {len(selections)} selected actions:").pack(pady=(0, 10))
        
        due_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(main_frame, textvariable=due_date_var).pack(fill='x', pady=(0, 15))
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        def apply_due_date():
            try:
                new_due_date = datetime.strptime(due_date_var.get(), '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
                
            updated_count = 0
            
            for selection in selections:
                item = self.pending_tree.item(selection)
                action_id = item['values'][0]
                
                # Find and update action
                for action in self.pending_actions:
                    if action['id'] == action_id:
                        action['due_date'] = new_due_date
                        action['modified_date'] = datetime.now()
                        updated_count += 1
                        break
            
            self.refresh_pending_actions()
            self.log_action(f"Bulk updated due date for {updated_count} actions")
            dialog.destroy()
            messagebox.showinfo("Success", f"Updated due date for {updated_count} actions")
        
        ttk.Button(buttons_frame, text="Apply", command=apply_due_date).pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side='left')

    # Smart Suggestions and Automation Methods
    def show_smart_suggestions(self):
        """Display smart rule-based suggestions dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Smart Rule-Based Suggestions")
        dialog.geometry("800x600")
        dialog.resizable(True, True)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="📊 Rule-Based Smart Suggestions", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 15))
        
        # Create notebook for different suggestion types
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Material recommendations tab
        recommendations_frame = ttk.Frame(notebook)
        notebook.add(recommendations_frame, text="Material Recommendations")
        
        # Get and display recommendations
        recommendations = self.climate_manager.get_smart_recommendations()
        
        recommendations_tree = ttk.Treeview(recommendations_frame, 
                                          columns=('Material', 'Risk', 'Urgency', 'Actions'), 
                                          show='headings', height=15)
        recommendations_tree.heading('Material', text='Material')
        recommendations_tree.heading('Risk', text='Risk Level')
        recommendations_tree.heading('Urgency', text='Urgency Score')
        recommendations_tree.heading('Actions', text='Recommended Actions')
        
        recommendations_tree.column('Material', width=100)
        recommendations_tree.column('Risk', width=80)
        recommendations_tree.column('Urgency', width=80)
        recommendations_tree.column('Actions', width=400)
        
        for rec in recommendations:
            actions_text = "; ".join(rec['recommendations'][:3])  # Show first 3 actions
            if len(rec['recommendations']) > 3:
                actions_text += f" (+{len(rec['recommendations'])-3} more)"
                
            recommendations_tree.insert('', 'end', values=(
                rec['material_name'],
                rec['current_risk_level'],
                f"{rec['urgency_score']:.1f}",
                actions_text
            ))
        
        recommendations_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Supplier integration tab
        supplier_frame = ttk.Frame(notebook)
        notebook.add(supplier_frame, text="Supplier Integration")
        
        supplier_suggestions = self.climate_manager.get_supplier_integration_suggestions()
        
        supplier_tree = ttk.Treeview(supplier_frame,
                                   columns=('Material', 'Risk', 'Action', 'Priority', 'Timeline'),
                                   show='headings', height=15)
        supplier_tree.heading('Material', text='Material')
        supplier_tree.heading('Risk', text='Current Risk')
        supplier_tree.heading('Action', text='Suggested Action')
        supplier_tree.heading('Priority', text='Priority')
        supplier_tree.heading('Timeline', text='Timeline')
        
        for suggestion in supplier_suggestions:
            for sug in suggestion['suggestions']:
                supplier_tree.insert('', 'end', values=(
                    suggestion['material_name'],
                    suggestion['current_risk'],
                    sug['action'],
                    sug['priority'],
                    sug['timeline']
                ))
        
        supplier_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Automation tab
        automation_frame = ttk.Frame(notebook)
        notebook.add(automation_frame, text="Automation Status")
        
        # Run automation check
        automation_results = self.climate_manager.run_automated_monitoring()
        
        automation_text = tk.Text(automation_frame, wrap='word', font=('Courier', 10))
        automation_scrollbar = ttk.Scrollbar(automation_frame, orient="vertical", command=automation_text.yview)
        automation_text.configure(yscrollcommand=automation_scrollbar.set)
        
        # Display automation results
        automation_text.insert('end', f"Automated Monitoring Report\n")
        automation_text.insert('end', f"{'='*50}\n\n")
        automation_text.insert('end', f"Monitoring Time: {automation_results['monitoring_time']}\n")
        automation_text.insert('end', f"Email Alerts Sent: {automation_results['alerts_sent']}\n")
        automation_text.insert('end', f"Actions Triggered: {automation_results['actions_triggered']}\n")
        automation_text.insert('end', f"Recommendations Generated: {automation_results['recommendations_generated']}\n\n")
        
        automation_text.insert('end', "Material Processing Results:\n")
        automation_text.insert('end', f"{'-'*30}\n")
        
        for material in automation_results['processed_materials']:
            automation_text.insert('end', f"\n{material['material_name']}:\n")
            if material['alerts']:
                automation_text.insert('end', f"  • Alerts: {', '.join(material['alerts'])}\n")
            if material['automated_actions']:
                automation_text.insert('end', f"  • Automated Actions: {len(material['automated_actions'])} rules triggered\n")
            if material['recommendations']:
                automation_text.insert('end', f"  • Recommendations: {material['recommendations']} generated\n")
        
        automation_text.configure(state='disabled')
        automation_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        automation_scrollbar.pack(side='right', fill='y', pady=10)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=dialog.destroy).pack(pady=(15, 0))

    def show_email_settings(self):
        """Show email-only alert settings dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Email Alert Settings")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="📧 Email Alert Configuration", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 15))
        
        # Email settings section
        email_frame = ttk.LabelFrame(main_frame, text="Email Configuration", padding="10")
        email_frame.pack(fill='x', pady=(0, 15))
        
        # SMTP settings
        ttk.Label(email_frame, text="SMTP Server:").grid(row=0, column=0, sticky='w', pady=5)
        smtp_server_var = tk.StringVar(value=self.climate_manager.email_config['smtp_server'])
        ttk.Entry(email_frame, textvariable=smtp_server_var, width=40).grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(email_frame, text="SMTP Port:").grid(row=1, column=0, sticky='w', pady=5)
        smtp_port_var = tk.StringVar(value=str(self.climate_manager.email_config['smtp_port']))
        ttk.Entry(email_frame, textvariable=smtp_port_var, width=40).grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(email_frame, text="Sender Email:").grid(row=2, column=0, sticky='w', pady=5)
        sender_email_var = tk.StringVar(value=self.climate_manager.email_config['sender_email'])
        ttk.Entry(email_frame, textvariable=sender_email_var, width=40).grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(email_frame, text="App Password:").grid(row=3, column=0, sticky='w', pady=5)
        password_var = tk.StringVar(value=self.climate_manager.email_config['sender_password'])
        ttk.Entry(email_frame, textvariable=password_var, width=40, show='*').grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        email_frame.columnconfigure(1, weight=1)
        
        # Recipients section
        recipients_frame = ttk.LabelFrame(main_frame, text="Alert Recipients", padding="10")
        recipients_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        ttk.Label(recipients_frame, text="Email Addresses (one per line):").pack(anchor='w')
        
        recipients_text = tk.Text(recipients_frame, height=8, width=60)
        recipients_scrollbar = ttk.Scrollbar(recipients_frame, orient="vertical", command=recipients_text.yview)
        recipients_text.configure(yscrollcommand=recipients_scrollbar.set)
        
        # Load current recipients
        current_recipients = "\n".join(self.climate_manager.email_config['recipient_emails'])
        recipients_text.insert('1.0', current_recipients)
        
        recipients_text.pack(side='left', fill='both', expand=True)
        recipients_scrollbar.pack(side='right', fill='y')
        
        # Alert thresholds section
        thresholds_frame = ttk.LabelFrame(main_frame, text="Alert Thresholds", padding="10")
        thresholds_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(thresholds_frame, text="High Risk Delay (%):").grid(row=0, column=0, sticky='w', pady=5)
        high_risk_var = tk.StringVar(value=str(self.climate_manager.thresholds['high_risk_delay']))
        ttk.Entry(thresholds_frame, textvariable=high_risk_var, width=10).grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        ttk.Label(thresholds_frame, text="Medium Risk Delay (%):").grid(row=0, column=2, sticky='w', padx=(20, 0), pady=5)
        medium_risk_var = tk.StringVar(value=str(self.climate_manager.thresholds['medium_risk_delay']))
        ttk.Entry(thresholds_frame, textvariable=medium_risk_var, width=10).grid(row=0, column=3, sticky='w', padx=(10, 0), pady=5)
        
        ttk.Label(thresholds_frame, text="Critical Production Drop (%):").grid(row=1, column=0, sticky='w', pady=5)
        critical_var = tk.StringVar(value=str(self.climate_manager.thresholds['critical_production_drop']))
        ttk.Entry(thresholds_frame, textvariable=critical_var, width=10).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Note about email-only alerts
        note_frame = ttk.Frame(main_frame)
        note_frame.pack(fill='x', pady=(0, 15))
        
        note_text = """📌 Note: All alerts are sent via email only. No in-app notifications or SMS alerts are available.
This ensures reliable delivery and maintains a permanent record of all climate-related alerts."""
        ttk.Label(note_frame, text=note_text, foreground='blue', wraplength=550).pack()
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        def save_email_settings():
            try:
                # Update email configuration
                self.climate_manager.email_config.update({
                    'smtp_server': smtp_server_var.get(),
                    'smtp_port': int(smtp_port_var.get()),
                    'sender_email': sender_email_var.get(),
                    'sender_password': password_var.get(),
                    'recipient_emails': [email.strip() for email in recipients_text.get('1.0', 'end').strip().split('\n') if email.strip()]
                })
                
                # Update thresholds
                self.climate_manager.thresholds.update({
                    'high_risk_delay': float(high_risk_var.get()),
                    'medium_risk_delay': float(medium_risk_var.get()),
                    'critical_production_drop': float(critical_var.get())
                })
                
                messagebox.showinfo("Success", "Email settings saved successfully!")
                self.log_action("Updated email alert settings and thresholds")
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving settings: {e}")
        
        def test_email():
            try:
                self.climate_manager.send_email_alert(
                    "Test Alert - DigiClimate Store Hub",
                    "This is a test email alert from the DigiClimate Store Hub system.\n\nIf you receive this message, the email configuration is working correctly."
                )
                messagebox.showinfo("Success", "Test email sent successfully!")
                self.log_action("Sent test email alert")
            except Exception as e:
                messagebox.showerror("Error", f"Error sending test email: {e}")
        
        ttk.Button(buttons_frame, text="Save Settings", command=save_email_settings).pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="Send Test Email", command=test_email).pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side='left')

    def refresh_smart_suggestions(self):
        """Refresh the smart suggestions display"""
        try:
            self.suggestions_text.configure(state='normal')
            self.suggestions_text.delete('1.0', 'end')
            
            # Get top 3 urgent recommendations
            recommendations = self.climate_manager.get_smart_recommendations()
            top_recommendations = recommendations[:3]
            
            if top_recommendations:
                self.suggestions_text.insert('end', "🤖 Smart Recommendations (Rule-Based):\n\n")
                
                for i, rec in enumerate(top_recommendations, 1):
                    self.suggestions_text.insert('end', f"{i}. {rec['material_name']} ({rec['current_risk_level']} Risk)\n")
                    self.suggestions_text.insert('end', f"   Urgency: {rec['urgency_score']:.1f}/100\n")
                    
                    # Show top 2 actions
                    for action in rec['recommendations'][:2]:
                        self.suggestions_text.insert('end', f"   • {action}\n")
                    
                    if len(rec['recommendations']) > 2:
                        self.suggestions_text.insert('end', f"   ... (+{len(rec['recommendations'])-2} more actions)\n")
                    
                    self.suggestions_text.insert('end', "\n")
            else:
                self.suggestions_text.insert('end', "✅ No urgent recommendations at this time.\n")
                self.suggestions_text.insert('end', "All materials are within acceptable risk levels.")
            
            self.suggestions_text.configure(state='disabled')
            
        except Exception as e:
            logger.error(f"Error refreshing smart suggestions: {e}")
            self.suggestions_text.configure(state='normal')
            self.suggestions_text.delete('1.0', 'end')
            self.suggestions_text.insert('end', f"Error loading suggestions: {e}")
            self.suggestions_text.configure(state='disabled')
