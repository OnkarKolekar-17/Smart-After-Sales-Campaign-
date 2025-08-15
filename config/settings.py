import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from dataclasses import dataclass

load_dotenv()

@dataclass
class DatabaseConfig:
    host: str = os.getenv('DB_HOST', 'localhost')
    database: str = os.getenv('DB_NAME', 'car_campaigns')
    user: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD')
    port: str = os.getenv('DB_PORT', '5432')

@dataclass
class OpenAIConfig:
    api_key: str = os.getenv('OPENAI_API_KEY')
    model: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    temperature: float = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    max_tokens: int = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))

@dataclass
class WeatherConfig:
    api_key: str = os.getenv('WEATHER_API_KEY')
    api_url: str = os.getenv('WEATHER_API_URL', 'https://api.openweathermap.org/data/2.5')
    default_location: str = os.getenv('DEFAULT_LOCATION', 'Mumbai')

@dataclass
class BrevoConfig:
    api_key: str = os.getenv('BREVO_API_KEY')
    sender_email: str = os.getenv('BREVO_SENDER_EMAIL')
    sender_name: str = os.getenv('BREVO_SENDER_NAME', 'Smart Campaigns')

@dataclass
class CampaignConfig:
    batch_size: int = int(os.getenv('CAMPAIGN_BATCH_SIZE', '50'))
    max_retry_attempts: int = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
    
    # Campaign types mapping
    campaign_types: Dict[str, str] = None
    
    def __post_init__(self):
        if self.campaign_types is None:
            self.campaign_types = {
                'seasonal': 'Seasonal Maintenance',
                'holiday': 'Holiday Special Offers',
                'lifecycle': 'Vehicle Lifecycle Based',
                'weather': 'Weather-Based Services',
                'geographic': 'Location-Specific Campaigns'
            }

class Settings:
    def __init__(self):
        self.database = DatabaseConfig()
        self.openai = OpenAIConfig()
        self.weather = WeatherConfig()
        self.brevo = BrevoConfig()
        self.campaigns = CampaignConfig()
        
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that all required settings are present"""
        required_vars = [
            ('OPENAI_API_KEY', self.openai.api_key),
            ('WEATHER_API_KEY', self.weather.api_key),
            ('BREVO_API_KEY', self.brevo.api_key),
            ('BREVO_SENDER_EMAIL', self.brevo.sender_email),
            ('DB_PASSWORD', self.database.password)
        ]
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Global settings instance
settings = Settings()