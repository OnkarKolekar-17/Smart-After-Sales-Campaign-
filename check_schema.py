import psycopg2
from psycopg2.extras import RealDictCursor

# Check vehicle table structure
conn = psycopg2.connect(
    host='localhost',
    database='car_campaigns', 
    user='Retailer',
    password='Kolekar@3234',
    cursor_factory=RealDictCursor
)
cur = conn.cursor()

# Show table structure
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'vehicles' 
    ORDER BY ordinal_position;
""")

columns = cur.fetchall()
print("Vehicle table structure:")
for col in columns:
    print(f"  {col['column_name']}: {col['data_type']}")

# Show sample data
cur.execute("SELECT * FROM vehicles LIMIT 1;")
sample = cur.fetchone()
if sample:
    print("\nSample vehicle record:")
    for key, value in sample.items():
        print(f"  {key}: {value}")
else:
    print("\nNo vehicles found in table")

cur.close()
conn.close()
