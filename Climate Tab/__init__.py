"""
Climate Tab Package
Climate management and monitoring system for DigiClimate Store Hub
"""

# Import main classes for easy access
from .climate_ui import ClimateUI
from .climate_data import (
    ClimateDataManager,
    climate_manager,
    get_current_climate_status,
    get_climate_forecast,
    get_affected_products,
    get_overall_climate_risk,
    get_climate_alerts
)
from .climate_base import (
    ClimateBaseUI,
    ClimateConstants,
    create_climate_metric_card,
    create_risk_indicator,
    create_material_status_card,
    get_material_info,
    get_climate_category_info
)

__version__ = "1.0.0"
__author__ = "DigiClimate Store Hub Team"
__description__ = "Climate monitoring and management system"

# Package metadata
__all__ = [
    'ClimateUI',
    'ClimateDataManager',
    'climate_manager',
    'ClimateBaseUI', 
    'ClimateConstants',
    'get_current_climate_status',
    'get_climate_forecast',
    'get_affected_products',
    'get_overall_climate_risk',
    'get_climate_alerts',
    'create_climate_metric_card',
    'create_risk_indicator',
    'create_material_status_card',
    'get_material_info',
    'get_climate_category_info'
]
