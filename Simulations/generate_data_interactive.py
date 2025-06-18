#!/usr/bin/env python3
"""
Interactive Data Generator for DigiClimate Store Hub
Generates user-defined numbers of purchases, purchase items, and inventory adjustments
"""

import random
import datetime
from decimal import Decimal
from database import get_db, close_db
import mysql.connector
from mysql.connector.errors import Error

class DataGenerator:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.suppliers = []
        self.products = []
        self.employees = []
        
    def connect_database(self):
        """Connect to the database"""
        try:
            self.connection, self.cursor = get_db()
            print("✓ Connected to MySQL database successfully")
            return True
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return False
    
    def load_reference_data(self):
        """Load existing suppliers, products, and employees for reference"""
        try:
            # Load suppliers
            self.cursor.execute("SELECT supplier_id, name FROM Suppliers")
            self.suppliers = self.cursor.fetchall()
            
            # Load products
            self.cursor.execute("SELECT SKU, name, price, cost FROM Products")
            self.products = self.cursor.fetchall()
            
            # Load employees
            self.cursor.execute("SELECT employee_id, name FROM Employees")
            self.employees = self.cursor.fetchall()
            
            print(f"✓ Loaded {len(self.suppliers)} suppliers, {len(self.products)} products, {len(self.employees)} employees")
            
            if not self.suppliers or not self.products or not self.employees:
                print("⚠ Warning: Some reference data is missing. Please ensure you have suppliers, products, and employees in your database.")
                return False
            return True
            
        except Exception as e:
            print(f"✗ Error loading reference data: {e}")
            return False
    
    def get_user_input(self):
        """Get user input for number of records to generate"""
        try:
            print("\n" + "="*50)
            print("DIGICLIMATE STORE HUB DATA GENERATOR")
            print("="*50)
            
            # Get purchases and purchase items count
            print("\n📦 PURCHASES & PURCHASE ITEMS")
            print("-" * 30)
            num_purchases = int(input("Enter number of purchase orders to generate: "))
            
            if num_purchases > 0:
                min_items = int(input("Minimum items per purchase order (default 1): ") or "1")
                max_items = int(input("Maximum items per purchase order (default 5): ") or "5")
            else:
                min_items = max_items = 0
            
            # Get inventory adjustments count
            print("\n📋 INVENTORY ADJUSTMENTS")
            print("-" * 30)
            num_adjustments = int(input("Enter number of inventory adjustments to generate: "))
            
            return {
                'purchases': num_purchases,
                'min_items_per_purchase': min_items,
                'max_items_per_purchase': max_items,
                'adjustments': num_adjustments
            }
            
        except ValueError:
            print("✗ Please enter valid numbers")
            return None
        except KeyboardInterrupt:
            print("\n\n✗ Operation cancelled by user")
            return None
    
    def generate_purchases_and_items(self, num_purchases, min_items, max_items):
        """Generate purchases and their items"""
        try:
            total_items = 0
            successful_purchases = 0
            
            print(f"\n🔄 Generating {num_purchases} purchase orders...")
            
            for i in range(num_purchases):
                # Random supplier
                supplier = random.choice(self.suppliers)
                
                # Random purchase datetime (last 90 days)
                days_ago = random.randint(0, 90)
                purchase_datetime = datetime.datetime.now() - datetime.timedelta(days=days_ago)
                
                # Random shipping cost
                shipping_cost = round(random.uniform(5.0, 50.0), 2)
                
                # Random delivery status (80% received, 20% pending)
                delivery_status = 'received' if random.random() < 0.8 else 'pending'
                
                # Insert purchase
                purchase_query = """
                INSERT INTO Purchases (supplier_id, purchase_datetime, shipping_cost, delivery_status)
                VALUES (%s, %s, %s, %s)
                """
                self.cursor.execute(purchase_query, (
                    supplier['supplier_id'],
                    purchase_datetime,
                    shipping_cost,
                    delivery_status
                ))
                
                purchase_id = self.cursor.lastrowid
                
                # Generate purchase items
                num_items = random.randint(min_items, max_items)
                selected_products = random.sample(self.products, min(num_items, len(self.products)))
                
                for product in selected_products:
                    quantity = random.randint(10, 100)
                    
                    # Unit cost (slightly lower than selling price)
                    base_cost = float(product['cost']) if product['cost'] else float(product['price']) * 0.7
                    unit_cost = round(random.uniform(base_cost * 0.8, base_cost * 1.2), 2)
                    
                    # Insert purchase item
                    item_query = """
                    INSERT INTO PurchaseItems (purchase_id, SKU, quantity, unit_cost)
                    VALUES (%s, %s, %s, %s)
                    """
                    self.cursor.execute(item_query, (
                        purchase_id,
                        product['SKU'],
                        quantity,
                        unit_cost
                    ))
                    
                    # Update inventory if purchase is received
                    if delivery_status == 'received':
                        update_query = """
                        UPDATE Products SET stock = stock + %s WHERE SKU = %s
                        """
                        self.cursor.execute(update_query, (quantity, product['SKU']))
                    
                    total_items += 1
                
                successful_purchases += 1
                
                # Progress indicator
                if (i + 1) % 100 == 0 or (i + 1) == num_purchases:
                    print(f"  Generated {i + 1}/{num_purchases} purchases ({total_items} items)")
            
            self.connection.commit()
            print(f"✓ Successfully generated {successful_purchases} purchases with {total_items} items")
            return successful_purchases, total_items
            
        except Exception as e:
            self.connection.rollback()
            print(f"✗ Error generating purchases: {e}")
            return 0, 0
    
    def generate_inventory_adjustments(self, num_adjustments):
        """Generate inventory adjustments"""
        try:
            successful_adjustments = 0
            adjustment_reasons = [
                'Stock count correction',
                'Damaged goods',
                'Expired products',
                'Theft/Loss',
                'Supplier error correction',
                'Quality control rejection',
                'Return to supplier',
                'Found inventory'
            ]
            
            print(f"\n🔄 Generating {num_adjustments} inventory adjustments...")
            
            for i in range(num_adjustments):
                # Random product
                product = random.choice(self.products)
                
                # Random employee
                employee = random.choice(self.employees)
                
                # Random adjustment datetime (last 30 days)
                days_ago = random.randint(0, 30)
                adjustment_datetime = datetime.datetime.now() - datetime.timedelta(days=days_ago)
                
                # Random quantity change (-50 to +20, more negative adjustments)
                if random.random() < 0.7:  # 70% chance of negative adjustment
                    quantity_change = random.randint(-50, -1)
                else:  # 30% chance of positive adjustment
                    quantity_change = random.randint(1, 20)
                
                # Random reason
                reason = random.choice(adjustment_reasons)
                
                # Get current stock
                self.cursor.execute("SELECT stock FROM Products WHERE SKU = %s", (product['SKU'],))
                current_stock = self.cursor.fetchone()['stock']
                
                # Ensure we don't go below 0 stock
                if current_stock + quantity_change < 0:
                    quantity_change = -current_stock
                
                # Skip if no change needed
                if quantity_change == 0:
                    continue
                
                # Insert inventory adjustment
                adjustment_query = """
                INSERT INTO InventoryAdjustments (SKU, adjustment_datetime, quantity_change, reason, employee_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                self.cursor.execute(adjustment_query, (
                    product['SKU'],
                    adjustment_datetime,
                    quantity_change,
                    reason,
                    employee['employee_id']
                ))
                
                # Update product stock
                update_query = """
                UPDATE Products SET stock = stock + %s WHERE SKU = %s
                """
                self.cursor.execute(update_query, (quantity_change, product['SKU']))
                
                successful_adjustments += 1
                
                # Progress indicator
                if (i + 1) % 100 == 0 or (i + 1) == num_adjustments:
                    print(f"  Generated {i + 1}/{num_adjustments} adjustments")
            
            self.connection.commit()
            print(f"✓ Successfully generated {successful_adjustments} inventory adjustments")
            return successful_adjustments
            
        except Exception as e:
            self.connection.rollback()
            print(f"✗ Error generating inventory adjustments: {e}")
            return 0
    
    def print_summary(self, purchases, items, adjustments):
        """Print generation summary"""
        print("\n" + "="*50)
        print("GENERATION SUMMARY")
        print("="*50)
        print(f"📦 Purchase Orders: {purchases}")
        print(f"📋 Purchase Items: {items}")
        print(f"🔧 Inventory Adjustments: {adjustments}")
        print(f"📊 Total Records: {purchases + items + adjustments}")
        print("="*50)
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.cursor:
            close_db(self.connection, self.cursor)

def main():
    generator = DataGenerator()
    
    # Connect to database
    if not generator.connect_database():
        return
    
    try:
        # Load reference data
        if not generator.load_reference_data():
            return
        
        # Get user input
        config = generator.get_user_input()
        if not config:
            return
        
        # Generate data
        purchases = items = adjustments = 0
        
        # Generate purchases and items
        if config['purchases'] > 0:
            purchases, items = generator.generate_purchases_and_items(
                config['purchases'],
                config['min_items_per_purchase'],
                config['max_items_per_purchase']
            )
        
        # Generate inventory adjustments
        if config['adjustments'] > 0:
            adjustments = generator.generate_inventory_adjustments(config['adjustments'])
        
        # Print summary
        generator.print_summary(purchases, items, adjustments)
        
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    finally:
        generator.close_connection()

if __name__ == "__main__":
    main()
