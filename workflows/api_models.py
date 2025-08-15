"""
API models for the Smart After-Sales Campaign system
These models define the request/response structures for API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class CampaignTrigger(str, Enum):
    """Campaign trigger types"""
    SCHEDULED = "scheduled"
    WEATHER_ALERT = "weather_alert"
    HOLIDAY = "holiday"
    MANUAL = "manual"
    API_REQUEST = "api_request"

class CampaignRequest(BaseModel):
    """Request model for creating a new campaign"""
    location: str = Field(..., description="Target location for the campaign", min_length=2)
    campaign_trigger: CampaignTrigger = Field(default=CampaignTrigger.SCHEDULED, description="What triggered this campaign")
    target_audience: Optional[Dict[str, Any]] = Field(default=None, description="Specific audience targeting criteria")
    campaign_type: Optional[str] = Field(default=None, description="Specific campaign type to generate")
    priority: Optional[str] = Field(default="normal", description="Campaign priority level")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for campaign generation")
    
    @validator('location')
    def validate_location(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Location must be at least 2 characters long')
        return v.strip()
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if v and v.lower() not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v.lower() if v else 'normal'

class CampaignResponse(BaseModel):
    """Response model for campaign creation"""
    workflow_id: str = Field(..., description="Unique workflow identifier")
    status: str = Field(..., description="Campaign execution status")
    message: str = Field(..., description="Human-readable status message")
    campaigns_created: int = Field(default=0, description="Number of campaigns created")
    campaigns_sent: int = Field(default=0, description="Number of campaigns sent")
    total_targeted: int = Field(default=0, description="Total customers targeted")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    execution_time: float = Field(default=0.0, description="Execution time in seconds")
    created_at: datetime = Field(default_factory=datetime.now, description="Response creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CampaignStatus(BaseModel):
    """Model for campaign status tracking"""
    workflow_id: str = Field(..., description="Workflow identifier")
    current_step: str = Field(..., description="Current workflow step")
    progress: float = Field(default=0.0, description="Progress percentage (0-100)")
    status: str = Field(..., description="Current status")
    started_at: datetime = Field(..., description="Workflow start time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CustomerTargetingCriteria(BaseModel):
    """Model for customer targeting criteria"""
    location: Optional[str] = Field(default=None, description="Geographic location filter")
    vehicle_age_min: Optional[int] = Field(default=None, description="Minimum vehicle age in years", ge=0)
    vehicle_age_max: Optional[int] = Field(default=None, description="Maximum vehicle age in years", le=50)
    last_service_months: Optional[int] = Field(default=None, description="Months since last service", ge=0)
    warranty_expiring_days: Optional[int] = Field(default=None, description="Warranty expiring within days", ge=0)
    service_types: Optional[List[str]] = Field(default=None, description="Filter by specific service types")
    customer_segments: Optional[List[str]] = Field(default=None, description="Target specific customer segments")
    vehicle_makes: Optional[List[str]] = Field(default=None, description="Filter by vehicle makes")
    high_value_only: Optional[bool] = Field(default=False, description="Target only high-value customers")
    exclude_recent_campaigns: Optional[int] = Field(default=30, description="Exclude customers who received campaigns in last N days")
    
    @validator('vehicle_age_min', 'vehicle_age_max')
    def validate_vehicle_ages(cls, v):
        if v is not None and (v < 0 or v > 50):
            raise ValueError('Vehicle age must be between 0 and 50 years')
        return v
    
    @validator('last_service_months')
    def validate_service_months(cls, v):
        if v is not None and (v < 0 or v > 120):
            raise ValueError('Last service months must be between 0 and 120')
        return v

class CampaignMetricsRequest(BaseModel):
    """Request model for campaign metrics"""
    workflow_id: Optional[str] = Field(default=None, description="Specific workflow ID")
    campaign_ids: Optional[List[str]] = Field(default=None, description="Specific campaign IDs")
    date_from: Optional[datetime] = Field(default=None, description="Start date for metrics")
    date_to: Optional[datetime] = Field(default=None, description="End date for metrics")
    campaign_type: Optional[str] = Field(default=None, description="Filter by campaign type")
    location: Optional[str] = Field(default=None, description="Filter by location")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CampaignMetricsResponse(BaseModel):
    """Response model for campaign metrics"""
    total_campaigns: int = Field(default=0, description="Total campaigns in period")
    total_sent: int = Field(default=0, description="Total emails sent")
    total_delivered: int = Field(default=0, description="Total emails delivered")
    total_opened: int = Field(default=0, description="Total emails opened")
    total_clicked: int = Field(default=0, description="Total emails clicked")
    
    # Calculated rates
    delivery_rate: float = Field(default=0.0, description="Delivery rate percentage")
    open_rate: float = Field(default=0.0, description="Open rate percentage")
    click_rate: float = Field(default=0.0, description="Click rate percentage")
    
    # Breakdown by campaign type
    campaign_type_breakdown: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Metrics by campaign type")
    
    # Location breakdown
    location_breakdown: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Metrics by location")
    
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    version: str = Field(default="1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    services: Dict[str, str] = Field(default_factory=dict, description="Individual service statuses")
    uptime_seconds: Optional[float] = Field(default=None, description="Service uptime in seconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BulkCampaignRequest(BaseModel):
    """Request model for bulk campaign creation"""
    campaigns: List[CampaignRequest] = Field(..., description="List of campaign requests", min_items=1, max_items=10)
    batch_id: Optional[str] = Field(default=None, description="Optional batch identifier")
    priority: Optional[str] = Field(default="normal", description="Batch priority level")
    
    @validator('campaigns')
    def validate_campaigns_count(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 campaigns allowed per bulk request')
        return v

class BulkCampaignResponse(BaseModel):
    """Response model for bulk campaign creation"""
    batch_id: str = Field(..., description="Unique batch identifier")
    total_requested: int = Field(..., description="Total campaigns requested")
    successful: int = Field(default=0, description="Successfully created campaigns")
    failed: int = Field(default=0, description="Failed campaigns")
    results: List[CampaignResponse] = Field(default_factory=list, description="Individual campaign results")
    overall_status: str = Field(..., description="Overall batch status")
    execution_time: float = Field(default=0.0, description="Total execution time")
    created_at: datetime = Field(default_factory=datetime.now, description="Batch creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WebhookPayload(BaseModel):
    """Webhook payload model for external integrations"""
    event_type: str = Field(..., description="Type of event")
    workflow_id: str = Field(..., description="Related workflow ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")
    source: str = Field(default="campaign_system", description="Event source")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Request/Response models for specific endpoints
class ValidateEmailRequest(BaseModel):
    """Request model for email validation"""
    emails: List[str] = Field(..., description="List of email addresses to validate", max_items=100)
    
    @validator('emails')
    def validate_email_list(cls, v):
        if not v:
            raise ValueError('At least one email address is required')
        return v

class ValidateEmailResponse(BaseModel):
    """Response model for email validation"""
    results: Dict[str, bool] = Field(..., description="Validation results for each email")
    valid_count: int = Field(..., description="Number of valid emails")
    invalid_count: int = Field(..., description="Number of invalid emails")
    processed_at: datetime = Field(default_factory=datetime.now, description="Processing timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TemplatePreviewRequest(BaseModel):
    """Request model for template preview"""
    template_content: str = Field(..., description="Template content with placeholders")
    sample_data: Dict[str, Any] = Field(..., description="Sample data for personalization")
    template_type: Optional[str] = Field(default="email", description="Type of template")

class TemplatePreviewResponse(BaseModel):
    """Response model for template preview"""
    rendered_content: str = Field(..., description="Rendered template content")
    missing_fields: List[str] = Field(default_factory=list, description="Missing required fields")
    warnings: List[str] = Field(default_factory=list, description="Template warnings")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }