from config.database import get_db_connection

def check_db_structure():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check customers table structure
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='customers' 
        ORDER BY ordinal_position
    """)
    
    print("CUSTOMERS TABLE COLUMNS:")
    for row in cur.fetchall():
        col_name = row[0] if isinstance(row, tuple) else row['column_name']
        data_type = row[1] if isinstance(row, tuple) else row['data_type']
        print(f"  {col_name} - {data_type}")
    
    # Check vehicles table structure
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='vehicles' 
        ORDER BY ordinal_position
    """)
    
    print("\nVEHICLES TABLE COLUMNS:")
    for row in cur.fetchall():
        col_name = row[0] if isinstance(row, tuple) else row['column_name']
        data_type = row[1] if isinstance(row, tuple) else row['data_type']
        print(f"  {col_name} - {data_type}")
    
    # Check sample data from customers
    cur.execute("SELECT * FROM customers LIMIT 2")
    results = cur.fetchall()
    if results:
        print(f"\nSAMPLE CUSTOMERS DATA:")
        print(f"Row 1: {results[0]}")
        if len(results) > 1:
            print(f"Row 2: {results[1]}")
    
    conn.close()

if __name__ == "__main__":
    check_db_structure()
