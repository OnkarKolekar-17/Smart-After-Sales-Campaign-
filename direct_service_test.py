#!/usr/bin/env python3
"""
Direct test of service campaigns with manual data structure
"""

import os
import sys
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_db_connection, init_db
from agents.vehicle_lifecycle_agent import VehicleLifecycleAgent
from agents.campaign_generator_agent import CampaignGeneratorAgent
from agents.email_sender_agent import EmailSenderAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_customer_vehicle_data():
    """Get customer and vehicle data directly from database"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to get customers with their vehicles
    query = """
    SELECT 
        c.id as customer_id,
        c.name,
        c.email,
        c.phone,
        c.preferred_location,
        c.created_at as customer_created,
        v.id as vehicle_id,
        v.make,
        v.model,
        v.year,
        v.mileage,
        v.registration_date,
        v.last_service_date,
        v.warranty_start,
        v.warranty_end,
        v.next_service_due
    FROM customers c
    LEFT JOIN vehicles v ON c.id = v.customer_id
    WHERE c.preferred_location ILIKE %s
    ORDER BY c.id
    """
    
    cursor.execute(query, ('%Mumbai%',))
    rows = cursor.fetchall()
    
    # Structure data for the lifecycle agent
    customers = []
    for row in rows:
        if row['vehicle_id']:  # Only include customers with vehicles
            customer_data = {
                'customer_id': row['customer_id'],
                'name': row['name'],
                'email': row['email'],
                'phone': row['phone'],
                'preferred_location': row['preferred_location'],
                'vehicle': {
                    'id': row['vehicle_id'],
                    'make': row['make'],
                    'model': row['model'],
                    'year': row['year'],
                    'mileage': row['mileage'],
                    'registration_date': row['registration_date'].strftime('%Y-%m-%d') if row['registration_date'] else None,
                    'last_service_date': row['last_service_date'].strftime('%Y-%m-%d') if row['last_service_date'] else None,
                    'warranty_start': row['warranty_start'].strftime('%Y-%m-%d') if row['warranty_start'] else None,
                    'warranty_end': row['warranty_end'].strftime('%Y-%m-%d') if row['warranty_end'] else None,
                    'next_service_due': row['next_service_due'].strftime('%Y-%m-%d') if row['next_service_due'] else None,
                    'purchase_date': row['customer_created'].strftime('%Y-%m-%d') if row['customer_created'] else None
                }
            }
            customers.append(customer_data)
    
    cursor.close()
    conn.close()
    
    return customers

def test_service_campaigns():
    """Test service-based campaigns with proper data structure"""
    
    print("="*80)
    print("DIRECT TEST: SERVICE-BASED CAMPAIGNS")
    print("="*80)
    
    # Initialize database
    init_db()
    
    # Get customer and vehicle data
    print("\n🔍 1. FETCHING CUSTOMER & VEHICLE DATA")
    customers = get_customer_vehicle_data()
    print(f"   Found {len(customers)} customers with vehicles in Mumbai")
    
    if not customers:
        print("❌ No customers with vehicles found!")
        return
    
    # Display customer details
    print(f"\n📋 Customer & Vehicle Details:")
    for i, customer in enumerate(customers, 1):
        vehicle = customer['vehicle']
        print(f"   {i}. {customer['name']} ({customer['email']})")
        print(f"      Vehicle: {vehicle['make']} {vehicle['model']} ({vehicle['year']})")
        print(f"      Mileage: {vehicle['mileage']:,} km")
        print(f"      Last Service: {vehicle['last_service_date'] or 'Never'}")
        print(f"      Warranty Ends: {vehicle['warranty_end'] or 'N/A'}")
        print()
    
    # Test lifecycle analysis
    print("🔧 2. ANALYZING VEHICLE LIFECYCLE PATTERNS")
    lifecycle_agent = VehicleLifecycleAgent()
    
    state = {
        'location': 'Mumbai',
        'campaign_trigger': 'lifecycle',
        'targeted_customers': customers
    }
    
    result_state = lifecycle_agent.process(state)
    lifecycle_campaigns = result_state.get('lifecycle_campaigns', [])
    
    print(f"   🎯 Generated {len(lifecycle_campaigns)} lifecycle campaign types")
    
    if not lifecycle_campaigns:
        print("❌ No lifecycle campaigns generated!")
        return
    
    # Display campaigns by type
    print(f"\n📢 SERVICE CAMPAIGN TYPES IDENTIFIED:")
    for i, campaign in enumerate(lifecycle_campaigns, 1):
        target_count = len(campaign.get('target_customers', []))
        print(f"   {i}. {campaign.get('title')}")
        print(f"      Type: {campaign.get('campaign_type', 'unknown')}")
        print(f"      Target Customers: {target_count}")
        print(f"      Priority: {campaign.get('priority', 'N/A')} | Urgency: {campaign.get('urgency', 'N/A')}")
        
        # Show target customers for this campaign
        target_customers = campaign.get('target_customers', [])
        if target_customers:
            print(f"      Customers:")
            for target in target_customers[:3]:  # Show first 3
                customer_info = target.get('customer', target)
                vehicle_info = customer_info.get('vehicle', {})
                name = customer_info.get('name', 'Unknown')
                mileage = target.get('mileage', vehicle_info.get('mileage', 0))
                print(f"        • {name} ({mileage:,} km)")
        
        # Show key benefits
        benefits = campaign.get('benefits', [])
        if benefits:
            print(f"      Key Benefits: {', '.join(benefits[:2])}")
        print()
    
    # Generate campaign content
    print("✍️  3. GENERATING CAMPAIGN CONTENT")
    campaign_generator = CampaignGeneratorAgent()
    
    # Prepare state for content generation (disable weather/holiday)
    content_state = result_state.copy()
    content_state['weather_data'] = None
    content_state['holiday_data'] = None
    
    content_result = campaign_generator.process(content_state)
    generated_campaigns = content_result.get('generated_campaigns', [])
    
    print(f"   📝 Generated content for {len(generated_campaigns)} campaigns")
    
    # Display campaign content samples
    for i, campaign_content in enumerate(generated_campaigns[:3], 1):  # Show first 3
        print(f"\n   📧 Campaign {i}: {campaign_content.get('title', 'Untitled')}")
        print(f"      Type: {campaign_content.get('campaign_type', 'N/A')}")
        print(f"      Subject: {campaign_content.get('subject_line', 'N/A')}")
        
        content = campaign_content.get('content', '')
        if content:
            # Show first 150 characters of content
            content_preview = content.replace('\n', ' ')[:150] + '...'
            print(f"      Content: {content_preview}")
        
        print(f"      CTA: {campaign_content.get('cta_text', 'N/A')}")
    
    # Send campaigns via email
    print("\n📧 4. SENDING SERVICE CAMPAIGNS VIA EMAIL")
    email_agent = EmailSenderAgent()
    
    # Prepare state for email sending
    email_state = content_result.copy()
    email_state['campaigns_created'] = []
    email_state['campaigns_sent'] = []
    
    final_state = email_agent.process(email_state)
    
    campaigns_created = len(final_state.get('campaigns_created', []))
    campaigns_sent = len(final_state.get('campaigns_sent', []))
    
    print(f"   📮 Campaigns Created: {campaigns_created}")
    print(f"   ✅ Campaigns Sent: {campaigns_sent}")
    
    if campaigns_sent > 0:
        print(f"   🎯 Email delivery successful!")
        
        # Show sent campaign details
        sent_campaigns = final_state.get('campaigns_sent', [])
        if sent_campaigns:
            print(f"\n   📬 SENT CAMPAIGNS:")
            for i, campaign in enumerate(sent_campaigns[:3], 1):
                customer_email = campaign.get('customer_email', 'N/A')
                campaign_type = campaign.get('campaign_type', 'N/A')
                print(f"     {i}. {customer_email} - {campaign_type.replace('_', ' ').title()}")
    else:
        print(f"   ⚠️  No campaigns sent - check email configuration")
    
    # Summary
    print("\n" + "="*80)
    print("🎉 SERVICE-BASED CAMPAIGN ANALYSIS COMPLETE")
    print("="*80)
    
    # Categorize campaigns by service type
    service_types = {}
    for campaign in lifecycle_campaigns:
        campaign_type = campaign.get('campaign_type', 'unknown')
        if campaign_type not in service_types:
            service_types[campaign_type] = 0
        service_types[campaign_type] += len(campaign.get('target_customers', []))
    
    print(f"\n📊 CAMPAIGN BREAKDOWN:")
    print(f"   Total Customers Analyzed: {len(customers)}")
    print(f"   Lifecycle Campaign Types: {len(lifecycle_campaigns)}")
    print(f"   Campaign Contents Generated: {len(generated_campaigns)}")
    print(f"   Campaigns Created: {campaigns_created}")
    print(f"   Campaigns Sent: {campaigns_sent}")
    
    print(f"\n🔧 SERVICE TYPES DETECTED:")
    for service_type, customer_count in service_types.items():
        service_name = service_type.replace('_', ' ').title()
        print(f"   • {service_name}: {customer_count} customers")
    
    print(f"\n✅ SERVICE CAMPAIGN WORKFLOW COMPLETED!")
    print(f"   📧 {campaigns_sent} emails delivered successfully!")
    
    return generated_campaigns, customers, final_state

if __name__ == "__main__":
    test_service_campaigns()
