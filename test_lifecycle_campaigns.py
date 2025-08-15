#!/usr/bin/env python3
"""
Test script specifically for service-based lifecycle campaigns
"""

import os
import sys
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import init_db
from agents.vehicle_lifecycle_agent import VehicleLifecycleAgent
from agents.targeting_agent import TargetingAgent
from agents.campaign_generator_agent import CampaignGeneratorAgent
from agents.email_sender_agent import EmailSenderAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lifecycle_campaigns():
    """Test lifecycle-based campaigns with our vehicle data"""
    
    print("="*60)
    print("TESTING SERVICE-BASED LIFECYCLE CAMPAIGNS")
    print("="*60)
    
    # Initialize database
    init_db()
    
    # Step 1: Get targeted customers
    print("\n1. Getting customer data...")
    targeting_agent = TargetingAgent()
    state = {
        'location': 'Mumbai',
        'campaign_trigger': 'lifecycle'
    }
    
    state = targeting_agent.process(state)
    customers = state.get('targeted_customers', [])
    print(f"   Found {len(customers)} customers")
    
    if not customers:
        print("No customers found. Exiting.")
        return
    
    # Display customer vehicle details
    print("\n   Customer Vehicle Details:")
    for i, customer in enumerate(customers, 1):
        vehicle = customer.vehicle if hasattr(customer, 'vehicle') and customer.vehicle else {}
        customer_name = customer.name if hasattr(customer, 'name') else str(customer)
        
        if vehicle:
            make = vehicle.make if hasattr(vehicle, 'make') else vehicle.get('make', 'N/A') if isinstance(vehicle, dict) else 'N/A'
            model = vehicle.model if hasattr(vehicle, 'model') else vehicle.get('model', 'N/A') if isinstance(vehicle, dict) else 'N/A'
            mileage = vehicle.mileage if hasattr(vehicle, 'mileage') else vehicle.get('mileage', 0) if isinstance(vehicle, dict) else 0
            year = vehicle.year if hasattr(vehicle, 'year') else vehicle.get('year', 'N/A') if isinstance(vehicle, dict) else 'N/A'
            print(f"   {i}. {customer_name} - {make} {model} ({mileage}km, {year})")
        else:
            print(f"   {i}. {customer_name} - No vehicle data")
    
    # Step 2: Analyze vehicle lifecycle
    print("\n2. Analyzing vehicle lifecycle patterns...")
    lifecycle_agent = VehicleLifecycleAgent()
    state = lifecycle_agent.process(state)
    
    lifecycle_campaigns = state.get('lifecycle_campaigns', [])
    print(f"   Generated {len(lifecycle_campaigns)} lifecycle campaign types")
    
    # Display lifecycle campaigns
    print("\n   Lifecycle Campaigns Identified:")
    for i, campaign in enumerate(lifecycle_campaigns, 1):
        print(f"   {i}. {campaign.get('title')} ({campaign.get('campaign_type')})")
        print(f"      Target: {len(campaign.get('target_customers', []))} customers")
        print(f"      Priority: {campaign.get('priority')} | Urgency: {campaign.get('urgency')}")
        print(f"      Benefits: {', '.join(campaign.get('benefits', [])[:2])}...")
        print()
    
    if not lifecycle_campaigns:
        print("   No lifecycle campaigns generated.")
        return
    
    # Step 3: Generate campaign content for service campaigns only
    print("3. Generating service-based campaign content...")
    campaign_generator = CampaignGeneratorAgent()
    
    # Force the system to only generate lifecycle campaigns
    temp_state = state.copy()
    temp_state['weather_data'] = None  # Disable weather campaigns
    temp_state['holiday_data'] = None  # Disable holiday campaigns
    
    temp_state = campaign_generator.process(temp_state)
    
    generated_campaigns = temp_state.get('generated_campaigns', [])
    print(f"   Generated {len(generated_campaigns)} campaign contents")
    
    # Display campaign content samples
    for i, campaign in enumerate(generated_campaigns, 1):
        if i > 3:  # Limit to first 3 campaigns
            break
        print(f"\n   Campaign {i}: {campaign.get('title', 'Untitled')}")
        print(f"   Type: {campaign.get('campaign_type', 'N/A')}")
        print(f"   Subject: {campaign.get('subject_line', 'N/A')}")
        if campaign.get('content'):
            content_preview = campaign.get('content', '')[:200].replace('\n', ' ')
            print(f"   Content Preview: {content_preview}...")
    
    # Step 4: Send service-based campaigns
    print(f"\n4. Sending service-based campaigns...")
    
    # Create email-ready state
    email_state = state.copy()
    email_state['generated_campaigns'] = generated_campaigns
    
    # Send campaigns using EmailSenderAgent
    email_agent = EmailSenderAgent()
    final_state = email_agent.process(email_state)
    
    campaigns_sent = len(final_state.get('campaigns_sent', []))
    campaigns_created = len(final_state.get('campaigns_created', []))
    
    print(f"   Campaigns Created: {campaigns_created}")
    print(f"   Campaigns Sent: {campaigns_sent}")
    
    print("\n" + "="*60)
    print("SERVICE-BASED LIFECYCLE CAMPAIGNS TEST COMPLETED")
    print("="*60)
    
    # Summary
    print("\nSUMMARY:")
    print(f"✅ Customers analyzed: {len(customers)}")
    print(f"✅ Lifecycle campaigns identified: {len(lifecycle_campaigns)}")
    print(f"✅ Campaign contents generated: {len(generated_campaigns)}")
    print(f"✅ Campaigns sent: {campaigns_sent}")
    
    # List specific service types detected
    service_types = list(set([camp.get('campaign_type', 'unknown') for camp in lifecycle_campaigns]))
    print(f"\n🔧 Service Campaign Types Detected:")
    for service_type in service_types:
        print(f"   • {service_type.replace('_', ' ').title()}")

if __name__ == "__main__":
    test_lifecycle_campaigns()
