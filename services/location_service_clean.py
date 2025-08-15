"""
Location Service for fetching and managing customer locations
"""

import logging
from typing import List, Dict, Any
from config.database import get_db_connection

logger = logging.getLogger(__name__)

class LocationService:
    """Service for managing customer locations"""
    
    def __init__(self):
        self.logger = logger
    
    def get_all_locations(self) -> List[str]:
        """Get all unique customer locations from database"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            query = """
                SELECT DISTINCT preferred_location 
                FROM customers 
                WHERE preferred_location IS NOT NULL 
                AND preferred_location != '' 
                ORDER BY preferred_location
            """
            
            cur.execute(query)
            locations = [row[0] for row in cur.fetchall()]
            
            conn.close()
            self.logger.info(f"Found {len(locations)} unique locations: {locations}")
            
            return locations
            
        except Exception as e:
            self.logger.error(f"Error fetching locations: {e}")
            return []
    
    def get_location_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics for each location"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            query = """
                SELECT 
                    c.preferred_location,
                    COUNT(DISTINCT c.customer_id) as customer_count,
                    COUNT(DISTINCT v.id) as vehicle_count,
                    STRING_AGG(DISTINCT v.make, ', ') as brands,
                    AVG(EXTRACT(YEAR FROM CURRENT_DATE) - v.year) as avg_vehicle_age,
                    MIN(c.created_at) as first_customer_date
                FROM customers c
                LEFT JOIN vehicles v ON c.customer_id = v.customer_id
                WHERE c.preferred_location IS NOT NULL 
                AND c.preferred_location != ''
                GROUP BY c.preferred_location
                HAVING COUNT(DISTINCT c.customer_id) > 0
                ORDER BY customer_count DESC
            """
            
            cur.execute(query)
            results = []
            
            for row in cur.fetchall():
                location_stats = {
                    'location': row[0],
                    'customer_count': row[1],
                    'vehicle_count': row[2] if row[2] else 0, 
                    'brands': row[3][:50] + '...' if row[3] and len(row[3]) > 50 else (row[3] or 'N/A'),
                    'avg_vehicle_age': round(float(row[4]), 1) if row[4] else 0,
                    'first_customer_date': row[5]
                }
                results.append(location_stats)
            
            conn.close()
            self.logger.info(f"Generated statistics for {len(results)} locations")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error generating location statistics: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def get_customers_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Get all customers for a specific location"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            query = """
                SELECT 
                    c.customer_id,
                    c.name,
                    c.email,
                    c.phone,
                    c.preferred_location,
                    COUNT(v.id) as vehicle_count
                FROM customers c
                LEFT JOIN vehicles v ON c.customer_id = v.customer_id
                WHERE c.preferred_location = %s
                GROUP BY c.customer_id, c.name, c.email, c.phone, c.preferred_location
                ORDER BY c.name
            """
            
            cur.execute(query, (location,))
            results = []
            
            for row in cur.fetchall():
                customer = {
                    'customer_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'location': row[4],
                    'vehicle_count': row[5] if row[5] else 0
                }
                results.append(customer)
            
            conn.close()
            self.logger.info(f"Found {len(results)} customers in {location}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error fetching customers for {location}: {e}")
            return []
    
    def filter_locations_by_criteria(self, min_customers: int = 1, min_vehicles: int = 0) -> List[str]:
        """Filter locations based on customer/vehicle count criteria"""
        
        stats = self.get_location_statistics()
        
        filtered_locations = [
            stat['location'] 
            for stat in stats 
            if stat['customer_count'] >= min_customers and stat['vehicle_count'] >= min_vehicles
        ]
        
        self.logger.info(f"Filtered to {len(filtered_locations)} locations (min customers: {min_customers}, min vehicles: {min_vehicles})")
        
        return filtered_locations
