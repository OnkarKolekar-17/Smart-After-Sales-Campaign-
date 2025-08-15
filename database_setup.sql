-- ===============================================
-- Smart After-Sales Campaign System - Database Setup
-- Run this script in pgAdmin to create all tables and sample data
-- ===============================================

-- 1. Create the database (run this separately first)
-- CREATE DATABASE car_campaigns;

-- 2. Connect to the car_campaigns database and run the rest

-- ===============================================
-- CREATE TABLES
-- ===============================================

-- Drop tables if they exist (for fresh start)
DROP TABLE IF EXISTS campaign_metrics CASCADE;
DROP TABLE IF EXISTS campaigns CASCADE;
DROP TABLE IF EXISTS service_history CASCADE;
DROP TABLE IF EXISTS vehicles CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- Create customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    preferred_location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vehicles table
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
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
);

-- Create service_history table
CREATE TABLE service_history (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(id) ON DELETE CASCADE,
    service_date DATE NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    mileage INTEGER,
    description TEXT,
    cost DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create campaigns table
CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(36) UNIQUE NOT NULL,
    vehicle_id INTEGER REFERENCES vehicles(id) ON DELETE SET NULL,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    campaign_type VARCHAR(50) NOT NULL,
    campaign_title VARCHAR(200),
    subject_line VARCHAR(200),
    content TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    location VARCHAR(100),
    trigger_type VARCHAR(50),
    brevo_message_id VARCHAR(100)
);

-- Create campaign_metrics table
CREATE TABLE campaign_metrics (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(36) NOT NULL,
    total_sent INTEGER DEFAULT 0,
    delivered INTEGER DEFAULT 0,
    opened INTEGER DEFAULT 0,
    clicked INTEGER DEFAULT 0,
    bounced INTEGER DEFAULT 0,
    unsubscribed INTEGER DEFAULT 0,
    open_rate DECIMAL(5,4) DEFAULT 0.0,
    click_rate DECIMAL(5,4) DEFAULT 0.0,
    bounce_rate DECIMAL(5,4) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================
-- CREATE INDEXES FOR PERFORMANCE
-- ===============================================

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_location ON customers(preferred_location);
CREATE INDEX idx_vehicles_customer_id ON vehicles(customer_id);
CREATE INDEX idx_vehicles_last_service ON vehicles(last_service_date);
CREATE INDEX idx_vehicles_warranty_end ON vehicles(warranty_end);
CREATE INDEX idx_service_history_vehicle_id ON service_history(vehicle_id);
CREATE INDEX idx_service_history_date ON service_history(service_date);
CREATE INDEX idx_campaigns_customer_id ON campaigns(customer_id);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at);
CREATE INDEX idx_campaigns_status ON campaigns(status);

-- ===============================================
-- INSERT SAMPLE DATA
-- ===============================================

-- Insert sample customers
INSERT INTO customers (name, email, phone, preferred_location) VALUES
('Raj Sharma', 'raj.sharma@example.com', '+919876543210', 'Mumbai'),
('Priya Patel', 'priya.patel@example.com', '+919876543211', 'Delhi'),
('Amit Kumar', 'amit.kumar@example.com', '+919876543212', 'Bangalore'),
('Sunita Singh', 'sunita.singh@example.com', '+919876543213', 'Mumbai'),
('Vikash Gupta', 'vikash.gupta@example.com', '+919876543214', 'Chennai'),
('Neha Joshi', 'neha.joshi@example.com', '+919876543215', 'Pune'),
('Ravi Mehta', 'ravi.mehta@example.com', '+919876543216', 'Hyderabad'),
('Kavita Agarwal', 'kavita.agarwal@example.com', '+919876543217', 'Mumbai'),
('Suresh Verma', 'suresh.verma@example.com', '+919876543218', 'Kolkata'),
('Meera Jain', 'meera.jain@example.com', '+919876543219', 'Ahmedabad'),
('Anil Bansal', 'anil.bansal@example.com', '+919876543220', 'Mumbai'),
('Pooja Malhotra', 'pooja.malhotra@example.com', '+919876543221', 'Delhi'),
('Deepak Chopra', 'deepak.chopra@example.com', '+919876543222', 'Bangalore'),
('Sita Saxena', 'sita.saxena@example.com', '+919876543223', 'Mumbai'),
('Rahul Srivastava', 'rahul.srivastava@example.com', '+919876543224', 'Lucknow');

-- Insert sample vehicles
INSERT INTO vehicles (customer_id, make, model, year, vin, registration_date, last_service_date, last_service_type, next_service_due, mileage, warranty_start, warranty_end) VALUES
(1, 'Maruti Suzuki', 'Swift', 2020, 'MA1RJ65S0L0123456', '2020-03-15', '2024-06-10', 'Oil Change', '2024-12-10', 45000, '2020-03-15', '2025-03-15'),
(2, 'Hyundai', 'i20', 2019, 'MA1RJ65S0L0123457', '2019-07-20', '2024-05-15', 'AC Service', '2024-11-15', 58000, '2019-07-20', '2024-07-20'),
(3, 'Tata', 'Nexon', 2021, 'MA1RJ65S0L0123458', '2021-01-10', '2024-07-20', 'Brake Service', '2025-01-20', 32000, '2021-01-10', '2026-01-10'),
(4, 'Honda', 'City', 2022, 'MA1RJ65S0L0123459', '2022-05-12', '2024-08-01', 'Annual Service', '2025-02-01', 18000, '2022-05-12', '2027-05-12'),
(5, 'Toyota', 'Innova', 2018, 'MA1RJ65S0L0123460', '2018-09-25', '2024-03-10', 'Engine Tune-up', '2024-09-10', 78000, '2018-09-25', '2023-09-25'),
(6, 'Mahindra', 'XUV300', 2020, 'MA1RJ65S0L0123461', '2020-11-08', '2024-07-15', 'Tire Rotation', '2025-01-15', 41000, '2020-11-08', '2025-11-08'),
(7, 'Ford', 'EcoSport', 2019, 'MA1RJ65S0L0123462', '2019-12-03', '2024-04-20', 'Battery Replacement', '2024-10-20', 62000, '2019-12-03', '2024-12-03'),
(8, 'Volkswagen', 'Polo', 2021, 'MA1RJ65S0L0123463', '2021-06-18', '2024-08-05', 'Oil Change', '2025-02-05', 28000, '2021-06-18', '2026-06-18'),
(9, 'Maruti Suzuki', 'Baleno', 2020, 'MA1RJ65S0L0123464', '2020-02-14', '2024-05-25', 'AC Service', '2024-11-25', 48000, '2020-02-14', '2025-02-14'),
(10, 'Hyundai', 'Creta', 2022, 'MA1RJ65S0L0123465', '2022-08-30', '2024-07-10', 'Brake Service', '2025-01-10', 22000, '2022-08-30', '2027-08-30'),
(11, 'Tata', 'Harrier', 2021, 'MA1RJ65S0L0123466', '2021-04-22', '2024-06-30', 'Suspension Repair', '2024-12-30', 35000, '2021-04-22', '2026-04-22'),
(12, 'Honda', 'Amaze', 2019, 'MA1RJ65S0L0123467', '2019-10-15', '2024-04-05', 'Transmission Service', '2024-10-05', 67000, '2019-10-15', '2024-10-15'),
(13, 'Toyota', 'Fortuner', 2023, 'MA1RJ65S0L0123468', '2023-01-20', '2024-08-10', 'Oil Change', '2025-02-10', 12000, '2023-01-20', '2028-01-20'),
(14, 'Mahindra', 'Scorpio', 2018, 'MA1RJ65S0L0123469', '2018-06-05', '2024-03-20', 'Engine Repair', '2024-09-20', 89000, '2018-06-05', '2023-06-05'),
(15, 'Ford', 'Figo', 2020, 'MA1RJ65S0L0123470', '2020-09-12', '2024-07-25', 'Annual Service', '2025-01-25', 43000, '2020-09-12', '2025-09-12');

-- Insert sample service history
INSERT INTO service_history (vehicle_id, service_date, service_type, mileage, description, cost) VALUES
(1, '2024-06-10', 'Oil Change', 45000, 'Regular oil change with filter replacement', 2500.00),
(1, '2024-03-15', 'Brake Service', 42000, 'Brake pad replacement and fluid change', 4500.00),
(1, '2023-12-20', 'AC Service', 38000, 'AC gas refill and filter cleaning', 3200.00),
(2, '2024-05-15', 'AC Service', 58000, 'Complete AC system service and repair', 5500.00),
(2, '2024-01-10', 'Oil Change', 54000, 'Synthetic oil change with premium filter', 3000.00),
(3, '2024-07-20', 'Brake Service', 32000, 'Front brake pad replacement', 4200.00),
(3, '2024-04-15', 'Oil Change', 29000, 'Regular maintenance oil change', 2800.00),
(4, '2024-08-01', 'Annual Service', 18000, 'Comprehensive annual maintenance', 8500.00),
(5, '2024-03-10', 'Engine Tune-up', 78000, 'Complete engine service and tuning', 12000.00),
(5, '2023-11-25', 'Transmission Service', 74000, 'Automatic transmission service', 9500.00),
(6, '2024-07-15', 'Tire Rotation', 41000, 'All four tires rotated and balanced', 1500.00),
(7, '2024-04-20', 'Battery Replacement', 62000, 'New battery installation with warranty', 6500.00),
(8, '2024-08-05', 'Oil Change', 28000, 'Premium oil change service', 3200.00),
(9, '2024-05-25', 'AC Service', 48000, 'AC compressor repair and gas refill', 7800.00),
(10, '2024-07-10', 'Brake Service', 22000, 'Rear brake service and adjustment', 3800.00);

-- ===============================================
-- CREATE SOME SAMPLE CAMPAIGNS (OPTIONAL)
-- ===============================================

INSERT INTO campaigns (campaign_id, customer_id, vehicle_id, campaign_type, campaign_title, subject_line, content, status, location, trigger_type) VALUES
('campaign-001', 1, 1, 'seasonal', 'Summer AC Service Special', 'Beat the Heat - AC Service for Your Swift', 'Dear Raj, Summer is here! Ensure your Maruti Swift''s AC is running perfectly...', 'sent', 'Mumbai', 'seasonal'),
('campaign-002', 5, 5, 'lifecycle', 'Warranty Expired - Service Package', 'Important: Warranty Update for Your Innova', 'Dear Vikash, Your Toyota Innova''s warranty has expired. Here''s our special service package...', 'pending', 'Chennai', 'warranty_alert'),
('campaign-003', 7, 7, 'holiday', 'Diwali Special Offer', 'Diwali Celebration - 25% Off on Services!', 'Dear Ravi, Celebrate Diwali with special savings on your Ford EcoSport maintenance...', 'sent', 'Hyderabad', 'holiday');

-- ===============================================
-- VERIFY DATA INSERTION
-- ===============================================

-- Show summary of created data
SELECT 
    'customers' as table_name, COUNT(*) as record_count 
FROM customers
UNION ALL
SELECT 
    'vehicles' as table_name, COUNT(*) as record_count 
FROM vehicles
UNION ALL
SELECT 
    'service_history' as table_name, COUNT(*) as record_count 
FROM service_history
UNION ALL
SELECT 
    'campaigns' as table_name, COUNT(*) as record_count 
FROM campaigns;

-- Show sample data with joins
SELECT 
    c.name as customer_name,
    c.preferred_location,
    v.make,
    v.model,
    v.year,
    v.last_service_date,
    CASE 
        WHEN v.warranty_end > CURRENT_DATE THEN 'Active'
        ELSE 'Expired'
    END as warranty_status
FROM customers c
JOIN vehicles v ON c.id = v.customer_id
ORDER BY c.name
LIMIT 10;

-- ===============================================
-- SCRIPT COMPLETE
-- ===============================================
-- Your database is now ready for the Smart Campaign System!
-- You can now run: python main.py --location Mumbai
