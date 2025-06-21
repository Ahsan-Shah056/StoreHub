
"""
Future Data Generator for DigiClimate Store Hub
================================================
Generates realistic sales data and inventory adjustments for the next 3 months

Features:
- Realistic sales patterns with seasonal trends
- Smart inventory adjustments based on sales patterns
- Proper stock management with reorder points
- Employee performance simulation
- Customer behavior patterns
- Weekend/weekday sales variations
- Time-of-day sales patterns

Usage:
    python generate_future_data.py
    
Author: DigiClimate Store Hub Team
Version: 2.0
"""

import sys
import os
import random
import math
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple

# Try to import numpy for poisson distribution, fallback to alternative if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("📝 Note: numpy not available, using alternative distribution method")

# Add the parent directory to the path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from core.database import get_db

class FutureDataGenerator:
    """Enhanced data generator for future sales and inventory management"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.employees = []
        self.customers = []
        self.regular_customers = []
        self.anonymous_customers = []
        self.products = []
        self.categories = []
        
        # Configuration
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=90)  # 3 months
        
        # Sales patterns
        self.peak_hours = [11, 12, 13, 17, 18, 19]  # Lunch and evening rush
        self.weekend_multiplier = 1.3  # 30% more sales on weekends
        self.seasonal_trend = 1.1  # 10% growth trend over 3 months
        
        # Performance optimization settings
        self.batch_size = 1000  # Process in batches for better performance
        self.commit_interval = 500  # Commit every N records
    
    def poisson_alternative(self, lam: float) -> int:
        """Alternative to numpy's poisson when numpy is not available"""
        if HAS_NUMPY:
            return int(np.random.poisson(lam))
        else:
            # Simple approximation using exponential distribution
            if lam <= 0:
                return 0
            elif lam < 30:
                # For small lambda, use inverse transform sampling
                L = math.exp(-lam)
                k = 0
                p = 1.0
                while p > L:
                    k += 1
                    p *= random.random()
                return k - 1
            else:
                # For large lambda, use normal approximation
                return max(0, int(random.normalvariate(lam, math.sqrt(lam))))
        
    def connect_database(self):
        """Establish database connection"""
        try:
            self.conn, self.cursor = get_db()
            print("✓ Connected to database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def load_base_data(self):
        """Load base data from database"""
        try:
            # Load employees
            self.cursor.execute("SELECT employee_id, name FROM Employees")
            self.employees = self.cursor.fetchall()
            print(f"✓ Loaded {len(self.employees)} employees")
            
            # Load customers
            self.cursor.execute("SELECT customer_id, name, is_anonymous FROM Customers")
            self.customers = self.cursor.fetchall()
            
            # Separate customer types
            self.regular_customers = [c for c in self.customers if not c['is_anonymous']]
            self.anonymous_customers = [c for c in self.customers if c['is_anonymous']]
            
            print(f"✓ Loaded {len(self.customers)} total customers")
            print(f"  - Regular customers: {len(self.regular_customers)}")
            print(f"  - Anonymous customers: {len(self.anonymous_customers)}")
            
            # Load products
            self.cursor.execute("""
                SELECT p.SKU, p.name, p.price, p.stock, p.cost, p.low_stock_threshold,
                       c.name as category_name, p.supplier_id
                FROM Products p 
                JOIN Categories c ON p.category_id = c.category_id
            """)
            self.products = self.cursor.fetchall()
            print(f"✓ Loaded {len(self.products)} products")
            
            # Load categories
            self.cursor.execute("SELECT category_id, name FROM Categories")
            self.categories = self.cursor.fetchall()
            print(f"✓ Loaded {len(self.categories)} categories")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading base data: {e}")
            return False
    
    def calculate_sales_probability(self, current_date: datetime) -> float:
        """Calculate sales probability based on time patterns"""
        # Base probability
        base_prob = 0.3
        
        # Hour of day effect
        hour = current_date.hour
        if hour in self.peak_hours:
            hour_multiplier = 1.5
        elif 7 <= hour <= 21:  # Regular hours
            hour_multiplier = 1.0
        else:  # Off hours
            hour_multiplier = 0.1
        
        # Day of week effect
        day_of_week = current_date.weekday()
        if day_of_week >= 5:  # Weekend
            day_multiplier = self.weekend_multiplier
        else:  # Weekday
            day_multiplier = 1.0
        
        # Seasonal trend (gradual increase over 3 months)
        days_elapsed = (current_date - self.start_date).days
        seasonal_factor = 1 + (self.seasonal_trend - 1) * (days_elapsed / 90)
        
        return base_prob * hour_multiplier * day_multiplier * seasonal_factor
    
    def get_random_customer(self) -> Dict:
        """Get a random customer with realistic distribution"""
        # 80% regular customers, 20% anonymous
        if self.regular_customers and random.random() < 0.8:
            return random.choice(self.regular_customers)
        elif self.anonymous_customers:
            return random.choice(self.anonymous_customers)
        else:
            return random.choice(self.customers)
    
    def generate_sale_items(self) -> List[Dict]:
        """Generate realistic sale items"""
        # Number of items per sale (weighted towards fewer items)
        weights = [40, 30, 20, 8, 2]  # 1-5 items
        num_items = random.choices(range(1, 6), weights=weights)[0]
        
        # Select random products
        selected_products = random.sample(self.products, min(num_items, len(self.products)))
        
        sale_items = []
        for product in selected_products:
            # Realistic quantity distribution
            if product['price'] > 50:  # Expensive items
                quantity = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
            else:  # Cheaper items
                quantity = random.choices([1, 2, 3, 4, 5], weights=[40, 25, 20, 10, 5])[0]
            
            # Price with small realistic variation
            base_price = float(product['price'])
            price_variation = random.uniform(0.98, 1.02)  # ±2% variation
            item_price = Decimal(str(round(base_price * price_variation, 2)))
            
            sale_items.append({
                'SKU': product['SKU'],
                'name': product['name'],
                'quantity': quantity,
                'price': item_price,
                'category': product['category_name']
            })
        
        return sale_items
    
    def generate_sales_data(self, target_sales: int):
        """Generate realistic sales data for the next 3 months - optimized for large datasets"""
        print(f"\n📊 Generating {target_sales:,} sales from {self.start_date.date()} to {self.end_date.date()}")
        print("="*70)
        
        sales_generated = 0
        items_generated = 0
        total_revenue = Decimal('0.00')
        
        # Pre-calculate sales distribution for better performance
        print("📈 Pre-calculating sales distribution...")
        sales_schedule = []
        
        # Instead of hour-by-hour generation, create a more efficient approach
        # Generate all sale timestamps first, then batch insert
        current_date = self.start_date
        remaining_sales = target_sales
        
        while current_date < self.end_date and remaining_sales > 0:
            # Calculate sales for this day
            daily_prob = 0
            for hour in range(24):
                check_time = current_date.replace(hour=hour)
                daily_prob += self.calculate_sales_probability(check_time)
            
            # Expected sales for this day
            expected_daily_sales = daily_prob * (remaining_sales / ((self.end_date - current_date).days + 1))
            actual_daily_sales = min(remaining_sales, max(0, self.poisson_alternative(expected_daily_sales)))
            
            # Distribute sales throughout the day
            for _ in range(actual_daily_sales):
                # Weight hours by their probability
                hour_weights = []
                hours = []
                for hour in range(24):
                    check_time = current_date.replace(hour=hour)
                    prob = self.calculate_sales_probability(check_time)
                    hours.append(hour)
                    hour_weights.append(prob)
                
                # Select weighted random hour
                if sum(hour_weights) > 0:
                    selected_hour = random.choices(hours, weights=hour_weights)[0]
                else:
                    selected_hour = random.randint(9, 17)  # Fallback to business hours
                
                # Random time within the hour
                sale_time = current_date.replace(hour=selected_hour) + timedelta(
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )
                
                sales_schedule.append(sale_time)
            
            remaining_sales -= actual_daily_sales
            current_date += timedelta(days=1)
            
            # Progress update for schedule generation
            if current_date.day % 10 == 0:
                print(f"   ✓ Scheduled sales through {current_date.date()}...")
        
        # Sort sales by time for realistic sequence
        sales_schedule.sort()
        print(f"✓ Generated schedule for {len(sales_schedule):,} sales")
        
        # Now generate actual sales data in batches
        print("\n💾 Generating sales records in batches...")
        
        for batch_start in range(0, len(sales_schedule), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(sales_schedule))
            batch_sales = sales_schedule[batch_start:batch_end]
            
            # Prepare batch data
            sales_data = []
            sale_items_data = []
            
            for sale_time in batch_sales:
                # Select employee and customer
                employee = random.choice(self.employees)
                customer = self.get_random_customer()
                
                # Generate sale items
                sale_items = self.generate_sale_items()
                
                # Calculate total
                sale_total = sum(item['price'] * item['quantity'] for item in sale_items)
                
                # Add to batch
                sales_data.append((
                    sale_time,
                    sale_total,
                    employee['employee_id'],
                    customer['customer_id']
                ))
                
                # Store items for this sale (we'll get sale_id after insert)
                sale_items_data.append(sale_items)
                total_revenue += sale_total
            
            # Batch insert sales
            sale_query = """
                INSERT INTO Sales (sale_datetime, total, employee_id, customer_id)
                VALUES (%s, %s, %s, %s)
            """
            
            self.cursor.executemany(sale_query, sales_data)
            
            # Get the sale IDs for the items
            first_sale_id = self.cursor.lastrowid - len(sales_data) + 1
            
            # Batch insert sale items
            items_batch = []
            for i, sale_items in enumerate(sale_items_data):
                sale_id = first_sale_id + i
                for item in sale_items:
                    items_batch.append((
                        sale_id,
                        item['SKU'],
                        item['quantity'],
                        item['price']
                    ))
                    items_generated += 1
            
            if items_batch:
                item_query = """
                    INSERT INTO SaleItems (sale_id, SKU, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """
                self.cursor.executemany(item_query, items_batch)
            
            sales_generated += len(batch_sales)
            
            # Commit batch and show progress
            if sales_generated % self.commit_interval == 0 or sales_generated >= len(sales_schedule):
                self.conn.commit()
                progress = (sales_generated / len(sales_schedule)) * 100
                print(f"   ✓ Processed {sales_generated:,}/{len(sales_schedule):,} sales ({progress:.1f}%)")
        
        # Final commit
        self.conn.commit()
        
        print(f"\n✅ Sales Generation Complete:")
        print(f"   Sales Generated: {sales_generated:,}")
        print(f"   Items Generated: {items_generated:,}")
        print(f"   Total Revenue: ${total_revenue:,.2f}")
        print(f"   Average Sale: ${total_revenue/sales_generated if sales_generated > 0 else 0:.2f}")
        
        return sales_generated, items_generated, total_revenue
    
    def generate_inventory_adjustments(self, num_adjustments: int):
        """Generate realistic inventory adjustments - optimized for large datasets"""
        print(f"\n📦 Generating {num_adjustments:,} inventory adjustments...")
        print("="*50)
        
        adjustments_generated = 0
        adjustment_reasons = [
            "Stock replenishment",
            "Inventory count correction",
            "Damaged goods removal",
            "Expired product disposal",
            "Theft/loss adjustment",
            "Supplier delivery",
            "Return to supplier",
            "Promotional stock",
            "Seasonal adjustment",
            "Quality control rejection"
        ]
        
        positive_reasons = [
            "Stock replenishment",
            "Inventory count correction", 
            "Supplier delivery",
            "Promotional stock",
            "Seasonal adjustment"
        ]
        
        # Process in batches for better performance
        for batch_start in range(0, num_adjustments, self.batch_size):
            batch_end = min(batch_start + self.batch_size, num_adjustments)
            batch_size_actual = batch_end - batch_start
            
            adjustments_batch = []
            stock_updates = []
            
            for i in range(batch_size_actual):
                # Random date and time within the 3-month period
                random_days = random.randint(0, 89)
                random_hours = random.randint(8, 18)  # Business hours
                random_minutes = random.randint(0, 59)
                
                adjustment_time = self.start_date + timedelta(
                    days=random_days,
                    hours=random_hours,
                    minutes=random_minutes
                )
                
                # Select random product and employee
                product = random.choice(self.products)
                employee = random.choice(self.employees)
                reason = random.choice(adjustment_reasons)
                
                # Determine quantity change based on reason
                if reason in positive_reasons:
                    # Positive adjustments (restocking)
                    if product['stock'] < product['low_stock_threshold']:
                        # Low stock - bigger restock
                        quantity_change = random.randint(20, 100)
                    else:
                        # Regular restock
                        quantity_change = random.randint(5, 50)
                else:
                    # Negative adjustments (removals)
                    max_reduction = min(product['stock'], 20)
                    if max_reduction > 0:
                        quantity_change = -random.randint(1, max_reduction)
                    else:
                        quantity_change = 0
                
                if quantity_change != 0:
                    # Add to batch
                    adjustments_batch.append((
                        product['SKU'],
                        adjustment_time,
                        quantity_change,
                        reason,
                        employee['employee_id']
                    ))
                    
                    # Update local product stock for consistency
                    new_stock = max(0, product['stock'] + quantity_change)
                    stock_updates.append((new_stock, product['SKU']))
                    product['stock'] = new_stock
                    
                    adjustments_generated += 1
            
            # Batch insert adjustments
            if adjustments_batch:
                adjustment_query = """
                    INSERT INTO InventoryAdjustments 
                    (SKU, adjustment_datetime, quantity_change, reason, employee_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                self.cursor.executemany(adjustment_query, adjustments_batch)
                
                # Batch update stock levels
                stock_query = "UPDATE Products SET stock = %s WHERE SKU = %s"
                self.cursor.executemany(stock_query, stock_updates)
            
            # Commit batch and show progress
            if adjustments_generated % 100 == 0 or batch_end >= num_adjustments:
                self.conn.commit()
                progress = (adjustments_generated / num_adjustments) * 100
                print(f"   ✓ Generated {adjustments_generated:,}/{num_adjustments:,} adjustments ({progress:.1f}%)")
        
        # Final commit
        self.conn.commit()
        
        print(f"\n✅ Inventory Adjustments Complete:")
        print(f"   Adjustments Generated: {adjustments_generated:,}")
        
        return adjustments_generated
    
    def generate_comprehensive_data(self, num_sales: int, num_adjustments: int):
        """Generate both sales and inventory data with proper coordination"""
        print("🚀 COMPREHENSIVE FUTURE DATA GENERATION")
        print("="*60)
        print(f"Target Sales: {num_sales:,}")
        print(f"Target Adjustments: {num_adjustments:,}")
        print(f"Date Range: {self.start_date.date()} to {self.end_date.date()}")
        print(f"Batch Size: {self.batch_size:,}")
        print(f"Commit Interval: {self.commit_interval:,}")
        print("="*60)
        
        # Initialize
        if not self.connect_database():
            return False
        
        if not self.load_base_data():
            return False
        
        # Validate data availability
        if not self.employees:
            print("❌ No employees found in database")
            return False
        if not self.customers:
            print("❌ No customers found in database")
            return False
        if not self.products:
            print("❌ No products found in database")
            return False
        
        try:
            # Optimize database for bulk operations
            print("⚡ Optimizing database settings for bulk operations...")
            self.cursor.execute("SET autocommit = 0")
            self.cursor.execute("SET unique_checks = 0")
            self.cursor.execute("SET foreign_key_checks = 0")
            
            start_time = datetime.now()
            
            # Generate sales data
            sales_generated, items_generated, revenue = self.generate_sales_data(num_sales)
            
            # Generate inventory adjustments
            adjustments_generated = self.generate_inventory_adjustments(num_adjustments)
            
            # Restore database settings
            print("🔧 Restoring database settings...")
            self.cursor.execute("SET foreign_key_checks = 1")
            self.cursor.execute("SET unique_checks = 1")
            self.cursor.execute("SET autocommit = 1")
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            # Summary statistics
            print("\n" + "="*60)
            print("📈 GENERATION SUMMARY")
            print("="*60)
            print(f"✓ Sales Generated: {sales_generated:,}")
            print(f"✓ Sale Items Generated: {items_generated:,}")
            print(f"✓ Inventory Adjustments: {adjustments_generated:,}")
            print(f"✓ Total Revenue: ${revenue:,.2f}")
            print(f"✓ Period: 3 months ({self.start_date.date()} to {self.end_date.date()})")
            print(f"✓ Generation Time: {duration}")
            
            # Performance metrics
            if sales_generated > 0:
                print(f"\n📊 Performance Metrics:")
                print(f"   Average Daily Sales: {sales_generated/90:.1f}")
                print(f"   Average Sale Value: ${revenue/sales_generated:.2f}")
                print(f"   Average Items per Sale: {items_generated/sales_generated:.1f}")
                print(f"   Records per Second: {(sales_generated + adjustments_generated)/duration.total_seconds():.1f}")
            
            print("="*60)
            print("🎉 DATA GENERATION COMPLETED SUCCESSFULLY!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during data generation: {e}")
            import traceback
            traceback.print_exc()
            
            # Try to restore database settings on error
            try:
                self.cursor.execute("SET foreign_key_checks = 1")
                self.cursor.execute("SET unique_checks = 1")
                self.cursor.execute("SET autocommit = 1")
                self.conn.rollback()
            except:
                pass
            
            return False
        
        finally:
            if self.conn:
                self.conn.close()

def main():
    """Main function to run the data generator"""
    print("🎯 FUTURE DATA GENERATOR - DigiClimate Store Hub v2.0")
    print("   Generates sales and inventory data for next 3 months")
    print("   Resilience meets innovation")
    print("   Optimized for large datasets with batch processing")
    print()
    
    try:
        # Get user input with better guidance
        print("📋 Configuration:")
        print("   Recommended ranges:")
        print("   • Small test: 100-1,000 sales")
        print("   • Medium load: 1,000-10,000 sales") 
        print("   • Large dataset: 10,000-100,000 sales")
        print("   • Enterprise: 100,000+ sales")
        print()
        
        num_sales = int(input("Enter number of sales to generate (default 2000): ") or "2000")
        
        # Auto-calculate reasonable number of adjustments
        suggested_adjustments = max(50, num_sales // 20)  # ~5% of sales count
        num_adjustments = int(input(f"Enter number of inventory adjustments (default {suggested_adjustments}): ") or str(suggested_adjustments))
        
        # Estimate processing time
        estimated_time = (num_sales + num_adjustments) / 1000 * 0.5  # Rough estimate
        
        print(f"\n⚡ Configuration Summary:")
        print(f"   Sales: {num_sales:,}")
        print(f"   Adjustments: {num_adjustments:,}")
        print(f"   Total Records: {num_sales + num_adjustments:,}")
        print(f"   Estimated Time: ~{estimated_time:.1f} minutes")
        
        # Warning for very large datasets
        if num_sales > 50000:
            print(f"\n⚠️  Large Dataset Warning:")
            print(f"   You're generating {num_sales:,} sales records.")
            print(f"   This may take significant time and database space.")
            print(f"   Consider starting with a smaller test batch first.")
        
        # Confirm before proceeding
        confirm = input("\nProceed with data generation? (y/N): ").lower()
        if confirm != 'y':
            print("❌ Operation cancelled")
            return
        
        # Generate data
        print(f"\n🚀 Starting generation at {datetime.now().strftime('%H:%M:%S')}...")
        generator = FutureDataGenerator()
        success = generator.generate_comprehensive_data(num_sales, num_adjustments)
        
        if success:
            print(f"\n✨ All operations completed successfully at {datetime.now().strftime('%H:%M:%S')}!")
            print("   Your database now contains 3 months of future sales and inventory data.")
            print("   You can now test the dashboard and reporting features with realistic data.")
        else:
            print("\n❌ Operation failed. Please check the error messages above.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except ValueError:
        print("❌ Invalid number entered")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
