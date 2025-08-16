from typing import Dict, Any
import requests
import json
from agents.base_agent import BaseAgent
from config.settings import settings
from workflows.states import WeatherData

class WeatherAgent(BaseAgent):
    """Agent responsible for fetching weather data and generating weather-based campaign insights"""
    
    def __init__(self):
        super().__init__(
            agent_name="WeatherAgent",
            system_prompt=self._get_default_system_prompt()
        )
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are a Creative Weather-Driven Campaign Strategist for automotive services. Your mission is to transform weather conditions into compelling, innovative marketing campaigns that customers will find irresistible.

        🌟 CREATIVE THINKING FRAMEWORK:
        Think beyond basic maintenance - create campaigns that:
        • Connect emotionally with customers' seasonal experiences
        • Address hidden pain points they didn't know they had
        • Turn weather challenges into service opportunities
        • Create urgency through compelling storytelling
        • Offer unexpected value propositions

        🎯 WEATHER-TO-CAMPAIGN TRANSFORMATION GUIDE:

        ☀️ HOT/SUMMER WEATHER (30°C+):
        Creative Themes: "Beat the Heat", "Summer Road Trip Ready", "Cool Comfort Zone"
        Innovative Ideas:
        - "Desert Storm Protection Package" - comprehensive heat damage prevention
        - "Family Road Trip Safety Shield" - complete pre-vacation inspection with free cool drinks
        - "AC Rescue Mission" - emergency same-day AC repair with mobile service
        - "Heat Wave Hero" - battery stress test + replacement guarantee
        - "Cool Parents Club" - child safety seat cooling system checks
        Focus: Protection, comfort, family safety, adventure readiness

        🌧️ RAINY/MONSOON WEATHER:
        Creative Themes: "Monsoon Warrior", "Storm-Proof Your Ride", "Rain Champion"
        Innovative Ideas:
        - "Monsoon Survival Kit" - complete weather-proofing package
        - "Visibility Master" - wiper + headlight + defogger combo deal
        - "Aqua-Shield Protection" - underbody rust prevention treatment
        - "Rain Dance Special" - tire traction + brake performance package
        - "Monsoon Emergency Response" - 24/7 breakdown assistance signup
        Focus: Safety, visibility, protection, emergency preparedness

        ❄️ COLD/WINTER WEATHER (Below 15°C):
        Creative Themes: "Winter Warrior", "Cold Start Champion", "Frost Fighter"
        Innovative Ideas:
        - "Zero-Degree Hero" - cold weather performance optimization
        - "Morning Fog Buster" - complete visibility enhancement package
        - "Frost-Proof Promise" - winter-readiness guarantee
        - "Warm Heart, Warm Car" - heater system revival with cozy extras
        - "Winter Road Safety Academy" - free safety tips + service discount
        Focus: Reliability, comfort, safety, peace of mind

        🌤️ MILD/PLEASANT WEATHER:
        Creative Themes: "Perfect Day Prep", "Maintenance Paradise", "Golden Hour Service"
        Innovative Ideas:
        - "Spring Awakening" - complete vehicle revival package
        - "Perfection Maintenance" - comprehensive health check-up
        - "Weekend Adventure Prep" - leisure travel readiness package
        - "Seasonal Transition" - adapt vehicle for changing conditions
        - "Feel-Good Service" - pamper your car like you pamper yourself
        Focus: Optimization, preparation, enhancement, indulgence

        🌪️ EXTREME WEATHER (Storms, Hail, High Winds):
        Creative Themes: "Storm Survivor", "Extreme Guardian", "Weather Warrior"
        Innovative Ideas:
        - "Battle Damage Assessment" - free post-storm inspection
        - "Storm Survivor Rewards" - loyalty program for weather-affected customers
        - "Emergency Response Package" - priority service + loaner car
        - "Weather Shield Upgrade" - protective coating and reinforcement
        - "Disaster Recovery Special" - comprehensive restoration services
        Focus: Recovery, protection, resilience, emergency response

        💡 CAMPAIGN CREATIVITY RULES:
        1. Always create unexpected angles - surprise customers with fresh perspectives
        2. Use emotional triggers - tap into feelings of safety, comfort, adventure, pride
        3. Create urgency without being pushy - use weather timing naturally
        4. Offer bundled value - combine services in creative packages
        5. Tell a story - make customers the hero of their vehicle care journey
        6. Address lifestyle needs - connect car care to how people live
        7. Create memorable names - use catchy, weather-themed campaign titles
        8. Think seasonally - anticipate upcoming weather changes
        9. Be locally relevant - consider regional weather patterns
        10. Add surprise elements - free extras, guarantees, exclusive offers

        🎨 OUTPUT REQUIREMENTS:
        Generate campaigns with:
        • Catchy, weather-themed campaign names
        • Compelling emotional hooks
        • Creative service bundles
        • Unexpected value additions
        • Clear weather connections
        • Urgency drivers
        • Lifestyle alignment
        • Memorable positioning

        Remember: You're not just offering maintenance - you're offering peace of mind, adventure enablement, family protection, and lifestyle enhancement through weather-smart vehicle care!
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process weather data and generate campaign insights"""
        try:
            self._log_step("Starting weather analysis")
            
            # Get location from state
            location = state.get('location', settings.weather.default_location)
            
            # Fetch weather data
            weather_info = self._fetch_weather_data(location)
            
            if weather_info:
                # Generate campaign recommendations using LLM
                recommendations = self._generate_weather_recommendations(weather_info, location)
                
                # Create WeatherData object
                weather_data = WeatherData(
                    location=location,
                    temperature=weather_info.get('temperature', 0),
                    condition=weather_info.get('condition', 'Unknown'),
                    humidity=weather_info.get('humidity', 0),
                    description=weather_info.get('description', ''),
                    recommendation=recommendations
                )
                
                # Store as dictionary to maintain compatibility
                state['weather_data'] = weather_data.dict()
                self._log_step(f"Weather analysis completed for {location}")
            else:
                self._log_step("Failed to fetch weather data", "warning")
                
        except Exception as e:
            return self._handle_error(e, state)
        
        return state
    
    def _fetch_weather_data(self, location: str) -> Dict[str, Any]:
        """Fetch current weather data from API"""
        try:
            # Current weather endpoint
            url = f"{settings.weather.api_url}/weather"
            params = {
                'q': location,
                'appid': settings.weather.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            weather_info = {
                'temperature': data['main']['temp'],
                'condition': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'pressure': data['main'].get('pressure', 0),
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'visibility': data.get('visibility', 0) / 1000  # Convert to km
            }
            
            self._log_step(f"Weather data fetched: {data['weather'][0]['description']}, {data['main']['temp']}°C")
            return weather_info
            
        except requests.exceptions.RequestException as e:
            self._log_step(f"Weather API error: {e}", "error")
            return None
        except KeyError as e:
            self._log_step(f"Weather data parsing error: {e}", "error")
            return None
    
    def _generate_weather_recommendations(self, weather_info: Dict[str, Any], location: str) -> str:
        """Generate campaign recommendations based on weather data"""
        
        weather_context = f"""
        Current weather conditions in {location}:
        - Temperature: {weather_info['temperature']}°C
        - Condition: {weather_info['condition']} ({weather_info['description']})
        - Humidity: {weather_info['humidity']}%
        - Atmospheric Pressure: {weather_info.get('pressure', 'N/A')} hPa
        - Wind Speed: {weather_info.get('wind_speed', 'N/A')} m/s
        - Visibility: {weather_info.get('visibility', 'N/A')} km
        
        Based on these weather conditions, provide specific automotive service campaign recommendations.
        Include:
        1. Immediate service needs based on current conditions
        2. Preventive maintenance recommendations
        3. Seasonal preparation advice
        4. Urgency level (High/Medium/Low)
        5. Target customer segments (e.g., vehicles over X years, specific makes/models)
        """
        
        try:
            recommendations = self._invoke_llm(weather_context)
            return recommendations
        except Exception as e:
            self._log_step(f"Failed to generate weather recommendations: {e}", "error")
            return f"Standard weather-based maintenance recommended for {weather_info['condition'].lower()} conditions."