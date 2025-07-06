"""
Enhanced Dashboard Backend Functions for DigiClimate Store Hub POS & Inventory System
Provides comprehensive business intelligence and analytics capabilities
"""

import mysql.connector
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import get_db

# Configure logging
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
    
    def get_sales_summary(self, start_date: str, end_date: str, employee_id: Optional[int] = None, 
                         supplier_id: Optional[int] = None, category_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get comprehensive sales summary with profit calculations
        Returns total sales, orders, profit, and comparison metrics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Base query for sales summary with extended filtering
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
            """
            
            # Build WHERE clause with conditions
            conditions = ["DATE(s.sale_datetime) BETWEEN %s AND %s"]
            params = [start_date, end_date]
            
            if employee_id:
                conditions.append("s.employee_id = %s")
                params.append(employee_id)
                
            if supplier_id:
                conditions.append("p.supplier_id = %s")
                params.append(supplier_id)
                
            if category_id:
                conditions.append("p.category_id = %s")
                params.append(category_id)
            
            base_query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(base_query, params)
            current_period = cursor.fetchone()
            
            # Calculate previous period for comparison with same filters
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            period_days = (end_dt - start_dt).days + 1
            
            prev_start = (start_dt - timedelta(days=period_days)).strftime('%Y-%m-%d')
            prev_end = (start_dt - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Apply same filters to previous period
            prev_params = [prev_start, prev_end]
            if employee_id:
                prev_params.append(employee_id)
            if supplier_id:
                prev_params.append(supplier_id)
            if category_id:
                prev_params.append(category_id)
                
            cursor.execute(base_query.replace("BETWEEN %s AND %s", "BETWEEN %s AND %s"), prev_params)
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

    def get_top_products(self, start_date: str, end_date: str, limit: int = 5, employee_id: Optional[int] = None,
                        supplier_id: Optional[int] = None, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
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
            """
            
            # Build WHERE clause with conditions
            conditions = ["DATE(s.sale_datetime) BETWEEN %s AND %s"]
            params = [start_date, end_date]
            
            if employee_id:
                conditions.append("s.employee_id = %s")
                params.append(employee_id)
                
            if supplier_id:
                conditions.append("p.supplier_id = %s")
                params.append(supplier_id)
                
            if category_id:
                conditions.append("p.category_id = %s")
                params.append(category_id)
            
            query += " WHERE " + " AND ".join(conditions)
            query += """
                GROUP BY p.SKU, p.name, p.cost, p.stock
                ORDER BY units_sold DESC
                LIMIT %s
            """
            
            params.append(limit)
            cursor.execute(query, params)
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
                WHERE e.employee_id = %s AND DATE(s.sale_datetime) BETWEEN %s AND %s
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
                WHERE DATE(s.sale_datetime) BETWEEN %s AND %s
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

    # Performance optimized dashboard data functions
    @staticmethod
    def get_dashboard_summary_fast(start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get essential dashboard summary with minimal data load for fast initial display
        Returns only the most critical metrics with optimized queries
        """
        try:
            conn, cursor = get_db()
            
            # Single optimized query for key metrics
            summary_query = """
                SELECT 
                    COUNT(DISTINCT s.sale_id) as total_orders,
                    COALESCE(SUM(s.total), 0) as total_sales,
                    COALESCE(AVG(s.total), 0) as avg_order_value,
                    COUNT(DISTINCT s.employee_id) as active_employees,
                    COUNT(DISTINCT s.customer_id) as active_customers
                FROM Sales s
                WHERE DATE(s.sale_datetime) BETWEEN %s AND %s
            """
            
            cursor.execute(summary_query, (start_date, end_date))
            summary = cursor.fetchone()
            
            # Quick low stock count
            low_stock_query = """
                SELECT COUNT(*) as low_stock_count
                FROM Products 
                WHERE stock <= low_stock_threshold
                LIMIT 1
            """
            cursor.execute(low_stock_query)
            low_stock = cursor.fetchone()
            
            # Combine results
            result = dict(summary) if summary else {}
            result['low_stock_count'] = low_stock['low_stock_count'] if low_stock else 0
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {}
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()
            except:
                pass

    @staticmethod
    def get_top_products_fast(start_date: str, end_date: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top products with minimal data for fast display
        """
        try:
            conn, cursor = get_db()
            
            query = """
                SELECT 
                    p.SKU,
                    p.name,
                    SUM(si.quantity) as units_sold,
                    COALESCE(SUM(si.quantity * si.price), 0) as revenue
                FROM SaleItems si
                JOIN Sales s ON si.sale_id = s.sale_id
                JOIN Products p ON si.SKU = p.SKU
                WHERE DATE(s.sale_datetime) BETWEEN %s AND %s
                GROUP BY p.SKU, p.name
                ORDER BY units_sold DESC
                LIMIT %s
            """
            
            cursor.execute(query, (start_date, end_date, limit))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return []
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()
            except:
                pass

    @staticmethod
    def get_recent_sales_fast(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent sales with minimal data for fast display
        """
        try:
            conn, cursor = get_db()
            
            query = """
                SELECT 
                    s.sale_id,
                    s.sale_datetime,
                    s.total,
                    e.name as employee_name
                FROM Sales s
                JOIN Employees e ON s.employee_id = e.employee_id
                ORDER BY s.sale_datetime DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting recent sales: {e}")
            return []
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()
            except:
                pass

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
    
    def get_recent_activities(self, limit: int = 10, employee_id: Optional[int] = None,
                             supplier_id: Optional[int] = None, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
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
            """
            
            # Build WHERE clause with conditions
            conditions = []
            params = []
            
            if employee_id:
                conditions.append("s.employee_id = %s")
                params.append(employee_id)
                
            if supplier_id:
                conditions.append("p.supplier_id = %s")
                params.append(supplier_id)
                
            if category_id:
                conditions.append("p.category_id = %s")
                params.append(category_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += """
                GROUP BY s.sale_id, s.sale_datetime, s.total, e.name, c.name
                ORDER BY s.sale_datetime DESC
                LIMIT %s
            """
            
            params.append(limit)
            cursor.execute(query, params)
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
            
            return rows_affected
            
        except Exception as e:
            logger.error(f"Error in update_product_costs_from_purchases: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    # === PERFORMANCE ANALYSIS FUNCTIONS (Phase 5A) ===

    def get_employee_performance_ranking(self, start_date: str, end_date: str):
        """Get employee performance ranking with comprehensive metrics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    e.employee_id,
                    e.name as employee_name,
                    COUNT(DISTINCT s.sale_id) as total_sales,
                    SUM(s.total) as total_revenue,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as total_profit,
                    AVG(s.total) as avg_sale_value,
                    SUM(si.quantity) as items_sold,
                    RANK() OVER (ORDER BY SUM(s.total) DESC) as sales_rank,
                    RANK() OVER (ORDER BY SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) DESC) as profit_rank
                FROM Employees e
                JOIN Sales s ON e.employee_id = s.employee_id
                JOIN SaleItems si ON s.sale_id = si.sale_id
                LEFT JOIN Products p ON si.SKU = p.SKU
                WHERE s.sale_datetime BETWEEN %s AND %s
                GROUP BY e.employee_id, e.name
                ORDER BY sales_rank, profit_rank
            """
            
            cursor.execute(query, (start_date, end_date))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_employee_performance_ranking: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_product_performance_analysis(self, start_date: str, end_date: str):
        """Get detailed product performance analysis"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    p.SKU,
                    p.name,
                    SUM(si.quantity) as total_units_sold,
                    SUM(si.quantity * si.price) as total_revenue,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as total_profit,
                    AVG(si.price) as avg_selling_price,
                    p.cost,
                    p.stock as current_stock,
                    RANK() OVER (ORDER BY SUM(si.quantity * si.price) DESC) as revenue_rank,
                    RANK() OVER (ORDER BY SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) DESC) as profit_rank
                FROM Products p
                JOIN SaleItems si ON p.SKU = si.SKU
                JOIN Sales s ON si.sale_id = s.sale_id
                WHERE s.sale_datetime BETWEEN %s AND %s
                GROUP BY p.SKU, p.name, p.cost, p.stock
                ORDER BY revenue_rank, profit_rank
            """
            
            cursor.execute(query, (start_date, end_date))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_product_performance_analysis: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_cost_efficiency_metrics(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get cost efficiency metrics for products and categories with optional date filtering"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Base query
            query = """
                SELECT 
                    p.SKU,
                    p.name,
                    p.cost,
                    p.price,
                    (p.price - p.cost) as profit_per_unit,
                    ((p.price - p.cost) / p.price) * 100 as profit_margin,
                    c.name as category_name,
                    SUM(si.quantity) as total_units_sold,
                    SUM(si.quantity * si.price) as total_revenue,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as total_profit
                FROM Products p
                JOIN SaleItems si ON p.SKU = si.SKU
                JOIN Sales s ON si.sale_id = s.sale_id
                LEFT JOIN Categories c ON p.category_id = c.category_id
            """
            
            # Add date filtering if provided
            params = []
            if start_date and end_date:
                query += " WHERE s.sale_datetime BETWEEN %s AND %s"
                params = [start_date, end_date]
            
            query += """
                GROUP BY p.SKU, p.name, p.cost, p.price, c.name
                HAVING total_units_sold > 0
                ORDER BY profit_margin DESC, total_profit DESC
            """
            
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_cost_efficiency_metrics: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_employee_productivity_trends(self, employee_id: int, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get employee productivity trends over time"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    DATE(s.sale_datetime) as sale_date,
                    SUM(s.total) as daily_revenue,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as daily_profit,
                    COUNT(DISTINCT s.sale_id) as daily_orders,
                    SUM(si.quantity) as daily_items,
                    e.name as employee_name
                FROM Sales s
                JOIN SaleItems si ON s.sale_id = si.sale_id
                LEFT JOIN Products p ON si.SKU = p.SKU
                JOIN Employees e ON s.employee_id = e.employee_id
                WHERE e.employee_id = %s AND s.sale_datetime BETWEEN %s AND %s
                GROUP BY DATE(s.sale_datetime), e.name
                ORDER BY sale_date
            """
            
            cursor.execute(query, (employee_id, start_date, end_date))
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_employee_productivity_trends: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_performance_benchmarks(self) -> Dict[str, Any]:
        """Get performance benchmarks and targets"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Example query for benchmarks (this should be customized)
            query = """
                SELECT 
                    'sales' as metric,
                    AVG(total_sales) as benchmark_value
                FROM (
                    SELECT 
                        DATE(sale_datetime) as sale_date,
                        SUM(total) as total_sales
                    FROM Sales
                    GROUP BY DATE(sale_datetime)
                ) daily_sales
            """
            
            cursor.execute(query)
            sales_benchmark = cursor.fetchone()
            
            return {
                'sales_benchmark': sales_benchmark['benchmark_value'] if sales_benchmark else 0,
                # Add more benchmarks as needed
            }
            
        except Exception as e:
            logger.error(f"Error in get_performance_benchmarks: {e}")
            return {
                'sales_benchmark': 0,
                # Default values for other benchmarks
            }
        finally:
            if cursor:
                cursor.close()

    # === SIMULATION AND FORECASTING FUNCTIONS (Phase 5B) ===

    def simulate_price_changes(self, sku: str, price_scenarios: List[float]) -> List[Dict[str, Any]]:
        """Simulate revenue impact of different price scenarios for a product"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get historical sales data for the product
            query = """
                SELECT 
                    AVG(si.quantity) as avg_quantity_sold,
                    AVG(si.price) as current_avg_price,
                    SUM(si.quantity) as total_units_sold,
                    COUNT(DISTINCT s.sale_id) as total_transactions,
                    p.name as product_name,
                    p.stock as current_stock,
                    p.cost as product_cost
                FROM SaleItems si
                JOIN Sales s ON si.sale_id = s.sale_id
                JOIN Products p ON si.SKU = p.SKU
                WHERE p.SKU = %s
                AND s.sale_datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
                GROUP BY p.SKU, p.name, p.stock, p.cost
            """
            
            cursor.execute(query, (sku,))
            base_data = cursor.fetchone()
            
            if not base_data:
                return []
            
            results = []
            current_price = float(base_data['current_avg_price'])
            avg_quantity = float(base_data['avg_quantity_sold'])
            product_cost = float(base_data['product_cost']) if base_data['product_cost'] else 0
            
            for new_price in price_scenarios:
                # Simple price elasticity simulation (can be enhanced)
                price_change_ratio = new_price / current_price
                # Assume elasticity of -1.5 (when price increases 10%, demand decreases 15%)
                elasticity = -1.5
                demand_change_ratio = price_change_ratio ** elasticity
                
                simulated_quantity = avg_quantity * demand_change_ratio
                simulated_revenue = simulated_quantity * new_price
                simulated_profit = simulated_quantity * (new_price - product_cost)
                current_revenue = avg_quantity * current_price
                current_profit = avg_quantity * (current_price - product_cost)
                
                results.append({
                    'sku': sku,
                    'product_name': base_data['product_name'],
                    'scenario_price': new_price,
                    'current_price': current_price,
                    'price_change_percent': ((new_price - current_price) / current_price) * 100,
                    'estimated_quantity': simulated_quantity,
                    'current_quantity': avg_quantity,
                    'quantity_change_percent': ((simulated_quantity - avg_quantity) / avg_quantity) * 100,
                    'estimated_revenue': simulated_revenue,
                    'current_revenue': current_revenue,
                    'revenue_change': simulated_revenue - current_revenue,
                    'revenue_change_percent': ((simulated_revenue - current_revenue) / current_revenue) * 100,
                    'estimated_profit': simulated_profit,
                    'current_profit': current_profit,
                    'profit_change': simulated_profit - current_profit,
                    'profit_change_percent': ((simulated_profit - current_profit) / current_profit) * 100 if current_profit > 0 else 0
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in simulate_price_changes: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def simulate_inventory_scenarios(self, reorder_levels: Dict[str, int]) -> Dict[str, Any]:
        """Simulate inventory scenarios with different reorder levels"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            simulation_results = {}
            
            for sku, new_reorder_level in reorder_levels.items():
                # Get current product data
                query = """
                    SELECT 
                        p.SKU,
                        p.name,
                        p.stock,
                        p.cost,
                        p.price,
                        AVG(si.quantity) as avg_daily_sales,
                        COUNT(DISTINCT DATE(s.sale_datetime)) as sales_days
                    FROM Products p
                    LEFT JOIN SaleItems si ON p.SKU = si.SKU
                    LEFT JOIN Sales s ON si.sale_id = s.sale_id
                    WHERE p.SKU = %s
                    AND s.sale_datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
                    GROUP BY p.SKU, p.name, p.stock, p.cost, p.price
                """
                
                cursor.execute(query, (sku,))
                product_data = cursor.fetchone()
                
                if product_data:
                    current_stock = int(product_data['stock'])
                    avg_daily_sales = float(product_data['avg_daily_sales']) if product_data['avg_daily_sales'] else 0
                    sales_days = int(product_data['sales_days']) if product_data['sales_days'] else 1
                    cost_per_unit = float(product_data['cost'])
                    price_per_unit = float(product_data['price'])
                    
                    # Normalize daily sales rate (handle cases with sparse sales data)
                    if sales_days > 0 and avg_daily_sales > 0:
                        actual_daily_sales = avg_daily_sales * (sales_days / 30)  # Adjust for actual selling days
                    else:
                        actual_daily_sales = 0.1  # Minimum assumption for rarely sold items
                    
                    # Calculate realistic inventory metrics
                    if actual_daily_sales > 0:
                        days_until_stockout = current_stock / actual_daily_sales
                        days_until_reorder = max(0, (current_stock - new_reorder_level) / actual_daily_sales)
                    else:
                        days_until_stockout = float('inf')
                        days_until_reorder = float('inf')
                    
                    # More realistic carrying cost calculation
                    # Annual carrying cost typically 20-30% of inventory value
                    annual_carrying_rate = 0.25  # 25% annually
                    daily_carrying_rate = annual_carrying_rate / 365
                    carrying_cost_per_unit_per_day = cost_per_unit * daily_carrying_rate
                    
                    # More realistic stockout cost (consider profit margin and customer impact)
                    profit_margin = max(0, price_per_unit - cost_per_unit)
                    # Stockout cost includes lost profit + customer goodwill impact
                    stockout_cost_per_unit = profit_margin + (price_per_unit * 0.1)  # 10% goodwill impact
                    
                    # Simulate 60-day scenario for better accuracy
                    simulation_days = 60
                    
                    # Calculate inventory costs
                    avg_inventory_level = (current_stock + new_reorder_level) / 2
                    total_carrying_cost = avg_inventory_level * carrying_cost_per_unit_per_day * simulation_days
                    
                    # Calculate stockout risk and cost
                    if days_until_stockout < simulation_days:
                        potential_stockout_days = simulation_days - days_until_stockout
                        stockout_units = potential_stockout_days * actual_daily_sales
                        stockout_cost = stockout_units * stockout_cost_per_unit
                    else:
                        stockout_cost = 0
                    
                    # Service level calculation
                    if days_until_stockout >= 30:
                        service_level = "Excellent (30+ days)"
                        risk_level = "Low"
                    elif days_until_stockout >= 14:
                        service_level = "Good (14-30 days)"
                        risk_level = "Medium"
                    elif days_until_stockout >= 7:
                        service_level = "Adequate (7-14 days)"
                        risk_level = "Medium"
                    else:
                        service_level = f"Critical ({days_until_stockout:.1f} days)"
                        risk_level = "High"
                    
                    simulation_results[sku] = {
                        'product_name': product_data['name'],
                        'current_stock': current_stock,
                        'new_reorder_level': new_reorder_level,
                        'avg_daily_sales': actual_daily_sales,
                        'days_until_stockout': days_until_stockout,
                        'days_until_reorder': days_until_reorder,
                        'estimated_carrying_cost': total_carrying_cost,
                        'estimated_stockout_cost': stockout_cost,
                        'total_estimated_cost': total_carrying_cost + stockout_cost,
                        'risk_level': risk_level,
                        'service_level': service_level,
                        'profit_margin': profit_margin,
                        'simulation_period_days': simulation_days
                    }
            
            return simulation_results
            
        except Exception as e:
            logger.error(f"Error in simulate_inventory_scenarios: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()

    def forecast_revenue(self, months_ahead: int = 3) -> List[Dict[str, Any]]:
        """Forecast revenue for the next specified months with improved statistical methods"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get historical monthly revenue data
            query = """
                SELECT 
                    YEAR(sale_datetime) as year,
                    MONTH(sale_datetime) as month,
                    SUM(total) as monthly_revenue,
                    COUNT(DISTINCT sale_id) as transaction_count,
                    AVG(total) as avg_transaction_value
                FROM Sales
                WHERE sale_datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
                GROUP BY YEAR(sale_datetime), MONTH(sale_datetime)
                ORDER BY year, month
            """
            
            cursor.execute(query)
            historical_data = cursor.fetchall()
            
            if len(historical_data) < 3:  # Need at least 3 months of data
                return []
            
            # Extract revenue data and calculate statistics
            revenues = [float(row['monthly_revenue']) for row in historical_data]
            months_count = len(revenues)
            
            # Calculate basic statistics for validation
            mean_revenue = sum(revenues) / months_count
            revenue_std = (sum((r - mean_revenue) ** 2 for r in revenues) / months_count) ** 0.5
            coefficient_of_variation = revenue_std / mean_revenue if mean_revenue > 0 else 0
            
            # Calculate trend (simple linear regression)
            x_values = list(range(months_count))
            x_mean = sum(x_values) / months_count
            y_mean = sum(revenues) / months_count
            
            numerator = sum((x_values[i] - x_mean) * (revenues[i] - y_mean) for i in range(months_count))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(months_count))
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            intercept = y_mean - slope * x_mean
            
            # Calculate R-squared for model quality assessment
            y_pred = [intercept + slope * x for x in x_values]
            ss_res = sum((revenues[i] - y_pred[i]) ** 2 for i in range(months_count))
            ss_tot = sum((revenues[i] - y_mean) ** 2 for i in range(months_count))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Adjust confidence based on model quality and data stability
            base_confidence = 0.85
            if r_squared < 0.3:  # Poor trend fit
                base_confidence *= 0.7
            if coefficient_of_variation > 0.5:  # High volatility
                base_confidence *= 0.8
            if months_count < 6:  # Limited data
                base_confidence *= 0.9
            
            # Generate forecasts
            forecasts = []
            for i in range(1, months_ahead + 1):
                future_month_index = months_count + i - 1
                
                # Use hybrid approach: trend + recent average for stability
                trend_forecast = intercept + slope * future_month_index
                recent_average = sum(revenues[-min(3, months_count):]) / min(3, months_count)
                
                # Weight trend vs recent average based on trend quality
                trend_weight = max(0.3, r_squared) if r_squared > 0 else 0.3
                recent_weight = 1 - trend_weight
                
                base_forecast = (trend_forecast * trend_weight) + (recent_average * recent_weight)
                
                # Apply seasonal adjustment
                current_month = (datetime.now().month + i - 1) % 12 + 1
                seasonal_factor = 1.1 if current_month in [11, 12] else 0.95 if current_month in [1, 2] else 1.0
                
                forecasted_revenue = base_forecast * seasonal_factor
                
                # Calculate adaptive confidence intervals based on data quality
                # Higher uncertainty for poor fits and volatile data
                base_uncertainty = 0.15  # 15% base uncertainty
                if r_squared < 0.3:
                    base_uncertainty *= 1.5  # Increase uncertainty for poor trends
                if coefficient_of_variation > 0.5:
                    base_uncertainty *= 1.3  # Increase for high volatility
                
                # Increase uncertainty for longer forecasts
                time_factor = 1 + (i - 1) * 0.1  # 10% increase per month
                adjusted_uncertainty = base_uncertainty * time_factor
                
                confidence_range = forecasted_revenue * adjusted_uncertainty
                
                # Ensure realistic bounds
                lower_bound = max(0, forecasted_revenue - confidence_range)
                upper_bound = forecasted_revenue + confidence_range
                
                # Cap unrealistic forecasts (prevent exponential growth)
                max_realistic_growth = mean_revenue * 2  # Don't exceed 2x historical average
                if forecasted_revenue > max_realistic_growth:
                    forecasted_revenue = max_realistic_growth
                    upper_bound = min(upper_bound, max_realistic_growth * 1.2)
                
                forecasts.append({
                    'month_ahead': i,
                    'forecasted_revenue': max(0, forecasted_revenue),
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'confidence_level': base_confidence,
                    'trend_direction': 'Increasing' if slope > 0 else 'Decreasing' if slope < 0 else 'Stable',
                    'model_quality': 'Good' if r_squared > 0.7 else 'Fair' if r_squared > 0.3 else 'Poor',
                    'data_reliability': 'High' if coefficient_of_variation < 0.3 else 'Medium' if coefficient_of_variation < 0.5 else 'Low'
                })
            
            return forecasts
            
        except Exception as e:
            logger.error(f"Error in forecast_revenue: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def simulate_staff_scenarios(self, staff_changes: Dict[str, int]) -> Dict[str, Any]:
        """Simulate impact of staff level changes on operations"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get current staff performance metrics
            query = """
                SELECT 
                    e.employee_id,
                    e.name,
                    e.hourly_rate,
                    COUNT(DISTINCT s.sale_id) as sales_count,
                    SUM(s.total) as total_revenue,
                    AVG(s.total) as avg_sale_value,
                    COUNT(DISTINCT DATE(s.sale_datetime)) as working_days
                FROM Employees e
                LEFT JOIN Sales s ON e.employee_id = s.employee_id
                WHERE s.sale_datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
                GROUP BY e.employee_id, e.name, e.hourly_rate
            """
            
            cursor.execute(query)
            current_staff = cursor.fetchall()
            
            # Calculate current metrics
            total_current_revenue = sum(float(emp['total_revenue']) for emp in current_staff if emp['total_revenue'])
            total_current_staff = len(current_staff)
            avg_revenue_per_employee = total_current_revenue / total_current_staff if total_current_staff > 0 else 0
            
            simulation_results = {}
            
            for scenario_name, staff_change in staff_changes.items():
                new_staff_count = total_current_staff + staff_change
                
                if new_staff_count <= 0:
                    continue
                
                # Estimate new revenue (assuming linear relationship with diminishing returns)
                efficiency_factor = 1.0 if staff_change <= 0 else max(0.7, 1.0 - (staff_change * 0.05))
                estimated_new_revenue = total_current_revenue * (new_staff_count / total_current_staff) * efficiency_factor
                
                # Estimate costs
                avg_hourly_rate = 15.0  # Default hourly rate
                if current_staff and current_staff[0]['hourly_rate']:
                    avg_hourly_rate = sum(float(emp['hourly_rate']) for emp in current_staff if emp['hourly_rate']) / len(current_staff)
                
                additional_staff_cost = staff_change * avg_hourly_rate * 160  # 160 hours per month
                
                simulation_results[scenario_name] = {
                    'current_staff_count': total_current_staff,
                    'new_staff_count': new_staff_count,
                    'staff_change': staff_change,
                    'current_monthly_revenue': total_current_revenue,
                    'estimated_new_revenue': estimated_new_revenue,
                    'revenue_change': estimated_new_revenue - total_current_revenue,
                    'additional_staff_cost': additional_staff_cost,
                    'net_impact': (estimated_new_revenue - total_current_revenue) - additional_staff_cost,
                    'roi_percentage': (((estimated_new_revenue - total_current_revenue) - additional_staff_cost) / abs(additional_staff_cost)) * 100 if additional_staff_cost != 0 else 0,
                    'efficiency_factor': efficiency_factor
                }
            
            return simulation_results
            
        except Exception as e:
            logger.error(f"Error in simulate_staff_scenarios: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()

    def analyze_optimal_pricing(self, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Analyze optimal pricing strategies for products"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    p.SKU,
                    p.name,
                    p.cost,
                    p.price,
                    AVG(si.price) as avg_selling_price,
                    SUM(si.quantity) as total_units_sold,
                    SUM(si.quantity * si.price) as total_revenue,
                    SUM(si.quantity * (si.price - COALESCE(p.cost, 0))) as total_profit,
                    COUNT(DISTINCT s.sale_id) as transaction_count,
                    MAX(si.price) as highest_price_sold,
                    MIN(si.price) as lowest_price_sold
                FROM Products p
                JOIN SaleItems si ON p.SKU = si.SKU
                JOIN Sales s ON si.sale_id = s.sale_id
                WHERE s.sale_datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
            """
            
            params = []
            if category_id:
                query += " AND p.category_id = %s"
                params.append(category_id)
            
            query += """
                GROUP BY p.SKU, p.name, p.cost, p.price
                HAVING total_units_sold > 0
                ORDER BY total_revenue DESC
            """
            
            cursor.execute(query, params)
            products = cursor.fetchall()
            
            optimization_results = []
            
            for product in products:
                current_price = float(product['price'])
                cost = float(product['cost']) if product['cost'] else 0
                current_margin = ((current_price - cost) / current_price) * 100 if current_price > 0 else 0
                avg_selling_price = float(product['avg_selling_price'])
                units_sold = float(product['total_units_sold'])
                current_profit = float(product['total_profit'])
                
                # Suggest optimal price based on various factors with detailed reasoning
                recommended_price = current_price
                recommendation_reason = "✅ Current pricing is well optimized - no changes needed"
                
                # Factor 1: If selling below list price consistently, might decrease
                if avg_selling_price < current_price * 0.9:
                    recommended_price = current_price * 0.95
                    price_gap = ((current_price - avg_selling_price) / current_price) * 100
                    recommendation_reason = f"💡 Reduce by 5% to ${recommended_price:.2f} - customers consistently pay {price_gap:.0f}% below list price"
                
                # Factor 2: If cost margin is too low, increase price
                elif current_margin < 30 and cost > 0:
                    recommended_price = cost * 1.43  # Target 30% margin (cost / 0.7)
                    recommendation_reason = f"📈 Increase to ${recommended_price:.2f} to achieve healthy 30% margin (currently {current_margin:.0f}%)"
                
                # Factor 3: Market-based pricing adjustment
                elif product['highest_price_sold'] > current_price * 1.05:
                    recommended_price = min(current_price * 1.05, float(product['highest_price_sold']) * 0.95)
                    highest_sold = float(product['highest_price_sold'])
                    recommendation_reason = f"🚀 Increase to ${recommended_price:.2f} - market data shows customers will pay up to ${highest_sold:.2f}"
                
                # Factor 4: High margin products - consider small price increase
                elif current_margin > 50 and units_sold > 10:
                    recommended_price = current_price * 1.02
                    recommendation_reason = f"💰 Premium pricing opportunity: increase to ${recommended_price:.2f} (strong {units_sold:.0f} unit sales, {current_margin:.0f}% margin)"
                
                # Factor 5: Low volume products - consider price reduction
                elif units_sold < 5 and current_margin > 25:
                    recommended_price = current_price * 0.95
                    recommendation_reason = f"🎯 Stimulate demand: reduce to ${recommended_price:.2f} to boost sales (only {units_sold:.0f} units sold in 90 days)"
                
                # Calculate improved impact estimates
                price_change_ratio = recommended_price / current_price
                
                # More realistic demand elasticity
                if price_change_ratio > 1.0:
                    # Price increase - assume some customer loss
                    elasticity = -0.3 if current_margin > 40 else -0.5
                    demand_change = (price_change_ratio - 1) * elasticity
                else:
                    # Price decrease - assume demand increase
                    elasticity = 0.4 if current_margin > 30 else 0.2
                    demand_change = (1 - price_change_ratio) * elasticity
                
                # Projected monthly sales (scale from 90-day data)
                monthly_units = units_sold / 3  # Convert 90-day to monthly
                estimated_new_monthly_units = monthly_units * (1 + demand_change)
                
                # Monthly profit calculations
                current_monthly_profit = monthly_units * (current_price - cost)
                estimated_new_monthly_profit = estimated_new_monthly_units * (recommended_price - cost)
                monthly_profit_impact = estimated_new_monthly_profit - current_monthly_profit
                
                optimization_results.append({
                    'sku': product['SKU'],
                    'product_name': product['name'],
                    'current_price': current_price,
                    'recommended_price': recommended_price,
                    'price_change_percent': ((recommended_price - current_price) / current_price) * 100,
                    'current_margin_percent': current_margin,
                    'new_margin_percent': ((recommended_price - cost) / recommended_price) * 100 if recommended_price > 0 else 0,
                    'current_monthly_profit': current_monthly_profit,
                    'estimated_new_profit': estimated_new_monthly_profit,
                    'profit_impact': monthly_profit_impact,
                    'units_sold_last_90_days': units_sold,
                    'estimated_new_units': estimated_new_monthly_units,
                    'recommendation_reason': recommendation_reason
                })
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error in analyze_optimal_pricing: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def _get_pricing_recommendation_reason(self, current_price, recommended_price, margin, avg_selling):
        """Helper method to generate pricing recommendation explanations"""
        if recommended_price > current_price:
            if margin < 30:
                return "Increase price to improve profit margin"
            elif avg_selling < current_price * 0.9:
                return "Market accepts higher prices based on sales data"
            else:
                return "Optimize for better profitability"
        elif recommended_price < current_price:
            return "Lower price to increase demand and market share"
        else:
            return "Current pricing appears optimal"

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all product categories"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT category_id, name FROM Categories ORDER BY name"
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error in get_categories: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

# === GLOBAL ANALYTICS INSTANCE ===
dashboard_analytics = DashboardAnalytics()

# === OPTIMIZED FAST FUNCTION STUBS ===

def get_dashboard_summary_fast(start_date: str, end_date: str):
    """Get essential dashboard summary with minimal data load for fast initial display"""
    return DashboardAnalytics.get_dashboard_summary_fast(start_date, end_date)

def get_top_products_fast(start_date: str, end_date: str, limit: int = 5):
    """Get top products with minimal data for fast display"""
    return DashboardAnalytics.get_top_products_fast(start_date, end_date, limit)

def get_recent_sales_fast(limit: int = 10):
    """Get recent sales with minimal data for fast display"""
    return DashboardAnalytics.get_recent_sales_fast(limit)

# === CORE ANALYTICS FUNCTION STUBS ===

def get_sales_summary(start_date: str, end_date: str, employee_id: Optional[int] = None,
                     supplier_id: Optional[int] = None, category_id: Optional[int] = None):
    """Get comprehensive sales summary with enhanced filtering"""
    return dashboard_analytics.get_sales_summary(start_date, end_date, employee_id, supplier_id, category_id)

def get_inventory_value():
    """Get total inventory value and metrics"""
    return dashboard_analytics.get_inventory_value()

def calculate_profit_margins():
    """Calculate profit margins for all products"""
    return dashboard_analytics.calculate_profit_margins()

def get_top_products(start_date: str, end_date: str, limit: int = 10, employee_id: Optional[int] = None,
                    supplier_id: Optional[int] = None, category_id: Optional[int] = None):
    """Get top performing products by sales with enhanced filtering"""
    return dashboard_analytics.get_top_products(start_date, end_date, limit, employee_id, supplier_id, category_id)

def get_low_stock_analytics():
    """Get low stock items analysis"""
    return dashboard_analytics.get_low_stock_analytics()

def get_recent_activities(limit: int = 10, employee_id: Optional[int] = None,
                         supplier_id: Optional[int] = None, category_id: Optional[int] = None):
    """Get recent sales activities with enhanced filtering"""
    return dashboard_analytics.get_recent_activities(limit, employee_id, supplier_id, category_id)

def get_supplier_performance():
    """Get supplier performance metrics"""
    return dashboard_analytics.get_supplier_performance()

def get_daily_sales_data(start_date: str, end_date: str):
    """Get daily sales data for charting"""
    return dashboard_analytics.get_daily_sales_data(start_date, end_date)

def get_category_analytics():
    """Get product category analytics"""
    return dashboard_analytics.get_category_analytics()

# === PERFORMANCE ANALYSIS FUNCTION STUBS (Phase 5A) ===

def get_employee_performance_ranking(start_date: str, end_date: str):
    """Get employee performance ranking with comprehensive metrics"""
    return dashboard_analytics.get_employee_performance_ranking(start_date, end_date)

def get_product_performance_analysis(start_date: str, end_date: str):
    """Get detailed product performance analysis"""
    return dashboard_analytics.get_product_performance_analysis(start_date, end_date)

def get_cost_efficiency_metrics(start_date: str = None, end_date: str = None):
    """Get cost efficiency metrics for products and categories with optional date filtering"""
    return dashboard_analytics.get_cost_efficiency_metrics(start_date, end_date)

def get_employee_productivity_trends(employee_id: int, start_date: str, end_date: str):
    """Get employee productivity trends over time"""
    return dashboard_analytics.get_employee_productivity_trends(employee_id, start_date, end_date)

def get_performance_benchmarks():
    """Get performance benchmarks and targets"""
    return dashboard_analytics.get_performance_benchmarks()

# === SIMULATION FUNCTION STUBS (Phase 5B) ===

def simulate_price_changes(sku: str, price_scenarios: List[float]):
    """Simulate revenue impact of different price scenarios for a product"""
    return dashboard_analytics.simulate_price_changes(sku, price_scenarios)

def simulate_inventory_scenarios(reorder_levels: Dict[str, int]):
    """Simulate inventory scenarios with different reorder levels"""
    return dashboard_analytics.simulate_inventory_scenarios(reorder_levels)

def forecast_revenue(months_ahead: int = 3):
    """Forecast revenue for the next specified months"""
    return dashboard_analytics.forecast_revenue(months_ahead)

def simulate_staff_scenarios(staff_changes: Dict[str, int]):
    """Simulate impact of staff level changes on operations"""
    return dashboard_analytics.simulate_staff_scenarios(staff_changes)

def analyze_optimal_pricing(category_id: Optional[int] = None):
    """Analyze optimal pricing strategies for products"""
    return dashboard_analytics.analyze_optimal_pricing(category_id)

def get_categories():
    """Get all product categories"""
    return dashboard_analytics.get_categories()