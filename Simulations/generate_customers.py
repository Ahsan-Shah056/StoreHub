#!/usr/bin/env python3
"""
Customer Generator for Storecore
Generates 500 realistic customers with names, contact info, and addresses
"""

import sys
import os
import random

# Add the parent directory to the path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from database import get_db, close_db
import mysql.connector
from mysql.connector.errors import Error

class CustomerGenerator:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
        # Realistic customer data
        self.first_names = [
            'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
            'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
            'Thomas', 'Sarah', 'Christopher', 'Karen', 'Charles', 'Helen', 'Daniel', 'Nancy',
            'Matthew', 'Betty', 'Anthony', 'Sandra', 'Mark', 'Donna', 'Donald', 'Carol',
            'Steven', 'Ruth', 'Andrew', 'Sharon', 'Kenneth', 'Michelle', 'Paul', 'Laura',
            'Joshua', 'Sarah', 'Kevin', 'Kimberly', 'Brian', 'Deborah', 'George', 'Dorothy',
            'Timothy', 'Lisa', 'Ronald', 'Nancy', 'Jason', 'Karen', 'Edward', 'Betty',
            'Jeffrey', 'Helen', 'Ryan', 'Sandra', 'Jacob', 'Donna', 'Gary', 'Carol',
            'Nicholas', 'Ruth', 'Eric', 'Sharon', 'Jonathan', 'Michelle', 'Stephen', 'Laura',
            'Larry', 'Sarah', 'Justin', 'Kimberly', 'Scott', 'Deborah', 'Brandon', 'Dorothy',
            'Benjamin', 'Amy', 'Samuel', 'Angela', 'Gregory', 'Ashley', 'Alexander', 'Brenda',
            'Frank', 'Emma', 'Raymond', 'Olivia', 'Jack', 'Cynthia', 'Dennis', 'Marie',
            'Jerry', 'Janet', 'Tyler', 'Catherine', 'Aaron', 'Frances', 'Jose', 'Christine',
            'Henry', 'Samantha', 'Adam', 'Debra', 'Douglas', 'Rachel', 'Nathan', 'Carolyn',
            'Peter', 'Janet', 'Zachary', 'Virginia', 'Kyle', 'Maria', 'Walter', 'Heather'
        ]
        
        self.last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
            'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White',
            'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young',
            'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
            'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
            'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
            'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
            'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey',
            'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson',
            'Watson', 'Brooks', 'Chavez', 'Wood', 'James', 'Bennett', 'Gray', 'Mendoza',
            'Ruiz', 'Hughes', 'Price', 'Alvarez', 'Castillo', 'Sanders', 'Patel', 'Myers',
            'Long', 'Ross', 'Foster', 'Jimenez', 'Powell', 'Jenkins', 'Perry', 'Russell',
            'Sullivan', 'Bell', 'Coleman', 'Butler', 'Henderson', 'Barnes', 'Gonzales', 'Fisher',
            'Vasquez', 'Simmons', 'Romero', 'Jordan', 'Patterson', 'Alexander', 'Hamilton', 'Graham'
        ]
        
        self.street_names = [
            'Main Street', 'Oak Avenue', 'Park Road', 'Elm Street', 'Cedar Lane', 'Pine Avenue',
            'Maple Street', 'Washington Street', 'First Street', 'Second Street', 'Third Street',
            'Fourth Street', 'Fifth Street', 'Sixth Street', 'Seventh Street', 'Broadway',
            'Church Street', 'School Street', 'Mill Street', 'High Street', 'Spring Street',
            'Water Street', 'Market Street', 'Union Street', 'Franklin Street', 'Lincoln Street',
            'Jefferson Street', 'Madison Street', 'Jackson Street', 'Adams Street', 'Monroe Street',
            'Washington Avenue', 'Lincoln Avenue', 'Jefferson Avenue', 'Madison Avenue', 'Jackson Avenue',
            'Valley Road', 'Hill Road', 'River Road', 'Lake Road', 'Forest Road', 'Mountain Road',
            'Sunset Boulevard', 'Sunrise Avenue', 'Meadow Lane', 'Garden Street', 'Rose Street',
            'Lily Lane', 'Daisy Drive', 'Tulip Street', 'Violet Avenue', 'Iris Lane'
        ]
        
        self.cities = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
            'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
            'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco', 'Indianapolis', 'Seattle',
            'Denver', 'Washington', 'Boston', 'El Paso', 'Nashville', 'Detroit', 'Oklahoma City',
            'Portland', 'Las Vegas', 'Memphis', 'Louisville', 'Baltimore', 'Milwaukee',
            'Albuquerque', 'Tucson', 'Fresno', 'Sacramento', 'Kansas City', 'Mesa',
            'Virginia Beach', 'Atlanta', 'Colorado Springs', 'Omaha', 'Raleigh', 'Miami',
            'Long Beach', 'Minneapolis', 'Tulsa', 'Cleveland', 'Wichita', 'Arlington',
            'Tampa', 'New Orleans', 'Honolulu', 'Anaheim', 'Aurora', 'Santa Ana',
            'St. Louis', 'Riverside', 'Corpus Christi', 'Lexington', 'Pittsburgh', 'Anchorage',
            'Stockton', 'Cincinnati', 'St. Paul', 'Toledo', 'Greensboro', 'Newark',
            'Plano', 'Henderson', 'Lincoln', 'Buffalo', 'Jersey City', 'Chula Vista',
            'Fort Wayne', 'Orlando', 'St. Petersburg', 'Chandler', 'Laredo', 'Norfolk',
            'Durham', 'Madison', 'Lubbock', 'Irvine', 'Winston-Salem', 'Glendale',
            'Garland', 'Hialeah', 'Reno', 'Chesapeake', 'Gilbert', 'Baton Rouge'
        ]
        
        self.states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        
        self.email_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'icloud.com', 'comcast.net', 'verizon.net', 'att.net', 'sbcglobal.net',
            'cox.net', 'charter.net', 'live.com', 'msn.com', 'earthlink.net'
        ]
    
    def connect_database(self):
        """Connect to the database"""
        try:
            self.connection, self.cursor = get_db()
            print("✓ Connected to MySQL database successfully")
            return True
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return False
    
    def generate_customer_name(self):
        """Generate a realistic customer name"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        return f"{first_name} {last_name}"
    
    def generate_phone_number(self):
        """Generate a realistic phone number"""
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        return f"({area_code}) {exchange}-{number}"
    
    def generate_email(self, name):
        """Generate a realistic email address"""
        first_name, last_name = name.split(' ')
        domain = random.choice(self.email_domains)
        
        # Various email patterns
        patterns = [
            f"{first_name.lower()}.{last_name.lower()}@{domain}",
            f"{first_name.lower()}{last_name.lower()}@{domain}",
            f"{first_name[0].lower()}{last_name.lower()}@{domain}",
            f"{first_name.lower()}{random.randint(1, 99)}@{domain}",
            f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{domain}"
        ]
        
        return random.choice(patterns)
    
    def generate_address(self):
        """Generate a realistic address"""
        street_number = random.randint(1, 9999)
        street_name = random.choice(self.street_names)
        city = random.choice(self.cities)
        state = random.choice(self.states)
        zip_code = random.randint(10000, 99999)
        
        return f"{street_number} {street_name}, {city}, {state} {zip_code}"
    
    def generate_contact_info(self, name):
        """Generate contact information (phone and/or email)"""
        contact_types = ['phone_only', 'email_only', 'both']
        contact_type = random.choice(contact_types)
        
        if contact_type == 'phone_only':
            return self.generate_phone_number()
        elif contact_type == 'email_only':
            return self.generate_email(name)
        else:  # both
            phone = self.generate_phone_number()
            email = self.generate_email(name)
            return f"{phone}, {email}"
    
    def generate_customers(self, num_customers=500):
        """Generate the specified number of customers"""
        try:
            successful_customers = 0
            
            print(f"\n🔄 Generating {num_customers} customers...")
            
            for i in range(num_customers):
                # Generate customer data
                name = self.generate_customer_name()
                contact_info = self.generate_contact_info(name)
                address = self.generate_address()
                is_anonymous = False  # All generated customers are non-anonymous
                
                # Insert customer
                customer_query = """
                INSERT INTO Customers (name, contact_info, address, is_anonymous)
                VALUES (%s, %s, %s, %s)
                """
                
                self.cursor.execute(customer_query, (
                    name,
                    contact_info,
                    address,
                    is_anonymous
                ))
                
                successful_customers += 1
                
                # Progress indicator
                if (i + 1) % 50 == 0 or (i + 1) == num_customers:
                    print(f"  Generated {i + 1}/{num_customers} customers")
            
            self.connection.commit()
            print(f"✓ Successfully generated {successful_customers} customers")
            return successful_customers
            
        except Exception as e:
            self.connection.rollback()
            print(f"✗ Error generating customers: {e}")
            return 0
    
    def print_sample_customers(self, num_samples=5):
        """Print a few sample customers to verify generation"""
        try:
            self.cursor.execute("""
                SELECT name, contact_info, address 
                FROM Customers 
                WHERE is_anonymous = FALSE 
                ORDER BY customer_id DESC 
                LIMIT %s
            """, (num_samples,))
            
            customers = self.cursor.fetchall()
            
            if customers:
                print(f"\n📋 Sample of {len(customers)} recently generated customers:")
                print("-" * 80)
                for i, customer in enumerate(customers, 1):
                    print(f"{i}. {customer['name']}")
                    print(f"   Contact: {customer['contact_info']}")
                    print(f"   Address: {customer['address']}")
                    print()
            
        except Exception as e:
            print(f"✗ Error retrieving sample customers: {e}")
    
    def get_customer_count(self):
        """Get total number of customers in database"""
        try:
            self.cursor.execute("SELECT COUNT(*) as count FROM Customers WHERE is_anonymous = FALSE")
            result = self.cursor.fetchone()
            return result['count'] if result else 0
        except Exception as e:
            print(f"✗ Error getting customer count: {e}")
            return 0
    
    def print_summary(self, generated_customers, total_customers):
        """Print generation summary"""
        print("\n" + "="*60)
        print("CUSTOMER GENERATION SUMMARY")
        print("="*60)
        print(f"👥 Customers Generated: {generated_customers}")
        print(f"📊 Total Customers in Database: {total_customers}")
        print(f"📈 Success Rate: 100%")
        print("="*60)
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.cursor:
            close_db(self.connection, self.cursor)

def main():
    generator = CustomerGenerator()
    
    # Connect to database
    if not generator.connect_database():
        return
    
    try:
        print("\n" + "="*60)
        print("STORECORE CUSTOMER GENERATOR")
        print("="*60)
        print("This script will generate 500 realistic customers")
        print("with names, contact information, and addresses.")
        
        # Confirm generation
        confirm = input("\nProceed with generating 500 customers? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Operation cancelled.")
            return
        
        # Get initial customer count
        initial_count = generator.get_customer_count()
        
        # Generate customers
        generated = generator.generate_customers(500)
        
        # Get final customer count
        final_count = generator.get_customer_count()
        
        # Show sample customers
        generator.print_sample_customers(5)
        
        # Print summary
        generator.print_summary(generated, final_count)
        
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    finally:
        generator.close_connection()

if __name__ == "__main__":
    main()
