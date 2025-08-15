from typing import Dict, Any, List
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from config.database import get_db_connection
from workflows.states import CustomerData, TargetingCriteria
from workflows.states import CustomerData, TargetingCriteria

class TargetingAgent(BaseAgent):
    """Agent responsible for segmenting customers based on various criteria"""
    
    def __init__(self):
        super().__init__(
            agent_name="TargetingAgent",
            system_prompt=self._get_default_system_prompt()
        )
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are a Customer Targeting Agent specializing in automotive service campaign segmentation.
        
        Your role is to analyze customer and vehicle data to create precise targeting criteria for campaigns.
        
        Consider these factors:
        - Vehicle lifecycle stages (new, mid-life, aging)
        - Service history patterns (regular, irregular, overdue)
        - Warranty status (active, expiring, expired)
        - Geographic location and climate impact
        - Customer behavior and engagement history
        - Seasonal maintenance needs
        - Vehicle make/model specific requirements
        
        Create targeting rules that:
        1. Maximize campaign relevance and conversion potential
        2. Avoid over-targeting the same customers
        3. Consider customer preferences and communication history
        4. Balance reach with precision
        
        Always provide specific, data-driven targeting criteria with clear business rationale.
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process targeting criteria and segment customers"""
        try:
            self._log_step("Starting customer targeting analysis")
            
            # Get location and campaign context
            location = state.get('location', 'Mumbai')
            campaign_trigger = state.get('campaign_trigger', 'scheduled')
            weather_data = state.get('weather_data')
            holiday_data = state.get('holiday_data')
            
            # Generate targeting criteria using LLM
            targeting_criteria = self._generate_targeting_criteria(
                campaign_trigger, weather_data, holiday_data
            )
            
            # Add location to criteria
            targeting_criteria.location = location
            
            # Apply targeting criteria to get customer segments
            customer_segments = self._segment_customers(targeting_criteria)
            
            # Update state with targeted customers
            state['targeting_criteria'] = targeting_criteria
            state['customer_segments'] = customer_segments
            state['targeted_customers'] = customer_segments  # For compatibility
            state['total_targeted'] = len(customer_segments)
            
            self._log_step(f"Targeting completed: {len(customer_segments)} customers segmented")
            
        except Exception as e:
            return self._handle_error(e, state)
        
        return state
    
    def _generate_targeting_criteria(self, campaign_trigger: str, weather_data, holiday_data) -> TargetingCriteria:
        """Generate targeting criteria based on campaign context"""
        
        context = f"""
        Campaign Context:
        - Trigger: {campaign_trigger}
        - Weather Data: {weather_data if weather_data else 'Not available'}
        - Holiday Data: {holiday_data if holiday_data else 'Not available'}
        
        Based on this context, define specific targeting criteria for customer segmentation.
        
        Consider:
        1. Vehicle age ranges most relevant for this campaign
        2. Service history patterns to target (e.g., overdue services, regular customers)
        3. Warranty status relevance
        4. Geographic/location considerations
        5. Seasonal timing factors
        
        Provide your recommendations in a structured format covering:
        - Vehicle age range (in years)
        - Last service timeframe (in months)
        - Warranty expiry considerations (in days)
        - Location preferences
        - Any custom filters
        """
        
        try:
            criteria_text = self._invoke_llm(context)
            
            # Parse LLM response to extract criteria (simplified version)
            # In production, you might want more sophisticated parsing
            criteria = TargetingCriteria()
            
            # Extract numeric values using simple parsing
            if "vehicle age" in criteria_text.lower():
                # This is a simplified extraction - you might want to use regex or NLP
                criteria.vehicle_age_range = [2, 10]  # Default range
            
            if "service" in criteria_text.lower() and "month" in criteria_text.lower():
                criteria.last_service_months = 6  # Default
            
            if "warranty" in criteria_text.lower():
                criteria.warranty_expiry_days = 90  # Default
            
            # Store the full LLM analysis for reference
            criteria.custom_filters = {"llm_analysis": criteria_text}
            
            return criteria
            
        except Exception as e:
            self._log_step(f"Error generating targeting criteria: {e}", "error")
            # Return default criteria
            return TargetingCriteria(
                vehicle_age_range=[1, 15],
                last_service_months=6,
                warranty_expiry_days=90
            )
    
    def _segment_customers(self, criteria: TargetingCriteria) -> List[CustomerData]:
        """Segment customers based on targeting criteria"""
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # First, let's try a simple query to check if we have any data at all
            self._log_step("Testing database connection and basic data availability")
            
            # Test basic customer count
            cur.execute("SELECT COUNT(*) FROM customers")
            result = cur.fetchone()
            customer_count = result['count'] if isinstance(result, dict) else result[0]
            self._log_step(f"Total customers in database: {customer_count}")
            
            # Test location-specific customers
            if criteria.location:
                cur.execute("SELECT COUNT(*) FROM customers WHERE preferred_location ILIKE %s", [f"%{criteria.location}%"])
                result = cur.fetchone()
                location_count = result['count'] if isinstance(result, dict) else result[0]
                self._log_step(f"Customers in {criteria.location}: {location_count}")
            
            # Build simplified query to get all customers with vehicles in the specified location
            query = """
            SELECT DISTINCT
                c.id as customer_id,
                c.name,
                c.email,
                c.phone,
                c.preferred_location,
                c.created_at as purchase_date,
                v.id as vehicle_id,
                v.make,
                v.model,
                v.year,
                v.last_service_date,
                v.next_service_due,
                v.warranty_end,
                v.mileage
            FROM customers c
            LEFT JOIN vehicles v ON c.id = v.customer_id
            WHERE 1=1
            """
            
            params = []
            
            # Add location filter if specified (primary filter)
            if criteria.location:
                query += " AND c.preferred_location ILIKE %s"
                params.append(f"%{criteria.location}%")
            
            # Simplified ordering
            query += " ORDER BY c.id"
            
            self._log_step(f"Executing query: {query}")
            self._log_step(f"Query parameters: {params}")
            
            cur.execute(query, params)
            results = cur.fetchall()
            
            # Group by customer and aggregate vehicle data
            customer_dict = {}
            for row in results:
                customer_id = row['customer_id']
                
                if customer_id not in customer_dict:
                    # Helper function to safely convert dates
                    def safe_date_convert(date_value):
                        if date_value is None:
                            return None
                        if hasattr(date_value, 'isoformat'):
                            return date_value.isoformat()
                        return str(date_value)
                    
                    customer_dict[customer_id] = CustomerData(
                        customer_id=customer_id,
                        name=row['name'],
                        email=row['email'],
                        phone=row['phone'],
                        preferred_location=row['preferred_location'],
                        city=row['preferred_location'],  # Use preferred_location as city
                        purchase_date=safe_date_convert(row['purchase_date']),
                        vehicles=[]
                    )
                
                # Add vehicle data if vehicle exists
                if row['vehicle_id']:
                    vehicle_data = {
                        'vehicle_id': row['vehicle_id'],
                        'make': row['make'],
                        'model': row['model'],
                        'year': row['year'],
                        'last_service_date': safe_date_convert(row['last_service_date']),
                        'next_service_due': safe_date_convert(row['next_service_due']),
                        'warranty_end': safe_date_convert(row['warranty_end']),
                        'mileage': row['mileage']
                    }
                    
                    customer_dict[customer_id].vehicles.append(vehicle_data)
            
            customer_segments = list(customer_dict.values())
            
            cur.close()
            conn.close()
            
            self._log_step(f"Segmented {len(customer_segments)} customers with targeting criteria")
            return customer_segments
            
        except Exception as e:
            self._log_step(f"Error segmenting customers: {e}", "error")
            return []
    
    def _apply_advanced_filters(self, customers: List[CustomerData], criteria: TargetingCriteria) -> List[CustomerData]:
        """Apply additional filtering logic based on business rules"""
        
        filtered_customers = []
        
        for customer in customers:
            # Skip customers with recent campaign interactions (avoid fatigue)
            if self._recently_contacted(customer.customer_id, days=7):
                continue
            
            # Ensure email is valid
            if not customer.email or '@' not in customer.email:
                continue
            
            # Apply custom business logic
            if self._meets_business_criteria(customer, criteria):
                filtered_customers.append(customer)
        
        return filtered_customers
    
    def _recently_contacted(self, customer_id: int, days: int = 7) -> bool:
        """Check if customer was contacted recently"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM campaigns 
                WHERE customer_id = %s AND sent_at > %s
            """, (customer_id, cutoff_date))
            
            result = cur.fetchone()
            cur.close()
            conn.close()
            
            return result['count'] > 0
            
        except Exception:
            return False  # If we can't check, assume not contacted
    
    def _meets_business_criteria(self, customer: CustomerData, criteria: TargetingCriteria) -> bool:
        """Apply additional business logic for customer selection"""
        
        # Ensure customer has at least one vehicle
        if not customer.vehicles:
            return False
        
        # Check for valid contact information
        if not customer.email:
            return False
        
        # Add more business rules as needed
        return True