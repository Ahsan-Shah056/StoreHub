#!/usr/bin/env python3
"""
Raw Materials Data Importer
Script to import CSV data from the Datasets folder into corresponding database tables

This script imports data for:
- Wheat production data -> WheatProduction table
- Rice production data -> RiceProduction table  
- Cotton production data -> CottonProduction table
- Sugarcane production data -> SugarcaneProduction table
"""

import sys
import os
import csv
import mysql.connector
from datetime import datetime
from ..core.database import get_db, close_db

# CSV to table mapping
CSV_TABLE_MAPPING = {
    'wheat-data.csv': 'WheatProduction',
    'rice-data.csv': 'RiceProduction', 
    'cotton-data.csv': 'CottonProduction',
    'sugarcane-Data.csv': 'SugarcaneProduction'
}

# Column mapping from CSV headers to database columns
COLUMN_MAPPING = {
    'Material_id': 'material_id',
    'time_stamp': 'timestamp',
    'Expected Condition': 'expected_condition',
    'Category': 'category',
    'Original_production': 'original_production',
    'delay_percent': 'delay_percent',
    'expected_production': 'expected_production'
}

def setup_raw_materials():
    """Set up the RawMaterials table with basic materials"""
    try:
        connection, cursor = get_db()
        
        # Insert basic raw materials if they don't exist
        raw_materials = [
            (1, 'Wheat'),
            (2, 'Sugarcane'),
            (3, 'Cotton'),
            (4, 'Rice')
        ]
        
        print("Setting up RawMaterials table...")
        
        for material_id, name in raw_materials:
            # Check if material already exists
            cursor.execute("SELECT material_id FROM RawMaterials WHERE material_id = %s", (material_id,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO RawMaterials (material_id, name) VALUES (%s, %s)",
                    (material_id, name)
                )
                print(f"  ✅ Added {name} (ID: {material_id})")
            else:
                print(f"  ℹ️  {name} (ID: {material_id}) already exists")
        
        connection.commit()
        print("✅ RawMaterials setup completed")
        
    except Exception as e:
        print(f"❌ Error setting up RawMaterials: {e}")
        raise
    finally:
        close_db(connection, cursor)

def parse_timestamp(timestamp_str):
    """Parse timestamp string to MySQL datetime format"""
    try:
        # Handle the format: "2025/1/1 0:00"
        dt = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Try alternative format if needed
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"⚠️  Warning: Could not parse timestamp '{timestamp_str}', using current time")
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def import_csv_to_table(csv_file, table_name):
    """Import data from a CSV file to the corresponding database table"""
    
    csv_path = os.path.join("Datasets", csv_file)
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    try:
        connection, cursor = get_db()
        
        print(f"\n📊 Importing {csv_file} -> {table_name}")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        cursor.execute(f"DELETE FROM {table_name}")
        print(f"  🗑️  Cleared existing data from {table_name}")
        
        # Read and import CSV data
        imported_count = 0
        skipped_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Verify CSV headers
            expected_headers = list(COLUMN_MAPPING.keys())
            actual_headers = csv_reader.fieldnames
            
            print(f"  📋 Expected headers: {expected_headers}")
            print(f"  📋 Actual headers: {actual_headers}")
            
            missing_headers = set(expected_headers) - set(actual_headers)
            if missing_headers:
                print(f"  ⚠️  Warning: Missing headers: {missing_headers}")
            
            # Prepare the INSERT statement
            db_columns = [COLUMN_MAPPING[header] for header in expected_headers if header in actual_headers]
            placeholders = ', '.join(['%s'] * len(db_columns))
            insert_query = f"INSERT INTO {table_name} ({', '.join(db_columns)}) VALUES ({placeholders})"
            
            print(f"  🔧 SQL Query: {insert_query}")
            
            # Process each row
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because of header
                try:
                    # Extract values in the correct order
                    values = []
                    for header in expected_headers:
                        if header in actual_headers:
                            value = row[header].strip()
                            
                            # Special handling for timestamp
                            if header == 'time_stamp':
                                value = parse_timestamp(value)
                            # Special handling for numeric fields
                            elif header in ['Original_production', 'delay_percent', 'expected_production']:
                                try:
                                    value = float(value) if value else 0.0
                                except ValueError:
                                    print(f"  ⚠️  Warning: Invalid numeric value '{value}' in row {row_num}, using 0")
                                    value = 0.0
                            # Special handling for material_id
                            elif header == 'Material_id':
                                try:
                                    value = int(value) if value else None
                                except ValueError:
                                    print(f"  ⚠️  Warning: Invalid material_id '{value}' in row {row_num}, skipping row")
                                    skipped_count += 1
                                    continue
                            
                            values.append(value)
                    
                    # Insert the row
                    cursor.execute(insert_query, values)
                    imported_count += 1
                    
                    # Progress indicator
                    if imported_count % 50 == 0:
                        print(f"  📈 Imported {imported_count} rows...")
                
                except Exception as e:
                    print(f"  ❌ Error processing row {row_num}: {e}")
                    print(f"     Row data: {row}")
                    skipped_count += 1
                    continue
        
        # Commit the transaction
        connection.commit()
        
        print(f"  ✅ Import completed:")
        print(f"     📥 Imported: {imported_count} rows")
        print(f"     ⏭️  Skipped: {skipped_count} rows")
        print(f"     💾 Data committed to {table_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing {csv_file}: {e}")
        if 'connection' in locals():
            connection.rollback()
        return False
    finally:
        close_db(connection, cursor)

def verify_import():
    """Verify the imported data by checking row counts"""
    try:
        connection, cursor = get_db()
        
        print(f"\n📊 Verifying imported data...")
        
        for csv_file, table_name in CSV_TABLE_MAPPING.items():
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            result = cursor.fetchone()
            count = result['count'] if result else 0
            
            print(f"  📋 {table_name}: {count:,} rows")
            
            # Show sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            samples = cursor.fetchall()
            if samples:
                print(f"     Sample data from {table_name}:")
                for i, sample in enumerate(samples, 1):
                    material_id = sample.get('material_id', 'N/A')
                    timestamp = sample.get('timestamp', 'N/A')
                    category = sample.get('category', 'N/A')
                    production = sample.get('expected_production', 'N/A')
                    print(f"       {i}. Material ID: {material_id}, Date: {timestamp}, Category: {category}, Production: {production}")
        
        print(f"✅ Verification completed")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    finally:
        close_db(connection, cursor)

def main():
    """Main function to run the import process"""
    print("=" * 80)
    print("🌾 RAW MATERIALS DATA IMPORTER")
    print("=" * 80)
    
    try:
        # Step 1: Setup RawMaterials table
        setup_raw_materials()
        
        # Step 2: Import CSV data for each material
        success_count = 0
        total_files = len(CSV_TABLE_MAPPING)
        
        for csv_file, table_name in CSV_TABLE_MAPPING.items():
            if import_csv_to_table(csv_file, table_name):
                success_count += 1
        
        # Step 3: Verify imports
        verify_import()
        
        # Summary
        print(f"\n" + "=" * 80)
        print(f"📊 IMPORT SUMMARY")
        print(f"=" * 80)
        print(f"✅ Successfully imported: {success_count}/{total_files} files")
        print(f"📁 Processed files:")
        for csv_file, table_name in CSV_TABLE_MAPPING.items():
            print(f"   • {csv_file} → {table_name}")
        
        if success_count == total_files:
            print(f"\n🎉 All imports completed successfully!")
            print(f"💾 Raw materials production data is now available in the database")
        else:
            print(f"\n⚠️  Some imports failed. Please check the error messages above.")
            
    except Exception as e:
        print(f"❌ Critical error during import process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
