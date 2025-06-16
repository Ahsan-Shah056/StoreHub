import csv
import tkinter as tk
from tkinter import filedialog, messagebox

def export_treeview_to_csv(treeview, parent_window=None):
    # Export the contents of a Tkinter Treeview to a CSV file
    # Prompt user for file location
    file_path = filedialog.asksaveasfilename(
        parent=parent_window,
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save Treeview Data as CSV"
    )
    if not file_path:
        return  # User cancelled
    try:
        # Get column headers
        columns = treeview['columns']
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(columns)
            # Write all rows
            for row_id in treeview.get_children():
                row = treeview.item(row_id)['values']
                writer.writerow(row)
        messagebox.showinfo("Export Successful", f"Data exported to {file_path}", parent=parent_window)
    except Exception as e:
        messagebox.showerror("Export Failed", f"An error occurred while exporting: {e}", parent=parent_window)
