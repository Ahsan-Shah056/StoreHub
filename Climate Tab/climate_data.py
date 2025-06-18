"""
Climate Data Module
Functions for accessing and managing raw materials climate data
"""

import mysql.connector
from mysql.connector.errors import Error
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# Import database connection
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, close_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateDataManager:
    """Climate data access and management class"""
    
    def __init__(self):
        self.material_mapping = {
            1: "Wheat",
            2: "Sugarcane", 
            3: "Cotton",
            4: "Rice"
        }
        
    def get_connection(self):
        """Get database connection"""
        try:
            connection, cursor = get_db()
            return connection, cursor
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def get_current_climate_status(self) -> List[Dict[str, Any]]:
        """Get current climate status for all raw materials"""
        try:
            connection, cursor = self.get_connection()
            
            results = []
            for material_id, material_name in self.material_mapping.items():
                # Get latest climate data for each material
                if material_name == "Wheat":
                    table = "WheatProduction"
                elif material_name == "Cotton":
                    table = "CottonProduction"
                elif material_name == "Rice":
                    table = "RiceProduction"
                elif material_name == "Sugarcane":
                    table = "SugarcaneProduction"
                else:
                    continue
                
                query = f"""
                    SELECT 
                        material_id,
                        timestamp,
                        expected_condition,
                        category,
                        original_production,
                        delay_percent,
                        expected_production
                    FROM {table}
                    WHERE material_id = %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                """
                
                cursor.execute(query, (material_id,))
                result = cursor.fetchone()
                
                if result:
                    # Calculate production impact
                    original = float(result['original_production'])
                    expected = float(result['expected_production'])
                    delay_percent = float(result['delay_percent'])
                    
                    # Determine risk level
                    risk_level = self._calculate_risk_level(delay_percent)
                    
                    results.append({
                        'material_id': material_id,
                        'material_name': material_name,
                        'current_condition': result['expected_condition'],
                        'category': result['category'],
                        'original_production': original,
                        'expected_production': expected,
                        'delay_percent': delay_percent,
                        'production_impact': expected - original,
                        'risk_level': risk_level,
                        'last_updated': result['timestamp']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting current climate status: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_climate_forecast(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get climate forecast for next N days"""
        try:
            connection, cursor = self.get_connection()
            
            # Calculate date range
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)
            
            results = []
            for material_id, material_name in self.material_mapping.items():
                # Get forecast data for each material
                table_map = {
                    "Wheat": "WheatProduction",
                    "Cotton": "CottonProduction", 
                    "Rice": "RiceProduction",
                    "Sugarcane": "SugarcaneProduction"
                }
                
                table = table_map.get(material_name)
                if not table:
                    continue
                
                query = f"""
                    SELECT 
                        timestamp,
                        expected_condition,
                        category,
                        delay_percent,
                        expected_production,
                        original_production
                    FROM {table}
                    WHERE material_id = %s 
                    AND timestamp BETWEEN %s AND %s
                    ORDER BY timestamp ASC
                """
                
                cursor.execute(query, (material_id, start_date, end_date))
                forecast_data = cursor.fetchall()
                
                for row in forecast_data:
                    risk_level = self._calculate_risk_level(float(row['delay_percent']))
                    
                    results.append({
                        'material_id': material_id,
                        'material_name': material_name,
                        'forecast_date': row['timestamp'],
                        'expected_condition': row['expected_condition'],
                        'category': row['category'],
                        'delay_percent': float(row['delay_percent']),
                        'risk_level': risk_level,
                        'days_from_now': (row['timestamp'].date() - start_date.date()).days
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting climate forecast: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_affected_products(self, material_id: int) -> List[Dict[str, Any]]:
        """Get products that use a specific raw material"""
        try:
            connection, cursor = self.get_connection()
            
            query = """
                SELECT 
                    p.SKU,
                    p.name,
                    p.price,
                    p.cost,
                    p.stock,
                    p.category,
                    p.low_stock_threshold,
                    rm.name as material_name
                FROM Products p
                JOIN RawMaterials rm ON p.material_id = rm.material_id
                WHERE p.material_id = %s
                AND p.stock > 0
                ORDER BY p.stock ASC
            """
            
            cursor.execute(query, (material_id,))
            products = cursor.fetchall()
            
            results = []
            for product in products:
                # Calculate days until critical stock
                current_stock = int(product['stock'])
                threshold = int(product['low_stock_threshold'])
                
                # Estimate days based on average daily sales (simplified)
                days_until_critical = max(0, (current_stock - threshold) // 2)  # Assume 2 units/day avg
                
                # Determine priority
                if current_stock <= threshold:
                    priority = "CRITICAL"
                elif days_until_critical <= 3:
                    priority = "HIGH"
                elif days_until_critical <= 7:
                    priority = "MEDIUM"
                else:
                    priority = "LOW"
                
                results.append({
                    'sku': product['SKU'],
                    'product_name': product['name'],
                    'current_stock': current_stock,
                    'threshold': threshold,
                    'days_until_critical': days_until_critical,
                    'priority': priority,
                    'material_name': product['material_name'],
                    'price': float(product['price']),
                    'category': product['category']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting affected products: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def _calculate_risk_level(self, delay_percent: float) -> str:
        """Calculate risk level based on delay percentage"""
        if delay_percent >= 30:
            return "CRITICAL"
        elif delay_percent >= 20:
            return "HIGH"
        elif delay_percent >= 10:
            return "MEDIUM"
        else:
            return "LOW"

    def get_overall_climate_risk(self) -> Dict[str, Any]:
        """Calculate overall climate risk score"""
        try:
            status_data = self.get_current_climate_status()
            
            if not status_data:
                return {'risk_score': 0, 'risk_level': 'LOW', 'materials_at_risk': 0}
            
            total_risk = 0
            materials_at_risk = 0
            
            for material in status_data:
                delay = material['delay_percent']
                total_risk += delay
                
                if delay >= 10:  # Consider 10%+ delay as "at risk"
                    materials_at_risk += 1
            
            # Calculate average risk score (0-100)
            avg_risk = total_risk / len(status_data)
            
            # Determine overall risk level
            if avg_risk >= 30:
                overall_risk = "CRITICAL"
            elif avg_risk >= 20:
                overall_risk = "HIGH"
            elif avg_risk >= 10:
                overall_risk = "MEDIUM"
            else:
                overall_risk = "LOW"
            
            return {
                'risk_score': round(avg_risk, 1),
                'risk_level': overall_risk,
                'materials_at_risk': materials_at_risk,
                'total_materials': len(status_data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall climate risk: {e}")
            return {'risk_score': 0, 'risk_level': 'ERROR', 'materials_at_risk': 0}

    def get_climate_alerts(self) -> List[Dict[str, Any]]:
        """Get current climate alerts and warnings"""
        try:
            alerts = []
            forecast_data = self.get_climate_forecast(7)  # Next 7 days
            
            # Group by material and check for concerning patterns
            material_forecasts = {}
            for item in forecast_data:
                material = item['material_name']
                if material not in material_forecasts:
                    material_forecasts[material] = []
                material_forecasts[material].append(item)
            
            # Generate alerts based on forecast patterns
            for material, forecasts in material_forecasts.items():
                # Check for high risk periods
                high_risk_days = [f for f in forecasts if f['risk_level'] in ['CRITICAL', 'HIGH']]
                
                if high_risk_days:
                    earliest_risk = min(high_risk_days, key=lambda x: x['days_from_now'])
                    
                    alert = {
                        'material_name': material,
                        'alert_type': 'CLIMATE_RISK',
                        'severity': earliest_risk['risk_level'],
                        'days_until_impact': earliest_risk['days_from_now'],
                        'expected_condition': earliest_risk['expected_condition'],
                        'message': f"{material} {earliest_risk['risk_level'].lower()} risk in {earliest_risk['days_from_now']} days",
                        'affected_products_count': len(self.get_affected_products(earliest_risk['material_id']))
                    }
                    alerts.append(alert)
            
            return sorted(alerts, key=lambda x: x['days_until_impact'])
            
        except Exception as e:
            logger.error(f"Error getting climate alerts: {e}")
            return []

# Global instance for easy access
climate_manager = ClimateDataManager()

# Convenience functions for backward compatibility
def get_current_climate_status():
    """Get current climate status for all materials"""
    return climate_manager.get_current_climate_status()

def get_climate_forecast(days_ahead=7):
    """Get climate forecast"""
    return climate_manager.get_climate_forecast(days_ahead)

def get_affected_products(material_id):
    """Get products affected by material climate issues"""
    return climate_manager.get_affected_products(material_id)

def get_overall_climate_risk():
    """Get overall climate risk assessment"""
    return climate_manager.get_overall_climate_risk()

def get_climate_alerts():
    """Get current climate alerts"""
    return climate_manager.get_climate_alerts()
