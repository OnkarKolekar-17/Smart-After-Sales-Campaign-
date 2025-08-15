"""
Utility functions for the Smart After-Sales Campaign system
"""

import re
import json
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

def generate_campaign_id() -> str:
    """Generate a unique campaign ID"""
    return str(uuid.uuid4())

def clean_email(email: str) -> str:
    """Clean and validate email address"""
    if not email:
        return ""
    email = email.strip().lower()
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return email
    return ""

def clean_phone(phone: str) -> str:
    """Clean phone number"""
    if not phone:
        return ""
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    return cleaned if len(cleaned) >= 10 else ""

def calculate_vehicle_age(registration_date: Union[date, str]) -> int:
    """Calculate vehicle age in years"""
    if isinstance(registration_date, str):
        try:
            registration_date = datetime.strptime(registration_date, '%Y-%m-%d').date()
        except ValueError:
            return 0
    
    if not isinstance(registration_date, date):
        return 0
    
    today = date.today()
    age = today.year - registration_date.year
    if today.month < registration_date.month or (today.month == registration_date.month and today.day < registration_date.day):
        age -= 1
    
    return max(0, age)

def days_since_last_service(last_service_date: Union[date, str]) -> int:
    """Calculate days since last service"""
    if isinstance(last_service_date, str):
        try:
            last_service_date = datetime.strptime(last_service_date, '%Y-%m-%d').date()
        except ValueError:
            return 9999  # Very large number if date is invalid
    
    if not isinstance(last_service_date, date):
        return 9999
    
    return (date.today() - last_service_date).days

def days_until_warranty_expiry(warranty_end: Union[date, str]) -> int:
    """Calculate days until warranty expiry"""
    if isinstance(warranty_end, str):
        try:
            warranty_end = datetime.strptime(warranty_end, '%Y-%m-%d').date()
        except ValueError:
            return -1  # Negative if date is invalid
    
    if not isinstance(warranty_end, date):
        return -1
    
    return (warranty_end - date.today()).days

def is_warranty_expiring_soon(warranty_end: Union[date, str], days_threshold: int = 30) -> bool:
    """Check if warranty is expiring within threshold days"""
    days_left = days_until_warranty_expiry(warranty_end)
    return 0 <= days_left <= days_threshold

def format_currency(amount: float, currency: str = "₹") -> str:
    """Format amount as currency"""
    if amount is None:
        return f"{currency}0.00"
    return f"{currency}{amount:,.2f}"

def personalize_content(template: str, customer_data: Dict[str, Any]) -> str:
    """Personalize content using Jinja2 template"""
    try:
        template_obj = Template(template)
        return template_obj.render(**customer_data)
    except Exception as e:
        logger.error(f"Error personalizing content: {e}")
        return template

def extract_personalization_fields(template: str) -> List[str]:
    """Extract personalization field names from a template"""
    pattern = r'\{\{\s*(\w+)\s*\}\}'
    fields = re.findall(pattern, template)
    return list(set(fields))  # Remove duplicates

def safe_json_load(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with fallback"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default or {}

def safe_json_dump(data: Any, default: str = "{}") -> str:
    """Safely dump data to JSON string"""
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return default

def get_season(date_obj: Union[date, datetime] = None) -> str:
    """Determine current season based on date"""
    if date_obj is None:
        date_obj = date.today()
    elif isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    month = date_obj.month
    
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:  # [9, 10, 11]
        return "autumn"

def get_next_service_recommendation(last_service_date: Union[date, str], service_type: str = "") -> Dict[str, Any]:
    """Get next service recommendation based on last service"""
    days_since = days_since_last_service(last_service_date)
    
    if days_since >= 365:
        urgency = "high"
        message = "Annual service is overdue"
    elif days_since >= 180:
        urgency = "medium"
        message = "Half-yearly service recommended"
    elif days_since >= 90:
        urgency = "low"
        message = "Quarterly check-up available"
    else:
        urgency = "none"
        message = "Service up to date"
    
    return {
        "urgency": urgency,
        "message": message,
        "days_since": days_since,
        "recommended_service": get_recommended_service_type(days_since, service_type)
    }

def get_recommended_service_type(days_since: int, last_service_type: str = "") -> str:
    """Recommend service type based on days since last service"""
    if days_since >= 365:
        return "Annual Comprehensive Service"
    elif days_since >= 180:
        return "Half-yearly Maintenance"
    elif days_since >= 90:
        return "Quarterly Check-up"
    elif days_since >= 30:
        return "Oil Change & Basic Check"
    else:
        return "No service needed"

def batch_list(items: List[Any], batch_size: int = 50) -> List[List[Any]]:
    """Split list into batches of specified size"""
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that required fields are present and not empty"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            missing_fields.append(field)
    return missing_fields

def sanitize_for_email(text: str) -> str:
    """Sanitize text for email content"""
    if not text:
        return ""
    
    # Remove potentially harmful HTML tags while keeping basic formatting
    allowed_tags = ['b', 'i', 'u', 'br', 'p', 'strong', 'em']
    # This is a simple implementation - in production, use a proper HTML sanitizer
    return text.strip()

def get_time_period_description(days: int) -> str:
    """Convert days to human-readable time period"""
    if days < 7:
        return f"{days} day{'s' if days != 1 else ''}"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''}"
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months != 1 else ''}"
    else:
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''}"

def create_email_preview_text(content: str, max_length: int = 150) -> str:
    """Create preview text for email from content"""
    # Remove HTML tags and get plain text
    plain_text = re.sub('<[^<]+?>', '', content)
    # Remove extra whitespace
    plain_text = ' '.join(plain_text.split())
    
    if len(plain_text) <= max_length:
        return plain_text
    
    # Truncate at word boundary
    truncated = plain_text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  # If we have a good word boundary
        truncated = truncated[:last_space]
    
    return truncated + "..."

def log_performance(operation: str, start_time: datetime, additional_info: Dict[str, Any] = None):
    """Log performance metrics"""
    execution_time = (datetime.now() - start_time).total_seconds()
    info = additional_info or {}
    info['execution_time'] = execution_time
    
    logger.info(f"Performance - {operation}: {info}")
    
    # Log warning if operation takes too long
    if execution_time > 30:  # 30 seconds threshold
        logger.warning(f"Slow operation detected - {operation}: {execution_time:.2f}s")