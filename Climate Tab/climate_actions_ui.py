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
        
        # Recent actions log
        log_frame = ttk.LabelFrame(container, text="📋 Recent Actions", padding="10")
        log_frame.pack(fill='both', expand=True)
        
        # Action log with improved styling
        self.action_log = tk.Text(log_frame, 
                                 height=12, 
                                 font=('Segoe UI', 10),
                                 bg='#f8f9fa',
                                 fg='#2c3e50',
                                 relief='flat',
                                 borderwidth=1,
                                 selectbackground='#3498db',
                                 selectforeground='white')
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.action_log.yview)
        self.action_log.configure(yscrollcommand=log_scrollbar.set)
        
        self.action_log.pack(side='left', fill='both', expand=True, padx=(0, 5))
        log_scrollbar.pack(side='right', fill='y')
        
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
    
    # Essential action methods
    def create_weather_alert(self):
        """Create weather alert action"""
        self.log_action("🌧️ Weather alert created for all materials")
        messagebox.showinfo("Weather Alert", "Weather monitoring alert has been activated!")
        
    def secure_inventory_action(self):
        """Secure inventory action"""
        self.log_action("📦 Inventory security measures activated")
        messagebox.showinfo("Inventory Secured", "Inventory protection protocols enabled!")
        
    def notify_suppliers_action(self):
        """Notify suppliers action"""
        self.log_action("📞 Supplier notifications sent")
        messagebox.showinfo("Suppliers Notified", "All suppliers have been contacted about current conditions!")
        
    def generate_risk_report(self):
        """Generate risk assessment report"""
        self.log_action("📊 Risk assessment report generated")
        messagebox.showinfo("Report Generated", "Climate risk assessment report has been created!")
        
    def complete_selected_action(self):
        """Mark selected action as complete"""
        selection = self.actions_tree.selection()
        if selection:
            item = selection[0]
            values = list(self.actions_tree.item(item, 'values'))
            if len(values) >= 5:
                values[4] = '✅ Complete'
                self.actions_tree.item(item, values=values)
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
    
    def log_action(self, message):
        """Log action to the action log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.action_log.config(state='normal')
        self.action_log.insert('end', log_entry)
        self.action_log.see('end')
        self.action_log.config(state='disabled')
    
    def refresh_data(self):
        """Refresh action data"""
        self.log_action("🔄 Data refreshed")
        
    def load_initial_data(self):
        """Load initial action data"""
        self.log_action("🚀 Climate Action Center initialized")
        self.log_action("📊 Ready to manage climate-related actions")
