
"""
Enhanced Sales Data Generator - Adds sales records without stock limitations
Now includes realistic customer distribution using newly generated customers
- 85% sales to regular customers (with names and contact info)
- 15% sales to anonymous customers
"""

import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Add the parent directory to the path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from database import get_db

def generate_unlimited_sales(num_sales=5000):
    """Generate sales data without reducing stock (for testing purposes)"""
    print(f"🚀 GENERATING {num_sales} SALES RECORDS")
    print("="*50)
    
    try:
        conn, cursor = get_db()
        print("✓ Connected to database")
        
        # Load base data
        cursor.execute("SELECT employee_id, name FROM Employees")
        employees = cursor.fetchall()
        print(f"✓ Loaded {len(employees)} employees")
        
        cursor.execute("SELECT customer_id, name, is_anonymous FROM Customers")
        customers = cursor.fetchall()
        
        # Separate anonymous and regular customers
        regular_customers = [c for c in customers if not c['is_anonymous']]
        anonymous_customers = [c for c in customers if c['is_anonymous']]
        
        print(f"✓ Loaded {len(customers)} total customers")
        print(f"  - Regular customers: {len(regular_customers)}")
        print(f"  - Anonymous customers: {len(anonymous_customers)}")
        
        cursor.execute("SELECT SKU, name, price FROM Products")
        products = cursor.fetchall()
        print(f"✓ Loaded {len(products)} products")
        
        # Check current sales count
        cursor.execute("SELECT COUNT(*) as current_count FROM Sales")
        current_count = cursor.fetchone()['current_count']
        print(f"✓ Current sales in database: {current_count}")
        
        sales_generated = 0
        items_generated = 0
        
        # Generate sales over the last 90 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        print(f"\n📊 Generating sales from {start_date.date()} to {end_date.date()}")
        
        for i in range(num_sales):
            # Random date and time
            random_days = random.randint(0, 90)
            random_hours = random.randint(7, 23)
            random_minutes = random.randint(0, 59)
            random_seconds = random.randint(0, 59)
            
            sale_datetime = start_date + timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes,
                seconds=random_seconds
            )
            
            # Random employee and customer
            employee = random.choice(employees)
            
            # 85% chance of regular customer, 15% chance of anonymous
            # This gives more realistic distribution favoring registered customers
            if regular_customers and random.random() < 0.85:
                customer = random.choice(regular_customers)
            elif anonymous_customers:
                customer = random.choice(anonymous_customers)
            else:
                customer = random.choice(customers)  # fallback
            
            # Generate 1-4 items per sale
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            sale_total = Decimal('0.00')
            sale_items = []
            
            for product in selected_products:
                # Random quantity (1-10)
                quantity = random.randint(1, 10)
                
                # Use product price with small variation
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
            
            # Insert sale
            sale_query = """
                INSERT INTO Sales (sale_datetime, total, employee_id, customer_id)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(sale_query, (
                sale_datetime,
                sale_total,
                employee['employee_id'],
                customer['customer_id']
            ))
            
            sale_id = cursor.lastrowid
            sales_generated += 1
            
            # Insert sale items (without reducing stock)
            for item in sale_items:
                item_query = """
                    INSERT INTO SaleItems (sale_id, SKU, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """
                
                cursor.execute(item_query, (
                    sale_id,
                    item['SKU'],
                    item['quantity'],
                    item['price']
                ))
                
                items_generated += 1
            
            # Show progress every 1000 sales
            if (i + 1) % 1000 == 0:
                conn.commit()
                print(f"   ✓ Generated {i + 1}/{num_sales} sales...")
        
        # Final commit
        conn.commit()
        
        # Check final count and customer distribution
        cursor.execute("SELECT COUNT(*) as final_count FROM Sales")
        final_count = cursor.fetchone()['final_count']
        
        cursor.execute("SELECT COUNT(*) as total_items FROM SaleItems")
        total_items = cursor.fetchone()['total_items']
        
        cursor.execute("SELECT SUM(total) as total_revenue FROM Sales")
        total_revenue = cursor.fetchone()['total_revenue']
        
        # Get customer distribution in recent sales
        cursor.execute("""
            SELECT 
                c.is_anonymous,
                COUNT(*) as sale_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Sales), 1) as percentage
            FROM Sales s 
            JOIN Customers c ON s.customer_id = c.customer_id 
            GROUP BY c.is_anonymous
            ORDER BY c.is_anonymous
        """)
        customer_distribution = cursor.fetchall()
        
        print("\n" + "="*60)
        print("📈 SALES GENERATION COMPLETE")
        print("="*60)
        print(f"✓ Sales Generated: {sales_generated}")
        print(f"✓ Sale Items Generated: {items_generated}")
        print(f"✓ Total Sales in DB: {final_count}")
        print(f"✓ Total Sale Items in DB: {total_items}")
        print(f"✓ Total Revenue: ${total_revenue:,.2f}")
        print(f"✓ New Sales Added: {final_count - current_count}")
        
        # Show customer distribution
        print(f"\n📊 Customer Distribution in Sales:")
        for dist in customer_distribution:
            customer_type = "Anonymous" if dist['is_anonymous'] else "Regular"
            print(f"   {customer_type}: {dist['sale_count']} sales ({dist['percentage']}%)")
        
        print("="*60)
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 UNLIMITED SALES GENERATOR")
    print("   (Does not reduce product stock)")
    print()
    
    try:
        num_sales = int(input("Enter number of sales to generate (default 5000): ") or "5000")
        
        success = generate_unlimited_sales(num_sales)
        
        if success:
            print("\n🎉 Sales generation completed successfully!")
        else:
            print("\n❌ Sales generation failed")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except ValueError:
        print("❌ Invalid number entered")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
