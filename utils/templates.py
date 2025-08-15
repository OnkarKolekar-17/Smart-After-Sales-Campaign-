"""
Email templates for different campaign types
"""

from typing import Dict, Any

# Base email template structure
BASE_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject_line }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px 20px; background-color: #f8f9fa; }
        .cta-button { display: inline-block; background-color: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .cta-button:hover { background-color: #2980b9; }
        .footer { background-color: #34495e; color: white; padding: 20px; text-align: center; font-size: 12px; }
        .highlight { background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0; }
        .vehicle-info { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; border: 1px solid #dee2e6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name | default("Your Trusted Auto Service") }}</h1>
    </div>
    
    <div class="content">
        <h2>Hello {{ customer_name }},</h2>
        {{ content }}
        
        <div style="text-align: center;">
            <a href="{{ cta_link | default('#') }}" class="cta-button">{{ cta_text }}</a>
        </div>
    </div>
    
    <div class="footer">
        <p>{{ company_name | default("Your Trusted Auto Service") }}</p>
        <p>{{ company_address | default("") }}</p>
        <p>{{ company_phone | default("") }} | {{ company_email | default("") }}</p>
        <p><a href="{{ unsubscribe_link | default('#') }}" style="color: #bdc3c7;">Unsubscribe</a></p>
    </div>
</body>
</html>
"""

# Template for seasonal maintenance campaigns
SEASONAL_MAINTENANCE_TEMPLATE = {
    "subject": "{{ season | title }} Service Special for Your {{ vehicle_make }} {{ vehicle_model }}",
    "content": """
        <p>As {{ season }} approaches, it's the perfect time to ensure your {{ vehicle_make }} {{ vehicle_model }} is ready for the changing conditions.</p>
        
        <div class="vehicle-info">
            <h3>Your Vehicle Details:</h3>
            <ul>
                <li><strong>Vehicle:</strong> {{ vehicle_make }} {{ vehicle_model }} ({{ vehicle_year }})</li>
                <li><strong>Last Service:</strong> {{ last_service_date | default("Not recorded") }}</li>
                <li><strong>Mileage:</strong> {{ mileage | default("N/A") }} km</li>
            </ul>
        </div>
        
        <div class="highlight">
            <h3>{{ season | title }} Service Recommendations:</h3>
            <ul>
                {% for service in seasonal_services %}
                <li>{{ service }}</li>
                {% endfor %}
            </ul>
        </div>
        
        <p>Book your {{ season }} service today and enjoy:</p>
        <ul>
            <li>✓ 20% discount on {{ season }} maintenance packages</li>
            <li>✓ Free multi-point inspection</li>
            <li>✓ Extended warranty on services</li>
            <li>✓ Priority booking slots</li>
        </ul>
        
        <p>Don't wait - this offer is valid only until {{ offer_expiry_date }}!</p>
    """,
    "cta_text": "Book {{ season | title }} Service Now"
}

# Template for holiday campaigns
HOLIDAY_CAMPAIGN_TEMPLATE = {
    "subject": "{{ holiday_name }} Special Offer - {{ discount }}% Off on Services!",
    "content": """
        <h2 style="color: #e74c3c;">🎉 {{ holiday_name }} Celebration Special! 🎉</h2>
        
        <p>Celebrate {{ holiday_name }} with special savings on your vehicle's maintenance!</p>
        
        <div class="vehicle-info">
            <h3>Your Vehicle:</h3>
            <p>{{ vehicle_make }} {{ vehicle_model }} ({{ vehicle_year }})</p>
        </div>
        
        <div class="highlight">
            <h3>🎁 {{ holiday_name }} Offer:</h3>
            <ul>
                <li><strong>{{ discount }}% OFF</strong> on all service packages</li>
                <li><strong>Free</strong> vehicle wash with any service</li>
                <li><strong>Complimentary</strong> safety inspection</li>
            </ul>
        </div>
        
        <p>{{ holiday_greeting | default("Make this " + holiday_name + " memorable with a perfectly maintained vehicle!") }}</p>
        
        <p><strong>Offer valid until {{ offer_end_date }}</strong></p>
    """,
    "cta_text": "Claim {{ holiday_name }} Offer"
}

# Template for vehicle lifecycle campaigns (warranty expiry, service due, etc.)
LIFECYCLE_CAMPAIGN_TEMPLATE = {
    "subject": "Important: {{ lifecycle_event }} for Your {{ vehicle_make }} {{ vehicle_model }}",
    "content": """
        <div class="highlight">
            <h3>⚠️ Important Notice for Your Vehicle</h3>
            <p><strong>{{ lifecycle_message }}</strong></p>
        </div>
        
        <div class="vehicle-info">
            <h3>Vehicle Information:</h3>
            <ul>
                <li><strong>Vehicle:</strong> {{ vehicle_make }} {{ vehicle_model }} ({{ vehicle_year }})</li>
                <li><strong>Registration:</strong> {{ registration_date }}</li>
                <li><strong>Last Service:</strong> {{ last_service_date | default("Not recorded") }}</li>
                {% if warranty_end_date %}
                <li><strong>Warranty Expires:</strong> {{ warranty_end_date }}</li>
                {% endif %}
            </ul>
        </div>
        
        <h3>Recommended Actions:</h3>
        <ul>
            {% for recommendation in recommendations %}
            <li>{{ recommendation }}</li>
            {% endfor %}
        </ul>
        
        <p>{{ urgency_message | default("Don't delay - ensure your vehicle's optimal performance and safety.") }}</p>
        
        {% if special_offer %}
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3>💰 Special Offer:</h3>
            <p>{{ special_offer }}</p>
        </div>
        {% endif %}
    """,
    "cta_text": "{{ cta_text | default('Schedule Service Now') }}"
}

# Template for weather-based campaigns
WEATHER_CAMPAIGN_TEMPLATE = {
    "subject": "{{ weather_condition }} Alert: Protect Your {{ vehicle_make }} {{ vehicle_model }}",
    "content": """
        <h2 style="color: #f39c12;">🌤️ Weather Alert for {{ location }}</h2>
        
        <div class="highlight">
            <h3>Current Weather Conditions:</h3>
            <ul>
                <li><strong>Condition:</strong> {{ weather_condition }}</li>
                <li><strong>Temperature:</strong> {{ temperature }}°C</li>
                <li><strong>Humidity:</strong> {{ humidity }}%</li>
            </ul>
            <p><strong>{{ weather_recommendation }}</strong></p>
        </div>
        
        <div class="vehicle-info">
            <h3>Your Vehicle:</h3>
            <p>{{ vehicle_make }} {{ vehicle_model }} ({{ vehicle_year }})</p>
        </div>
        
        <h3>Weather Protection Services:</h3>
        <ul>
            {% for service in weather_services %}
            <li>{{ service }}</li>
            {% endfor %}
        </ul>
        
        <p>{{ weather_message | default("Ensure your vehicle is ready for these weather conditions!") }}</p>
        
        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3>🛡️ Weather Protection Package:</h3>
            <p>{{ weather_package_description }}</p>
        </div>
    """,
    "cta_text": "Get Weather Protection"
}

# Template for geographic/location-based campaigns
GEOGRAPHIC_CAMPAIGN_TEMPLATE = {
    "subject": "Exclusive {{ location }} Offer for Your {{ vehicle_make }} {{ vehicle_model }}",
    "content": """
        <h2>📍 Special Offer for {{ location }} Residents</h2>
        
        <p>As a valued customer in {{ location }}, you're eligible for our exclusive local offer!</p>
        
        <div class="vehicle-info">
            <h3>Your Vehicle:</h3>
            <p>{{ vehicle_make }} {{ vehicle_model }} ({{ vehicle_year }})</p>
            <p><strong>Preferred Service Location:</strong> {{ preferred_location | default(location) }}</p>
        </div>
        
        <div class="highlight">
            <h3>🌟 {{ location }} Exclusive Benefits:</h3>
            <ul>
                {% for benefit in location_benefits %}
                <li>{{ benefit }}</li>
                {% endfor %}
            </ul>
        </div>
        
        <h3>Local Service Advantages:</h3>
        <ul>
            <li>✓ Convenient {{ location }} location</li>
            <li>✓ Local pickup and drop service</li>
            <li>✓ Same-day service availability</li>
            <li>✓ Local parts inventory</li>
        </ul>
        
        <p>{{ location_message | default("Experience the best automotive service right in your neighborhood!") }}</p>
    """,
    "cta_text": "Book Local Service"
}

# Template mappings for easy access
TEMPLATE_MAPPING = {
    "seasonal": SEASONAL_MAINTENANCE_TEMPLATE,
    "holiday": HOLIDAY_CAMPAIGN_TEMPLATE,
    "lifecycle": LIFECYCLE_CAMPAIGN_TEMPLATE,
    "weather": WEATHER_CAMPAIGN_TEMPLATE,
    "geographic": GEOGRAPHIC_CAMPAIGN_TEMPLATE
}

def get_template(campaign_type: str) -> Dict[str, str]:
    """Get template for specific campaign type"""
    return TEMPLATE_MAPPING.get(campaign_type.lower(), LIFECYCLE_CAMPAIGN_TEMPLATE)

def get_seasonal_services(season: str) -> list:
    """Get recommended services for each season"""
    services = {
        "spring": [
            "AC system check and service",
            "Tire pressure and tread inspection",
            "Battery and electrical system check",
            "Brake system inspection",
            "Engine oil change"
        ],
        "summer": [
            "AC system maintenance and refrigerant check",
            "Cooling system service",
            "Tire condition and pressure check",
            "Engine cooling fan inspection",
            "Comprehensive safety check"
        ],
        "monsoon": [
            "Wiper blade replacement",
            "Tire tread and grip inspection",
            "Brake system service",
            "Headlight and taillight check",
            "Electrical system waterproofing"
        ],
        "autumn": [
            "Winter preparation service",
            "Battery health check",
            "Heating system inspection",
            "Tire change to winter tires",
            "Comprehensive maintenance check"
        ],
        "winter": [
            "Engine warm-up system check",
            "Battery and starter inspection",
            "Antifreeze level check",
            "Heater and defrost system service",
            "Tire condition for winter driving"
        ]
    }
    return services.get(season.lower(), services["spring"])

def get_weather_services(weather_condition: str) -> list:
    """Get recommended services based on weather condition"""
    services = {
        "hot": [
            "AC system service and refrigerant top-up",
            "Engine cooling system check",
            "Tire pressure adjustment for hot weather",
            "Battery cooling system inspection"
        ],
        "cold": [
            "Battery health and starting system check",
            "Engine oil viscosity optimization",
            "Heating system service",
            "Winter tire installation"
        ],
        "rainy": [
            "Wiper blade replacement",
            "Brake system inspection for wet conditions",
            "Tire tread depth check",
            "Electrical system waterproofing"
        ],
        "humid": [
            "AC system dehumidification service",
            "Interior moisture control",
            "Electrical connection protection",
            "Air filter replacement"
        ]
    }
    return services.get(weather_condition.lower(), services["hot"])

# Common placeholder values for testing
SAMPLE_DATA = {
    "customer_name": "John Doe",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "vehicle_year": "2020",
    "last_service_date": "2024-06-15",
    "mileage": "25000",
    "location": "Mumbai",
    "season": "winter",
    "holiday_name": "Diwali",
    "discount": "25",
    "company_name": "Premium Auto Services",
    "offer_expiry_date": "2024-12-31"
}