-- Sample data for testing the Smart After-Sales Campaigns System

-- Insert sample customers
INSERT INTO customers (name, email, phone, preferred_location) VALUES
('Rajesh Kumar', 'rajesh.kumar@email.com', '+91-9876543210', 'Mumbai'),
('Priya Sharma', 'priya.sharma@email.com', '+91-9876543211', 'Delhi'),
('Amit Patel', 'amit.patel@email.com', '+91-9876543212', 'Ahmedabad'),
('Sneha Reddy', 'sneha.reddy@email.com', '+91-9876543213', 'Hyderabad'),
('Vikram Singh', 'vikram.singh@email.com', '+91-9876543214', 'Pune'),
('Kavya Nair', 'kavya.nair@email.com', '+91-9876543215', 'Bangalore'),
('Arjun Gupta', 'arjun.gupta@email.com', '+91-9876543216', 'Chennai'),
('Deepika Joshi', 'deepika.joshi@email.com', '+91-9876543217', 'Mumbai'),
('Rohit Verma', 'rohit.verma@email.com', '+91-9876543218', 'Delhi'),
('Anjali Das', 'anjali.das@email.com', '+91-9876543219', 'Kolkata'),
('Suresh Mehta', 'suresh.mehta@email.com', '+91-9876543220', 'Mumbai'),
('Neha Agarwal', 'neha.agarwal@email.com', '+91-9876543221', 'Jaipur'),
('Kiran Kumar', 'kiran.kumar@email.com', '+91-9876543222', 'Bangalore'),
('Pooja Shah', 'pooja.shah@email.com', '+91-9876543223', 'Surat'),
('Manoj Tiwari', 'manoj.tiwari@email.com', '+91-9876543224', 'Lucknow'),
('Ritu Malhotra', 'ritu.malhotra@email.com', '+91-9876543225', 'Chandigarh'),
('Sanjay Rao', 'sanjay.rao@email.com', '+91-9876543226', 'Pune'),
('Gayatri Iyer', 'gayatri.iyer@email.com', '+91-9876543227', 'Chennai'),
('Abhishek Jain', 'abhishek.jain@email.com', '+91-9876543228', 'Indore'),
('Madhuri Kulkarni', 'madhuri.kulkarni@email.com', '+91-9876543229', 'Nagpur');

-- Insert sample vehicles with varying service histories
INSERT INTO vehicles (customer_id, make, model, year, vin, registration_date, last_service_date, last_service_type, next_service_due, mileage, warranty_start, warranty_end) VALUES
-- Vehicles needing immediate attention (overdue service)
(1, 'Maruti Suzuki', 'Swift', 2020, 'MA3EJGC26G0123001', '2020-03-15', '2024-10-15', 'Regular Service', '2025-01-15', 45000, '2020-03-15', '2025-03-15'),
(2, 'Hyundai', 'i20', 2019, 'HY2EJGC26G0123002', '2019-08-10', '2024-09-20', 'Oil Change', '2024-12-20', 52000, '2019-08-10', '2024-08-10'),
(3, 'Tata', 'Nexon', 2021, 'TA4EJGC26G0123003', '2021-01-20', '2024-11-05', 'Regular Service', '2025-02-05', 38000, '2021-01-20', '2026-01-20'),

-- Vehicles with upcoming service due
(4, 'Honda', 'City', 2022, 'HO5EJGC26G0123004', '2022-06-12', '2024-12-10', 'Regular Service', '2025-03-10', 28000, '2022-06-12', '2027-06-12'),
(5, 'Mahindra', 'XUV300', 2020, 'MA6EJGC26G0123005', '2020-11-25', '2024-11-30', 'AC Service', '2025-02-28', 41000, '2020-11-25', '2025-11-25'),
(6, 'Toyota', 'Innova', 2018, 'TO7EJGC26G0123006', '2018-04-08', '2024-12-01', 'Regular Service', '2025-03-01', 78000, '2018-04-08', '2023-04-08'),

-- Vehicles with warranty expiring soon
(7, 'Kia', 'Seltos', 2022, 'KI8EJGC26G0123007', '2022-09-15', '2024-12-20', 'Regular Service', '2025-03-20', 25000, '2022-09-15', '2025-09-15'),
(8, 'Ford', 'EcoSport', 2021, 'FO9EJGC26G0123008', '2021-07-05', '2024-11-25', 'Brake Service', '2025-02-25', 35000, '2021-07-05', '2025-07-05'),
(9, 'Nissan', 'Magnite', 2023, 'NI0EJGC26G0123009', '2023-02-18', '2024-12-18', 'Regular Service', '2025-03-18', 18000, '2023-02-18', '2028-02-18'),

-- Well-maintained vehicles (regular service)
(10, 'Volkswagen', 'Polo', 2019, 'VW1EJGC26G0123010', '2019-12-03', '2024-12-15', 'Regular Service', '2025-03-15', 48000, '2019-12-03', '2024-12-03'),
(11, 'Skoda', 'Rapid', 2020, 'SK2EJGC26G0123011', '2020-05-20', '2024-12-10', 'Oil Change', '2025-03-10', 42000, '2020-05-20', '2025-05-20'),
(12, 'Renault', 'Duster', 2018, 'RE3EJGC26G0123012', '2018-10-12', '2024-11-28', 'Regular Service', '2025-02-28', 65000, '2018-10-12', '2023-10-12'),

-- Luxury vehicles
(13, 'BMW', '3 Series', 2021, 'BM4EJGC26G0123013', '2021-03-25', '2024-12-05', 'Premium Service', '2025-03-05', 32000, '2021-03-25', '2026-03-25'),
(14, 'Audi', 'A4', 2022, 'AU5EJGC26G0123014', '2022-01-15', '2024-12-12', 'Regular Service', '2025-03-12', 22000, '2022-01-15', '2027-01-15'),
(15, 'Mercedes-Benz', 'C-Class', 2020, 'ME6EJGC26G0123015', '2020-08-30', '2024-11-20', 'Premium Service', '2025-02-20', 38000, '2020-08-30', '2025-08-30'),

-- Multiple vehicles for some customers
(1, 'Honda', 'Amaze', 2019, 'HO7EJGC26G0123016', '2019-06-20', '2024-10-25', 'Regular Service', '2025-01-25', 55000, '2019-06-20', '2024-06-20'),
(5, 'Maruti Suzuki', 'Baleno', 2021, 'MA8EJGC26G0123017', '2021-09-10', '2024-12-08', 'Regular Service', '2025-03-08', 31000, '2021-09-10', '2026-09-10'),
(10, 'Tata', 'Harrier', 2022, 'TA9EJGC26G0123018', '2022-04-15', '2024-12-02', 'Regular Service', '2025-03-02', 27000, '2022-04-15', '2027-04-15'),

-- Commercial vehicles
(16, 'Mahindra', 'Bolero', 2019, 'MA0EJGC26G0123019', '2019-11-08', '2024-11-15', 'Heavy Service', '2025-02-15', 85000, '2019-11-08', '2024-11-08'),
(17, 'Tata', 'Ace', 2020, 'TA1EJGC26G0123020', '2020-02-28', '2024-12-18', 'Commercial Service', '2025-03-18', 95000, '2020-02-28', '2025-02-28');

-- Insert sample service history records
INSERT INTO service_history (vehicle_id, service_date, service_type, mileage, description, cost) VALUES
-- Recent service history
(1, '2024-10-15', 'Regular Service', 43000, 'Oil change, filter replacement, general inspection', 3500.00),
(1, '2024-07-10', 'AC Service', 41000, 'AC gas refill and cleaning', 2800.00),
(1, '2024-04-05', 'Regular Service', 38000, 'Oil change, brake inspection', 3200.00),

(2, '2024-09-20', 'Oil Change', 50000, 'Engine oil and filter change', 2200.00),
(2, '2024-06-15', 'Regular Service', 47000, 'Comprehensive service and inspection', 4500.00),
(2, '2024-03-10', 'Brake Service', 44000, 'Brake pad replacement and fluid change', 3800.00),

(3, '2024-11-05', 'Regular Service', 36000, 'Scheduled maintenance service', 3800.00),
(3, '2024-08-01', 'Tire Service', 33000, 'Tire rotation and alignment', 2500.00),
(3, '2024-05-20', 'Regular Service', 30000, 'Oil change and filter replacement', 3500.00),

-- Service history for luxury vehicles
(13, '2024-12-05', 'Premium Service', 30000, 'BMW authorized service with genuine parts', 12000.00),
(13, '2024-09-01', 'Software Update', 28000, 'ECU software update and diagnostics', 3500.00),
(13, '2024-06-10', 'Premium Service', 25000, 'Comprehensive premium service', 15000.00),

(14, '2024-12-12', 'Regular Service', 20000, 'Audi scheduled maintenance', 8500.00),
(14, '2024-09-15', 'Brake Service', 18000, 'Brake system service and inspection', 6500.00),
(14, '2024-06-20', 'Regular Service', 15000, 'First scheduled service', 7200.00),

-- Service history for commercial vehicles
(19, '2024-11-15', 'Heavy Service', 80000, 'Heavy-duty commercial vehicle service', 8500.00),
(19, '2024-08-20', 'Engine Service', 75000, 'Engine overhaul and maintenance', 15000.00),
(19, '2024-05-25', 'Regular Service', 70000, 'Routine commercial vehicle maintenance', 6500.00),

(20, '2024-12-18', 'Commercial Service', 90000, 'Commercial vehicle comprehensive service', 7200.00),
(20, '2024-09-22', 'Transmission Service', 85000, 'Transmission fluid and filter change', 4800.00),
(20, '2024-06-28', 'Regular Service', 80000, 'Scheduled maintenance', 5500.00);

-- Note: Additional service records can be added for more comprehensive testing