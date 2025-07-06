"""
Base components and utilities for Dashboard UI modules
Shared utilities, constants, and base classes for dashboard components
"""

import tkinter as tk
import logging
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
from PIL import Image, ImageTk
from tkcalendar import DateEntry

# Get logger instance
logger = logging.getLogger(__name__)

class DashboardBaseUI:
    """Base class for dashboard UI components with common functionality"""
    
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.current_filters = {}
        
    def update_filters(self, filters):
        """Update current filters and refresh data"""
        self.current_filters = filters
        self.refresh_data(filters)
        
    def refresh_data(self, filters):
        """Override in subclasses to refresh data based on filters"""
        pass
        
    def show_error(self, title, message):
        """Show error message dialog"""
        messagebox.showerror(title, message)
        
    def show_info(self, title, message):
        """Show info message dialog"""
        messagebox.showinfo(title, message)
        
    def format_currency(self, value):
        """Format value as currency"""
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"
            
    def format_number(self, value):
        """Format number with commas"""
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return "0"
            
    def format_percentage(self, value, decimal_places=1):
        """Format value as percentage"""
        try:
            return f"{float(value):.{decimal_places}f}%"
        except (ValueError, TypeError):
            return "0.0%"

class DashboardConstants:
    """Constants used across dashboard components"""
    
    # Colors
    PRIMARY_COLOR = "#2E86AB"
    SUCCESS_COLOR = "#28a745"
    WARNING_COLOR = "#ffc107"
    DANGER_COLOR = "#dc3545"
    INFO_COLOR = "#17a2b8"
    TEXT_COLOR = "#333333"
    BACKGROUND_COLOR = "#ffffff"
    
    # Fonts
    HEADER_FONT = ("Helvetica", 16, "bold")
    SUBHEADER_FONT = ("Helvetica", 12, "bold")
    BODY_FONT = ("Helvetica", 10)
    SMALL_FONT = ("Helvetica", 9)
    
    # Chart colors
    CHART_COLORS = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
        '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
    ]
    
    # Default dimensions
    CHART_WIDTH = 800
    CHART_HEIGHT = 400
    CARD_WIDTH = 200
    CARD_HEIGHT = 120

def create_metric_card(parent, title, value, subtitle="", color=DashboardConstants.PRIMARY_COLOR):
    """Create a metric card widget"""
    card_frame = ttk.LabelFrame(parent, text=title, padding="10")
    
    # Value label
    value_label = ttk.Label(card_frame, text=str(value), 
                           font=DashboardConstants.HEADER_FONT,
                           foreground=color)
    value_label.pack()
    
    # Subtitle label
    if subtitle:
        subtitle_label = ttk.Label(card_frame, text=subtitle,
                                  font=DashboardConstants.SMALL_FONT)
        subtitle_label.pack()
    
    return card_frame

def create_status_indicator(parent, status, text=""):
    """Create a status indicator (green/yellow/red circle)"""
    frame = ttk.Frame(parent)
    
    # Status circle (simulated with colored label)
    if status == "good":
        color = DashboardConstants.SUCCESS_COLOR
        symbol = "●"
    elif status == "warning": 
        color = DashboardConstants.WARNING_COLOR
        symbol = "●"
    else:  # danger
        color = DashboardConstants.DANGER_COLOR
        symbol = "●"
        
    status_label = ttk.Label(frame, text=symbol, foreground=color,
                            font=("Helvetica", 12))
    status_label.pack(side='left')
    
    if text:
        text_label = ttk.Label(frame, text=text, font=DashboardConstants.BODY_FONT)
        text_label.pack(side='left', padx=(5, 0))
    
    return frame
