#!/usr/bin/env python3
"""
Sample data insertion script for Smart After-Sales Campaign System
This script populates the database with realistic test data
"""

import sys
import os
from datetime import datetime, date, timedelta
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_service import DatabaseService
from utils.helpers import clean_email, clean_phone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SampleDataGenerator:
    """Generates and inserts sample data for testing"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        
        # Sample data sets
        self.first_names = [
            'Raj', 'Priya', 'Amit', 'Sunita', 'Vikash', 'Neha', 'Ravi', 'Kavita',
            'Suresh', 'Meera', 'Anil', 'Pooja', 'Deepak', 'Sita', 'Rahul', 'Geeta',
            'Vijay', 'Asha', 'Mohan', 'Lakshmi', 'Kiran', 'Usha', 'Ajay', 'Rekha'
        ]
        
        self.last_names = [
            'Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Shah', 'Mehta',
            'Agarwal', 'Verma', 'Jain', 'Bansal', 'Malhotra', 'Chopra', 'Saxena',
            'Srivastava', 'Tiwari', 'Mishra', 'Pandey', 'Yadav', 'Reddy', 'Nair'
        ]
        
        self.cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata',
            'Pune', 'Ahmedabad', 'Surat', 'Jaipur', 'Lucknow', 'Kanpur',
            'Nagpur', 'Indore', 'Bhopal', 'Visakhapatnam', 'Patna', 'Vadodara'
        ]
        
        self.car_makes = [
            'Maruti Suzuki', 'Hyundai', 'Tata', 'Mahindra', 'Honda', 'Toyota',
            'Ford', 'Volkswagen', 'Skoda', 'Nissan', 'Renault', 'Kia'
        ]
        
        self.car_models = {
            'Maruti Suzuki': ['Swift', 'Baleno', 'Alto', 'Wagon R', 'Dzire', 'Vitara Brezza', 'Ertiga'],
            'Hyundai': ['i20', 'Creta', 'Venue', 'Verna', 'Grand i10', 'Elantra', 'Tucson'],
            'Tata': ['Nexon', 'Harrier', 'Tiago', 'Tigor', 'Altroz', 'Safari', 'Punch'],
            'Mahindra': ['XUV300', 'XUV500', 'Scorpio', 'Thar', 'Bolero', 'KUV100'],
            'Honda': ['City', 'Amaze', 'Jazz', 'WR-V', 'Civic', 'CR-V'],
            'Toyota': ['Innova', 'Fortuner', 'Camry', 'Yaris', 'Urban Cruiser', 'Glanza'],
            'Ford': ['EcoSport', 'Figo', 'Aspire', 'Endeavour', 'Freestyle'],
            'Volkswagen': ['Polo', 'Vento', 'Tiguan', 'T-Roc'],
            'Skoda': ['Rapid', 'Octavia', 'Superb', 'Kushaq'],
            'Nissan': ['Magnite', 'Kicks', 'GT-R', 'X-Trail'],
            'Renault': ['Kwid', 'Duster', 'Triber', 'Kiger'],
            'Kia': ['Seltos', 'Sonet', 'Carnival', 'Carens']
        }
        
        self.service_types = [
            'Oil Change', 'Brake Service', 'AC Service', 'Battery Replacement',
            'Tire Rotation', 'Engine Tune-up', 'Transmission Service', 
            'Suspension Repair', 'Electrical Repair', 'Body Work',
            'Annual Service', 'Preventive Maintenance', 'Emergency Repair'
        ]
    
    def generate_customers(self, count: int = 100) -> list:
        """Generate sample customer data"""
        customers = []
        
        for i in range(count):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            
            customer = {
                'name': f"{first_name} {last_name}",
                'email': f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com",
                'phone': f"+91{random.randint(6000000000, 9999999999)}",
                'preferred_location': random.choice(self.cities)
            }
            
            customers.append(customer)
        
        return customers
    
    def generate_vehicles(self, customer_ids: list) -> list:
        """Generate sample vehicle data for customers"""
        vehicles = []
        
        for customer_id in customer_ids:
            # Each customer has 1-3 vehicles
            num_vehicles = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
            
            for _ in range(num_vehicles):
                make = random.choice(self.car_makes)
                model = random.choice(self.car_models[make])
                year = random.randint(2015, 2024)
                
                # Registration date based on year
                reg_date = date(year, random.randint(1, 12), random.randint(1, 28))
                
                # Last service date (random within last 2 years)
                last_service = reg_date + timedelta(days=random.randint(30, 730))
                if last_service > date.today():
                    last_service = date.today() - timedelta(days=random.randint(1, 365))
                
                # Warranty period (typically 3-5 years)
                warranty_years = random.choice([3, 4, 5])
                warranty_end = reg_date.replace(year=reg_date.year + warranty_years)
                
                # Next service due
                next_service = last_service + timedelta(days=random.randint(90, 365))
                
                vehicle = {
                    'customer_id': customer_id,
                    'make': make,
                    'model': model,
                    'year': year,
                    'vin': f"MA1{random.randint(100000000000000, 999999999999999)}",
                    'registration_date': reg_date,
                    'last_service_date': last_service,
                    'last_service_type': random.choice(self.service_types),
                    'next_service_due': next_service,
                    'mileage': random.randint(5000, 150000),
                    'warranty_start': reg_date,
                    'warranty_end': warranty_end
                }
                
                vehicles.append(vehicle)
        
        return vehicles
    
    def generate_service_history(self, vehicle_ids: list) -> list:
        """Generate sample service history for vehicles"""
        service_history = []
        
        for vehicle_id in vehicle_ids:
            # Each vehicle has 1-10 service records
            num_services = random.randint(1, 10)
            
            # Get vehicle info to determine service dates
            vehicle_query = "SELECT registration_date, last_service_date FROM vehicles WHERE id = %s"
            vehicle_data = self.db_service.execute_query(vehicle_query, [vehicle_id])
            
            if not vehicle_data:
                continue
            
            reg_date = vehicle_data[0]['registration_date']
            last_service = vehicle_data[0]['last_service_date']
            
            # Generate service dates between registration and last service
            for i in range(num_services):
                service_date = reg_date + timedelta(
                    days=random.randint(0, (last_service - reg_date).days)
                )
                
                service_record = {
                    'vehicle_id': vehicle_id,
                    'service_date': service_date,
                    'service_type': random.choice(self.service_types),
                    'mileage': random.randint(1000, 100000),
                    'description': f"Routine {random.choice(self.service_types).lower()} performed",
                    'cost': round(random.uniform(500, 15000), 2)
                }
                
                service_history.append(service_record)
        
        return service_history
    
    def insert_customers(self, customers: list) -> list:
        """Insert customers into database and return their IDs"""
        logger.info(f"Inserting {len(customers)} customers...")
        
        customer_ids = []
        insert_query = """
        INSERT INTO customers (name, email, phone, preferred_location)
        VALUES (%(name)s, %(email)s, %(phone)s, %(preferred_location)s)
        RETURNING id
        """
        
        for customer in customers:
            result = self.db_service.execute_query(insert_query, customer)
            if result:
                customer_ids.append(result[0]['id'])
        
        logger.info(f"Successfully inserted {len(customer_ids)} customers")
        return customer_ids
    
    def insert_vehicles(self, vehicles: list) -> list:
        """Insert vehicles into database and return their IDs"""
        logger.info(f"Inserting {len(vehicles)} vehicles...")
        
        vehicle_ids = []
        insert_query = """
        INSERT INTO vehicles (customer_id, make, model, year, vin, registration_date,
                             last_service_date, last_service_type, next_service_due,
                             mileage, warranty_start, warranty_end)
        VALUES (%(customer_id)s, %(make)s, %(model)s, %(year)s, %(vin)s, %(registration_date)s,
                %(last_service_date)s, %(last_service_type)s, %(next_service_due)s,
                %(mileage)s, %(warranty_start)s, %(warranty_end)s)
        RETURNING id
        """
        
        for vehicle in vehicles:
            try:
                result = self.db_service.execute_query(insert_query, vehicle)
                if result:
                    vehicle_ids.append(result[0]['id'])
            except Exception as e:
                logger.warning(f"Failed to insert vehicle: {e}")
                continue
        
        logger.info(f"Successfully inserted {len(vehicle_ids)} vehicles")
        return vehicle_ids
    
    def insert_service_history(self, service_records: list):
        """Insert service history into database"""
        logger.info(f"Inserting {len(service_records)} service records...")
        
        insert_query = """
        INSERT INTO service_history (vehicle_id, service_date, service_type, 
                                   mileage, description, cost)
        VALUES (%(vehicle_id)s, %(service_date)s, %(service_type)s,
                %(mileage)s, %(description)s, %(cost)s)
        """
        
        successful = 0
        for record in service_records:
            try:
                result = self.db_service.execute_query(insert_query, record)
                if result is not None:  # Even empty list means success
                    successful += 1
            except Exception as e:
                logger.warning(f"Failed to insert service record: {e}")
                continue
        
        logger.info(f"Successfully inserted {successful} service records")
    
    def clear_existing_data(self):
        """Clear existing sample data from database"""
        logger.info("Clearing existing data...")
        
        tables = ['service_history', 'campaigns', 'vehicles', 'customers']
        
        for table in tables:
            try:
                self.db_service.execute_query(f"DELETE FROM {table}")
                logger.info(f"Cleared {table} table")
            except Exception as e:
                logger.error(f"Failed to clear {table}: {e}")
    
    def generate_all_data(self, num_customers: int = 100, clear_existing: bool = True):
        """Generate and insert all sample data"""
        logger.info("Starting sample data generation...")
        
        if clear_existing:
            response = input("Clear existing data? (y/N): ")
            if response.lower() == 'y':
                self.clear_existing_data()
        
        # Generate data
        logger.info("Generating sample data...")
        customers = self.generate_customers(num_customers)
        
        # Insert customers first
        customer_ids = self.insert_customers(customers)
        
        if not customer_ids:
            logger.error("No customers were inserted. Stopping.")
            return
        
        # Generate and insert vehicles
        vehicles = self.generate_vehicles(customer_ids)
        vehicle_ids = self.insert_vehicles(vehicles)
        
        if not vehicle_ids:
            logger.error("No vehicles were inserted. Stopping.")
            return
        
        # Generate and insert service history
        service_records = self.generate_service_history(vehicle_ids)
        self.insert_service_history(service_records)
        
        # Show summary
        self.show_data_summary()
        
        logger.info("Sample data generation completed!")
    
    def show_data_summary(self):
        """Display summary of inserted data"""
        logger.info("\n" + "="*50)
        logger.info("Data Summary:")
        logger.info("="*50)
        
        # Count records in each table
        tables = ['customers', 'vehicles', 'service_history', 'campaigns']
        
        for table in tables:
            try:
                result = self.db_service.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result[0]['count'] if result else 0
                logger.info(f"{table.upper()}: {count} records")
            except Exception as e:
                logger.error(f"Error counting {table}: {e}")
        
        # Show some sample data
        try:
            sample_query = """
            SELECT c.name, c.preferred_location, v.make, v.model, v.year
            FROM customers c
            JOIN vehicles v ON c.id = v.customer_id
            LIMIT 5
            """
            samples = self.db_service.execute_query(sample_query)
            
            if samples:
                logger.info("\nSample Records:")
                for sample in samples:
                    logger.info(f"- {sample['name']} ({sample['preferred_location']}): {sample['make']} {sample['model']} ({sample['year']})")
        except Exception as e:
            logger.error(f"Error fetching sample data: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample data for Smart Campaign System')
    parser.add_argument('--customers', type=int, default=100, 
                       help='Number of customers to generate (default: 100)')
    parser.add_argument('--no-clear', action='store_true',
                       help='Do not clear existing data')
    
    args = parser.parse_args()
    
    generator = SampleDataGenerator()
    generator.generate_all_data(
        num_customers=args.customers,
        clear_existing=not args.no_clear
    )

if __name__ == "__main__":
    main()
