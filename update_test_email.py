"""
Update test customer email for real email testing
"""
from config.database import get_db_connection
import psycopg2

def update_test_email():
    """Update one test customer to use real email for testing"""
    
    print("🔄 Updating test customer email...")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Update one Mumbai customer to use your real email
        update_query = """
        UPDATE customers 
        SET email = %s 
        WHERE city = 'Mumbai' 
        AND name = 'Neha Joshi'
        RETURNING customer_id, name, email, city;
        """
        
        cur.execute(update_query, ('onkar.kolekar23@vit.edu',))
        updated_customer = cur.fetchone()
        
        if updated_customer:
            print(f"✅ SUCCESS! Updated customer:")
            print(f"   ID: {updated_customer[0]}")
            print(f"   Name: {updated_customer[1]}")
            print(f"   Email: {updated_customer[2]}")
            print(f"   City: {updated_customer[3]}")
        else:
            print("❌ No customer found to update")
        
        # Commit changes
        conn.commit()
        
        # Verify the update
        print("\n🔍 Verifying Mumbai customers:")
        cur.execute("SELECT customer_id, name, email FROM customers WHERE city = 'Mumbai'")
        mumbai_customers = cur.fetchall()
        
        for customer in mumbai_customers:
            print(f"   - {customer[1]}: {customer[2]}")
        
        cur.close()
        conn.close()
        
        print(f"\n🎯 Ready for testing!")
        print(f"When you run the campaign, 'Neha Joshi' will receive emails at: onkar.kolekar23@vit.edu")
        
    except Exception as e:
        print(f"❌ Error updating email: {e}")

if __name__ == "__main__":
    update_test_email()
