import os
import sqlite3
from contextlib import contextmanager
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Use SQLite for local development
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'campaigns.db')

def get_db_connection():
    """Get SQLite database connection"""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create customers table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                preferred_location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create vehicles table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                vin TEXT UNIQUE,
                registration_date DATE,
                last_service_date DATE,
                last_service_type TEXT,
                next_service_due DATE,
                mileage INTEGER,
                warranty_start DATE,
                warranty_end DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')

        # Create service_history table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS service_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                service_date DATE NOT NULL,
                service_type TEXT NOT NULL,
                mileage INTEGER,
                description TEXT,
                cost DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )
        ''')

        # Create campaigns table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                customer_id INTEGER,
                campaign_type TEXT NOT NULL,
                campaign_title TEXT,
                campaign_content TEXT,
                subject_line TEXT,
                status TEXT DEFAULT 'pending',
                weather_context TEXT,
                holiday_context TEXT,
                personalization_factors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP,
                opened_at TIMESTAMP,
                clicked_at TIMESTAMP,
                conversion_at TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')

        # Create campaign_performance table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS campaign_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                metric_name TEXT NOT NULL,
                metric_value DECIMAL(10,4),
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')

        conn.commit()
        logger.info("Database initialized successfully with SQLite")
        
        # Insert sample data if tables are empty
        cur.execute("SELECT COUNT(*) FROM customers")
        if cur.fetchone()[0] == 0:
            insert_sample_data(conn)
        
    except sqlite3.Error as e:
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
            VALUES (?, ?, ?, ?)
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', vehicles_data)
        
        conn.commit()
        logger.info("Sample data inserted successfully")
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Sample data insertion error: {e}")
        raise
