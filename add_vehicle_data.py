#!/usr/bin/env python3
"""
Simple Vehicle Data Enhancement Script
"""

import os
import sys
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration with explicit credentials
DB_CONFIG = {
    'host': 'localhost',
    'database': 'car_campaigns',
    'user': 'Retailer',
    'password': 'Kolekar@3234',
    'port': '5432'
}

def get_db_connection():
    """Get database connection with explicit credentials"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def add_service_vehicle_data():
    """Add vehicles with specific service needs"""
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Service-focused vehicle data using correct column names
    vehicles = [
        # Customer 1: Warranty expiring soon
        (1, 'Maruti Suzuki', 'Swift', 2022, 'MH01AB1234', '2022-09-15', '2025-06-15', 'Full Service', '2025-12-15', 45000, '2022-09-15', '2025-09-15'),
        
        # Customer 2: High mileage needing major service  
        (2, 'Hyundai', 'i20', 2020, 'MH01CD5678', '2020-03-20', '2025-05-10', 'Oil Change', '2025-11-10', 85000, '2020-03-20', '2025-03-20'),
        
        # Customer 3: First service due (new car)
        (3, 'Tata', 'Nexon', 2025, 'MH01EF9012', '2025-02-10', None, None, '2025-08-10', 8000, '2025-02-10', '2030-02-10'),
        
        # Customer 4: Mid-life service needs
        (4, 'Honda', 'City', 2021, 'MH01GH3456', '2021-01-15', '2025-04-20', 'Basic Service', '2025-10-20', 62000, '2021-01-15', '2026-01-15'),
        
        # Customer 5: Major overhaul due
        (5, 'Toyota', 'Innova', 2018, 'MH01IJ7890', '2018-05-10', '2025-03-15', 'Oil Change', '2025-09-15', 125000, '2018-05-10', '2023-05-10'),
    ]
    
    try:
        # Clear existing vehicles
        cur.execute("DELETE FROM vehicles")
        print("Cleared existing vehicle data")
        
        # Insert new vehicles using correct column names
        for vehicle in vehicles:
            cur.execute("""
                INSERT INTO vehicles (
                    customer_id, make, model, year, vin, registration_date, 
                    last_service_date, last_service_type, next_service_due, mileage, warranty_start, warranty_end
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, vehicle)
            print(f"Added: {vehicle[1]} {vehicle[2]} ({vehicle[9]} km)")
        
        conn.commit()
        
        # Show results
        cur.execute("""
            SELECT c.name, v.make, v.model, v.mileage, v.warranty_end
            FROM vehicles v 
            JOIN customers c ON v.customer_id = c.id 
            ORDER BY v.mileage
        """)
        
        results = cur.fetchall()
        print(f"\nAdded {len(results)} vehicles:")
        for row in results:
            warranty_status = "Active" if len(row) > 4 and row[4] and row[4] > datetime.now().date() else "Expired"
            mileage = row[3] if len(row) > 3 else "N/A"
            print(f"  {row[0]}: {row[1]} {row[2]} - {mileage}km - Warranty: {warranty_status}")
        
        print("\nService Campaign Opportunities:")
        
        # Show warranty expiring soon
        cur.execute("""
            SELECT COUNT(*) FROM vehicles 
            WHERE warranty_end BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '60 days'
        """)
        expiring_count = cur.fetchone()[0]
        print(f"  - Warranty expiring (next 60 days): {expiring_count}")
        
        # Show high mileage
        cur.execute("SELECT COUNT(*) FROM vehicles WHERE mileage >= 80000")
        high_mileage_count = cur.fetchone()[0]
        print(f"  - High mileage (80k+ km): {high_mileage_count}")
        
        # Show first service due
        cur.execute("SELECT COUNT(*) FROM vehicles WHERE mileage <= 15000 AND last_service_date IS NULL")
        first_service_count = cur.fetchone()[0]
        print(f"  - First service due: {first_service_count}")
        
        # Show overdue service
        cur.execute("SELECT COUNT(*) FROM vehicles WHERE next_service_due < CURRENT_DATE")
        overdue_count = cur.fetchone()[0]
        print(f"  - Service overdue: {overdue_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Adding enhanced vehicle data for service campaigns...")
    add_service_vehicle_data()
    print("Done!")
