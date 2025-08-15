from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent
from utils.helpers import personalize_content, calculate_vehicle_age, days_since_last_service
from utils.templates import get_template, BASE_EMAIL_TEMPLATE
from models.campaign_models import PersonalizedCampaign, CampaignContent
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

class PersonalizationAgent(BaseAgent):
    """Agent responsible for personalizing campaign content for individual customers"""
    
    def __init__(self):
        super().__init__(
            agent_name="PersonalizationAgent",
            system_prompt=self._get_default_system_prompt()
        )
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are a Personalization Expert specializing in creating highly personalized automotive service communications.
        
        Your role is to take campaign templates and customer data to create personalized, engaging content that speaks directly to each customer's specific situation and needs.
        
        Key principles:
        1. Use customer's name and vehicle details naturally throughout the content
        2. Reference specific service history, dates, and vehicle lifecycle stage
        3. Create urgency based on actual service needs and timing
        4. Adjust tone and messaging based on customer segment and history
        5. Include relevant local context (weather, location, seasonal factors)
        6. Ensure all personalization feels natural and conversational
        7. Maintain consistency with brand voice while being personal
        
        Personalization techniques:
        - Dynamic content based on vehicle age, service history, and warranty status
        - Location-specific offers and service center references
        - Seasonal and weather-appropriate service recommendations
        - Customer lifecycle stage messaging (new vs. loyal customers)
        - Service urgency indicators based on actual vehicle needs
        - Previous service acknowledgments and follow-ups
        
        Always ensure personalized content is:
        - Relevant to the specific customer and vehicle
        - Actionable with clear next steps
        - Properly formatted for email delivery
        - Free of placeholder text or generic language
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Personalize campaign content for targeted customers"""
        try:
            self._log_step("Starting content personalization")
            
            # Get required data from state
            campaign_content = state.get('generated_campaigns', [])
            targeted_customers = state.get('targeted_customers', [])
            weather_data = state.get('weather_data')
            holiday_data = state.get('holiday_data')
            
            if not campaign_content or not targeted_customers:
                raise ValueError("Missing campaign content or targeted customers")
            
            personalized_campaigns = []
            
            # Personalize content for each customer
            for campaign in campaign_content:
                for customer in targeted_customers:
                    try:
                        personalized_campaign = self._personalize_for_customer(
                            campaign, customer, weather_data, holiday_data, state
                        )
                        if personalized_campaign:
                            personalized_campaigns.append(personalized_campaign)
                    
                    except Exception as e:
                        logger.warning(f"Failed to personalize campaign for customer {customer.get('customer_id')}: {e}")
                        continue
            
            # Update state with personalized campaigns
            state['personalized_campaigns'] = personalized_campaigns
            state['personalization_timestamp'] = datetime.now().isoformat()
            
            self._log_step(f"Personalized {len(personalized_campaigns)} campaigns")
            logger.info(f"Successfully personalized campaigns for {len(personalized_campaigns)} customer-campaign combinations")
            
            return state
            
        except Exception as e:
            error_msg = f"Content personalization failed: {str(e)}"
            logger.error(error_msg)
            state.setdefault('errors', []).append(error_msg)
            return state
    
    def _personalize_for_customer(self, 
                                  campaign: Dict[str, Any], 
                                  customer: Dict[str, Any],
                                  weather_data: Dict[str, Any] = None,
                                  holiday_data: Dict[str, Any] = None,
                                  state: Dict[str, Any] = None) -> PersonalizedCampaign:
        """Personalize a single campaign for a specific customer"""
        
        # Prepare personalization context
        context = self._build_personalization_context(
            customer, weather_data, holiday_data, state
        )
        
        # Get the primary vehicle for this customer
        primary_vehicle = self._get_primary_vehicle(customer)
        
        # Personalize subject line
        personalized_subject = self._personalize_subject_line(
            campaign.get('subject_line', ''), context, primary_vehicle
        )
        
        # Personalize content
        personalized_content = self._personalize_content(
            campaign.get('content', ''), context, primary_vehicle, campaign
        )
        
        # Create personalized campaign object
        return PersonalizedCampaign(
            customer_id=customer['customer_id'],
            customer_name=customer['name'],
            customer_email=customer['email'],
            subject_line=personalized_subject,
            content=personalized_content,
            campaign_type=campaign.get('campaign_type', 'general'),
            metadata={
                'original_campaign_title': campaign.get('campaign_title'),
                'vehicle_info': primary_vehicle,
                'personalization_context': context,
                'campaign_trigger': state.get('campaign_trigger', 'scheduled')
            }
        )
    
    def _build_personalization_context(self, 
                                     customer: Dict[str, Any],
                                     weather_data: Dict[str, Any] = None,
                                     holiday_data: Dict[str, Any] = None,
                                     state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build comprehensive personalization context"""
        
        primary_vehicle = self._get_primary_vehicle(customer)
        
        # Base customer context
        context = {
            'customer_name': customer['name'],
            'customer_id': customer['customer_id'],
            'email': customer['email'],
            'phone': customer.get('phone', ''),
            'preferred_location': customer.get('preferred_location', ''),
        }
        
        # Vehicle context
        if primary_vehicle:
            context.update({
                'vehicle_make': primary_vehicle['make'],
                'vehicle_model': primary_vehicle['model'],
                'vehicle_year': primary_vehicle['year'],
                'vehicle_age': calculate_vehicle_age(primary_vehicle.get('registration_date')),
                'registration_date': primary_vehicle.get('registration_date', ''),
                'last_service_date': primary_vehicle.get('last_service_date', ''),
                'last_service_type': primary_vehicle.get('last_service_type', ''),
                'mileage': primary_vehicle.get('mileage', ''),
                'warranty_end': primary_vehicle.get('warranty_end', ''),
                'days_since_last_service': days_since_last_service(primary_vehicle.get('last_service_date')),
            })
            
            # Service urgency and recommendations
            context.update(self._get_service_context(primary_vehicle))
        
        # Weather context
        if weather_data:
            context.update({
                'weather_condition': weather_data.get('condition', ''),
                'temperature': weather_data.get('temperature', ''),
                'humidity': weather_data.get('humidity', ''),
                'weather_recommendation': weather_data.get('recommendation', ''),
            })
        
        # Holiday context
        if holiday_data and holiday_data.get('current_holidays'):
            holiday = holiday_data['current_holidays'][0]  # Take first holiday
            context.update({
                'holiday_name': holiday.get('name', ''),
                'holiday_date': holiday.get('date', ''),
                'holiday_type': holiday.get('type', ''),
                'holiday_greeting': self._get_holiday_greeting(holiday.get('name', '')),
            })
        
        # Location context
        context.update({
            'location': state.get('location', 'your city') if state else 'your city',
            'current_date': datetime.now().strftime('%B %d, %Y'),
            'current_month': datetime.now().strftime('%B'),
            'current_year': datetime.now().year,
        })
        
        # Add campaign-specific context
        context.update(self._get_campaign_specific_context(primary_vehicle, weather_data))
        
        return context
    
    def _get_primary_vehicle(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Get the primary vehicle for personalization (newest or most recently serviced)"""
        vehicles = customer.get('vehicles', [])
        if not vehicles:
            return {}
        
        # Prefer newest vehicle or most recently serviced
        primary_vehicle = max(vehicles, key=lambda v: (
            v.get('year', 0),
            v.get('last_service_date', '1900-01-01')
        ))
        
        return primary_vehicle
    
    def _get_service_context(self, vehicle: Dict[str, Any]) -> Dict[str, Any]:
        """Get service-related context for personalization"""
        days_since_service = days_since_last_service(vehicle.get('last_service_date'))
        vehicle_age = calculate_vehicle_age(vehicle.get('registration_date'))
        
        context = {}
        
        # Service urgency
        if days_since_service > 365:
            context['service_urgency'] = 'high'
            context['urgency_message'] = 'Your vehicle is overdue for service'
        elif days_since_service > 180:
            context['service_urgency'] = 'medium'
            context['urgency_message'] = 'Your vehicle is due for service soon'
        else:
            context['service_urgency'] = 'low'
            context['urgency_message'] = 'Your vehicle service is up to date'
        
        # Service recommendations
        context['recommended_services'] = self._get_recommended_services(vehicle_age, days_since_service)
        
        # Warranty status
        warranty_end = vehicle.get('warranty_end')
        if warranty_end:
            from utils.helpers import days_until_warranty_expiry
            warranty_days_left = days_until_warranty_expiry(warranty_end)
            
            if 0 <= warranty_days_left <= 30:
                context['warranty_status'] = 'expiring_soon'
                context['warranty_message'] = f'Your warranty expires in {warranty_days_left} days'
            elif warranty_days_left < 0:
                context['warranty_status'] = 'expired'
                context['warranty_message'] = 'Your warranty has expired'
            else:
                context['warranty_status'] = 'active'
                context['warranty_message'] = f'Your warranty is valid for {warranty_days_left} more days'
        
        return context
    
    def _get_recommended_services(self, vehicle_age: int, days_since_service: int) -> List[str]:
        """Get service recommendations based on vehicle age and service history"""
        services = []
        
        if days_since_service > 180:
            services.append("Oil change and filter replacement")
            services.append("Brake system inspection")
            services.append("Tire rotation and alignment check")
        
        if vehicle_age >= 3:
            services.extend([
                "Comprehensive safety inspection",
                "AC system service",
                "Battery health check"
            ])
        
        if vehicle_age >= 5:
            services.extend([
                "Timing belt inspection",
                "Transmission service",
                "Suspension system check"
            ])
        
        return services[:4]  # Limit to 4 services
    
    def _get_campaign_specific_context(self, 
                                     vehicle: Dict[str, Any], 
                                     weather_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get campaign-specific context"""
        context = {}
        
        # Seasonal context
        current_month = datetime.now().month
        if current_month in [6, 7, 8, 9]:  # Monsoon/Summer
            context['seasonal_services'] = [
                'AC system check and service',
                'Wiper blade replacement',
                'Tire grip inspection',
                'Brake system service'
            ]
            context['season'] = 'monsoon'
        elif current_month in [10, 11, 12, 1]:  # Winter
            context['seasonal_services'] = [
                'Battery health check',
                'Engine warm-up service',
                'Heating system inspection',
                'Antifreeze level check'
            ]
            context['season'] = 'winter'
        else:  # Spring/Summer
            context['seasonal_services'] = [
                'AC system maintenance',
                'Cooling system check',
                'Tire pressure adjustment',
                'Comprehensive inspection'
            ]
            context['season'] = 'summer'
        
        # Weather-specific services
        if weather_data:
            condition = weather_data.get('condition', '').lower()
            if 'rain' in condition or 'storm' in condition:
                context['weather_services'] = [
                    'Wiper blade replacement',
                    'Brake system inspection',
                    'Tire tread check',
                    'Electrical system protection'
                ]
            elif weather_data.get('temperature', 0) > 35:
                context['weather_services'] = [
                    'AC system service',
                    'Cooling system check',
                    'Battery cooling inspection',
                    'Tire pressure adjustment'
                ]
        
        # Default offers
        context.update({
            'discount': '20',
            'offer_expiry_date': datetime.now().strftime('%B %d, %Y'),
            'special_offer': 'Free multi-point inspection with any service',
            'cta_link': '#book-service',
            'company_name': 'Premium Auto Services'
        })
        
        return context
    
    def _personalize_subject_line(self, 
                                subject_template: str, 
                                context: Dict[str, Any], 
                                vehicle: Dict[str, Any]) -> str:
        """Personalize email subject line"""
        try:
            template = Template(subject_template)
            personalized = template.render(**context)
            
            # Ensure subject line is not too long
            if len(personalized) > 78:  # Email subject limit
                # Try to shorten by removing some details
                short_template = subject_template.replace("{{ customer_name }}, ", "")
                template = Template(short_template)
                personalized = template.render(**context)
            
            return personalized
            
        except Exception as e:
            logger.warning(f"Error personalizing subject line: {e}")
            # Fallback to simple personalization
            return f"Service Update for Your {context.get('vehicle_make', 'Vehicle')}"
    
    def _personalize_content(self, 
                           content_template: str, 
                           context: Dict[str, Any], 
                           vehicle: Dict[str, Any], 
                           campaign: Dict[str, Any]) -> str:
        """Personalize email content"""
        try:
            # Use base email template and inject personalized content
            base_template = Template(BASE_EMAIL_TEMPLATE)
            content_template_obj = Template(content_template)
            
            # Render the content part
            personalized_content = content_template_obj.render(**context)
            
            # Render the full email with the personalized content
            full_context = {**context, 'content': personalized_content}
            full_email = base_template.render(**full_context)
            
            return full_email
            
        except Exception as e:
            logger.warning(f"Error personalizing content: {e}")
            # Fallback to basic personalization
            return self._create_fallback_content(context, campaign)
    
    def _create_fallback_content(self, context: Dict[str, Any], campaign: Dict[str, Any]) -> str:
        """Create fallback content if template personalization fails"""
        customer_name = context.get('customer_name', 'Valued Customer')
        vehicle_info = f"{context.get('vehicle_make', 'Your')} {context.get('vehicle_model', 'Vehicle')}"
        
        fallback_content = f"""
        <html>
        <body>
            <h2>Hello {customer_name},</h2>
            <p>We hope this message finds you well.</p>
            
            <p>This is a service reminder for your {vehicle_info}.</p>
            
            <p>Our team would like to help you maintain your vehicle in excellent condition. 
            Please contact us to schedule your next service appointment.</p>
            
            <p>Thank you for choosing our services.</p>
            
            <p>Best regards,<br>Your Service Team</p>
        </body>
        </html>
        """
        
        return fallback_content
    
    def _get_holiday_greeting(self, holiday_name: str) -> str:
        """Get appropriate greeting for holiday"""
        greetings = {
            'diwali': 'May this Festival of Lights bring joy and prosperity to your journey!',
            'holi': 'Wishing you a colorful and joyful Holi celebration!',
            'dussehra': 'May the victory of good over evil inspire your travels!',
            'christmas': 'Wishing you a Merry Christmas and safe travels!',
            'new year': 'Wishing you a Happy New Year filled with smooth journeys!',
            'eid': 'Eid Mubarak! May your celebrations be filled with joy!',
        }
        
        holiday_lower = holiday_name.lower()
        for key, greeting in greetings.items():
            if key in holiday_lower:
                return greeting
        
        return f"Wishing you a wonderful {holiday_name} celebration!"
    
    def _log_step(self, message: str):
        """Log step with agent name"""
        logger.info(f"[{self.agent_name}] {message}")