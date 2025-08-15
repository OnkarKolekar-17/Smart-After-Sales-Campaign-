#!/usr/bin/env python3
"""
Database connection test script
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection with different credential combinations"""
    
    configs = [
        # Your current config
        {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'car_campaigns'),
            'user': os.getenv('DB_USER', 'Retailer'),
            'password': os.getenv('DB_PASSWORD', 'Kolekar@3234'),
            'port': os.getenv('DB_PORT', '5432')
        },
        # Default postgres user
        {
            'host': 'localhost',
            'database': 'car_campaigns',
            'user': 'postgres',
            'password': 'Kolekar@3234',
            'port': '5432'
        }
    ]
    
    for i, config in enumerate(configs):
        print(f"\n🧪 Testing configuration {i+1}:")
        print(f"   User: {config['user']}")
        print(f"   Database: {config['database']}")
        print(f"   Host: {config['host']}:{config['port']}")
        
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT COUNT(*) FROM customers;")
            count = cursor.fetchone()[0]
            
            print(f"   ✅ Connection successful!")
            print(f"   📊 Found {count} customers in database")
            
            # Test sample query
            cursor.execute("SELECT name, preferred_location FROM customers LIMIT 3;")
            customers = cursor.fetchall()
            print(f"   👥 Sample customers:")
            for customer in customers:
                print(f"      - {customer[0]} ({customer[1]})")
                
            cursor.close()
            conn.close()
            
            print(f"   🎉 Database is ready to use!")
            return True
            
        except psycopg2.Error as e:
            print(f"   ❌ Connection failed: {e}")
            continue
    
    print("\n❌ All connection attempts failed.")
    print("\n🔧 Please check:")
    print("   1. PostgreSQL is running")
    print("   2. Database 'car_campaigns' exists")
    print("   3. User credentials are correct")
    print("   4. You ran the database_setup.sql script")
    
    return False

if __name__ == "__main__":
    print("🗄️  Database Connection Test")
    print("="*50)
    test_connection()
