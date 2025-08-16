from typing import Dict, Any, List
import json
from agents.base_agent import BaseAgent
from workflows.states import CampaignContent
from collections import defaultdict

class GroupBasedCampaignGenerator(BaseAgent):
    """Efficient group-based campaign generator to save LLM tokens"""
    
    def __init__(self):
        super().__init__(
            agent_name="GroupBasedCampaignGenerator",
            system_prompt=self._get_default_system_prompt()
        )
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are an Efficient Group-Based Campaign Generator Agent.
        
        Your role is to create ONE campaign template for each GROUP of customers with similar characteristics,
        rather than individual campaigns for each customer.
        
        Group customers by:
        1. Location/City (for holiday/weather campaigns)
        2. Service Type (for lifecycle campaigns: warranty, service overdue, etc.)
        3. Vehicle Category (if relevant)
        
        Create ONE compelling campaign template per group that can be personalized with customer data.
        
        Campaign Structure per Group:
        - Group Type: Location-based, Service-based, etc.
        - Campaign Title: Descriptive title for the group
        - Subject Line: With personalization placeholders like {customer_name}, {location}
        - Content: Template with placeholders for personalization
        - Target Count: Number of customers in this group
        - Personalization Fields: List of fields to be replaced per customer
        
        This approach saves LLM tokens while maintaining personalization quality.
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate group-based campaigns to save tokens"""
        try:
            self._log_step("Starting efficient group-based campaign generation")
            
            campaign_trigger = state.get('campaign_trigger', 'scheduled')
            targeted_customers = state.get('targeted_customers', [])
            
            if not targeted_customers:
                self._log_step("No targeted customers found")
                return state
            
            # Group customers based on campaign type
            grouped_campaigns = []
            
            if campaign_trigger == 'holiday':
                grouped_campaigns = self._create_location_based_groups(state, targeted_customers)
            elif campaign_trigger == 'weather':
                grouped_campaigns = self._create_location_based_groups(state, targeted_customers)
            elif campaign_trigger == 'lifecycle':
                grouped_campaigns = self._create_service_based_groups(state, targeted_customers)
            
            # Store grouped campaigns
            state['grouped_campaigns'] = grouped_campaigns
            state['total_groups'] = len(grouped_campaigns)
            
            total_customers = sum(len(group['customers']) for group in grouped_campaigns)
            self._log_step(f"Created {len(grouped_campaigns)} campaign groups for {total_customers} customers")
            
        except Exception as e:
            return self._handle_error(e, state)
        
        return state
    
    def _create_location_based_groups(self, state: Dict[str, Any], customers: List[Dict]) -> List[Dict]:
        """Group customers by location for holiday/weather campaigns"""
        
        # Group customers by location
        location_groups = defaultdict(list)
        for customer in customers:
            location = customer.get('preferred_location', 'Mumbai')
            location_groups[location].append(customer)
        
        grouped_campaigns = []
        campaign_trigger = state.get('campaign_trigger', 'holiday')
        
        for location, location_customers in location_groups.items():
            # Generate ONE campaign template for this location
            if campaign_trigger == 'holiday':
                campaign_template = self._generate_holiday_group_template(
                    location, len(location_customers), state.get('holiday_data', {})
                )
            else:  # weather
                campaign_template = self._generate_weather_group_template(
                    location, len(location_customers), state.get('weather_data', {})
                )
            
            grouped_campaigns.append({
                'group_type': f'{campaign_trigger}_{location}',
                'location': location,
                'campaign_template': campaign_template,
                'customers': location_customers,
                'customer_count': len(location_customers)
            })
        
        return grouped_campaigns
    
    def _create_service_based_groups(self, state: Dict[str, Any], customers: List[Dict]) -> List[Dict]:
        """Group customers by service type for lifecycle campaigns"""
        
        # Group customers by service needs
        service_groups = defaultdict(list)
        
        for customer in customers:
            # Check what services this customer needs
            service_type = self._determine_service_type(customer)
            service_groups[service_type].append(customer)
        
        grouped_campaigns = []
        
        for service_type, service_customers in service_groups.items():
            # Generate ONE campaign template for this service type
            campaign_template = self._generate_service_group_template(
                service_type, len(service_customers)
            )
            
            grouped_campaigns.append({
                'group_type': f'service_{service_type}',
                'service_type': service_type,
                'campaign_template': campaign_template,
                'customers': service_customers,
                'customer_count': len(service_customers)
            })
        
        return grouped_campaigns
    
    def _determine_service_type(self, customer: Dict) -> str:
        """Determine the primary service need for a customer"""
        
        # Check vehicle data for service needs
        vehicle = customer.get('vehicle', {})
        
        # Priority order: warranty > service_overdue > high_mileage > welcome
        if vehicle.get('warranty_expiring'):
            return 'warranty_expiring'
        elif vehicle.get('service_overdue'):
            return 'service_overdue'
        elif vehicle.get('high_mileage'):
            return 'high_mileage'
        else:
            return 'general_service'
    
    def _generate_holiday_group_template(self, location: str, customer_count: int, holiday_data: Dict) -> Dict:
        """Generate ONE holiday campaign template for a location group"""
        
        holiday_name = holiday_data.get('name', 'Festival')
        
        # This would normally call LLM, but for now return a template
        return {
            'title': f'{holiday_name} Campaign - {location}',
            'subject_line': f'🎉 Special {holiday_name} Offers for {location} Customers!',
            'content_template': f"""
Dear {{customer_name}},

Wishing you and your family a very Happy {holiday_name}!

As you prepare for the festivities and plan your travels around {location}, 
ensure your {{vehicle_make}} {{vehicle_model}} is ready for safe journeys.

🎁 Special {holiday_name} Offers:
- Free vehicle inspection
- 20% off on service packages
- Complimentary car wash

Book your service appointment today!

Best regards,
Your Service Team
            """,
            'cta_text': f'Book {holiday_name} Service',
            'personalization_fields': ['customer_name', 'vehicle_make', 'vehicle_model'],
            'target_count': customer_count
        }
    
    def _generate_weather_group_template(self, location: str, customer_count: int, weather_data: Dict) -> Dict:
        """Generate ONE weather campaign template for a location group"""
        
        weather_condition = weather_data.get('condition', 'changing weather')
        
        return {
            'title': f'Weather Advisory Campaign - {location}',
            'subject_line': f'🌦️ Weather Alert: Prepare Your Vehicle in {location}',
            'content_template': f"""
Dear {{customer_name}},

Weather update for {location}: {weather_condition}

Your {{vehicle_make}} {{vehicle_model}} needs attention for the current weather conditions.

💧 Weather-Ready Services:
- AC system check
- Tire pressure adjustment  
- Battery inspection
- Brake system review

Stay safe on the roads!

Best regards,
Your Service Team
            """,
            'cta_text': 'Book Weather Service',
            'personalization_fields': ['customer_name', 'vehicle_make', 'vehicle_model'],
            'target_count': customer_count
        }
    
    def _generate_service_group_template(self, service_type: str, customer_count: int) -> Dict:
        """Generate ONE service campaign template for a service group"""
        
        service_templates = {
            'warranty_expiring': {
                'title': 'Warranty Expiring Campaign',
                'subject_line': '⚠️ Your Vehicle Warranty is Expiring Soon!',
                'content': """
Dear {customer_name},

Your {vehicle_make} {vehicle_model}'s warranty is about to expire.

Don't miss out on covered services! Schedule your appointment before:
📅 Warranty Expiry: {warranty_end_date}

✅ Still Covered:
- Engine diagnostics
- Transmission check
- Electrical system
- Safety inspections

Book now to save money!
                """
            },
            'service_overdue': {
                'title': 'Service Overdue Campaign', 
                'subject_line': '🔧 Your Vehicle Service is Overdue',
                'content': """
Dear {customer_name},

Your {vehicle_make} {vehicle_model} is due for service.

Last Service: {last_service_date}
Recommended: Every {service_interval} months

⚠️ Overdue services can lead to:
- Decreased performance
- Higher fuel consumption  
- Potential breakdowns

Schedule your service today!
                """
            }
        }
        
        template = service_templates.get(service_type, service_templates['service_overdue'])
        
        return {
            'title': template['title'],
            'subject_line': template['subject_line'], 
            'content_template': template['content'],
            'cta_text': 'Book Service Now',
            'personalization_fields': ['customer_name', 'vehicle_make', 'vehicle_model', 'warranty_end_date', 'last_service_date', 'service_interval'],
            'target_count': customer_count
        }
