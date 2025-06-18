"""
Climate Base Module
Base components and utilities for Climate UI modules
Shared utilities, constants, and base classes for climate components
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
from PIL import Image, ImageTk

class ClimateBaseUI:
    """Base class for climate UI components with common functionality"""
    
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.current_filters = {}
        
    def update_filters(self, filters):
        """Update current filters and refresh data"""
        self.current_filters = filters
        self.refresh_data(filters)
        
    def refresh_data(self, filters=None):
        """Override in subclasses to refresh data based on filters"""
        pass
        
    def show_error(self, title, message):
        """Show error message dialog"""
        messagebox.showerror(title, message)
        
    def show_info(self, title, message):
        """Show info message dialog"""
        messagebox.showinfo(title, message)
        
    def show_warning(self, title, message):
        """Show warning message dialog"""
        messagebox.showwarning(title, message)
        
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
    
    def format_date(self, date_value):
        """Format date for display"""
        try:
            if isinstance(date_value, str):
                date_obj = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
            else:
                date_obj = date_value
            return date_obj.strftime('%Y-%m-%d')
        except:
            return str(date_value)
    
    def format_datetime(self, datetime_value):
        """Format datetime for display"""
        try:
            if isinstance(datetime_value, str):
                date_obj = datetime.strptime(datetime_value, '%Y-%m-%d %H:%M:%S')
            else:
                date_obj = datetime_value
            return date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            return str(datetime_value)

class ClimateConstants:
    """Constants used across climate components"""
    
    # Colors
    PRIMARY_COLOR = "#2E86AB"
    SUCCESS_COLOR = "#28a745"
    WARNING_COLOR = "#ffc107"
    DANGER_COLOR = "#dc3545"
    INFO_COLOR = "#17a2b8"
    
    # Climate-specific colors
    CLIMATE_SAFE_COLOR = "#28a745"      # Green for safe conditions
    CLIMATE_CAUTION_COLOR = "#ffc107"   # Yellow for caution
    CLIMATE_WARNING_COLOR = "#fd7e14"   # Orange for warning
    CLIMATE_DANGER_COLOR = "#dc3545"    # Red for danger/critical
    
    # Risk level colors
    RISK_COLORS = {
        'LOW': "#28a745",       # Green
        'MEDIUM': "#ffc107",    # Yellow
        'HIGH': "#fd7e14",      # Orange
        'CRITICAL': "#dc3545"   # Red
    }
    
    # Fonts
    HEADER_FONT = ("Helvetica", 16, "bold")
    SUBHEADER_FONT = ("Helvetica", 12, "bold")
    BODY_FONT = ("Helvetica", 10)
    SMALL_FONT = ("Helvetica", 9)
    LARGE_FONT = ("Helvetica", 14, "bold")
    
    # Chart colors for climate data
    CLIMATE_CHART_COLORS = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
        '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
    ]
    
    # Default dimensions
    CHART_WIDTH = 800
    CHART_HEIGHT = 400
    CARD_WIDTH = 200
    CARD_HEIGHT = 120
    
    # Climate categories and their display info
    CLIMATE_CATEGORIES = {
        'Drought': {
            'color': '#dc3545',
            'icon': '🏜️',
            'description': 'Very dry conditions with minimal rainfall'
        },
        'Slightly Dry': {
            'color': '#fd7e14', 
            'icon': '🌤️',
            'description': 'Below normal moisture levels'
        },
        'Rainfall / Flood Risk': {
            'color': '#17a2b8',
            'icon': '🌧️',
            'description': 'Heavy rainfall with potential flooding'
        },
        'Pre-Drought/Heatwave': {
            'color': '#ffc107',
            'icon': '🌡️',
            'description': 'Rising temperatures and decreasing moisture'
        },
        'Rainfall _ Drought': {
            'color': '#6f42c1',
            'icon': '⛈️',
            'description': 'Mixed conditions with variable moisture'
        },
        'Start of Rainfall': {
            'color': '#20c997',
            'icon': '🌦️',
            'description': 'Beginning of rainy season'
        }
    }
    
    # Material info
    MATERIALS = {
        1: {
            'name': 'Wheat',
            'icon': '🌾',
            'color': '#ffc107',
            'description': 'Primary grain crop'
        },
        2: {
            'name': 'Sugarcane', 
            'icon': '🎋',
            'color': '#28a745',
            'description': 'Sugar production crop'
        },
        3: {
            'name': 'Cotton',
            'icon': '🌱',
            'color': '#17a2b8',
            'description': 'Textile fiber crop'
        },
        4: {
            'name': 'Rice',
            'icon': '🌾',
            'color': '#fd7e14',
            'description': 'Staple grain crop'
        }
    }

def create_climate_metric_card(parent, title, value, subtitle="", icon="", color=ClimateConstants.PRIMARY_COLOR):
    """Create a climate metric card widget"""
    card_frame = ttk.LabelFrame(parent, text=f"{icon} {title}", padding="10")
    
    # Value label with color
    value_label = ttk.Label(card_frame, text=str(value), 
                           font=ClimateConstants.HEADER_FONT)
    value_label.pack()
    
    # Subtitle label
    if subtitle:
        subtitle_label = ttk.Label(card_frame, text=subtitle,
                                  font=ClimateConstants.SMALL_FONT)
        subtitle_label.pack()
    
    return card_frame

def create_risk_indicator(parent, risk_level, size="normal"):
    """Create a risk level indicator widget"""
    color = ClimateConstants.RISK_COLORS.get(risk_level, ClimateConstants.INFO_COLOR)
    
    # Choose font based on size
    if size == "large":
        font = ClimateConstants.SUBHEADER_FONT
    else:
        font = ClimateConstants.BODY_FONT
    
    # Risk icons
    risk_icons = {
        'LOW': '✅',
        'MEDIUM': '⚠️', 
        'HIGH': '🔶',
        'CRITICAL': '🔴'
    }
    
    icon = risk_icons.get(risk_level, '❓')
    
    indicator_frame = ttk.Frame(parent)
    
    # Icon and text
    risk_label = ttk.Label(indicator_frame, 
                          text=f"{icon} {risk_level}",
                          font=font)
    risk_label.pack()
    
    return indicator_frame

def create_material_status_card(parent, material_data):
    """Create a material status card with current climate info"""
    material_info = ClimateConstants.MATERIALS.get(material_data['material_id'], {})
    icon = material_info.get('icon', '📦')
    
    card_frame = ttk.LabelFrame(parent, text=f"{icon} {material_data['material_name']}", padding="10")
    
    # Current condition
    condition_label = ttk.Label(card_frame, 
                               text=material_data['current_condition'][:30] + "..." if len(material_data['current_condition']) > 30 else material_data['current_condition'],
                               font=ClimateConstants.SMALL_FONT,
                               wraplength=180)
    condition_label.pack(pady=(0, 5))
    
    # Production impact
    impact = material_data['production_impact']
    impact_text = f"Impact: {'+' if impact >= 0 else ''}{impact:,.0f}"
    impact_color = ClimateConstants.SUCCESS_COLOR if impact >= 0 else ClimateConstants.DANGER_COLOR
    
    impact_label = ttk.Label(card_frame, text=impact_text, font=ClimateConstants.BODY_FONT)
    impact_label.pack()
    
    # Delay percentage
    delay_text = f"Delay: {material_data['delay_percent']:.1f}%"
    delay_label = ttk.Label(card_frame, text=delay_text, font=ClimateConstants.SMALL_FONT)
    delay_label.pack()
    
    # Risk indicator
    risk_frame = create_risk_indicator(card_frame, material_data['risk_level'])
    risk_frame.pack(pady=(5, 0))
    
    return card_frame

def format_climate_text(value):
    """Format text for consistent display in climate UI"""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        text = str(value).strip()
        # Keep certain climate terms as-is
        climate_terms = ['drought', 'flood', 'rainfall', 'dry', 'wet', 'heat', 'cold']
        if any(term in text.lower() for term in climate_terms):
            return text.title()
        return text
    return str(value)

def get_climate_category_info(category):
    """Get display information for a climate category"""
    return ClimateConstants.CLIMATE_CATEGORIES.get(category, {
        'color': ClimateConstants.INFO_COLOR,
        'icon': '🌍',
        'description': 'Climate condition'
    })

def get_material_info(material_id):
    """Get display information for a material"""
    return ClimateConstants.MATERIALS.get(material_id, {
        'name': 'Unknown',
        'icon': '📦',
        'color': ClimateConstants.INFO_COLOR,
        'description': 'Material'
    })
