import psycopg2
from config.database import DB_CONFIG

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Get total customers
    cur.execute('SELECT COUNT(*) FROM customers')
    total_count = cur.fetchone()[0]
    print(f'Total customers in database: {total_count}')
    
    # Get customer distribution by preferred_location
    cur.execute('SELECT preferred_location, COUNT(*) FROM customers GROUP BY preferred_location ORDER BY preferred_location')
    location_results = cur.fetchall()
    print('\nCustomer distribution by location:')
    total_distributed = 0
    for location, count in location_results:
        print(f'  {location}: {count}')
        total_distributed += count
    
    print(f'Total distributed across locations: {total_distributed}')
    
    # Get all customer details
    cur.execute('SELECT id, name, preferred_location FROM customers ORDER BY preferred_location, name')
    all_customers = cur.fetchall()
    print(f'\nAll {len(all_customers)} customers:')
    for customer_id, name, location in all_customers:
        print(f'  ID: {customer_id}, Name: {name}, Location: {location}')
    
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
