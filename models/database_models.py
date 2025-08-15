from sqlalchemy import Column, Integer, String, Date, DateTime, Decimal, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    """Customer database model"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    preferred_location = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="customer")
    campaigns = relationship("Campaign", back_populates="customer")

class Vehicle(Base):
    """Vehicle database model"""
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    vin = Column(String(17), unique=True)
    registration_date = Column(Date)
    last_service_date = Column(Date)
    last_service_type = Column(String(50))
    next_service_due = Column(Date)
    mileage = Column(Integer)
    warranty_start = Column(Date)
    warranty_end = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="vehicles")
    service_history = relationship("ServiceHistory", back_populates="vehicle")
    campaigns = relationship("Campaign", back_populates="vehicle")

class ServiceHistory(Base):
    """Service history database model"""
    __tablename__ = 'service_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    service_date = Column(Date, nullable=False)
    service_type = Column(String(50), nullable=False)
    mileage = Column(Integer)
    description = Column(Text)
    cost = Column(Decimal(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="service_history")

class Campaign(Base):
    """Campaign database model"""
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(36), unique=True, nullable=False)  # UUID
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    campaign_type = Column(String(50), nullable=False)
    campaign_title = Column(String(200))
    subject_line = Column(String(200))
    content = Column(Text)
    status = Column(String(20), default='pending')
    
    # Tracking timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Campaign context
    location = Column(String(100))
    trigger_type = Column(String(50))
    
    # Email delivery tracking
    brevo_message_id = Column(String(100))
    
    # Relationships
    customer = relationship("Customer", back_populates="campaigns")
    vehicle = relationship("Vehicle", back_populates="campaigns")

class CampaignMetrics(Base):
    """Campaign metrics database model"""
    __tablename__ = 'campaign_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(36), nullable=False)
    total_sent = Column(Integer, default=0)
    delivered = Column(Integer, default=0)
    opened = Column(Integer, default=0)
    clicked = Column(Integer, default=0)
    bounced = Column(Integer, default=0)
    unsubscribed = Column(Integer, default=0)
    open_rate = Column(Decimal(5, 4), default=0.0)
    click_rate = Column(Decimal(5, 4), default=0.0)
    bounce_rate = Column(Decimal(5, 4), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CampaignTemplate(Base):
    """Campaign template database model"""
    __tablename__ = 'campaign_templates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    campaign_type = Column(String(50), nullable=False)
    subject_template = Column(String(200), nullable=False)
    content_template = Column(Text, nullable=False)
    required_fields = Column(Text)  # JSON string of required fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)