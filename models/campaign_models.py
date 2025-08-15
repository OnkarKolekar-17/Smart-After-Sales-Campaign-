from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class CampaignType(str, Enum):
    """Campaign types for categorization"""
    SEASONAL = "seasonal"
    HOLIDAY = "holiday" 
    LIFECYCLE = "lifecycle"
    WEATHER = "weather"
    GEOGRAPHIC = "geographic"
    MAINTENANCE = "maintenance"
    WARRANTY = "warranty"

class CampaignStatus(str, Enum):
    """Campaign status tracking"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"

class CampaignContent(BaseModel):
    """Model for campaign content"""
    campaign_title: str = Field(..., description="Internal campaign title")
    subject_line: str = Field(..., description="Email subject line")
    content: str = Field(..., description="Email body content with placeholders")
    cta_text: str = Field(..., description="Call to action button text")
    campaign_type: CampaignType = Field(..., description="Type of campaign")
    personalization_fields: List[str] = Field(default_factory=list, description="Fields used for personalization")
    created_at: datetime = Field(default_factory=datetime.now)

class CampaignRequest(BaseModel):
    """Request model for campaign creation"""
    location: str = Field(..., description="Target location")
    campaign_trigger: str = Field(default="scheduled", description="What triggered this campaign")
    target_audience: Optional[Dict[str, Any]] = Field(default=None, description="Audience criteria")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class CampaignResult(BaseModel):
    """Result model for campaign execution"""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    campaign_type: CampaignType = Field(..., description="Type of campaign")
    status: CampaignStatus = Field(..., description="Campaign status")
    total_targeted: int = Field(default=0, description="Number of customers targeted")
    total_sent: int = Field(default=0, description="Number of emails sent")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    created_at: datetime = Field(default_factory=datetime.now)
    sent_at: Optional[datetime] = Field(default=None, description="When campaign was sent")

class PersonalizedCampaign(BaseModel):
    """Model for personalized campaign ready to send"""
    customer_id: int = Field(..., description="Target customer ID")
    customer_name: str = Field(..., description="Customer name")
    customer_email: str = Field(..., description="Customer email")
    subject_line: str = Field(..., description="Personalized subject line")
    content: str = Field(..., description="Personalized email content")
    campaign_type: CampaignType = Field(..., description="Type of campaign")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CampaignMetrics(BaseModel):
    """Model for campaign performance metrics"""
    campaign_id: str = Field(..., description="Campaign identifier")
    total_sent: int = Field(default=0)
    delivered: int = Field(default=0)
    opened: int = Field(default=0)
    clicked: int = Field(default=0)
    bounced: int = Field(default=0)
    unsubscribed: int = Field(default=0)
    open_rate: float = Field(default=0.0)
    click_rate: float = Field(default=0.0)
    bounce_rate: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.now)

class TargetingCriteria(BaseModel):
    """Model for customer targeting criteria"""
    location: Optional[str] = None
    vehicle_age_min: Optional[int] = None
    vehicle_age_max: Optional[int] = None
    last_service_months: Optional[int] = None
    warranty_expiring_days: Optional[int] = None
    service_types: Optional[List[str]] = None
    customer_segments: Optional[List[str]] = None
    exclude_recent_campaigns: int = Field(default=30, description="Days to exclude recent campaign recipients")

class CampaignTemplate(BaseModel):
    """Model for campaign templates"""
    template_id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name")
    campaign_type: CampaignType = Field(..., description="Type of campaign")
    subject_template: str = Field(..., description="Subject line template with placeholders")
    content_template: str = Field(..., description="Email content template with placeholders")
    required_fields: List[str] = Field(..., description="Required personalization fields")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)