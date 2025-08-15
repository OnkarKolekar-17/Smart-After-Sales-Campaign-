from typing import Dict, Any, List
import json
from agents.base_agent import BaseAgent
from workflows.states import CampaignContent

class CampaignGeneratorAgent(BaseAgent):
    """Agent responsible for generating campaign content using LLM"""
    
    def __init__(self):
        super().__init__(
            agent_name="CampaignGeneratorAgent",
            system_prompt=self._get_default_system_prompt()
        )
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are a Creative Campaign Generator Agent specializing in automotive service marketing.
        
        Your role is to create compelling, personalized campaign content that drives customer engagement and conversions.
        
        Key principles:
        1. Create emotionally resonant content that connects with customer needs
        2. Use clear, compelling calls-to-action
        3. Incorporate relevant context (weather, holidays, vehicle lifecycle)
        4. Maintain a professional yet friendly tone
        5. Focus on value proposition and customer benefits
        6. Include urgency when appropriate
        7. Ensure cultural sensitivity and local relevance
        
        Campaign Structure:
        - Campaign Title: Catchy, descriptive title for internal use
        - Subject Line: Email subject that maximizes open rates
        - Content: Full email body with personalization placeholders
        - CTA Text: Clear, action-oriented button text
        - Campaign Type: Category classification
        
        Always create campaigns that:
        - Address specific customer pain points
        - Highlight immediate and long-term benefits
        - Use persuasive but not pushy language
        - Include social proof when relevant
        - Maintain brand consistency and professionalism
        
        Output your response as a structured JSON format for easy parsing.
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multiple campaign contents based on all available context"""
        try:
            self._log_step("Starting comprehensive campaign content generation")
            
            # Gather all contexts from different agents
            weather_context = state.get('weather_data', {})
            holiday_context = state.get('holiday_data', {})
            lifecycle_campaigns = state.get('lifecycle_campaigns', [])
            targeted_customers = state.get('targeted_customers', [])
            location = state.get('location', 'Mumbai')
            
            # Generate multiple campaigns
            generated_campaigns = []
            
            # 1. Weather-based campaign (if weather data available)
            if weather_context:
                weather_campaign = self._generate_weather_campaign(weather_context, location, targeted_customers)
                if weather_campaign:
                    generated_campaigns.append(weather_campaign)
            
            # 2. Holiday-based campaign (if holiday data available)
            if holiday_context:
                holiday_campaign = self._generate_holiday_campaign(holiday_context, location, targeted_customers)
                if holiday_campaign:
                    generated_campaigns.append(holiday_campaign)
            
            # 3. Lifecycle-based campaigns (from vehicle lifecycle agent)
            for lifecycle_campaign in lifecycle_campaigns:
                lifecycle_content = self._generate_lifecycle_campaign(lifecycle_campaign, location)
                if lifecycle_content:
                    generated_campaigns.append(lifecycle_content)
            
            # Store all generated campaigns
            state['generated_campaigns'] = generated_campaigns
            state['total_campaigns'] = len(generated_campaigns)
            
            self._log_step(f"Generated {len(generated_campaigns)} different campaign types")
            
            # For compatibility with existing email sender, also store the first campaign as 'campaign_content'
            if generated_campaigns:
                state['campaign_content'] = generated_campaigns[0]
            
        except Exception as e:
            return self._handle_error(e, state)
        
        return state
    
    def _build_campaign_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive context for campaign generation"""
        
        context = {
            'campaign_trigger': state.get('campaign_trigger', 'scheduled'),
            'location': state.get('location', 'Mumbai'),
            'total_targeted': state.get('total_targeted', 0),
            'weather_data': None,
            'holiday_data': None,
            'customer_insights': []
        }
        
        # Add weather context
        if 'weather_data' in state and state['weather_data']:
            weather = state['weather_data']
            context['weather_data'] = {
                'temperature': weather.get('temperature', 0) if isinstance(weather, dict) else weather.temperature,
                'condition': weather.get('condition', '') if isinstance(weather, dict) else weather.condition,
                'description': weather.get('description', '') if isinstance(weather, dict) else weather.description,
                'recommendation': weather.get('recommendation', '') if isinstance(weather, dict) else weather.recommendation
            }
        
        # Add holiday context
        if 'holiday_data' in state and state['holiday_data']:
            holiday = state['holiday_data']
            context['holiday_data'] = {
                'name': holiday.get('name', '') if isinstance(holiday, dict) else holiday.name,
                'date': holiday.get('date', '') if isinstance(holiday, dict) else holiday.date,
                'type': holiday.get('type', '') if isinstance(holiday, dict) else holiday.type,
                'description': holiday.get('description', '') if isinstance(holiday, dict) else holiday.description,
                'cultural_significance': holiday.get('cultural_significance', '') if isinstance(holiday, dict) else holiday.cultural_significance
            }
        
        # Add customer segment insights
        if 'customer_segments' in state:
            customers = state['customer_segments']
            if customers:
                # Analyze customer segment characteristics
                context['customer_insights'] = self._analyze_customer_segments(customers)
        
        return context
    
    def _analyze_customer_segments(self, customers) -> List[Dict[str, Any]]:
        """Analyze customer segments to extract insights for campaign personalization"""
        
        insights = {
            'total_customers': len(customers),
            'vehicle_makes': {},
            'vehicle_age_distribution': {'new': 0, 'mid_age': 0, 'old': 0},
            'service_patterns': {'overdue': 0, 'regular': 0, 'new_customer': 0},
            'locations': {}
        }
        
        current_year = 2025
        
        for customer in customers:
            # Count locations
            location = customer.preferred_location or 'Unknown'
            insights['locations'][location] = insights['locations'].get(location, 0) + 1
            
            for vehicle in customer.vehicles:
                # Count makes
                make = vehicle.get('make', 'Unknown')
                insights['vehicle_makes'][make] = insights['vehicle_makes'].get(make, 0) + 1
                
                # Analyze vehicle age
                vehicle_year = vehicle.get('year', current_year)
                age = current_year - vehicle_year
                if age <= 3:
                    insights['vehicle_age_distribution']['new'] += 1
                elif age <= 8:
                    insights['vehicle_age_distribution']['mid_age'] += 1
                else:
                    insights['vehicle_age_distribution']['old'] += 1
                
                # Analyze service patterns
                last_service = vehicle.get('last_service_date')
                if not last_service:
                    insights['service_patterns']['new_customer'] += 1
                else:
                    # This is simplified - in reality you'd parse the date
                    insights['service_patterns']['regular'] += 1
        
        return insights
    
    def _generate_campaign_content(self, context: Dict[str, Any]) -> CampaignContent:
        """Generate campaign content using LLM"""
        
        prompt = f"""
        Create a compelling automotive service campaign based on the following context:
        
        Campaign Context:
        {json.dumps(context, indent=2, default=str)}
        
        Requirements:
        1. Create content that resonates with the target audience
        2. Incorporate relevant weather/holiday context if available
        3. Address specific vehicle service needs
        4. Include compelling offers or value propositions
        5. Use personalization opportunities
        6. Maintain professional yet approachable tone
        
        Please provide your response in this exact JSON format:
        {{
            "title": "Internal campaign title",
            "subject_line": "Email subject line (max 50 chars)",
            "content": "Full email content with {{personalization}} placeholders",
            "cta_text": "Call to action button text",
            "campaign_type": "seasonal/holiday/lifecycle/weather/geographic",
            "personalization_factors": {{
                "key1": "description1",
                "key2": "description2"
            }}
        }}
        """
        
        try:
            response = self._invoke_llm(prompt)
            
            # Parse JSON response
            try:
                campaign_data = json.loads(response)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                campaign_data = self._create_fallback_campaign(context)
            
            # Create CampaignContent object
            campaign_content = CampaignContent(
                title=campaign_data.get('title', 'Service Reminder Campaign'),
                subject_line=campaign_data.get('subject_line', 'Your Vehicle Service is Due'),
                content=campaign_data.get('content', self._get_default_content()),
                cta_text=campaign_data.get('cta_text', 'Book Service Now'),
                campaign_type=campaign_data.get('campaign_type', 'lifecycle'),
                personalization_factors=campaign_data.get('personalization_factors', {})
            )
            
            return campaign_content
            
        except Exception as e:
            self._log_step(f"Error generating campaign content: {e}", "error")
            return self._create_fallback_campaign(context)
    
    def _create_fallback_campaign(self, context: Dict[str, Any]) -> CampaignContent:
        """Create a fallback campaign if LLM generation fails"""
        
        # Determine campaign type based on context
        campaign_type = "scheduled"
        title = "Vehicle Service Reminder"
        subject_line = "Your Vehicle Needs Attention"
        
        if context.get('holiday_data'):
            campaign_type = "holiday"
            holiday_name = context['holiday_data'].get('name', 'Festival')
            title = f"{holiday_name} Vehicle Preparation"
            subject_line = f"Prepare Your Vehicle for {holiday_name}"
        elif context.get('weather_data'):
            campaign_type = "weather"
            condition = context['weather_data'].get('condition', 'Current Weather')
            title = f"{condition} Weather Vehicle Care"
            subject_line = f"Vehicle Care for {condition} Conditions"
        
        content = self._get_default_content()
        
        return CampaignContent(
            title=title,
            subject_line=subject_line,
            content=content,
            cta_text="Schedule Service",
            campaign_type=campaign_type,
            personalization_factors={
                "customer_name": "Customer's name",
                "vehicle_info": "Vehicle make and model",
                "service_due": "Service due information"
            }
        )
    
    def _get_default_content(self) -> str:
        """Get default email content template"""
        return """
Dear {{customer_name}},

We hope this message finds you well. Our records indicate that your {{vehicle_info}} may be due for service attention.

Regular maintenance is crucial for:
• Vehicle safety and reliability
• Optimal performance and fuel efficiency  
• Maintaining warranty coverage
• Preventing costly repairs

Our expert technicians are ready to provide:
✓ Comprehensive vehicle inspection
✓ Quality parts and service
✓ Convenient scheduling options
✓ Competitive pricing

Don't wait until it's too late. Book your service appointment today and ensure your vehicle stays in perfect condition.

Best regards,
The Service Team

P.S. Contact us if you have any questions about your vehicle's maintenance needs.
"""
    
    def _generate_weather_campaign(self, weather_data: Dict, location: str, customers: List) -> Dict[str, Any]:
        """Generate weather-specific campaign content"""
        
        context = f"""
        Generate a weather-based vehicle service campaign for {location}.
        
        Weather Context:
        - Temperature: {weather_data.get('temperature', 'N/A')}°C
        - Condition: {weather_data.get('condition', 'N/A')}
        - Description: {weather_data.get('description', 'N/A')}
        - Recommendation: {weather_data.get('recommendation', 'N/A')}
        
        Create a campaign that addresses vehicle needs based on current weather conditions.
        Target customers: {len(customers)} customers in {location}
        
        Focus on weather-related vehicle maintenance needs, seasonal preparations, and safety considerations.
        """
        
        try:
            response = self._invoke_llm(context + self._get_campaign_format_instructions())
            campaign_data = json.loads(response)
            campaign_data['campaign_type'] = 'weather'
            campaign_data['target_customers'] = [c for c in customers]
            return campaign_data
        except:
            return self._create_weather_fallback_campaign(weather_data, location, customers)
    
    def _generate_holiday_campaign(self, holiday_data: Dict, location: str, customers: List) -> Dict[str, Any]:
        """Generate holiday-specific campaign content"""
        
        context = f"""
        Generate a holiday-based vehicle service campaign for {location}.
        
        Holiday Context:
        - Holiday: {holiday_data.get('name', 'N/A')}
        - Date: {holiday_data.get('date', 'N/A')}
        - Type: {holiday_data.get('type', 'N/A')}
        - Cultural Significance: {holiday_data.get('cultural_significance', 'N/A')}
        
        Create a campaign that connects the holiday celebration with vehicle care needs.
        Target customers: {len(customers)} customers in {location}
        
        Focus on holiday travel preparation, family safety, and celebration-related vehicle needs.
        """
        
        try:
            response = self._invoke_llm(context + self._get_campaign_format_instructions())
            campaign_data = json.loads(response)
            campaign_data['campaign_type'] = 'holiday'
            campaign_data['target_customers'] = [c for c in customers]
            return campaign_data
        except:
            return self._create_holiday_fallback_campaign(holiday_data, location, customers)
    
    def _generate_lifecycle_campaign(self, lifecycle_data: Dict, location: str) -> Dict[str, Any]:
        """Generate lifecycle-specific campaign content"""
        
        segment = lifecycle_data.get('segment', 'general')
        campaign_type = lifecycle_data.get('campaign_type', 'lifecycle')
        target_customers = lifecycle_data.get('target_customers', [])
        benefits = lifecycle_data.get('benefits', [])
        title = lifecycle_data.get('title', 'Vehicle Service Campaign')
        
        context = f"""
        Generate a vehicle lifecycle-based campaign for {location}.
        
        Lifecycle Context:
        - Campaign Type: {campaign_type}
        - Customer Segment: {segment}
        - Title: {title}
        - Benefits: {', '.join(benefits) if benefits else 'N/A'}
        - Target Customers: {len(target_customers)} customers
        
        Create a campaign that addresses specific vehicle lifecycle needs for this customer segment.
        Focus on the benefits and urgency appropriate for their vehicle's stage of life.
        """
        
        try:
            response = self._invoke_llm(context + self._get_campaign_format_instructions())
            campaign_data = json.loads(response)
            campaign_data['campaign_type'] = campaign_type
            campaign_data['segment'] = segment
            campaign_data['target_customers'] = target_customers
            return campaign_data
        except:
            return self._create_lifecycle_fallback_campaign(lifecycle_data, location)
    
    def _get_campaign_format_instructions(self) -> str:
        """Get format instructions for campaign generation"""
        return """
        
        Provide your response as a JSON object with this exact structure:
        {
            "title": "Internal campaign title",
            "subject_line": "Email subject line (max 50 chars)",
            "content": "Full email content with {{customer_name}}, {{vehicle_info}}, etc. placeholders",
            "cta_text": "Call to action button text",
            "personalization_factors": {
                "customer_name": "Customer's name",
                "vehicle_info": "Vehicle make and model",
                "last_service_date": "Last service date",
                "next_service_due": "Next service due date"
            }
        }
        """
    
    def _create_weather_fallback_campaign(self, weather_data: Dict, location: str, customers: List) -> Dict[str, Any]:
        """Fallback weather campaign"""
        condition = weather_data.get('condition', 'Current Weather')
        return {
            'title': f'{condition} Weather Vehicle Care - {location}',
            'subject_line': f'Prepare Your Vehicle for {condition} Weather',
            'content': f'Dear {{{{customer_name}}}}, with {condition.lower()} weather in {location}, ensure your {{{{vehicle_info}}}} is properly maintained for safe driving.',
            'cta_text': 'Schedule Weather Check',
            'campaign_type': 'weather',
            'target_customers': customers,
            'personalization_factors': {'customer_name': 'Name', 'vehicle_info': 'Vehicle'}
        }
    
    def _create_holiday_fallback_campaign(self, holiday_data: Dict, location: str, customers: List) -> Dict[str, Any]:
        """Fallback holiday campaign"""
        holiday_name = holiday_data.get('name', 'Upcoming Holiday')
        return {
            'title': f'{holiday_name} Vehicle Preparation - {location}',
            'subject_line': f'Prepare Your Vehicle for {holiday_name}',
            'content': f'Dear {{{{customer_name}}}}, with {holiday_name} approaching, ensure your {{{{vehicle_info}}}} is ready for holiday travels and celebrations.',
            'cta_text': 'Book Holiday Service',
            'campaign_type': 'holiday', 
            'target_customers': customers,
            'personalization_factors': {'customer_name': 'Name', 'vehicle_info': 'Vehicle'}
        }
    
    def _create_lifecycle_fallback_campaign(self, lifecycle_data: Dict, location: str) -> Dict[str, Any]:
        """Fallback lifecycle campaign"""
        title = lifecycle_data.get('title', 'Vehicle Service Campaign')
        segment = lifecycle_data.get('segment', 'general')
        return {
            'title': title,
            'subject_line': f'Important: {title[:40]}',
            'content': f'Dear {{{{customer_name}}}}, your {{{{vehicle_info}}}} needs attention based on its current lifecycle stage.',
            'cta_text': 'Schedule Service',
            'campaign_type': lifecycle_data.get('campaign_type', 'lifecycle'),
            'segment': segment,
            'target_customers': lifecycle_data.get('target_customers', []),
            'personalization_factors': {'customer_name': 'Name', 'vehicle_info': 'Vehicle'}
        }