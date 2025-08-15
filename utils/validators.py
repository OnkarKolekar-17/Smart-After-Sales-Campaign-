"""
Validation functions for the Smart After-Sales Campaign system
"""

import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from email_validator import validate_email, EmailNotValidError
import logging

logger = logging.getLogger(__name__)

def validate_email_address(email: str) -> tuple[bool, str]:
    """
    Validate email address format and deliverability
    Returns (is_valid, normalized_email)
    """
    if not email or not isinstance(email, str):
        return False, ""
    
    try:
        # Clean the email
        email = email.strip().lower()
        
        # Basic regex check first
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, ""
        
        # Use email-validator for more thorough validation
        valid_email = validate_email(email)
        return True, valid_email.email
    except EmailNotValidError:
        return False, ""
    except Exception as e:
        logger.warning(f"Email validation error for {email}: {e}")
        return False, ""

def validate_phone_number(phone: str, country_code: str = "+91") -> tuple[bool, str]:
    """
    Validate phone number format
    Returns (is_valid, formatted_phone)
    """
    if not phone or not isinstance(phone, str):
        return False, ""
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    
    # Handle Indian phone numbers
    if country_code == "+91":
        # Remove country code if present
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) > 10:
            cleaned = cleaned[2:]
        
        # Check if it's a valid 10-digit Indian mobile number
        if re.match(r'^[6-9]\d{9}$', cleaned):
            return True, f"+91{cleaned}"
    
    # Generic validation for other formats
    if 10 <= len(cleaned) <= 15:
        return True, cleaned
    
    return False, ""

def validate_vin(vin: str) -> bool:
    """Validate Vehicle Identification Number (VIN)"""
    if not vin or not isinstance(vin, str):
        return False
    
    vin = vin.upper().strip()
    
    # VIN should be 17 characters
    if len(vin) != 17:
        return False
    
    # VIN should contain only alphanumeric characters (excluding I, O, Q)
    if not re.match(r'^[ABCDEFGHJKLMNPRSTUVWXYZ0-9]{17}$', vin):
        return False
    
    return True

def validate_date(date_input: Union[str, date, datetime], date_format: str = "%Y-%m-%d") -> tuple[bool, Optional[date]]:
    """
    Validate date format and convert to date object
    Returns (is_valid, date_object)
    """
    if isinstance(date_input, date):
        return True, date_input
    
    if isinstance(date_input, datetime):
        return True, date_input.date()
    
    if not isinstance(date_input, str):
        return False, None
    
    try:
        parsed_date = datetime.strptime(date_input.strip(), date_format).date()
        return True, parsed_date
    except ValueError:
        # Try alternative formats
        alternative_formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%m/%d/%Y"]
        for fmt in alternative_formats:
            try:
                parsed_date = datetime.strptime(date_input.strip(), fmt).date()
                return True, parsed_date
            except ValueError:
                continue
        return False, None

def validate_vehicle_year(year: Union[int, str]) -> bool:
    """Validate vehicle year"""
    try:
        year_int = int(year)
        current_year = datetime.now().year
        # Vehicle years should be between 1900 and current year + 1 (for next year models)
        return 1900 <= year_int <= current_year + 1
    except (ValueError, TypeError):
        return False

def validate_mileage(mileage: Union[int, str]) -> bool:
    """Validate vehicle mileage"""
    try:
        mileage_int = int(mileage)
        # Reasonable range for vehicle mileage (0 to 1 million km)
        return 0 <= mileage_int <= 1000000
    except (ValueError, TypeError):
        return False

def validate_campaign_type(campaign_type: str) -> bool:
    """Validate campaign type"""
    valid_types = ["seasonal", "holiday", "lifecycle", "weather", "geographic", "maintenance", "warranty"]
    return campaign_type.lower() in valid_types

def validate_location(location: str) -> bool:
    """Validate location format"""
    if not location or not isinstance(location, str):
        return False
    
    location = location.strip()
    # Location should be at least 2 characters and contain only letters, spaces, and common punctuation
    return len(location) >= 2 and re.match(r'^[a-zA-Z\s\-\,\.]+$', location)

def validate_currency_amount(amount: Union[int, float, str]) -> tuple[bool, Optional[float]]:
    """
    Validate currency amount
    Returns (is_valid, normalized_amount)
    """
    try:
        if isinstance(amount, str):
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[₹$€£\s,]', '', amount.strip())
            amount_float = float(cleaned)
        else:
            amount_float = float(amount)
        
        # Amount should be non-negative and reasonable (up to 10 million)
        if 0 <= amount_float <= 10000000:
            return True, round(amount_float, 2)
        return False, None
    except (ValueError, TypeError):
        return False, None

def validate_customer_data(customer_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate customer data dictionary
    Returns dictionary with field names as keys and error messages as values
    """
    errors = {}
    
    # Required fields
    required_fields = ["name", "email"]
    for field in required_fields:
        if field not in customer_data or not customer_data[field]:
            errors[field] = [f"{field} is required"]
    
    # Validate email
    if "email" in customer_data and customer_data["email"]:
        is_valid, _ = validate_email_address(customer_data["email"])
        if not is_valid:
            errors.setdefault("email", []).append("Invalid email format")
    
    # Validate phone if provided
    if "phone" in customer_data and customer_data["phone"]:
        is_valid, _ = validate_phone_number(customer_data["phone"])
        if not is_valid:
            errors.setdefault("phone", []).append("Invalid phone number format")
    
    # Validate name format
    if "name" in customer_data and customer_data["name"]:
        name = str(customer_data["name"]).strip()
        if len(name) < 2:
            errors.setdefault("name", []).append("Name must be at least 2 characters")
        elif not re.match(r'^[a-zA-Z\s\-\.]+$', name):
            errors.setdefault("name", []).append("Name contains invalid characters")
    
    return errors

def validate_vehicle_data(vehicle_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate vehicle data dictionary
    Returns dictionary with field names as keys and error messages as values
    """
    errors = {}
    
    # Required fields
    required_fields = ["make", "model", "year"]
    for field in required_fields:
        if field not in vehicle_data or not vehicle_data[field]:
            errors[field] = [f"{field} is required"]
    
    # Validate year
    if "year" in vehicle_data and vehicle_data["year"]:
        if not validate_vehicle_year(vehicle_data["year"]):
            errors.setdefault("year", []).append("Invalid vehicle year")
    
    # Validate VIN if provided
    if "vin" in vehicle_data and vehicle_data["vin"]:
        if not validate_vin(vehicle_data["vin"]):
            errors.setdefault("vin", []).append("Invalid VIN format")
    
    # Validate mileage if provided
    if "mileage" in vehicle_data and vehicle_data["mileage"]:
        if not validate_mileage(vehicle_data["mileage"]):
            errors.setdefault("mileage", []).append("Invalid mileage value")
    
    # Validate dates
    date_fields = ["registration_date", "last_service_date", "warranty_start", "warranty_end"]
    for field in date_fields:
        if field in vehicle_data and vehicle_data[field]:
            is_valid, _ = validate_date(vehicle_data[field])
            if not is_valid:
                errors.setdefault(field, []).append(f"Invalid date format for {field}")
    
    return errors

def validate_campaign_content(content: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate campaign content
    Returns dictionary with field names as keys and error messages as values
    """
    errors = {}
    
    # Required fields
    required_fields = ["campaign_title", "subject_line", "content", "campaign_type"]
    for field in required_fields:
        if field not in content or not content[field]:
            errors[field] = [f"{field} is required"]
    
    # Validate campaign type
    if "campaign_type" in content and content["campaign_type"]:
        if not validate_campaign_type(content["campaign_type"]):
            errors.setdefault("campaign_type", []).append("Invalid campaign type")
    
    # Validate subject line length
    if "subject_line" in content and content["subject_line"]:
        subject = str(content["subject_line"]).strip()
        if len(subject) > 100:
            errors.setdefault("subject_line", []).append("Subject line too long (max 100 characters)")
        elif len(subject) < 10:
            errors.setdefault("subject_line", []).append("Subject line too short (min 10 characters)")
    
    # Validate content length
    if "content" in content and content["content"]:
        content_text = str(content["content"]).strip()
        if len(content_text) < 50:
            errors.setdefault("content", []).append("Content too short (min 50 characters)")
        elif len(content_text) > 10000:
            errors.setdefault("content", []).append("Content too long (max 10000 characters)")
    
    return errors

def validate_targeting_criteria(criteria: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate targeting criteria
    Returns dictionary with field names as keys and error messages as values
    """
    errors = {}
    
    # Validate location if provided
    if "location" in criteria and criteria["location"]:
        if not validate_location(criteria["location"]):
            errors.setdefault("location", []).append("Invalid location format")
    
    # Validate age ranges
    age_fields = ["vehicle_age_min", "vehicle_age_max"]
    for field in age_fields:
        if field in criteria and criteria[field] is not None:
            try:
                age = int(criteria[field])
                if age < 0 or age > 50:
                    errors.setdefault(field, []).append("Vehicle age must be between 0 and 50 years")
            except (ValueError, TypeError):
                errors.setdefault(field, []).append(f"Invalid {field} value")
    
    # Validate service months
    if "last_service_months" in criteria and criteria["last_service_months"] is not None:
        try:
            months = int(criteria["last_service_months"])
            if months < 0 or months > 120:
                errors.setdefault("last_service_months", []).append("Service months must be between 0 and 120")
        except (ValueError, TypeError):
            errors.setdefault("last_service_months", []).append("Invalid last service months value")
    
    return errors

def sanitize_input(value: Any, field_type: str = "string") -> Any:
    """Sanitize input values"""
    if value is None:
        return None
    
    if field_type == "string":
        return str(value).strip()
    elif field_type == "email":
        is_valid, email = validate_email_address(str(value))
        return email if is_valid else None
    elif field_type == "phone":
        is_valid, phone = validate_phone_number(str(value))
        return phone if is_valid else None
    elif field_type == "integer":
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    elif field_type == "float":
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    elif field_type == "date":
        is_valid, date_obj = validate_date(value)
        return date_obj if is_valid else None
    
    return value

def is_valid_json(json_string: str) -> bool:
    """Check if string is valid JSON"""
    try:
        import json
        json.loads(json_string)
        return True
    except (ValueError, TypeError):
        return False