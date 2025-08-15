from config.database import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor

conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute('SELECT campaign_id, customer_id, subject, status, created_at FROM campaigns ORDER BY created_at DESC LIMIT 5')
campaigns = cur.fetchall()
print('Recent campaigns in database:')
for campaign in campaigns:
    print(f'- {campaign["campaign_id"]}: {campaign["subject"]} ({campaign["status"]})')
cur.close()
conn.close()
