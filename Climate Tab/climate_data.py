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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateDataManager:
    """Climate data access and management class with rule-based automation and performance optimization"""
    
    def __init__(self):
        self.material_mapping = {
            1: "Wheat",
            2: "Sugarcane", 
            3: "Cotton",
            4: "Rice"
        }
        
        # Performance optimization - caching
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes cache timeout
        self._last_refresh = {}
        
        # Rule-based thresholds for automation
        self.thresholds = {
            'high_risk_delay': 30.0,  # 30% delay threshold
            'medium_risk_delay': 15.0,  # 15% delay threshold
            'critical_production_drop': 25.0,  # 25% production drop
            'severe_weather_threshold': 20.0,  # Severe weather impact
            'price_volatility_threshold': 0.15  # 15% price change
        }
        
        # Load email configuration from credentials.json
        self.email_config = self._load_email_config()
        
        # Rule-based recommendations database
        self.recommendation_rules = {
            'high_delay_risk': {
                'condition': lambda data: data['delay_percent'] > self.thresholds['high_risk_delay'],
                'actions': [
                    'Consider sourcing from alternative suppliers',
                    'Increase inventory buffer by 25-30%',
                    'Lock prices with current suppliers',
                    'Review supplier contracts for climate clauses'
                ],
                'priority': 'High',
                'automation': True
            },
            'production_drop': {
                'condition': lambda data: abs(data['production_impact']) > self.thresholds['critical_production_drop'],
                'actions': [
                    'Immediate contact with suppliers for updated forecasts',
                    'Explore spot market opportunities',
                    'Consider forward purchasing at current prices',
                    'Alert sales team of potential stock shortages'
                ],
                'priority': 'Critical',
                'automation': True
            },
            'weather_pattern_change': {
                'condition': lambda data: data['category'] in ['Extreme Weather', 'Severe Drought', 'Flooding'],
                'actions': [
                    'Monitor affected regions closely',
                    'Prepare alternative sourcing strategy',
                    'Review insurance coverage',
                    'Communicate with logistics partners'
                ],
                'priority': 'High',
                'automation': False
            },
            'seasonal_optimization': {
                'condition': lambda data: data['delay_percent'] < 5.0 and data['risk_level'] == 'Low',
                'actions': [
                    'Optimize inventory levels downward',
                    'Negotiate better terms with suppliers',
                    'Consider bulk purchasing discounts',
                    'Review storage costs'
                ],
                'priority': 'Medium',
                'automation': False
            }
        }
        
    def _load_email_config(self):
        """Load email configuration from credentials.json"""
        try:
            # Get the credentials file path (go up one directory from Climate Tab)
            credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credentials.json')
            
            with open(credentials_path, 'r') as f:
                credentials = json.load(f)
            
            # Extract email and password from credentials.json
            sender_email = credentials.get('email', '')
            sender_password = credentials.get('password', '')
            
            # Get manager emails from users list as recipients
            recipient_emails = []
            users = credentials.get('users', [])
            for user in users:
                if user.get('role') in ['manager', 'store_admin', 'inventory_manager']:
                    email = user.get('email', '')
                    if email and email != '':
                        recipient_emails.append(email)
            
            # If no recipients found, use a default
            if not recipient_emails:
                recipient_emails = ['manager@storecore.com']
            
            # Check if credentials are properly configured
            if sender_email == "Fill-this-field" or sender_password == "Fill-this-field" or not sender_email or not sender_password:
                logger.warning("Email credentials not configured in credentials.json - email alerts will be logged only")
                return {
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'sender_email': sender_email,
                    'sender_password': sender_password,
                    'recipient_emails': recipient_emails,
                    'configured': False
                }
            
            logger.info("Email configuration loaded successfully from credentials.json")
            return {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': sender_email,
                'sender_password': sender_password,
                'recipient_emails': recipient_emails,
                'configured': True
            }
            
        except FileNotFoundError:
            logger.error("credentials.json file not found - using default email configuration")
            return {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'digiclimatehub@gmail.com',
                'sender_password': 'your_app_password',
                'recipient_emails': ['manager@storecore.com'],
                'configured': False
            }
        except json.JSONDecodeError:
            logger.error("Error parsing credentials.json - using default email configuration")
            return {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'digiclimatehub@gmail.com',
                'sender_password': 'your_app_password',
                'recipient_emails': ['manager@storecore.com'],
                'configured': False
            }
        except Exception as e:
            logger.error(f"Error loading email configuration: {e}")
            return {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'digiclimatehub@gmail.com',
                'sender_password': 'your_app_password',
                'recipient_emails': ['manager@storecore.com'],
                'configured': False
            }
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache or key not in self._last_refresh:
            return False
        
        cache_age = (datetime.now() - self._last_refresh[key]).total_seconds()
        return cache_age < self._cache_timeout
    
    def _get_cached_data(self, key: str):
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            return self._cache[key]
        return None
    
    def _set_cache_data(self, key: str, data):
        """Set data in cache"""
        self._cache[key] = data
        self._last_refresh[key] = datetime.now()
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._last_refresh.clear()
        logger.info("Climate data cache cleared")
        
    def get_connection(self):
        """Get database connection"""
        try:
            connection, cursor = get_db()
            return connection, cursor
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def get_current_climate_status(self) -> List[Dict[str, Any]]:
        """Get current climate status for all raw materials with caching"""
        # Check cache first
        cached_data = self._get_cached_data('current_climate_status')
        if cached_data is not None:
            logger.debug("Returning cached climate status data")
            return cached_data
            
        connection = None
        cursor = None
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
                    AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    ORDER BY timestamp DESC
                    LIMIT 1
                """
                
                cursor.execute(query, (material_id,))
                result = cursor.fetchone()
                
                # If no recent data found, get the most recent data but use current date for display
                if not result:
                    query_fallback = f"""
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
                    cursor.execute(query_fallback, (material_id,))
                    result = cursor.fetchone()
                
                if result:
                    # Calculate production impact
                    original = float(result['original_production'])
                    expected = float(result['expected_production'])
                    delay_percent = float(result['delay_percent'])
                    
                    # Determine risk level
                    risk_level = self._calculate_risk_level(delay_percent)
                    
                    # Use current date if data is not from today or within the last 7 days
                    data_age = abs((datetime.now() - result['timestamp']).days)
                    display_timestamp = datetime.now() if data_age > 7 else result['timestamp']
                    
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
                        'last_updated': display_timestamp
                    })
            
            # Cache the results
            self._set_cache_data('current_climate_status', results)
            logger.debug(f"Cached climate status data for {len(results)} materials")
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting current climate status: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_material_status(self, material_id: int) -> Optional[Dict[str, Any]]:
        """Get current climate status for a specific material"""
        connection = None
        cursor = None
        try:
            # Get all current status data
            all_status = self.get_current_climate_status()
            
            # Find the specific material
            for material_status in all_status:
                if material_status.get('material_id') == material_id:
                    return material_status
            
            # If not found in current status, get latest data directly
            connection, cursor = self.get_connection()
            
            material_name = self.material_mapping.get(material_id)
            if not material_name:
                return None
                
            # Get table name for the material
            table_map = {
                "Wheat": "WheatProduction",
                "Cotton": "CottonProduction", 
                "Rice": "RiceProduction",
                "Sugarcane": "SugarcaneProduction"
            }
            
            table = table_map.get(material_name)
            if not table:
                return None
            
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
                AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                ORDER BY timestamp DESC
                LIMIT 1
            """
            
            cursor.execute(query, (material_id,))
            row = cursor.fetchone()
            
            # If no recent data found, get the most recent data
            if not row:
                query_fallback = f"""
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
                cursor.execute(query_fallback, (material_id,))
                row = cursor.fetchone()
            
            if row:
                risk_level = self._calculate_risk_level(float(row['delay_percent']))
                
                # Use current date if data is not from today or within the last 7 days
                data_age = abs((datetime.now() - row['timestamp']).days)
                display_timestamp = datetime.now() if data_age > 7 else row['timestamp']
                
                return {
                    'material_id': row['material_id'],
                    'material_name': material_name,
                    'last_updated': display_timestamp,
                    'current_condition': row['expected_condition'],
                    'category': row['category'],
                    'delay_percent': float(row['delay_percent']),
                    'risk_level': risk_level,
                    'original_production': row['original_production'],
                    'expected_production': row['expected_production'],
                    'production_impact': float(row['expected_production']) - float(row['original_production'])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting material status for material_id {material_id}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_climate_forecast(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get climate forecast for next N days"""
        connection = None
        cursor = None
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
        connection = None
        cursor = None
        try:
            connection, cursor = self.get_connection()
            
            query = """
                SELECT 
                    p.SKU,
                    p.name,
                    p.price,
                    p.cost,
                    p.stock,
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
                    'category': 'General'  # Default category since column may not exist
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

    def get_predictive_alerts(self, time_horizon: str = 'week') -> List[Dict[str, Any]]:
        """Get predictive alerts based on upcoming climate data (week/month ahead)"""
        try:
            alerts = []
            
            # Set time horizon
            if time_horizon == 'week':
                days_ahead = 7
                horizon_label = "next week"
            elif time_horizon == 'month':
                days_ahead = 30
                horizon_label = "next month"
            else:
                days_ahead = 14
                horizon_label = "next 2 weeks"
            
            # Get forecast data for the specified period
            forecast_data = self.get_climate_forecast(days_ahead)
            
            # Group by material for analysis
            material_forecasts = {}
            for item in forecast_data:
                material = item['material_name']
                if material not in material_forecasts:
                    material_forecasts[material] = []
                material_forecasts[material].append(item)
            
            # Analyze each material for predictive concerns
            for material, forecasts in material_forecasts.items():
                material_id = forecasts[0]['material_id']
                
                # Sort by date to analyze trends
                forecasts = sorted(forecasts, key=lambda x: x['forecast_date'])
                
                # Check for various predictive scenarios
                alerts.extend(self._analyze_delay_patterns(material, material_id, forecasts, horizon_label))
                alerts.extend(self._analyze_production_drops(material, material_id, forecasts, horizon_label))
                alerts.extend(self._analyze_weather_extremes(material, material_id, forecasts, horizon_label))
                alerts.extend(self._analyze_supply_chain_risks(material, material_id, forecasts, horizon_label))
            
            # Sort by urgency and days until impact
            alerts = sorted(alerts, key=lambda x: (x['urgency_score'], x['days_until_impact']))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting predictive alerts: {e}")
            return []

    def _analyze_delay_patterns(self, material: str, material_id: int, forecasts: List[Dict], horizon: str) -> List[Dict]:
        """Analyze for upcoming delay patterns"""
        alerts = []
        
        try:
            # Look for consecutive high-delay periods
            high_delay_periods = []
            current_period = []
            
            for forecast in forecasts:
                if forecast['delay_percent'] > 20:  # 20% delay threshold
                    current_period.append(forecast)
                else:
                    if len(current_period) >= 2:  # 2+ consecutive days
                        high_delay_periods.append(current_period)
                    current_period = []
            
            # Check final period
            if len(current_period) >= 2:
                high_delay_periods.append(current_period)
            
            # Generate alerts for significant delay periods
            for period in high_delay_periods:
                start_day = period[0]['days_from_now']
                end_day = period[-1]['days_from_now']
                max_delay = max(f['delay_percent'] for f in period)
                avg_delay = sum(f['delay_percent'] for f in period) / len(period)
                
                severity = 'CRITICAL' if max_delay > 40 else 'HIGH' if max_delay > 25 else 'MEDIUM'
                urgency = 100 - start_day  # More urgent if happening sooner
                
                alert = {
                    'material_name': material,
                    'material_id': material_id,
                    'alert_type': 'PREDICTED_DELAYS',
                    'severity': severity,
                    'days_until_impact': start_day,
                    'duration_days': len(period),
                    'expected_delay': f"{avg_delay:.1f}%",
                    'peak_delay': f"{max_delay:.1f}%",
                    'urgency_score': urgency,
                    'message': f"{material} expected {avg_delay:.1f}% delays for {len(period)} days starting in {start_day} days ({horizon})",
                    'recommendation': f"Consider ordering {material} earlier or sourcing from alternative suppliers",
                    'horizon': horizon
                }
                alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error analyzing delay patterns for {material}: {e}")
        
        return alerts

    def _analyze_production_drops(self, material: str, material_id: int, forecasts: List[Dict], horizon: str) -> List[Dict]:
        """Analyze for upcoming production drops"""
        alerts = []
        
        try:
            for forecast in forecasts:
                # Calculate production impact if data is available
                if 'expected_production' in forecast and 'original_production' in forecast:
                    if forecast['expected_production'] and forecast['original_production']:
                        production_drop = ((forecast['original_production'] - forecast['expected_production']) 
                                         / forecast['original_production']) * 100
                        
                        if production_drop > 15:  # 15% production drop threshold
                            severity = 'CRITICAL' if production_drop > 30 else 'HIGH'
                            urgency = 100 - forecast['days_from_now']
                            
                            alert = {
                                'material_name': material,
                                'material_id': material_id,
                                'alert_type': 'PREDICTED_PRODUCTION_DROP',
                                'severity': severity,
                                'days_until_impact': forecast['days_from_now'],
                                'production_drop': f"{production_drop:.1f}%",
                                'urgency_score': urgency,
                                'message': f"{material} production expected to drop {production_drop:.1f}% in {forecast['days_from_now']} days",
                                'recommendation': f"Increase {material} inventory buffer by {int(production_drop * 1.5)}% before impact",
                                'horizon': horizon,
                                'expected_condition': forecast.get('expected_condition', 'Unknown')
                            }
                            alerts.append(alert)
                            
        except Exception as e:
            logger.error(f"Error analyzing production drops for {material}: {e}")
        
        return alerts

    def _analyze_weather_extremes(self, material: str, material_id: int, forecasts: List[Dict], horizon: str) -> List[Dict]:
        """Analyze for extreme weather conditions"""
        alerts = []
        
        try:
            extreme_conditions = ['severe_drought', 'flooding', 'extreme_heat', 'frost', 'storm']
            
            for forecast in forecasts:
                condition = forecast.get('expected_condition', '').lower()
                
                # Check if condition contains extreme weather keywords
                for extreme in extreme_conditions:
                    if extreme in condition or any(word in condition for word in ['severe', 'extreme', 'critical', 'emergency']):
                        urgency = 100 - forecast['days_from_now']
                        
                        alert = {
                            'material_name': material,
                            'material_id': material_id,
                            'alert_type': 'EXTREME_WEATHER_WARNING',
                            'severity': 'CRITICAL',
                            'days_until_impact': forecast['days_from_now'],
                            'urgency_score': urgency,
                            'weather_condition': forecast['expected_condition'],
                            'message': f"Extreme weather ({forecast['expected_condition']}) predicted for {material} in {forecast['days_from_now']} days",
                            'recommendation': f"Secure {material} inventory and consider emergency sourcing arrangements",
                            'horizon': horizon
                        }
                        alerts.append(alert)
                        break  # One alert per forecast day
                        
        except Exception as e:
            logger.error(f"Error analyzing weather extremes for {material}: {e}")
        
        return alerts

    def _analyze_supply_chain_risks(self, material: str, material_id: int, forecasts: List[Dict], horizon: str) -> List[Dict]:
        """Analyze for supply chain disruption risks"""
        alerts = []
        
        try:
            # Look for patterns that indicate supply chain risks
            risk_days = [f for f in forecasts if f['delay_percent'] > 15 or f['risk_level'] in ['HIGH', 'CRITICAL']]
            
            if len(risk_days) >= 3:  # Multiple risky days indicate supply chain concern
                avg_risk_delay = sum(f['delay_percent'] for f in risk_days) / len(risk_days)
                earliest_impact = min(f['days_from_now'] for f in risk_days)
                
                # Check if this affects multiple products
                affected_products = self.get_affected_products(material_id)
                affected_count = len(affected_products)
                
                if affected_count > 0:
                    urgency = (100 - earliest_impact) + (affected_count * 2)  # More products = higher urgency
                    
                    alert = {
                        'material_name': material,
                        'material_id': material_id,
                        'alert_type': 'SUPPLY_CHAIN_RISK',
                        'severity': 'HIGH' if affected_count > 3 else 'MEDIUM',
                        'days_until_impact': earliest_impact,
                        'affected_products_count': affected_count,
                        'risk_days_count': len(risk_days),
                        'avg_delay': f"{avg_risk_delay:.1f}%",
                        'urgency_score': min(urgency, 100),
                        'message': f"{material} supply chain at risk - {len(risk_days)} problematic days in {horizon}, affecting {affected_count} products",
                        'recommendation': f"Review {material} suppliers and consider diversifying sources for {affected_count} affected products",
                        'horizon': horizon
                    }
                    alerts.append(alert)
                    
        except Exception as e:
            logger.error(f"Error analyzing supply chain risks for {material}: {e}")
        
        return alerts

    def get_climate_alerts(self) -> List[Dict[str, Any]]:
        """Get comprehensive climate alerts combining current and predictive analysis"""
        try:
            all_alerts = []
            
            # Get immediate alerts (next 7 days)
            immediate_alerts = self.get_predictive_alerts('week')
            all_alerts.extend(immediate_alerts)
            
            # Get longer-term alerts (next month) for planning
            monthly_alerts = self.get_predictive_alerts('month')
            
            # Filter monthly alerts to avoid duplicates with weekly alerts
            for monthly_alert in monthly_alerts:
                # Only include monthly alerts that are more than 7 days away
                if monthly_alert['days_until_impact'] > 7:
                    monthly_alert['alert_type'] = f"LONG_TERM_{monthly_alert['alert_type']}"
                    all_alerts.append(monthly_alert)
            
            # Add any critical current conditions
            current_alerts = self._get_current_condition_alerts()
            all_alerts.extend(current_alerts)
            
            # Add stock depletion alerts
            stock_alerts = self.get_stock_depletion_alerts()
            all_alerts.extend(stock_alerts)
            
            # Sort by urgency (most urgent first)
            all_alerts = sorted(all_alerts, key=lambda x: x.get('urgency_score', 0), reverse=True)
            
            # Limit to top 20 alerts to avoid overwhelming the user
            return all_alerts[:20]
            
        except Exception as e:
            logger.error(f"Error getting comprehensive climate alerts: {e}")
            return []

    def _get_current_condition_alerts(self) -> List[Dict[str, Any]]:
        """Get alerts for current critical conditions"""
        alerts = []
        
        try:
            # Get today's data for all materials
            today = datetime.now().date()
            
            for material_id, material_name in self.material_mapping.items():
                current_conditions = self.get_material_status(material_id)
                
                if current_conditions:
                    risk_level = current_conditions.get('risk_level', 'LOW')
                    delay_percent = current_conditions.get('delay_percent', 0)
                    
                    if risk_level in ['CRITICAL', 'HIGH'] or delay_percent > 25:
                        alert = {
                            'material_name': material_name,
                            'material_id': material_id,
                            'alert_type': 'CURRENT_CRITICAL_CONDITION',
                            'severity': risk_level,
                            'days_until_impact': 0,
                            'urgency_score': 100,  # Current conditions are most urgent
                            'delay_percent': delay_percent,
                            'message': f"{material_name} currently experiencing {risk_level.lower()} conditions with {delay_percent:.1f}% delays",
                            'recommendation': f"Immediate action required for {material_name} supply chain",
                            'horizon': 'current'
                        }
                        alerts.append(alert)
                        
        except Exception as e:
            logger.error(f"Error getting current condition alerts: {e}")
        
        return alerts

    def get_stock_depletion_alerts(self) -> List[Dict[str, Any]]:
        """Generate alerts for materials that will run out based on current consumption rates"""
        alerts = []
        
        try:
            connection, cursor = self.get_connection()
            
            # Check each material's stock status
            for material_id, material_name in self.material_mapping.items():
                try:
                    # For demonstration, let's simulate stock levels and consumption rates
                    # In a real system, this would come from inventory management
                    simulated_stock_data = {
                        "Wheat": {"current_stock": 500, "daily_consumption": 25, "safety_stock": 100},
                        "Sugarcane": {"current_stock": 290, "daily_consumption": 15, "safety_stock": 50},  # Will run out in ~19 days
                        "Cotton": {"current_stock": 800, "daily_consumption": 20, "safety_stock": 150},
                        "Rice": {"current_stock": 420, "daily_consumption": 30, "safety_stock": 120}  # Will run out in ~14 days
                    }
                    
                    if material_name in simulated_stock_data:
                        stock_info = simulated_stock_data[material_name]
                        current_stock = stock_info["current_stock"]
                        daily_consumption = stock_info["daily_consumption"]
                        safety_stock = stock_info["safety_stock"]
                        
                        # Calculate days until stock runs out
                        days_until_empty = current_stock / daily_consumption if daily_consumption > 0 else 999
                        days_until_safety = (current_stock - safety_stock) / daily_consumption if daily_consumption > 0 else 999
                        
                        # Generate alerts based on stock levels
                        if days_until_empty <= 7:  # Critical - will run out in a week
                            alerts.append({
                                'material_name': material_name,
                                'material_id': material_id,
                                'alert_type': 'STOCK_DEPLETION_CRITICAL',
                                'severity': 'CRITICAL',
                                'days_until_impact': max(1, int(days_until_empty)),
                                'days_until_empty': int(days_until_empty),
                                'current_stock': current_stock,
                                'daily_consumption': daily_consumption,
                                'urgency_score': 100 - int(days_until_empty),
                                'message': f"{material_name} will run out in {int(days_until_empty)} days",
                                'recommendation': f"Immediate restocking required for {material_name}",
                                'stock_status': 'CRITICAL'
                            })
                        elif days_until_empty <= 21:  # High - will run out in three weeks
                            alerts.append({
                                'material_name': material_name,
                                'material_id': material_id,
                                'alert_type': 'STOCK_DEPLETION_HIGH',
                                'severity': 'HIGH',
                                'days_until_impact': int(days_until_empty),
                                'days_until_empty': int(days_until_empty),
                                'current_stock': current_stock,
                                'daily_consumption': daily_consumption,
                                'urgency_score': 85 - int(days_until_empty * 2),
                                'message': f"{material_name} will run out in {int(days_until_empty)} days",
                                'recommendation': f"Order {material_name} within the next week",
                                'stock_status': 'LOW'
                            })
                        elif days_until_safety <= 10:  # Medium - approaching safety stock
                            alerts.append({
                                'material_name': material_name,
                                'material_id': material_id,
                                'alert_type': 'STOCK_SAFETY_WARNING',
                                'severity': 'MEDIUM',
                                'days_until_impact': max(1, int(days_until_safety)),
                                'days_until_safety': int(days_until_safety),
                                'current_stock': current_stock,
                                'safety_stock': safety_stock,
                                'daily_consumption': daily_consumption,
                                'urgency_score': 70 - int(days_until_safety),
                                'message': f"{material_name} will reach safety stock levels in {int(days_until_safety)} days",
                                'recommendation': f"Plan to reorder {material_name} soon",
                                'stock_status': 'APPROACHING_SAFETY'
                            })
                        
                except Exception as e:
                    logger.error(f"Error checking stock for {material_name}: {e}")
                    continue
            
            cursor.close()
            connection.close()
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting stock depletion alerts: {e}")
            return []

    def get_smart_recommendations(self, material_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get rule-based smart recommendations for materials"""
        try:
            climate_status = self.get_current_climate_status()
            recommendations = []
            
            for status in climate_status:
                if material_id and status['material_id'] != material_id:
                    continue
                    
                # Apply rule-based analysis
                material_recommendations = []
                triggered_rules = []
                
                for rule_name, rule in self.recommendation_rules.items():
                    if rule['condition'](status):
                        material_recommendations.extend(rule['actions'])
                        triggered_rules.append({
                            'rule_name': rule_name,
                            'priority': rule['priority'],
                            'automation': rule['automation']
                        })
                
                if material_recommendations:
                    recommendations.append({
                        'material_id': status['material_id'],
                        'material_name': status['material_name'],
                        'current_risk_level': status['risk_level'],
                        'delay_percent': status['delay_percent'],
                        'production_impact': status['production_impact'],
                        'recommendations': material_recommendations,
                        'triggered_rules': triggered_rules,
                        'urgency_score': self._calculate_urgency_score(status),
                        'last_updated': datetime.now()
                    })
            
            # Sort by urgency score (highest first)
            recommendations.sort(key=lambda x: x['urgency_score'], reverse=True)
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting smart recommendations: {e}")
            return []

    def _calculate_urgency_score(self, status: Dict[str, Any]) -> float:
        """Calculate urgency score based on rule-based criteria"""
        score = 0.0
        
        # Base score from delay percentage
        score += status['delay_percent'] * 0.5
        
        # Add points for production impact
        if abs(status['production_impact']) > self.thresholds['critical_production_drop']:
            score += 50.0
        elif abs(status['production_impact']) > 10.0:
            score += 25.0
            
        # Add points for severe weather categories
        severe_categories = ['Extreme Weather', 'Severe Drought', 'Flooding', 'Hurricane']
        if status.get('category') in severe_categories:
            score += 30.0
            
        # Risk level multiplier
        risk_multipliers = {'Critical': 2.0, 'High': 1.5, 'Medium': 1.0, 'Low': 0.5}
        score *= risk_multipliers.get(status['risk_level'], 1.0)
        
        return min(score, 100.0)  # Cap at 100

    def run_automated_monitoring(self) -> Dict[str, Any]:
        """Run automated monitoring and trigger email alerts"""
        try:
            results = {
                'monitoring_time': datetime.now(),
                'alerts_sent': 0,
                'actions_triggered': 0,
                'recommendations_generated': 0,
                'processed_materials': []
            }
            
            climate_status = self.get_current_climate_status()
            
            for status in climate_status:
                material_result = {
                    'material_id': status['material_id'],
                    'material_name': status['material_name'],
                    'alerts': [],
                    'automated_actions': [],
                    'recommendations': []
                }
                
                # Check for email alert conditions
                if status['delay_percent'] > self.thresholds['high_risk_delay']:
                    subject = f"CRITICAL: High Risk Alert for {status['material_name']}"
                    message = f"""
Critical climate risk detected for {status['material_name']}:

- Delay Percentage: {status['delay_percent']:.1f}%
- Production Impact: {status['production_impact']:.1f} units
- Risk Level: {status['risk_level']}
- Weather Condition: {status['current_condition']}

Immediate action recommended.
"""
                    self.send_email_alert(subject, message)
                    material_result['alerts'].append('High risk email sent')
                    results['alerts_sent'] += 1
                
                # Apply automated recommendations
                triggered_rules = self.apply_recommendations(status['material_id'], status)
                if triggered_rules:
                    material_result['automated_actions'] = triggered_rules
                    results['actions_triggered'] += len(triggered_rules)
                
                # Generate recommendations
                recommendations = self.get_smart_recommendations(status['material_id'])
                if recommendations:
                    material_result['recommendations'] = len(recommendations)
                    results['recommendations_generated'] += len(recommendations)
                
                results['processed_materials'].append(material_result)
            
            logger.info(f"Automated monitoring completed: {results['alerts_sent']} alerts, {results['actions_triggered']} actions")
            return results
            
        except Exception as e:
            logger.error(f"Error in automated monitoring: {e}")
            return {'error': str(e), 'monitoring_time': datetime.now()}

    def get_supplier_integration_suggestions(self) -> List[Dict[str, Any]]:
        """Get rule-based supplier integration suggestions"""
        try:
            climate_status = self.get_current_climate_status()
            suggestions = []
            
            for status in climate_status:
                material_suggestions = []
                
                # High-risk materials need diversification
                if status['delay_percent'] > self.thresholds['medium_risk_delay']:
                    material_suggestions.extend([
                        {
                            'type': 'diversification',
                            'action': 'Add backup suppliers from low-risk regions',
                            'priority': 'High',
                            'timeline': '2-4 weeks'
                        },
                        {
                            'type': 'contract_terms',
                            'action': 'Negotiate climate risk clauses in contracts',
                            'priority': 'Medium',
                            'timeline': '1-2 weeks'
                        }
                    ])
                
                # Weather-affected materials need monitoring
                if status.get('category') in ['Extreme Weather', 'Severe Drought']:
                    material_suggestions.append({
                        'type': 'monitoring',
                        'action': 'Implement real-time supplier monitoring system',
                        'priority': 'High',
                        'timeline': '3-5 days'
                    })
                
                # Low-risk materials can optimize costs
                if status['risk_level'] == 'Low':
                    material_suggestions.append({
                        'type': 'optimization',
                        'action': 'Consolidate suppliers for better pricing',
                        'priority': 'Low',
                        'timeline': '4-6 weeks'
                    })
                
                if material_suggestions:
                    suggestions.append({
                        'material_id': status['material_id'],
                        'material_name': status['material_name'],
                        'current_risk': status['risk_level'],
                        'suggestions': material_suggestions
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting supplier integration suggestions: {e}")
            return []

    def send_email_alert(self, subject: str, message: str):
        """Send email alert to stakeholders using credentials from credentials.json"""
        try:
            # Check if email is properly configured
            if not self.email_config.get('configured', False):
                logger.info(f"EMAIL ALERT (credentials not configured): {subject}")
                logger.info(f"MESSAGE: {message}")
                logger.info(f"Would send to: {', '.join(self.email_config['recipient_emails'])}")
                logger.info("To enable email alerts, please configure 'email' and 'password' fields in credentials.json")
                return
            
            # Send actual email if credentials are configured
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ", ".join(self.email_config['recipient_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(msg['From'], self.email_config['sender_password'])
                server.send_message(msg)
            
            logger.info(f"Email alert sent successfully: {subject}")
            logger.info(f"Sent to: {', '.join(self.email_config['recipient_emails'])}")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            # Log the alert content even if email fails
            logger.info(f"EMAIL ALERT (failed to send): {subject}")
            logger.info(f"MESSAGE: {message}")

    def apply_recommendations(self, material_id: int, risk_data: Dict[str, Any]):
        """Apply rule-based recommendations for a specific material"""
        try:
            rules_to_apply = []
            
            # Check each rule for the material's risk data
            for rule_name, rule in self.recommendation_rules.items():
                if rule['condition'](risk_data):
                    rules_to_apply.append(rule_name)
                    
                    # Execute automation actions if enabled
                    if rule['automation']:
                        for action in rule['actions']:
                            self._execute_action(action, material_id)
            
            return rules_to_apply
            
        except Exception as e:
            logger.error(f"Error applying recommendations: {e}")
            return []

    def _execute_action(self, action: str, material_id: int):
        """Execute a specific action for a recommendation"""
        try:
            if action == 'Consider sourcing from alternative suppliers':
                # Example: Add logic to find and suggest alternative suppliers
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Increase inventory buffer by 25-30%':
                # Example: Add logic to increase inventory buffer
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Lock prices with current suppliers':
                # Example: Add logic to lock prices
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Review supplier contracts for climate clauses':
                # Example: Add logic to review contracts
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Immediate contact with suppliers for updated forecasts':
                # Example: Add logic to contact suppliers
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Explore spot market opportunities':
                # Example: Add logic to explore spot market
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Consider forward purchasing at current prices':
                # Example: Add logic to forward purchase
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Alert sales team of potential stock shortages':
                # Example: Add logic to alert sales team
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Monitor affected regions closely':
                # Example: Add logic to monitor regions
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Prepare alternative sourcing strategy':
                # Example: Add logic to prepare sourcing strategy
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Review insurance coverage':
                # Example: Add logic to review insurance
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Communicate with logistics partners':
                # Example: Add logic to communicate with logistics
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Optimize inventory levels downward':
                # Example: Add logic to optimize inventory
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Negotiate better terms with suppliers':
                # Example: Add logic to negotiate terms
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Consider bulk purchasing discounts':
                # Example: Add logic to consider bulk discounts
                logger.info(f"Action: {action} for material_id: {material_id}")
            elif action == 'Review storage costs':
                # Example: Add logic to review storage costs
                logger.info(f"Action: {action} for material_id: {material_id}")
        except Exception as e:
            logger.error(f"Error executing action '{action}': {e}")
    
    def _load_email_config(self) -> Dict[str, Any]:
        """Load email configuration from credentials.json"""
        try:
            # Get the path to credentials.json (one directory up from Climate Tab)
            credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
            
            with open(credentials_path, 'r') as f:
                credentials = json.load(f)
            
            # Extract email configuration
            sender_email = credentials.get('email', '')
            sender_password = credentials.get('password', '')
            
            # Get recipient emails from user emails
            recipient_emails = []
            for user in credentials.get('users', []):
                if user.get('email') and user['email'] != 'Fill-this-field':
                    recipient_emails.append(user['email'])
            
            # Default recipients if none found
            if not recipient_emails:
                recipient_emails = ['manager@storecore.com']
            
            # Validate email configuration
            if sender_email in ['', 'Fill-this-field'] or sender_password in ['', 'Fill-this-field']:
                logger.warning("Email credentials not configured in credentials.json - email alerts will be disabled")
                return {
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'sender_email': '',
                    'sender_password': '',
                    'recipient_emails': recipient_emails,
                    'enabled': False
                }
            
            return {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': sender_email,
                'sender_password': sender_password,
                'recipient_emails': recipient_emails,
                'enabled': True
            }
            
        except FileNotFoundError:
            logger.error("credentials.json file not found - email alerts will be disabled")
            return {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',
                'recipient_emails': ['manager@storecore.com'],
                'enabled': False
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing credentials.json: {e} - email alerts will be disabled")
            return {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',
                'recipient_emails': ['manager@storecore.com'],
                'enabled': False
            }
        except Exception as e:
            logger.error(f"Error loading email configuration: {e} - email alerts will be disabled")
            return {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',
                'recipient_emails': ['manager@storecore.com'],
                'enabled': False
            }
        
    def get_stock_depletion_alerts(self) -> List[Dict[str, Any]]:
        """Generate alerts for materials that will run out based on current consumption rates"""
        alerts = []
        
        try:
            connection, cursor = self.get_connection()
            
            # Check each material's stock status
            for material_id, material_name in self.material_mapping.items():
                try:
                    # Get current stock level
                    cursor.execute("SELECT name FROM RawMaterials WHERE material_id = %s", (material_id,))
                    result = cursor.fetchone()
                    
                    if not result:
                        continue
                    
                    # For demonstration, let's simulate stock levels and consumption rates
                    # In a real system, this would come from inventory management
                    simulated_stock_data = {
                        "Wheat": {"current_stock": 500, "daily_consumption": 25, "safety_stock": 100},
                        "Sugarcane": {"current_stock": 300, "daily_consumption": 15, "safety_stock": 50},
                        "Cotton": {"current_stock": 800, "daily_consumption": 20, "safety_stock": 150},
                        "Rice": {"current_stock": 600, "daily_consumption": 30, "safety_stock": 120}
                    }
                    
                    if material_name in simulated_stock_data:
                        stock_info = simulated_stock_data[material_name]
                        current_stock = stock_info["current_stock"]
                        daily_consumption = stock_info["daily_consumption"]
                        safety_stock = stock_info["safety_stock"]
                        
                        # Calculate days until stock runs out
                        days_until_empty = current_stock / daily_consumption if daily_consumption > 0 else 999
                        days_until_safety = (current_stock - safety_stock) / daily_consumption if daily_consumption > 0 else 999
                        
                        # Generate alerts based on stock levels
                        if days_until_empty <= 7:  # Critical - will run out in a week
                            alerts.append({
                                'material_name': material_name,
                                'material_id': material_id,
                                'alert_type': 'STOCK_DEPLETION_CRITICAL',
                                'severity': 'CRITICAL',
                                'days_until_impact': max(1, int(days_until_empty)),
                                'days_until_empty': int(days_until_empty),
                                'current_stock': current_stock,
                                'daily_consumption': daily_consumption,
                                'urgency_score': 100 - int(days_until_empty),
                                'message': f"{material_name} will run out in {int(days_until_empty)} days",
                                'recommendation': f"Immediate restocking required for {material_name}",
                                'stock_status': 'CRITICAL'
                            })
                        elif days_until_empty <= 14:  # High - will run out in two weeks
                            alerts.append({
                                'material_name': material_name,
                                'material_id': material_id,
                                'alert_type': 'STOCK_DEPLETION_HIGH',
                                'severity': 'HIGH',
                                'days_until_impact': int(days_until_empty),
                                'days_until_empty': int(days_until_empty),
                                'current_stock': current_stock,
                                'daily_consumption': daily_consumption,
                                'urgency_score': 90 - int(days_until_empty),
                                'message': f"{material_name} will run out in {int(days_until_empty)} days",
                                'recommendation': f"Order {material_name} within the next few days",
                                'stock_status': 'LOW'
                            })
                        elif days_until_safety <= 7:  # Medium - approaching safety stock
                            alerts.append({
                                'material_name': material_name,
                                'material_id': material_id,
                                'alert_type': 'STOCK_SAFETY_WARNING',
                                'severity': 'MEDIUM',
                                'days_until_impact': max(1, int(days_until_safety)),
                                'days_until_safety': int(days_until_safety),
                                'current_stock': current_stock,
                                'safety_stock': safety_stock,
                                'daily_consumption': daily_consumption,
                                'urgency_score': 80 - int(days_until_safety),
                                'message': f"{material_name} will reach safety stock levels in {int(days_until_safety)} days",
                                'recommendation': f"Plan to reorder {material_name} soon",
                                'stock_status': 'APPROACHING_SAFETY'
                            })
                        
                except Exception as e:
                    logger.error(f"Error checking stock for {material_name}: {e}")
                    continue
            
            cursor.close()
            connection.close()
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting stock depletion alerts: {e}")
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

# New Phase 5 convenience functions for rule-based automation
def get_smart_recommendations(material_id=None):
    """Get rule-based smart recommendations"""
    return climate_manager.get_smart_recommendations(material_id)

def run_automated_monitoring():
    """Run automated monitoring and email alerts"""
    return climate_manager.run_automated_monitoring()

def get_supplier_integration_suggestions():
    """Get supplier integration suggestions"""
    return climate_manager.get_supplier_integration_suggestions()

def send_email_alert(subject, message):
    """Send email alert"""
    return climate_manager.send_email_alert(subject, message)
