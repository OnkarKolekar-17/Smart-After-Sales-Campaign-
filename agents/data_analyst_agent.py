from typing import Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from services.database_service import DatabaseService
from utils.helpers import calculate_vehicle_age, days_since_last_service, days_until_warranty_expiry
import logging

logger = logging.getLogger(__name__)

class DataAnalystAgent(BaseAgent):
    """Agent responsible for analyzing customer and vehicle data to provide insights"""
    
    def __init__(self):
        super().__init__(
            agent_name="DataAnalystAgent",
            system_prompt=self._get_default_system_prompt()
        )
        self.db_service = DatabaseService()
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are a Data Analysis Expert specializing in automotive customer behavior and service patterns.
        
        Your role is to analyze customer and vehicle data to provide actionable insights for targeted campaigns.
        
        Key responsibilities:
        1. Analyze customer service patterns and behavior
        2. Identify high-value customers and potential churn risks
        3. Segment customers based on vehicle lifecycle and service history
        4. Provide recommendations for campaign targeting and timing
        5. Calculate customer lifetime value and service propensity scores
        6. Identify seasonal trends and service patterns
        
        Analysis principles:
        - Use data-driven insights to guide marketing decisions
        - Focus on customer value and retention opportunities
        - Consider vehicle age, service history, and geographic factors
        - Identify optimal timing for different types of campaigns
        - Provide clear, actionable recommendations
        
        Always provide structured analysis with clear metrics and reasoning.
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer data and provide insights"""
        try:
            self._log_step("Starting data analysis")
            
            location = state.get('location', 'Mumbai')
            
            # Get customer and vehicle data
            customers_data = self._get_customers_data(location)
            
            # Perform various analyses
            analysis_results = {
                'customer_segments': self._segment_customers(customers_data),
                'high_value_customers': self._identify_high_value_customers(customers_data),
                'service_opportunities': self._identify_service_opportunities(customers_data),
                'churn_risk_customers': self._identify_churn_risk(customers_data),
                'seasonal_insights': self._analyze_seasonal_patterns(customers_data),
                'campaign_recommendations': self._generate_campaign_recommendations(customers_data),
                'analysis_summary': self._generate_analysis_summary(customers_data)
            }
            
            # Update state with analysis results
            state['data_analysis'] = analysis_results
            state['analysis_timestamp'] = datetime.now().isoformat()
            
            self._log_step("Data analysis completed successfully")
            logger.info(f"Analyzed data for {len(customers_data)} customers in {location}")
            
            return state
            
        except Exception as e:
            error_msg = f"Data analysis failed: {str(e)}"
            logger.error(error_msg)
            state.setdefault('errors', []).append(error_msg)
            return state
    
    def _get_customers_data(self, location: str = None) -> List[Dict[str, Any]]:
        """Get customer and vehicle data from database"""
        try:
            # Get all customers with their vehicles
            query = """
            SELECT 
                c.id as customer_id, c.name, c.email, c.phone, c.preferred_location,
                v.id as vehicle_id, v.make, v.model, v.year, v.vin,
                v.registration_date, v.last_service_date, v.last_service_type,
                v.next_service_due, v.mileage, v.warranty_start, v.warranty_end,
                sh.service_date as last_actual_service_date, sh.cost as last_service_cost
            FROM customers c
            LEFT JOIN vehicles v ON c.id = v.customer_id
            LEFT JOIN service_history sh ON v.id = sh.vehicle_id
            WHERE 1=1
            """
            
            params = []
            if location:
                query += " AND c.preferred_location ILIKE %s"
                params.append(f"%{location}%")
            
            query += " ORDER BY c.id, v.id, sh.service_date DESC"
            
            result = self.db_service.execute_query(query, params)
            
            # Process and structure the data
            customers_dict = {}
            for row in result:
                customer_id = row['customer_id']
                
                if customer_id not in customers_dict:
                    customers_dict[customer_id] = {
                        'customer_id': customer_id,
                        'name': row['name'],
                        'email': row['email'],
                        'phone': row['phone'],
                        'preferred_location': row['preferred_location'],
                        'vehicles': []
                    }
                
                if row['vehicle_id'] and row['vehicle_id'] not in [v['vehicle_id'] for v in customers_dict[customer_id]['vehicles']]:
                    vehicle_data = {
                        'vehicle_id': row['vehicle_id'],
                        'make': row['make'],
                        'model': row['model'],
                        'year': row['year'],
                        'vin': row['vin'],
                        'registration_date': row['registration_date'],
                        'last_service_date': row['last_service_date'],
                        'last_service_type': row['last_service_type'],
                        'next_service_due': row['next_service_due'],
                        'mileage': row['mileage'],
                        'warranty_start': row['warranty_start'],
                        'warranty_end': row['warranty_end'],
                        'last_actual_service_date': row['last_actual_service_date'],
                        'last_service_cost': float(row['last_service_cost']) if row['last_service_cost'] else 0
                    }
                    customers_dict[customer_id]['vehicles'].append(vehicle_data)
            
            return list(customers_dict.values())
            
        except Exception as e:
            logger.error(f"Error getting customer data: {e}")
            return []
    
    def _segment_customers(self, customers_data: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """Segment customers based on various criteria"""
        segments = {
            'new_customers': [],      # Customers with vehicles < 1 year old
            'regular_customers': [],  # Customers with regular service history
            'inactive_customers': [], # Customers with no service > 12 months
            'high_value_customers': [], # Customers with high service spending
            'warranty_expiring': [], # Customers with warranty expiring soon
            'service_due': []        # Customers with overdue service
        }
        
        for customer in customers_data:
            customer_id = customer['customer_id']
            
            for vehicle in customer['vehicles']:
                vehicle_age = calculate_vehicle_age(vehicle['registration_date'])
                days_since_service = days_since_last_service(vehicle['last_service_date'])
                warranty_days_left = days_until_warranty_expiry(vehicle['warranty_end'])
                
                # New customers
                if vehicle_age <= 1:
                    segments['new_customers'].append(customer_id)
                
                # Regular customers (service within last 6 months)
                if days_since_service <= 180:
                    segments['regular_customers'].append(customer_id)
                
                # Inactive customers (no service > 12 months)
                if days_since_service > 365:
                    segments['inactive_customers'].append(customer_id)
                
                # High value customers (high service spending)
                if vehicle['last_service_cost'] > 10000:  # ₹10,000+
                    segments['high_value_customers'].append(customer_id)
                
                # Warranty expiring soon
                if 0 <= warranty_days_left <= 60:
                    segments['warranty_expiring'].append(customer_id)
                
                # Service due
                if days_since_service > 180:  # More than 6 months
                    segments['service_due'].append(customer_id)
        
        # Remove duplicates
        for segment in segments:
            segments[segment] = list(set(segments[segment]))
        
        return segments
    
    def _identify_high_value_customers(self, customers_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify customers with highest value potential"""
        high_value_customers = []
        
        for customer in customers_data:
            total_vehicle_value = 0
            total_service_spend = 0
            vehicles_count = len(customer['vehicles'])
            
            for vehicle in customer['vehicles']:
                # Estimate vehicle value based on year (simplified)
                vehicle_age = calculate_vehicle_age(vehicle['registration_date'])
                estimated_value = max(200000 * (1 - vehicle_age * 0.1), 50000)  # Depreciation model
                total_vehicle_value += estimated_value
                total_service_spend += vehicle['last_service_cost']
            
            # Calculate customer value score
            value_score = (
                total_vehicle_value * 0.3 +
                total_service_spend * 2 +
                vehicles_count * 50000
            )
            
            if value_score > 300000:  # High value threshold
                high_value_customers.append({
                    'customer_id': customer['customer_id'],
                    'name': customer['name'],
                    'value_score': value_score,
                    'total_vehicle_value': total_vehicle_value,
                    'total_service_spend': total_service_spend,
                    'vehicles_count': vehicles_count
                })
        
        # Sort by value score
        high_value_customers.sort(key=lambda x: x['value_score'], reverse=True)
        return high_value_customers[:50]  # Top 50 high-value customers
    
    def _identify_service_opportunities(self, customers_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Identify various service opportunities"""
        opportunities = {
            'overdue_service': [],
            'warranty_expiring': [],
            'seasonal_maintenance': [],
            'high_mileage': []
        }
        
        for customer in customers_data:
            for vehicle in customer['vehicles']:
                customer_vehicle = {
                    'customer_id': customer['customer_id'],
                    'customer_name': customer['name'],
                    'vehicle_id': vehicle['vehicle_id'],
                    'vehicle': f"{vehicle['make']} {vehicle['model']} ({vehicle['year']})",
                }
                
                days_since_service = days_since_last_service(vehicle['last_service_date'])
                warranty_days_left = days_until_warranty_expiry(vehicle['warranty_end'])
                vehicle_age = calculate_vehicle_age(vehicle['registration_date'])
                
                # Overdue service
                if days_since_service > 180:
                    opportunities['overdue_service'].append({
                        **customer_vehicle,
                        'days_overdue': days_since_service - 180,
                        'urgency': 'high' if days_since_service > 365 else 'medium'
                    })
                
                # Warranty expiring
                if 0 <= warranty_days_left <= 90:
                    opportunities['warranty_expiring'].append({
                        **customer_vehicle,
                        'days_left': warranty_days_left,
                        'urgency': 'high' if warranty_days_left <= 30 else 'medium'
                    })
                
                # Seasonal maintenance (vehicles > 2 years old)
                if vehicle_age >= 2:
                    opportunities['seasonal_maintenance'].append({
                        **customer_vehicle,
                        'vehicle_age': vehicle_age,
                        'last_service': vehicle['last_service_date']
                    })
                
                # High mileage vehicles
                if vehicle['mileage'] and vehicle['mileage'] > 50000:
                    opportunities['high_mileage'].append({
                        **customer_vehicle,
                        'mileage': vehicle['mileage'],
                        'service_intensity': 'high' if vehicle['mileage'] > 100000 else 'medium'
                    })
        
        return opportunities
    
    def _identify_churn_risk(self, customers_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify customers at risk of churning"""
        churn_risk_customers = []
        
        for customer in customers_data:
            risk_factors = []
            risk_score = 0
            
            for vehicle in customer['vehicles']:
                days_since_service = days_since_last_service(vehicle['last_service_date'])
                
                # No service for > 18 months
                if days_since_service > 540:
                    risk_factors.append("Long service gap")
                    risk_score += 30
                
                # No service for > 12 months
                elif days_since_service > 365:
                    risk_factors.append("Extended service gap")
                    risk_score += 20
                
                # Low service spending
                if vehicle['last_service_cost'] < 2000:
                    risk_factors.append("Low service engagement")
                    risk_score += 10
                
                # Old vehicle with infrequent service
                vehicle_age = calculate_vehicle_age(vehicle['registration_date'])
                if vehicle_age > 7 and days_since_service > 180:
                    risk_factors.append("Old vehicle with service gap")
                    risk_score += 15
            
            if risk_score >= 25:  # Threshold for churn risk
                churn_risk_customers.append({
                    'customer_id': customer['customer_id'],
                    'name': customer['name'],
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'urgency': 'high' if risk_score >= 40 else 'medium'
                })
        
        # Sort by risk score
        churn_risk_customers.sort(key=lambda x: x['risk_score'], reverse=True)
        return churn_risk_customers
    
    def _analyze_seasonal_patterns(self, customers_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal service patterns"""
        current_month = datetime.now().month
        seasonal_insights = {
            'current_season': self._get_season(current_month),
            'seasonal_recommendations': [],
            'weather_considerations': []
        }
        
        # Add seasonal recommendations based on current season
        if seasonal_insights['current_season'] == 'summer':
            seasonal_insights['seasonal_recommendations'] = [
                'AC system maintenance',
                'Cooling system check',
                'Tire pressure adjustment',
                'Battery cooling inspection'
            ]
        elif seasonal_insights['current_season'] == 'monsoon':
            seasonal_insights['seasonal_recommendations'] = [
                'Wiper blade replacement',
                'Brake system service',
                'Tire tread inspection',
                'Electrical system protection'
            ]
        elif seasonal_insights['current_season'] == 'winter':
            seasonal_insights['seasonal_recommendations'] = [
                'Battery health check',
                'Engine warm-up system',
                'Heating system service',
                'Winter tire installation'
            ]
        
        return seasonal_insights
    
    def _generate_campaign_recommendations(self, customers_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific campaign recommendations based on analysis"""
        recommendations = []
        
        # Service reminder campaigns
        overdue_count = sum(1 for c in customers_data for v in c['vehicles'] 
                          if days_since_last_service(v['last_service_date']) > 180)
        if overdue_count > 10:
            recommendations.append({
                'campaign_type': 'service_reminder',
                'priority': 'high',
                'target_count': overdue_count,
                'description': 'Service reminder campaign for overdue vehicles',
                'timing': 'immediate'
            })
        
        # Warranty expiry campaigns
        warranty_expiring = sum(1 for c in customers_data for v in c['vehicles']
                              if 0 <= days_until_warranty_expiry(v['warranty_end']) <= 60)
        if warranty_expiring > 5:
            recommendations.append({
                'campaign_type': 'warranty_renewal',
                'priority': 'high',
                'target_count': warranty_expiring,
                'description': 'Warranty renewal campaign for expiring warranties',
                'timing': 'urgent'
            })
        
        # Seasonal campaigns
        recommendations.append({
            'campaign_type': 'seasonal',
            'priority': 'medium',
            'target_count': len(customers_data),
            'description': f'{self._get_season(datetime.now().month).title()} maintenance campaign',
            'timing': 'scheduled'
        })
        
        return recommendations
    
    def _generate_analysis_summary(self, customers_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall analysis summary"""
        total_customers = len(customers_data)
        total_vehicles = sum(len(c['vehicles']) for c in customers_data)
        
        # Calculate average service gap
        service_gaps = []
        for customer in customers_data:
            for vehicle in customer['vehicles']:
                if vehicle['last_service_date']:
                    service_gaps.append(days_since_last_service(vehicle['last_service_date']))
        
        avg_service_gap = sum(service_gaps) / len(service_gaps) if service_gaps else 0
        
        return {
            'total_customers': total_customers,
            'total_vehicles': total_vehicles,
            'average_service_gap_days': round(avg_service_gap),
            'customers_needing_attention': len([c for c in customers_data 
                                             for v in c['vehicles']
                                             if days_since_last_service(v['last_service_date']) > 180]),
            'analysis_date': datetime.now().isoformat(),
            'data_quality_score': self._calculate_data_quality_score(customers_data)
        }
    
    def _calculate_data_quality_score(self, customers_data: List[Dict[str, Any]]) -> float:
        """Calculate data quality score"""
        total_fields = 0
        complete_fields = 0
        
        for customer in customers_data:
            # Customer fields
            customer_fields = ['name', 'email', 'phone', 'preferred_location']
            total_fields += len(customer_fields)
            complete_fields += sum(1 for field in customer_fields if customer.get(field))
            
            # Vehicle fields
            for vehicle in customer['vehicles']:
                vehicle_fields = ['make', 'model', 'year', 'registration_date', 'last_service_date']
                total_fields += len(vehicle_fields)
                complete_fields += sum(1 for field in vehicle_fields if vehicle.get(field))
        
        return round((complete_fields / total_fields * 100), 2) if total_fields > 0 else 0
    
    def _get_season(self, month: int) -> str:
        """Get season based on month"""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8, 9]:
            return "monsoon"
        else:
            return "autumn"
    
    def _log_step(self, message: str):
        """Log step with agent name"""
        logger.info(f"[{self.agent_name}] {message}")