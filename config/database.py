import os
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'car_campaigns'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),  # Default password
    'port': os.getenv('DB_PORT', '5432')
}

# SQLAlchemy setup
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db_connection():
    """Get PostgreSQL database connection with RealDictCursor"""
    try:
        conn = psycopg2.connect(
            **DB_CONFIG,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

@contextmanager
def get_db_session():
    """Context manager for SQLAlchemy sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create customers table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                preferred_location VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create vehicles table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(id),
                make VARCHAR(50) NOT NULL,
                model VARCHAR(50) NOT NULL,
                year INTEGER NOT NULL,
                vin VARCHAR(17) UNIQUE,
                registration_date DATE,
                last_service_date DATE,
                last_service_type VARCHAR(50),
                next_service_due DATE,
                mileage INTEGER,
                warranty_start DATE,
                warranty_end DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create service_history table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS service_history (
                id SERIAL PRIMARY KEY,
                vehicle_id INTEGER REFERENCES vehicles(id),
                service_date DATE NOT NULL,
                service_type VARCHAR(50) NOT NULL,
                mileage INTEGER,
                description TEXT,
                cost DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create campaigns table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id SERIAL PRIMARY KEY,
                vehicle_id INTEGER REFERENCES vehicles(id),
                customer_id INTEGER REFERENCES customers(id),
                campaign_type VARCHAR(50) NOT NULL,
                campaign_title VARCHAR(200),
                campaign_content TEXT,
                subject_line VARCHAR(200),
                status VARCHAR(20) DEFAULT 'pending',
                weather_context TEXT,
                holiday_context TEXT,
                personalization_factors JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP,
                opened_at TIMESTAMP,
                clicked_at TIMESTAMP,
                conversion_at TIMESTAMP
            )
        ''')

        # Create campaign_performance table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS campaign_performance (
                id SERIAL PRIMARY KEY,
                campaign_id INTEGER REFERENCES campaigns(id),
                metric_name VARCHAR(50) NOT NULL,
                metric_value DECIMAL(10,4),
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        logger.info("Database initialized successfully")
        
        # Insert sample data if tables are empty
        cur.execute("SELECT COUNT(*) FROM customers")
        count_result = cur.fetchone()
        customer_count = count_result['count'] if isinstance(count_result, dict) else count_result[0]
        
        if customer_count == 0:
            insert_sample_data(conn)
        
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def insert_sample_data(conn):
    """Insert sample data for testing"""
    cur = conn.cursor()
    
    try:
        # Insert sample customers
        customers_data = [
            ('Rajesh Kumar', 'onkar.kolekar23@vit.edu', '+91-9876543210', 'Mumbai'),  # Use real email
            ('Priya Sharma', 'priya.sharma@email.com', '+91-9876543211', 'Delhi'),
            ('Amit Patel', 'amit.patel@email.com', '+91-9876543212', 'Mumbai'),
            ('Sneha Reddy', 'sneha.reddy@email.com', '+91-9876543213', 'Mumbai'),
        ]
        
        cur.executemany('''
            INSERT INTO customers (name, email, phone, preferred_location) 
            VALUES (%s, %s, %s, %s)
        ''', customers_data)
        
        # Insert sample vehicles
        vehicles_data = [
            (1, 'Maruti Suzuki', 'Swift', 2020, 'MA3EJGC26G0123001', '2020-03-15', '2024-10-15', 'Regular Service', '2025-01-15', 45000, '2020-03-15', '2025-03-15'),
            (2, 'Hyundai', 'i20', 2019, 'HY2EJGC26G0123002', '2019-08-10', '2024-09-20', 'Oil Change', '2024-12-20', 52000, '2019-08-10', '2024-08-10'),
            (3, 'Tata', 'Nexon', 2021, 'TA4EJGC26G0123003', '2021-01-20', '2024-11-05', 'Regular Service', '2025-02-05', 38000, '2021-01-20', '2026-01-20'),
            (4, 'Honda', 'City', 2022, 'HO5EJGC26G0123004', '2022-06-12', '2024-12-10', 'Regular Service', '2025-03-10', 28000, '2022-06-12', '2027-06-12'),
        ]
        
        cur.executemany('''
            INSERT INTO vehicles (customer_id, make, model, year, vin, registration_date, last_service_date, 
                                last_service_type, next_service_due, mileage, warranty_start, warranty_end) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', vehicles_data)
        
        conn.commit()
        logger.info("Sample data inserted successfully")
        
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Sample data insertion error: {e}")
        raise