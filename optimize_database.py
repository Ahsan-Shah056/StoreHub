"""
Database Performance Optimization Utility
Applies performance indexes to improve dashboard loading speed
"""

import mysql.connector
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import get_db, close_db

logger = logging.getLogger(__name__)

def apply_performance_indexes():
    """Apply performance optimization indexes to the database"""
    
    print("Attempting to connect to database...")
    
    # List of indexes to create (without IF NOT EXISTS)
    indexes = [
        "CREATE INDEX idx_sales_datetime ON Sales(sale_datetime)",
        "CREATE INDEX idx_sales_employee_datetime ON Sales(employee_id, sale_datetime)",
        "CREATE INDEX idx_sales_customer_datetime ON Sales(customer_id, sale_datetime)",
        "CREATE INDEX idx_sales_total_datetime ON Sales(total, sale_datetime)",
        "CREATE INDEX idx_saleitems_sale_id ON SaleItems(sale_id)",
        "CREATE INDEX idx_saleitems_sku_datetime ON SaleItems(SKU, sale_id)",
        "CREATE INDEX idx_saleitems_price_quantity ON SaleItems(price, quantity)",
        "CREATE INDEX idx_products_category_id ON Products(category_id)",
        "CREATE INDEX idx_products_supplier_id ON Products(supplier_id)",
        "CREATE INDEX idx_products_stock_threshold ON Products(stock, low_stock_threshold)",
        "CREATE INDEX idx_products_price ON Products(price)",
        "CREATE INDEX idx_products_name ON Products(name)",
        "CREATE INDEX idx_purchases_supplier_datetime ON Purchases(supplier_id, purchase_datetime)",
        "CREATE INDEX idx_purchases_datetime ON Purchases(purchase_datetime)",
        "CREATE INDEX idx_purchases_status ON Purchases(delivery_status)",
        "CREATE INDEX idx_purchaseitems_purchase_id ON PurchaseItems(purchase_id)",
        "CREATE INDEX idx_purchaseitems_sku ON PurchaseItems(SKU)",
        "CREATE INDEX idx_purchaseitems_cost ON PurchaseItems(unit_cost)",
        "CREATE INDEX idx_adjustments_sku_datetime ON InventoryAdjustments(SKU, adjustment_datetime)",
        "CREATE INDEX idx_adjustments_employee_datetime ON InventoryAdjustments(employee_id, adjustment_datetime)",
        "CREATE INDEX idx_adjustments_datetime ON InventoryAdjustments(adjustment_datetime)",
        "CREATE INDEX idx_sales_comprehensive ON Sales(sale_datetime, employee_id, customer_id, total)",
        "CREATE INDEX idx_saleitems_comprehensive ON SaleItems(sale_id, SKU, quantity, price)",
        "CREATE INDEX idx_products_dashboard_info ON Products(SKU, name, category_id, price, stock, supplier_id)",
        "CREATE INDEX idx_sales_dashboard_summary ON Sales(sale_datetime, total, employee_id)"
    ]
    
    try:
        print("Getting database connection...")
        connection, cursor = get_db()
        print("Database connection established successfully!")
        
        success_count = 0
        print(f"Creating {len(indexes)} performance indexes...")
        
        for i, index_sql in enumerate(indexes, 1):
            try:
                print(f"Creating index {i}/{len(indexes)}: {index_sql.split()[-1]}")
                cursor.execute(index_sql)
                success_count += 1
                logger.info(f"Successfully created index: {index_sql.split()[-1]}")
            except mysql.connector.Error as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    print(f"Index already exists, skipping: {index_sql.split()[-1]}")
                    logger.info(f"Index already exists, skipping: {index_sql.split()[-1]}")
                else:
                    print(f"Error creating index {index_sql.split()[-1]}: {e}")
                    logger.warning(f"Error creating index {index_sql.split()[-1]}: {e}")
        
        print("Committing changes...")
        connection.commit()
        print(f"Successfully applied {success_count} performance indexes")
        logger.info(f"Applied {success_count} performance indexes successfully")
        return True
        
    except Exception as e:
        print(f"Critical error applying performance indexes: {e}")
        logger.error(f"Error applying performance indexes: {e}")
        return False
    finally:
        try:
            print("Closing database connection...")
            close_db(connection, cursor)
            print("Database connection closed")
        except:
            print("Error closing database connection")
            pass

def analyze_index_usage():
    """Analyze index usage and provide recommendations"""
    try:
        print("Connecting to database for analysis...")
        connection, cursor = get_db()
        print("Connected! Analyzing indexes...")
        
        # Check existing indexes
        tables = ['Sales', 'SaleItems', 'Products', 'Purchases', 'PurchaseItems', 'InventoryAdjustments']
        
        for table in tables:
            try:
                cursor.execute(f"SHOW INDEX FROM {table}")
                indexes = cursor.fetchall()
                print(f"Table {table} has {len(indexes)} indexes")
                logger.info(f"Table {table} has {len(indexes)} indexes")
            except Exception as e:
                print(f"Error checking indexes for table {table}: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error analyzing indexes: {e}")
        logger.error(f"Error analyzing indexes: {e}")
        return False
    finally:
        try:
            close_db(connection, cursor)
        except:
            pass

if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("DigiClimate Store Hub - Database Performance Optimization")
    print("=" * 60)
    
    print("Applying performance indexes...")
    if apply_performance_indexes():
        print("✓ Performance indexes applied successfully!")
    else:
        print("✗ Failed to apply performance indexes")
    
    print("\nAnalyzing index usage...")
    if analyze_index_usage():
        print("✓ Index analysis completed")
    else:
        print("✗ Failed to analyze indexes")
    
    print("\nOptimization complete!")
