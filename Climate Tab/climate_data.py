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
    """Climate data access and management class with rule-based automation"""
    
    def __init__(self):
        self.material_mapping = {
            1: "Wheat",
            2: "Sugarcane", 
            3: "Cotton",
            4: "Rice"
        }
        
        # Rule-based thresholds for automation
        self.thresholds = {
            'high_risk_delay': 30.0,  # 30% delay threshold
            'medium_risk_delay': 15.0,  # 15% delay threshold
            'critical_production_drop': 25.0,  # 25% production drop
            'severe_weather_threshold': 20.0,  # Severe weather impact
            'price_volatility_threshold': 0.15  # 15% price change
        }
        
        # Email configuration
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'digiclimatehub@gmail.com',
            'sender_password': 'your_app_password',  # Use app password for Gmail
            'recipient_emails': ['manager@storecore.com', 'procurement@storecore.com']
        }
        
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
        """Send email alert to stakeholders"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ", ".join(self.email_config['recipient_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(msg['From'], self.email_config['sender_password'])
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {subject}")
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")

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
