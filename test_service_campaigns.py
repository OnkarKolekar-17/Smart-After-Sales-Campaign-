#!/usr/bin/env python3
"""
Enhanced Vehicle Service Campaign Test

This script adds diverse vehicle data to test different service-based campaigns:
- Warranty expiring vehicles
- High mileage service needs
- Ownership milestone campaigns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from config.database import get_db_connection, init_db

def add_enhanced_vehicle_data():
    """Add comprehensive vehicle data for testing service campaigns"""
    
    init_db()  # Ensure database is initialized
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Enhanced vehicle data for service-based campaigns
    enhanced_vehicles = [
        # Warranty expiring soon (within 30 days)
        {
            'customer_id': 1,
            'make': 'Maruti Suzuki',
            'model': 'Swift',
            'year': 2022,
            'purchase_date': '2022-09-15',  # ~3 years old, warranty ending
            'current_mileage': 45000,
            'last_service_date': '2025-06-15',
            'warranty_expiry_date': '2025-09-15',  # Expiring in ~1 month
            'vehicle_id': 'MH01AB1234'
        },
        # High mileage vehicle needing major service
        {
            'customer_id': 2,
            'make': 'Hyundai',
            'model': 'i20',
            'year': 2020,
            'purchase_date': '2020-03-20',  # 5+ years old
            'current_mileage': 85000,  # High mileage - needs major service
            'last_service_date': '2025-05-10',
            'warranty_expiry_date': '2025-03-20',  # Already expired
            'vehicle_id': 'MH01CD5678'
        },
        # New vehicle - first service due
        {
            'customer_id': 3,
            'make': 'Tata',
            'model': 'Nexon',
            'year': 2025,
            'purchase_date': '2025-02-10',  # 6 months old
            'current_mileage': 8000,  # Approaching first service
            'last_service_date': None,  # Never serviced
            'warranty_expiry_date': '2030-02-10',  # Long warranty
            'vehicle_id': 'MH01EF9012'
        },
        # Mid-life vehicle - brake/battery service
        {
            'customer_id': 4,
            'make': 'Honda',
            'model': 'City',
            'year': 2021,
            'purchase_date': '2021-01-15',  # 4+ years old
            'current_mileage': 62000,  # Mid-high mileage
            'last_service_date': '2025-04-20',
            'warranty_expiry_date': '2026-01-15',  # Still under warranty
            'vehicle_id': 'MH01GH3456'
        },
        # Very high mileage - timing belt/major overhaul
        {
            'customer_id': 5,
            'make': 'Toyota',
            'model': 'Innova',
            'year': 2018,
            'purchase_date': '2018-05-10',  # 7+ years old
            'current_mileage': 125000,  # Very high mileage
            'last_service_date': '2025-03-15',
            'warranty_expiry_date': '2023-05-10',  # Long expired
            'vehicle_id': 'MH01IJ7890'
        }
    ]
    
    print("🔧 Adding enhanced vehicle data for service campaigns...")
    
    try:
        # Clear existing vehicle data
        cur.execute("DELETE FROM vehicles")
        print("   Cleared existing vehicle data")
        
        # Insert enhanced vehicle data
        for vehicle in enhanced_vehicles:
            cur.execute("""
                INSERT INTO vehicles (
                    customer_id, make, model, year, purchase_date, 
                    current_mileage, last_service_date, warranty_expiry_date, vehicle_id
                ) VALUES (
                    %(customer_id)s, %(make)s, %(model)s, %(year)s, %(purchase_date)s,
                    %(current_mileage)s, %(last_service_date)s, %(warranty_expiry_date)s, %(vehicle_id)s
                )
            """, vehicle)
            print(f"   ✅ Added {vehicle['make']} {vehicle['model']} ({vehicle['current_mileage']} km)")
        
        conn.commit()
        print(f"\n🎯 Successfully added {len(enhanced_vehicles)} vehicles with diverse service needs:")
        print("   • Warranty expiring (Swift - 45k km)")
        print("   • High mileage service (i20 - 85k km)")
        print("   • First service due (Nexon - 8k km)")
        print("   • Mid-life service (City - 62k km)")
        print("   • Major overhaul needed (Innova - 125k km)")
        
        # Verify the data
        cur.execute("SELECT COUNT(*) FROM vehicles")
        count = cur.fetchone()[0]
        print(f"\n📊 Total vehicles in database: {count}")
        
        # Show service campaign opportunities
        print("\n🔍 Service Campaign Opportunities:")
        
        # Warranty expiring
        cur.execute("""
            SELECT c.name, v.make, v.model, v.warranty_expiry_date 
            FROM vehicles v 
            JOIN customers c ON v.customer_id = c.id 
            WHERE v.warranty_expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '60 days'
        """)
        expiring_warranty = cur.fetchall()
        if expiring_warranty:
            print(f"   • Warranty Expiring Soon: {len(expiring_warranty)} customers")
            for row in expiring_warranty:
                print(f"     - {row[0]}: {row[1]} {row[2]} (expires {row[3]})")
        
        # High mileage service
        cur.execute("""
            SELECT c.name, v.make, v.model, v.current_mileage 
            FROM vehicles v 
            JOIN customers c ON v.customer_id = c.id 
            WHERE v.current_mileage >= 80000
        """)
        high_mileage = cur.fetchall()
        if high_mileage:
            print(f"   • High Mileage Service: {len(high_mileage)} customers")
            for row in high_mileage:
                print(f"     - {row[0]}: {row[1]} {row[2]} ({row[3]} km)")
        
        # First service due
        cur.execute("""
            SELECT c.name, v.make, v.model, v.current_mileage 
            FROM vehicles v 
            JOIN customers c ON v.customer_id = c.id 
            WHERE v.current_mileage BETWEEN 8000 AND 15000 AND v.last_service_date IS NULL
        """)
        first_service = cur.fetchall()
        if first_service:
            print(f"   • First Service Due: {len(first_service)} customers")
            for row in first_service:
                print(f"     - {row[0]}: {row[1]} {row[2]} ({row[3]} km)")
        
    except Exception as e:
        print(f"❌ Error adding vehicle data: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def test_service_campaigns():
    """Test different service-based campaign triggers"""
    
    print("\n🚀 Testing Service-Based Campaigns")
    print("=" * 50)
    
    import subprocess
    import time
    
    test_scenarios = [
        {
            'trigger': 'lifecycle',
            'description': 'Vehicle Lifecycle Service Campaigns'
        },
        {
            'trigger': 'maintenance',
            'description': 'Maintenance-Based Campaigns'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🔧 Testing: {scenario['description']}")
        print(f"   Trigger: {scenario['trigger']}")
        
        try:
            cmd = [
                'python', 'main.py', 
                '--mode', 'single',
                '--location', 'Mumbai',
                '--trigger', scenario['trigger']
            ]
            
            print(f"   Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("   ✅ Campaign executed successfully!")
                # Look for key indicators in output
                if 'Campaigns Created:' in result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Campaigns Created:' in line or 'Campaigns Sent:' in line:
                            print(f"   📊 {line.strip()}")
                        elif 'Campaign title:' in line:
                            print(f"   📧 {line.strip()}")
            else:
                print(f"   ❌ Campaign failed: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Campaign timed out (>5 minutes)")
        except Exception as e:
            print(f"   ❌ Error running campaign: {e}")
        
        time.sleep(2)  # Brief pause between tests

if __name__ == "__main__":
    print("🔧 Enhanced Vehicle Service Campaign Test")
    print("=" * 50)
    
    # Add enhanced vehicle data
    add_enhanced_vehicle_data()
    
    # Test service-based campaigns
    test_service_campaigns()
    
    print("\n✅ Test completed!")
