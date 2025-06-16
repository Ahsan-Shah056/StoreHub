"""
Enhanced Dashboard Backend Functions for Storecore POS & Inventory System
Provides comprehensive business intelligence and analytics capabilities
"""

import mysql.connector
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardAnalytics:
    """Main class for dashboard analytics and business intelligence functions"""
    
    def __init__(self):
        self.connection = None
        
    def get_connection(self):
        """Get database connection"""
        if not self.connection or not self.connection.is_connected():
            self.connection, _ = get_db()
        return self.connection
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    # Core Dashboard Functions
    
    def get_sales_summary(self, start_date: str, end_date: str, employee_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get comprehensive sales summary with profit calculations
        Returns total sales, orders, profit, and comparison metrics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Base query for sales summary
            base_query = """
                SELECT 
                    COUNT(DISTINCT s.sale_id) as total_orders,
                    SUM(s.total) as total_sales,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as total_profit,
                    AVG(s.total) as avg_order_value,
                    SUM(si.quantity) as total_items_sold
                FROM Sales s
                JOIN SaleItems si ON s.sale_id = si.sale_id
                LEFT JOIN Products p ON si.SKU = p.SKU
                WHERE s.sale_datetime BETWEEN %s AND %s
            """
            
            params = [start_date, end_date]
            if employee_id:
                base_query += " AND s.employee_id = %s"
                params.append(employee_id)
            
            cursor.execute(base_query, params)
            current_period = cursor.fetchone()
            
            # Calculate previous period for comparison
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            period_days = (end_dt - start_dt).days + 1
            
            prev_start = (start_dt - timedelta(days=period_days)).strftime('%Y-%m-%d')
            prev_end = (start_dt - timedelta(days=1)).strftime('%Y-%m-%d')
            
            prev_params = [prev_start, prev_end]
            if employee_id:
                prev_params.append(employee_id)
                
            cursor.execute(base_query, prev_params)
            previous_period = cursor.fetchone()
            
            # Calculate percentage changes
            def calc_percentage_change(current, previous):
                if not previous or previous == 0:
                    return 0
                return ((current - previous) / previous) * 100
            
            result = {
                'total_sales': current_period['total_sales'] or 0,
                'total_orders': current_period['total_orders'] or 0,
                'total_profit': current_period['total_profit'] or 0,
                'avg_order_value': current_period['avg_order_value'] or 0,
                'total_items_sold': current_period['total_items_sold'] or 0,
                'profit_margin': 0,
                'sales_change': calc_percentage_change(
                    current_period['total_sales'] or 0, 
                    previous_period['total_sales'] or 0
                ),
                'orders_change': calc_percentage_change(
                    current_period['total_orders'] or 0, 
                    previous_period['total_orders'] or 0
                ),
                'profit_change': calc_percentage_change(
                    current_period['total_profit'] or 0, 
                    previous_period['total_profit'] or 0
                )
            }
            
            # Calculate profit margin
            if result['total_sales'] > 0:
                result['profit_margin'] = (result['total_profit'] / result['total_sales']) * 100
                
            return result
            
        except Exception as e:
            logger.error(f"Error in get_sales_summary: {e}")
            return {
                'total_sales': 0, 'total_orders': 0, 'total_profit': 0,
                'avg_order_value': 0, 'total_items_sold': 0, 'profit_margin': 0,
                'sales_change': 0, 'orders_change': 0, 'profit_change': 0
            }
        finally:
            if cursor:
                cursor.close()

    def get_top_products(self, start_date: str, end_date: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing products with profit analysis"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    p.SKU,
                    p.name,
                    SUM(si.quantity) as units_sold,
                    SUM(si.quantity * si.price) as revenue,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as profit,
                    CASE 
                        WHEN SUM(si.quantity * si.price) > 0 
                        THEN (SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) / SUM(si.quantity * si.price)) * 100 
                        ELSE 0 
                    END as profit_margin,
                    AVG(si.price) as avg_selling_price,
                    p.cost,
                    p.stock as current_stock
                FROM Products p
                JOIN SaleItems si ON p.SKU = si.SKU
                JOIN Sales s ON si.sale_id = s.sale_id
                WHERE s.sale_datetime BETWEEN %s AND %s
                GROUP BY p.SKU, p.name, p.cost, p.stock
                ORDER BY units_sold DESC
                LIMIT %s
            """
            
            cursor.execute(query, (start_date, end_date, limit))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_top_products: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_employee_sales(self, employee_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get individual employee performance with profit metrics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    e.name as employee_name,
                    COUNT(DISTINCT s.sale_id) as total_sales,
                    SUM(s.total) as total_revenue,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as total_profit,
                    AVG(s.total) as avg_sale_value,
                    SUM(si.quantity) as items_sold,
                    CASE 
                        WHEN SUM(s.total) > 0 
                        THEN (SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) / SUM(s.total)) * 100 
                        ELSE 0 
                    END as profit_margin
                FROM Employees e
                JOIN Sales s ON e.employee_id = s.employee_id
                JOIN SaleItems si ON s.sale_id = si.sale_id
                LEFT JOIN Products p ON si.SKU = p.SKU
                WHERE e.employee_id = %s AND s.sale_datetime BETWEEN %s AND %s
                GROUP BY e.employee_id, e.name
            """
            
            cursor.execute(query, (employee_id, start_date, end_date))
            result = cursor.fetchone()
            
            if not result:
                # Get employee name even if no sales
                cursor.execute("SELECT name FROM Employees WHERE employee_id = %s", (employee_id,))
                emp = cursor.fetchone()
                return {
                    'employee_name': emp['name'] if emp else 'Unknown',
                    'total_sales': 0, 'total_revenue': 0, 'total_profit': 0,
                    'avg_sale_value': 0, 'items_sold': 0, 'profit_margin': 0
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in get_employee_sales: {e}")
            return {
                'employee_name': 'Unknown', 'total_sales': 0, 'total_revenue': 0,
                'total_profit': 0, 'avg_sale_value': 0, 'items_sold': 0, 'profit_margin': 0
            }
        finally:
            if cursor:
                cursor.close()

    def get_daily_sales_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get daily sales data for chart generation"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    DATE(s.sale_datetime) as sale_date,
                    SUM(s.total) as daily_revenue,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as daily_profit,
                    COUNT(DISTINCT s.sale_id) as daily_orders,
                    SUM(si.quantity) as daily_items
                FROM Sales s
                JOIN SaleItems si ON s.sale_id = si.sale_id
                LEFT JOIN Products p ON si.SKU = p.SKU
                WHERE s.sale_datetime BETWEEN %s AND %s
                GROUP BY DATE(s.sale_datetime)
                ORDER BY sale_date
            """
            
            cursor.execute(query, (start_date, end_date))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_daily_sales_data: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    # Advanced Analytics Functions
    
    def calculate_profit_margins(self) -> List[Dict[str, Any]]:
        """Calculate profit margins for all products"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    SKU,
                    name,
                    price,
                    cost,
                    CASE 
                        WHEN price > 0 AND cost IS NOT NULL 
                        THEN ((price - cost) / price) * 100 
                        ELSE 0 
                    END as profit_margin,
                    (price - COALESCE(cost, 0)) as profit_per_unit,
                    stock,
                    (stock * COALESCE(cost, 0)) as inventory_cost_value,
                    (stock * price) as inventory_retail_value
                FROM Products
                ORDER BY profit_margin DESC
            """
            
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in calculate_profit_margins: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_inventory_value(self) -> Dict[str, float]:
        """Calculate total inventory value using cost and retail prices"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    SUM(stock * COALESCE(cost, 0)) as total_cost_value,
                    SUM(stock * price) as total_retail_value,
                    COUNT(*) as total_products,
                    SUM(stock) as total_units
                FROM Products
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            return {
                'total_cost_value': result['total_cost_value'] or 0,
                'total_retail_value': result['total_retail_value'] or 0,
                'potential_profit': (result['total_retail_value'] or 0) - (result['total_cost_value'] or 0),
                'total_products': result['total_products'] or 0,
                'total_units': result['total_units'] or 0
            }
            
        except Exception as e:
            logger.error(f"Error in get_inventory_value: {e}")
            return {
                'total_cost_value': 0, 'total_retail_value': 0,
                'potential_profit': 0, 'total_products': 0, 'total_units': 0
            }
        finally:
            if cursor:
                cursor.close()

    def get_supplier_performance(self) -> List[Dict[str, Any]]:
        """Get comprehensive supplier performance metrics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.supplier_id,
                    s.name as supplier_name,
                    COUNT(DISTINCT p.purchase_id) as total_orders,
                    COUNT(DISTINCT CASE WHEN p.delivery_status = 'received' THEN p.purchase_id END) as delivered_orders,
                    CASE 
                        WHEN COUNT(DISTINCT p.purchase_id) > 0 
                        THEN (COUNT(DISTINCT CASE WHEN p.delivery_status = 'received' THEN p.purchase_id END) / COUNT(DISTINCT p.purchase_id)) * 100 
                        ELSE 0 
                    END as delivery_success_rate,
                    AVG(p.shipping_cost) as avg_shipping_cost,
                    SUM(pi.quantity * pi.unit_cost) as total_purchase_value,
                    AVG(pi.unit_cost) as avg_unit_cost,
                    COUNT(DISTINCT pi.SKU) as products_supplied,
                    MAX(p.purchase_datetime) as last_order_date
                FROM Suppliers s
                LEFT JOIN Purchases p ON s.supplier_id = p.supplier_id
                LEFT JOIN PurchaseItems pi ON p.purchase_id = pi.purchase_id
                GROUP BY s.supplier_id, s.name
                ORDER BY delivery_success_rate DESC, total_purchase_value DESC
            """
            
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_supplier_performance: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def calculate_purchase_roi(self, supplier_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Calculate ROI on purchase decisions and bulk buying benefits"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    pi.SKU,
                    prod.name as product_name,
                    s.name as supplier_name,
                    SUM(pi.quantity) as total_purchased,
                    AVG(pi.unit_cost) as avg_purchase_cost,
                    prod.price as current_selling_price,
                    CASE 
                        WHEN AVG(pi.unit_cost) > 0 
                        THEN ((prod.price - AVG(pi.unit_cost)) / AVG(pi.unit_cost)) * 100 
                        ELSE 0 
                    END as purchase_roi,
                    SUM(pi.quantity * pi.unit_cost) as total_investment,
                    SUM(pi.quantity * prod.price) as potential_revenue,
                    SUM(pi.quantity * (prod.price - pi.unit_cost)) as potential_profit
                FROM PurchaseItems pi
                JOIN Purchases p ON pi.purchase_id = p.purchase_id
                JOIN Suppliers s ON p.supplier_id = s.supplier_id
                JOIN Products prod ON pi.SKU = prod.SKU
            """
            
            params = []
            if supplier_id:
                query += " WHERE s.supplier_id = %s"
                params.append(supplier_id)
            
            query += """
                GROUP BY pi.SKU, prod.name, s.name, prod.price
                ORDER BY purchase_roi DESC
            """
            
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in calculate_purchase_roi: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def track_cost_trends(self, supplier_id: Optional[int] = None, product_sku: Optional[str] = None) -> List[Dict[str, Any]]:
        """Track how supplier costs change over time"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    DATE(p.purchase_datetime) as purchase_date,
                    pi.SKU,
                    prod.name as product_name,
                    s.name as supplier_name,
                    pi.unit_cost,
                    pi.quantity,
                    LAG(pi.unit_cost) OVER (PARTITION BY pi.SKU, s.supplier_id ORDER BY p.purchase_datetime) as previous_cost,
                    CASE 
                        WHEN LAG(pi.unit_cost) OVER (PARTITION BY pi.SKU, s.supplier_id ORDER BY p.purchase_datetime) IS NOT NULL
                        THEN ((pi.unit_cost - LAG(pi.unit_cost) OVER (PARTITION BY pi.SKU, s.supplier_id ORDER BY p.purchase_datetime)) / 
                              LAG(pi.unit_cost) OVER (PARTITION BY pi.SKU, s.supplier_id ORDER BY p.purchase_datetime)) * 100
                        ELSE 0
                    END as cost_change_percent
                FROM PurchaseItems pi
                JOIN Purchases p ON pi.purchase_id = p.purchase_id
                JOIN Suppliers s ON p.supplier_id = s.supplier_id
                JOIN Products prod ON pi.SKU = prod.SKU
                WHERE 1=1
            """
            
            params = []
            if supplier_id:
                query += " AND s.supplier_id = %s"
                params.append(supplier_id)
            if product_sku:
                query += " AND pi.SKU = %s"
                params.append(product_sku)
            
            query += " ORDER BY p.purchase_datetime DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in track_cost_trends: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_category_analytics(self) -> List[Dict[str, Any]]:
        """Get revenue, profit, and performance by product category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    c.name as category_name,
                    COUNT(DISTINCT p.SKU) as products_count,
                    SUM(p.stock) as total_stock,
                    SUM(p.stock * COALESCE(p.cost, 0)) as inventory_cost_value,
                    SUM(p.stock * p.price) as inventory_retail_value,
                    COALESCE(sales_data.total_revenue, 0) as total_revenue,
                    COALESCE(sales_data.total_profit, 0) as total_profit,
                    COALESCE(sales_data.units_sold, 0) as units_sold,
                    CASE 
                        WHEN COALESCE(sales_data.total_revenue, 0) > 0 
                        THEN (COALESCE(sales_data.total_profit, 0) / sales_data.total_revenue) * 100 
                        ELSE 0 
                    END as profit_margin
                FROM Categories c
                LEFT JOIN Products p ON c.category_id = p.category_id
                LEFT JOIN (
                    SELECT 
                        p.category_id,
                        SUM(si.quantity * si.price) as total_revenue,
                        SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as total_profit,
                        SUM(si.quantity) as units_sold
                    FROM Products p
                    JOIN SaleItems si ON p.SKU = si.SKU
                    GROUP BY p.category_id
                ) sales_data ON c.category_id = sales_data.category_id
                GROUP BY c.category_id, c.name, sales_data.total_revenue, sales_data.total_profit, sales_data.units_sold
                ORDER BY total_revenue DESC
            """
            
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_category_analytics: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_low_stock_analytics(self) -> List[Dict[str, Any]]:
        """Get low stock items with cost implications"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    p.SKU,
                    p.name,
                    p.stock,
                    p.low_stock_threshold,
                    (p.low_stock_threshold - p.stock) as units_below_threshold,
                    p.price,
                    p.cost,
                    (p.price - COALESCE(p.cost, 0)) as profit_per_unit,
                    ((p.low_stock_threshold - p.stock) * COALESCE(p.cost, 0)) as reorder_cost,
                    ((p.low_stock_threshold - p.stock) * p.price) as potential_revenue,
                    s.name as supplier_name,
                    c.name as category_name
                FROM Products p
                LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
                LEFT JOIN Categories c ON p.category_id = c.category_id
                WHERE p.stock <= p.low_stock_threshold
                ORDER BY (p.low_stock_threshold - p.stock) DESC, reorder_cost DESC
            """
            
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_low_stock_analytics: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    # Utility Functions for Dashboard
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions with profit information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.sale_id,
                    s.sale_datetime,
                    s.total as sale_total,
                    e.name as employee_name,
                    c.name as customer_name,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as transaction_profit,
                    CASE 
                        WHEN s.total > 0 
                        THEN (SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) / s.total) * 100 
                        ELSE 0 
                    END as profit_margin
                FROM Sales s
                JOIN Employees e ON s.employee_id = e.employee_id
                LEFT JOIN Customers c ON s.customer_id = c.customer_id
                JOIN SaleItems si ON s.sale_id = si.sale_id
                LEFT JOIN Products p ON si.SKU = p.SKU
                GROUP BY s.sale_id, s.sale_datetime, s.total, e.name, c.name
                ORDER BY s.sale_datetime DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_recent_activities: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def update_product_costs_from_purchases(self):
        """Update product costs based on latest purchase data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Update products with average cost from recent purchases
            update_query = """
                UPDATE Products p
                SET cost = (
                    SELECT AVG(pi.unit_cost)
                    FROM PurchaseItems pi
                    JOIN Purchases pur ON pi.purchase_id = pur.purchase_id
                    WHERE pi.SKU = p.SKU
                    AND pur.purchase_datetime >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                )
                WHERE EXISTS (
                    SELECT 1
                    FROM PurchaseItems pi
                    JOIN Purchases pur ON pi.purchase_id = pur.purchase_id
                    WHERE pi.SKU = p.SKU
                    AND pur.purchase_datetime >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                )
            """
            
            cursor.execute(update_query)
            conn.commit()
            
            rows_affected = cursor.rowcount
            logger.info(f"Updated costs for {rows_affected} products based on purchase history")
            
            return rows_affected
            
        except Exception as e:
            logger.error(f"Error in update_product_costs_from_purchases: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

# Global instance for easy access
dashboard_analytics = DashboardAnalytics()

# Convenience functions for direct access
def get_sales_summary(start_date: str, end_date: str, employee_id: Optional[int] = None):
    return dashboard_analytics.get_sales_summary(start_date, end_date, employee_id)

def get_top_products(start_date: str, end_date: str, limit: int = 5):
    return dashboard_analytics.get_top_products(start_date, end_date, limit)

def get_employee_sales(employee_id: int, start_date: str, end_date: str):
    return dashboard_analytics.get_employee_sales(employee_id, start_date, end_date)

def get_daily_sales_data(start_date: str, end_date: str):
    return dashboard_analytics.get_daily_sales_data(start_date, end_date)

def calculate_profit_margins():
    return dashboard_analytics.calculate_profit_margins()

def get_inventory_value():
    return dashboard_analytics.get_inventory_value()

def get_supplier_performance():
    return dashboard_analytics.get_supplier_performance()

def calculate_purchase_roi(supplier_id: Optional[int] = None):
    return dashboard_analytics.calculate_purchase_roi(supplier_id)

def track_cost_trends(supplier_id: Optional[int] = None, product_sku: Optional[str] = None):
    return dashboard_analytics.track_cost_trends(supplier_id, product_sku)

def get_category_analytics():
    return dashboard_analytics.get_category_analytics()

def get_low_stock_analytics():
    return dashboard_analytics.get_low_stock_analytics()

def get_recent_activities(limit: int = 10):
    return dashboard_analytics.get_recent_activities(limit)

def update_product_costs_from_purchases():
    return dashboard_analytics.update_product_costs_from_purchases()
