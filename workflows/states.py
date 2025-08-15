from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class CustomerData(BaseModel):
    customer_id: int
    name: str
    email: str
    phone: Optional[str] = None
    preferred_location: Optional[str] = None
    city: Optional[str] = None
    purchase_date: Optional[str] = None
    vehicles: List[Dict[str, Any]] = []

class WeatherData(BaseModel):
    location: str
    temperature: float
    condition: str
    humidity: int
    description: str
    recommendation: str

class HolidayData(BaseModel):
    name: str
    date: str
    type: str
    description: str
    cultural_significance: Optional[str] = None

class CampaignContent(BaseModel):
    title: str
    subject_line: str
    content: str
    cta_text: str
    campaign_type: str
    personalization_factors: Dict[str, Any] = {}

class TargetingCriteria(BaseModel):
    vehicle_age_range: Optional[List[int]] = None
    last_service_months: Optional[int] = None
    warranty_expiry_days: Optional[int] = None
    location: Optional[str] = None
    custom_filters: Dict[str, Any] = {}

class CampaignState(BaseModel):
    """Main state object that flows through the LangGraph workflow"""
    
    # Input data
    location: str
    campaign_trigger: str  # 'scheduled', 'weather', 'holiday', 'lifecycle'
    
    # Agent outputs
    weather_data: Optional[WeatherData] = None
    holiday_data: Optional[HolidayData] = None
    customer_segments: List[CustomerData] = []
    targeting_criteria: Optional[TargetingCriteria] = None
    campaign_content: Optional[CampaignContent] = None
    
    # Workflow tracking
    current_step: str = "start"
    completed_steps: List[str] = []
    errors: List[str] = []
    
    # Campaign execution
    campaigns_created: List[Dict[str, Any]] = []
    campaigns_sent: List[Dict[str, Any]] = []
    total_targeted: int = 0
    
    # Metadata
    workflow_id: str
    created_at: datetime = datetime.now()
    
    class Config:
        arbitrary_types_allowed = True

class WorkflowResult(BaseModel):
    """Final result of the campaign workflow"""
    workflow_id: str
    status: str  # 'success', 'partial_success', 'failed'
    campaigns_created: int
    campaigns_sent: int
    total_targeted: int
    errors: List[str] = []
    execution_time: float
    summary: str