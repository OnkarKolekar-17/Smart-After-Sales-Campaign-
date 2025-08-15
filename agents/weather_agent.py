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
        You are a Weather Analysis Agent specializing in automotive service campaigns.
        
        Your role is to analyze weather data and generate campaign recommendations for car services.
        
        Consider these factors:
        - Seasonal maintenance needs (AC service in summer, battery check in winter)
        - Weather-specific vehicle issues (monsoon car care, winter tire services)
        - Preventive maintenance based on upcoming weather patterns
        - Regional climate considerations
        
        Always provide actionable, specific recommendations that directly relate to vehicle maintenance and customer needs.
        
        Output your analysis in a clear, structured format focusing on:
        1. Weather impact on vehicles
        2. Recommended services
        3. Urgency level
        4. Seasonal considerations
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