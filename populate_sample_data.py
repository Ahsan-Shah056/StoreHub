#!/usr/bin/env python3
"""
Sample Data Population Script for Storecore Database
Populates Sales, SaleItems, Purchases, and PurchaseItems tables with realistic test data
"""

import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db

class SampleDataPopulator:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.employees = []
        self.customers = []
        self.suppliers = []
        self.products = []
        
    def connect_db(self):
        """Connect to database"""
        try:
            self.conn, self.cursor = get_db()
            print("✓ Connected to database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def load_existing_data(self):
        """Load existing data from the database"""
        try:
            # Load employees
            self.cursor.execute("SELECT employee_id, name FROM Employees")
            self.employees = self.cursor.fetchall()
            print(f"✓ Loaded {len(self.employees)} employees")
            
            # Load customers
            self.cursor.execute("SELECT customer_id, name FROM Customers")
            self.customers = self.cursor.fetchall()
            print(f"✓ Loaded {len(self.customers)} customers")
            
            # Load suppliers
            self.cursor.execute("SELECT supplier_id, name FROM Suppliers")
            self.suppliers = self.cursor.fetchall()
            print(f"✓ Loaded {len(self.suppliers)} suppliers")
            
            # Load products with current stock and prices
            self.cursor.execute("""
                SELECT SKU, name, cost, price, stock, supplier_id 
                FROM Products 
                WHERE stock > 0 
                ORDER BY name
            """)
            self.products = self.cursor.fetchall()
            print(f"✓ Loaded {len(self.products)} products with stock")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading existing data: {e}")
            return False
    
    def generate_sales_data(self, num_sales=300):
        """Generate realistic sales data"""
        print(f"\n📊 Generating {num_sales} sales transactions...")
        
        try:
            sales_data = []
            sale_items_data = []
            
            # Generate sales over the last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            for i in range(num_sales):
                # Random date within the last 30 days
                random_days = random.randint(0, 30)
                random_hours = random.randint(8, 20)  # Business hours
                random_minutes = random.randint(0, 59)
                
                sale_datetime = start_date + timedelta(
                    days=random_days, 
                    hours=random_hours, 
                    minutes=random_minutes
                )
                
                # Random employee and customer
                employee = random.choice(self.employees)
                customer = random.choice(self.customers)
                
                # Generate 1-5 items per sale
                num_items = random.randint(1, 5)
                selected_products = random.sample(self.products, min(num_items, len(self.products)))
                
                sale_total = Decimal('0.00')
                sale_items = []
                
                for product in selected_products:
                    # Random quantity (1-10, but not more than available stock)
                    max_qty = min(10, int(product['stock']))
                    if max_qty <= 0:
                        continue
                        
                    quantity = random.randint(1, max_qty)
                    
                    # Use product price with small random variation (±10%)
                    base_price = float(product['price'])
                    price_variation = random.uniform(0.9, 1.1)
                    item_price = Decimal(str(round(base_price * price_variation, 2)))
                    
                    item_total = item_price * quantity
                    sale_total += item_total
                    
                    sale_items.append({
                        'SKU': product['SKU'],
                        'quantity': quantity,
                        'price': item_price
                    })
                
                if sale_items:  # Only add sale if it has items
                    sale_id = i + 1  # We'll get the actual ID after insertion
                    
                    sales_data.append({
                        'sale_datetime': sale_datetime,
                        'total': sale_total,
                        'employee_id': employee['employee_id'],
                        'customer_id': customer['customer_id'],
                        'items': sale_items
                    })
            
            # Insert sales data
            for sale_data in sales_data:
                # Insert sale
                sale_query = """
                    INSERT INTO Sales (sale_datetime, total, employee_id, customer_id)
                    VALUES (%s, %s, %s, %s)
                """
                
                self.cursor.execute(sale_query, (
                    sale_data['sale_datetime'],
                    sale_data['total'],
                    sale_data['employee_id'],
                    sale_data['customer_id']
                ))
                
                sale_id = self.cursor.lastrowid
                
                # Insert sale items
                for item in sale_data['items']:
                    item_query = """
                        INSERT INTO SaleItems (sale_id, SKU, quantity, price)
                        VALUES (%s, %s, %s, %s)
                    """
                    
                    self.cursor.execute(item_query, (
                        sale_id,
                        item['SKU'],
                        item['quantity'],
                        item['price']
                    ))
                    
                    # Update product stock
                    update_stock_query = """
                        UPDATE Products 
                        SET stock = stock - %s 
                        WHERE SKU = %s
                    """
                    self.cursor.execute(update_stock_query, (item['quantity'], item['SKU']))
            
            self.conn.commit()
            print(f"✓ Generated {len(sales_data)} sales with items")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating sales data: {e}")
            self.conn.rollback()
            return False
    
    def generate_sales_data(self, num_sales=5000):
        """Generate realistic sales data with inventory updates"""
        print(f"\n� Generating {num_sales} sales transactions...")
        
        try:
            sales_items_generated = 0
            
            # Generate sales over the last 60 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=60)
            
            for i in range(num_sales):
                # Random date within the last 60 days
                random_days = random.randint(0, 60)
                random_hours = random.randint(8, 22)  # Business hours
                random_minutes = random.randint(0, 59)
                
                sale_datetime = start_date + timedelta(
                    days=random_days,
                    hours=random_hours,
                    minutes=random_minutes
                )
                
                # Random employee and customer
                employee = random.choice(self.employees)
                customer = random.choice(self.customers)
                
                # Get products with stock > 0
                self.cursor.execute("SELECT SKU, name, cost, price, stock FROM Products WHERE stock > 0")
                available_products = self.cursor.fetchall()
                
                if not available_products:
                    print("⚠️ No products with stock available, skipping remaining sales")
                    break
                
                # Generate 1-8 items per sale
                num_items = random.randint(1, min(8, len(available_products)))
                selected_products = random.sample(available_products, num_items)
                
                sale_total = Decimal('0.00')
                sale_items = []
                
                for product in selected_products:
                    # Random quantity (1-20, but not more than available stock)
                    max_qty = min(20, int(product['stock']))
                    if max_qty <= 0:
                        continue
                        
                    quantity = random.randint(1, max_qty)
                    
                    # Use product price with small random variation (±5% for retail)
                    base_price = float(product['price'])
                    price_variation = random.uniform(0.95, 1.05)
                    item_price = Decimal(str(round(base_price * price_variation, 2)))
                    
                    item_total = item_price * quantity
                    sale_total += item_total
                    
                    sale_items.append({
                        'SKU': product['SKU'],
                        'quantity': quantity,
                        'price': item_price
                    })
                
                if sale_items:  # Only add sale if it has items
                    # Insert sale
                    sale_query = """
                        INSERT INTO Sales (sale_datetime, total, employee_id, customer_id)
                        VALUES (%s, %s, %s, %s)
                    """
                    
                    self.cursor.execute(sale_query, (
                        sale_datetime,
                        sale_total,
                        employee['employee_id'],
                        customer['customer_id']
                    ))
                    
                    sale_id = self.cursor.lastrowid
                    
                    # Insert sale items and update inventory
                    for item in sale_items:
                        # Insert sale item
                        item_query = """
                            INSERT INTO SaleItems (sale_id, SKU, quantity, price)
                            VALUES (%s, %s, %s, %s)
                        """
                        
                        self.cursor.execute(item_query, (
                            sale_id,
                            item['SKU'],
                            item['quantity'],
                            item['price']
                        ))
                        
                        sales_items_generated += 1
                        
                        # Update product stock (reduce inventory)
                        update_stock_query = """
                            UPDATE Products 
                            SET stock = stock - %s 
                            WHERE SKU = %s AND stock >= %s
                        """
                        self.cursor.execute(update_stock_query, (item['quantity'], item['SKU'], item['quantity']))
                
                # Commit every 500 sales to avoid memory issues
                if (i + 1) % 500 == 0:
                    self.conn.commit()
                    print(f"   Processed {i + 1}/{num_sales} sales...")
            
            self.conn.commit()
            print(f"✓ Generated {i + 1} sales transactions")
            print(f"✓ Generated {sales_items_generated} sales items")
            print(f"✓ Updated inventory for all sales")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating sales data: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False
    
    def generate_additional_sales(self, num_additional=100):
        """Generate additional recent sales to test dashboard features"""
        print(f"\n🔄 Generating {num_additional} additional recent sales...")
        
        try:
            # Generate sales from the last 7 days for better dashboard testing
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            for i in range(num_additional):
                # Random date within the last 7 days
                random_days = random.randint(0, 7)
                random_hours = random.randint(8, 20)
                random_minutes = random.randint(0, 59)
                
                sale_datetime = start_date + timedelta(
                    days=random_days,
                    hours=random_hours,
                    minutes=random_minutes
                )
                
                # Random employee and customer
                employee = random.choice(self.employees)
                customer = random.choice(self.customers)
                
                # Generate 1-3 items per sale
                num_items = random.randint(1, 3)
                
                # Get products with stock > 0
                self.cursor.execute("SELECT SKU, name, cost, price, stock FROM Products WHERE stock > 0")
                available_products = self.cursor.fetchall()
                
                if len(available_products) < num_items:
                    continue
                    
                selected_products = random.sample(available_products, num_items)
                
                sale_total = Decimal('0.00')
                sale_items = []
                
                for product in selected_products:
                    quantity = random.randint(1, min(5, int(product['stock'])))
                    
                    # Use product price
                    item_price = product['price']
                    item_total = item_price * quantity
                    sale_total += item_total
                    
                    sale_items.append({
                        'SKU': product['SKU'],
                        'quantity': quantity,
                        'price': item_price
                    })
                
                if sale_items:
                    # Insert sale
                    sale_query = """
                        INSERT INTO Sales (sale_datetime, total, employee_id, customer_id)
                        VALUES (%s, %s, %s, %s)
                    """
                    
                    self.cursor.execute(sale_query, (
                        sale_datetime,
                        sale_total,
                        employee['employee_id'],
                        customer['customer_id']
                    ))
                    
                    sale_id = self.cursor.lastrowid
                    
                    # Insert sale items
                    for item in sale_items:
                        item_query = """
                            INSERT INTO SaleItems (sale_id, SKU, quantity, price)
                            VALUES (%s, %s, %s, %s)
                        """
                        
                        self.cursor.execute(item_query, (
                            sale_id,
                            item['SKU'],
                            item['quantity'],
                            item['price']
                        ))
                        
                        # Update product stock
                        update_stock_query = """
                            UPDATE Products 
                            SET stock = stock - %s 
                            WHERE SKU = %s
                        """
                        self.cursor.execute(update_stock_query, (item['quantity'], item['SKU']))
            
            self.conn.commit()
            print(f"✓ Generated {num_additional} additional recent sales")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating additional sales: {e}")
            self.conn.rollback()
            return False
    
    def show_summary(self):
        """Show summary of generated purchase data"""
        print("\n" + "="*60)
        print("📈 PURCHASE DATA GENERATION SUMMARY")
        print("="*60)
        
        try:
            # Purchases summary
            self.cursor.execute("SELECT COUNT(*) as total_purchases FROM Purchases")
            purchases_summary = self.cursor.fetchone()
            
            self.cursor.execute("SELECT COUNT(*) as total_purchase_items FROM PurchaseItems")
            purchase_items_summary = self.cursor.fetchone()
            
            self.cursor.execute("SELECT SUM(shipping_cost) as total_shipping FROM Purchases")
            shipping_summary = self.cursor.fetchone()
            
            # Purchase items value
            self.cursor.execute("""
                SELECT SUM(quantity * unit_cost) as total_purchase_value 
                FROM PurchaseItems
            """)
            value_summary = self.cursor.fetchone()
            
            # Date ranges
            self.cursor.execute("SELECT MIN(purchase_datetime), MAX(purchase_datetime) FROM Purchases")
            purchase_date_range = self.cursor.fetchone()
            
            # Delivery status breakdown
            self.cursor.execute("""
                SELECT delivery_status, COUNT(*) as count 
                FROM Purchases 
                GROUP BY delivery_status
            """)
            delivery_status = self.cursor.fetchall()
            
            # Updated inventory summary
            self.cursor.execute("SELECT SUM(stock) as total_stock FROM Products")
            inventory_summary = self.cursor.fetchone()
            
            print(f"📦 PURCHASE DATA:")
            print(f"   • Total Purchases: {purchases_summary['total_purchases']}")
            print(f"   • Total Purchase Items: {purchase_items_summary['total_purchase_items']}")
            print(f"   • Total Purchase Value: ${value_summary['total_purchase_value']:,.2f}")
            print(f"   • Total Shipping Costs: ${shipping_summary['total_shipping']:,.2f}")
            if purchase_date_range and len(purchase_date_range) >= 2:
                print(f"   • Date Range: {purchase_date_range[0]} to {purchase_date_range[1]}")
            else:
                print(f"   • Date Range: Not available")
            
            print(f"\n📊 DELIVERY STATUS:")
            for status in delivery_status:
                print(f"   • {status['delivery_status'].title()}: {status['count']}")
            
            print(f"\n� INVENTORY UPDATE:")
            print(f"   • Total Stock After Purchases: {inventory_summary['total_stock']:,} units")
            
            print(f"\n✅ Purchase tables populated successfully!")
            print(f"✅ Inventory has been updated with received purchases")
            print(f"✅ Ready for sales data generation")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            import traceback
            traceback.print_exc()
    
    def cleanup_existing_data(self):
        """Clean up existing sales data (optional)"""
        response = input("\n⚠️  Do you want to clear existing Sales data first? (y/N): ")
        
        if response.lower() == 'y':
            try:
                print("🧹 Cleaning up existing sales data...")
                
                # Disable foreign key checks temporarily
                self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                
                # Clear existing data
                self.cursor.execute("DELETE FROM SaleItems")
                self.cursor.execute("DELETE FROM Sales")
                
                # Reset auto increment
                self.cursor.execute("ALTER TABLE Sales AUTO_INCREMENT = 1")
                self.cursor.execute("ALTER TABLE SaleItems AUTO_INCREMENT = 1")
                
                # Re-enable foreign key checks
                self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                
                self.conn.commit()
                print("✓ Existing sales data cleared")
                
                return True
                
            except Exception as e:
                print(f"❌ Error cleaning data: {e}")
                self.conn.rollback()
                return False
        
        return True
    
    def run(self):
        """Main execution method"""
        print("🚀 STORECORE SAMPLE DATA POPULATOR")
        print("="*50)
        
        # Connect to database
        if not self.connect_db():
            return False
        
        # Load existing data
        if not self.load_existing_data():
            return False
        
        # Check if we have required data
        if not self.employees or not self.customers or not self.suppliers or not self.products:
            print("❌ Missing required base data (employees, customers, suppliers, or products)")
            print("   Please ensure these tables are populated first")
            return False
        
        # Optional cleanup
        if not self.cleanup_existing_data():
            return False
        
        # Generate sample data
        print("\n🎯 Generating sales data only...")
        
        # Generate sales with inventory updates
        if not self.generate_sales_data(5000):
            return False
        
        # Show summary
        self.show_summary()
        
        # Close connection
        if self.conn:
            self.conn.close()
            print("\n✓ Database connection closed")
        
        return True

def main():
    """Main function"""
    populator = SampleDataPopulator()
    
    try:
        success = populator.run()
        
        if success:
            print("\n🎉 Sample data generation completed successfully!")
            print("   You can now test all dashboard and POS features")
        else:
            print("\n❌ Sample data generation failed")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
