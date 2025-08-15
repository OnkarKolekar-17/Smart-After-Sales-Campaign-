#!/usr/bin/env python3
"""
Smart After-Sales Campaigns System
Multi-agent AI system for generating and sending targeted automotive campaigns
"""

import os
import sys
import logging
from datetime import datetime
import argparse
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import init_db
from config.settings import settings
from workflows.campaign_workflow import CampaignWorkflow
from services.location_service import LocationService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/campaign_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Setup the environment and initialize database"""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        
        return True
    except Exception as e:
        logger.error(f"Environment setup failed: {e}")
        return False

def run_campaign(location: str = None, trigger: str = "scheduled"):
    """Run a single campaign"""
    
    if not location:
        location = settings.weather.default_location
    
    logger.info(f"Starting campaign for location: {location}, trigger: {trigger}")
    
    try:
        # Initialize workflow
        workflow = CampaignWorkflow()
        
        # Execute campaign
        result = workflow.run_campaign(location=location, campaign_trigger=trigger)
        
        # Log results
        logger.info("=" * 60)
        logger.info("CAMPAIGN EXECUTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"Workflow ID: {result.workflow_id}")
        logger.info(f"Status: {result.status}")
        logger.info(f"Location: {location}")
        logger.info(f"Execution Time: {result.execution_time:.2f} seconds")
        logger.info(f"Total Targeted: {result.total_targeted}")
        logger.info(f"Campaigns Created: {result.campaigns_created}")
        logger.info(f"Campaigns Sent: {result.campaigns_sent}")
        
        if result.errors:
            logger.info(f"Errors Encountered: {len(result.errors)}")
            for error in result.errors:
                logger.error(f"  - {error}")
        
        logger.info(f"Summary: {result.summary}")
        logger.info("=" * 60)
        
        return result
        
    except Exception as e:
        logger.error(f"Campaign execution failed: {e}")
        return None

def run_scheduled_campaigns():
    """Run scheduled campaigns for multiple locations"""
    
    logger.info("Fetching locations from database...")
    
    # Initialize location service
    location_service = LocationService()
    
    # Get all locations with at least 1 customer
    locations = location_service.filter_locations_by_criteria(min_customers=1)
    
    if not locations:
        logger.warning("No locations found with customers. Using default location.")
        locations = [settings.weather.default_location]
    
    logger.info(f"Running scheduled campaigns for {len(locations)} locations: {locations}")
    
    results = []
    for location in locations:
        try:
            logger.info(f"Starting campaign for location: {location}")
            result = run_campaign(location=location, trigger="scheduled")
            if result:
                results.append(result)
        except Exception as e:
            logger.error(f"Failed to run campaign for {location}: {e}")
    
    # Summary of all campaigns
    total_targeted = sum(r.total_targeted for r in results)
    total_sent = sum(r.campaigns_sent for r in results)
    
    logger.info("=" * 60)
    logger.info("BATCH CAMPAIGN SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Locations Processed: {len(results)}")
    logger.info(f"Total Customers Targeted: {total_targeted}")
    logger.info(f"Total Campaigns Sent: {total_sent}")
    logger.info(f"Average Success Rate: {(total_sent/total_targeted*100):.1f}%" if total_targeted > 0 else "N/A")
    logger.info("=" * 60)
    
    return results

def run_multi_location_campaigns(trigger: str = "scheduled", min_customers: int = 1):
    """Run campaigns for all locations with dynamic location fetching"""
    
    logger.info(f"Starting multi-location campaigns with trigger: {trigger}")
    
    # Initialize location service
    location_service = LocationService()
    
    # Get location statistics first
    location_stats = location_service.get_location_statistics()
    
    if not location_stats:
        logger.warning("No locations found in database")
        return []
    
    # Display location statistics
    logger.info("=" * 80)
    logger.info("LOCATION STATISTICS")
    logger.info("=" * 80)
    
    for stat in location_stats:
        logger.info(f"📍 {stat['location']}: {stat['customer_count']} customers, {stat['vehicle_count']} vehicles")
        logger.info(f"   Brands: {stat['brands']}")
        logger.info(f"   Avg Vehicle Age: {stat['avg_vehicle_age']} years")
        logger.info("")
    
    # Filter locations based on criteria
    locations = location_service.filter_locations_by_criteria(min_customers=min_customers)
    
    logger.info(f"Running campaigns for {len(locations)} locations (min customers: {min_customers})")
    logger.info("=" * 80)
    
    results = []
    for location in locations:
        try:
            logger.info(f"🚀 Starting campaign for location: {location}")
            result = run_campaign(location=location, trigger=trigger)
            if result:
                results.append(result)
                logger.info(f"✅ Completed campaign for {location}: {result.campaigns_sent} emails sent")
            else:
                logger.warning(f"❌ Failed to run campaign for {location}")
        except Exception as e:
            logger.error(f"❌ Error running campaign for {location}: {e}")
    
    # Summary of all campaigns
    total_targeted = sum(r.total_targeted for r in results)
    total_created = sum(r.campaigns_created for r in results)  
    total_sent = sum(r.campaigns_sent for r in results)
    
    logger.info("=" * 80)
    logger.info("MULTI-LOCATION CAMPAIGN SUMMARY")
    logger.info("=" * 80)
    logger.info(f"🎯 Trigger Type: {trigger}")
    logger.info(f"📍 Locations Processed: {len(results)}")
    logger.info(f"👥 Total Customers Targeted: {total_targeted}")
    logger.info(f"📧 Total Campaigns Created: {total_created}")
    logger.info(f"✅ Total Campaigns Sent: {total_sent}")
    logger.info(f"📊 Overall Success Rate: {(total_sent/total_targeted*100):.1f}%" if total_targeted > 0 else "N/A")
    
    # Individual location breakdown
    logger.info("")
    logger.info("LOCATION BREAKDOWN:")
    for i, result in enumerate(results, 1):
        success_rate = (result.campaigns_sent/result.total_targeted*100) if result.total_targeted > 0 else 0
        logger.info(f"  {i}. {result.summary} - Success Rate: {success_rate:.1f}%")
    
    logger.info("=" * 80)
    
    return results

def view_location_statistics():
    """Display location statistics"""
    
    print("\n" + "="*80)
    print("LOCATION STATISTICS")
    print("="*80)
    
    try:
        location_service = LocationService()
        stats = location_service.get_location_statistics()
        
        if not stats:
            print("No location data found in database.")
            return
        
        for stat in stats:
            print(f"\n📍 Location: {stat['location']}")
            print(f"   👥 Customers: {stat['customer_count']}")
            print(f"   🚗 Vehicles: {stat['vehicle_count']}")
            print(f"   🏭 Brands: {stat['brands']}")
            print(f"   📅 Avg Vehicle Age: {stat['avg_vehicle_age']} years")
            print(f"   📆 First Customer: {stat['first_customer_date']}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"Error fetching location statistics: {e}")

def test_weather_integration():
    """Test weather integration"""
    from agents.weather_agent import WeatherAgent
    
    print("\n" + "-"*40)
    print("TESTING WEATHER INTEGRATION")
    print("-"*40)
    
    location = input("Enter location to test (press Enter for Mumbai): ").strip()
    if not location:
        location = "Mumbai"
    
    try:
        weather_agent = WeatherAgent()
        state = {'location': location}
        result = weather_agent.process(state)
        
        weather_data = result.get('weather_data')
        if weather_data:
            print(f"\nWeather data for {location}:")
            print(f"Temperature: {weather_data.temperature}°C")
            print(f"Condition: {weather_data.condition}")
            print(f"Description: {weather_data.description}")
            print(f"Humidity: {weather_data.humidity}%")
            print(f"\nRecommendation:")
            print(weather_data.recommendation)
        else:
            print("Failed to fetch weather data")
            
    except Exception as e:
        print(f"Error testing weather integration: {e}")
    
def test_holiday_integration():
    """Test holiday integration"""
    from agents.holiday_agent import HolidayAgent
    
    print("\n" + "-"*40)
    print("TESTING HOLIDAY INTEGRATION")
    print("-"*40)
    
    try:
        holiday_agent = HolidayAgent()
        state = {'location': 'Mumbai'}
        result = holiday_agent.process(state)
        
        holiday_data = result.get('holiday_data')
        if holiday_data:
            print(f"\nUpcoming holidays:")
            print(f"Holiday: {holiday_data.name}")
            print(f"Date: {holiday_data.date}")
            print(f"Type: {holiday_data.holiday_type}")
            print(f"\nRecommendation:")
            print(holiday_data.recommendation)
        else:
            print("No upcoming holidays found")
            
    except Exception as e:
        print(f"Error testing holiday integration: {e}")

def show_system_status():
    """Show system status"""
    print("\n" + "-"*40)
    print("SYSTEM STATUS")
    print("-"*40)
    
    # Database status
    try:
        from config.database import get_db_connection
        conn = get_db_connection()
        conn.close()
        db_status = "✓ Connected"
    except Exception as e:
        db_status = f"✗ Connection failed: {e}"
    
    # API status checks
    openai_status = "✓ Configured" if settings.openai.api_key else "✗ Missing API key"
    weather_status = "✓ Configured" if settings.weather.api_key else "✗ Missing API key"
    brevo_status = "✓ Configured" if settings.brevo.api_key else "✗ Missing API key"
    
    print(f"Database: {db_status}")
    print(f"OpenAI API: {openai_status}")
    print(f"Weather API: {weather_status}")
    print(f"Brevo API: {brevo_status}")
    print(f"Environment: {settings.environment}")
    print(f"Log Level: {settings.log_level}")
    print(f"Default Location: {settings.weather.default_location}")

def interactive_mode():
    """Run in interactive mode for testing"""
    print("\n" + "="*60)
    print("SMART AFTER-SALES CAMPAIGNS SYSTEM")
    print("Interactive Mode")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Run single campaign")
        print("2. Run scheduled campaigns (all locations)")
        print("3. Run multi-location campaigns (dynamic)")
        print("4. View location statistics")
        print("5. Test weather integration")
        print("6. Test holiday integration")
        print("7. View system status")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            location = input("Enter location (press Enter for Mumbai): ").strip()
            if not location:
                location = "Mumbai"
            
            trigger_options = ["scheduled", "weather", "holiday", "lifecycle"]
            print(f"Trigger options: {', '.join(trigger_options)}")
            trigger = input("Enter trigger type (press Enter for scheduled): ").strip()
            if not trigger:
                trigger = "scheduled"
            
            run_campaign(location=location, trigger=trigger)
            
        elif choice == "2":
            run_scheduled_campaigns()
            
        elif choice == "3":
            trigger_options = ["scheduled", "weather", "holiday", "lifecycle"]
            print(f"Trigger options: {', '.join(trigger_options)}")
            trigger = input("Enter trigger type (press Enter for lifecycle): ").strip()
            if not trigger:
                trigger = "lifecycle"
            
            min_customers = input("Minimum customers per location (press Enter for 1): ").strip()
            min_customers = int(min_customers) if min_customers.isdigit() else 1
            
            run_multi_location_campaigns(trigger=trigger, min_customers=min_customers)
            
        elif choice == "4":
            view_location_statistics()
            
        elif choice == "5":
            test_weather_integration()
            
        elif choice == "6":
            test_holiday_integration()
            
        elif choice == "7":
            show_system_status()
            
        elif choice == "8":
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")

def test_weather_integration():
    """Test weather API integration"""
    from agents.weather_agent import WeatherAgent
    
    print("\n" + "-"*40)
    print("TESTING WEATHER INTEGRATION")
    print("-"*40)
    
    location = input("Enter location to test (press Enter for Mumbai): ").strip()
    if not location:
        location = "Mumbai"
    
    try:
        weather_agent = WeatherAgent()
        state = {'location': location}
        result = weather_agent.process(state)
        
        weather_data = result.get('weather_data')
        if weather_data:
            print(f"\nWeather data for {location}:")
            print(f"Temperature: {weather_data.temperature}°C")
            print(f"Condition: {weather_data.condition}")
            print(f"Description: {weather_data.description}")
            print(f"Humidity: {weather_data.humidity}%")
            print(f"\nRecommendation:")
            print(weather_data.recommendation)
        else:
            print("Failed to fetch weather data")
            
    except Exception as e:
        print(f"Error testing weather integration: {e}")

def test_holiday_integration():
    """Test holiday integration"""
    from agents.holiday_agent import HolidayAgent
    
    print("\n" + "-"*40)
    print("TESTING HOLIDAY INTEGRATION")
    print("-"*40)
    
    try:
        holiday_agent = HolidayAgent()
        state = {}
        result = holiday_agent.process(state)
        
        holiday_data = result.get('holiday_data')
        upcoming_holidays = result.get('upcoming_holidays', [])
        
        if holiday_data:
            print(f"Primary Holiday: {holiday_data.name}")
            print(f"Date: {holiday_data.date}")
            print(f"Type: {holiday_data.type}")
            print(f"Cultural Significance: {holiday_data.cultural_significance}")
            print(f"\nCampaign Description:")
            print(holiday_data.description)
        
        if upcoming_holidays:
            print(f"\nAll Upcoming Holidays ({len(upcoming_holidays)}):")
            for holiday in upcoming_holidays[:5]:  # Show first 5
                print(f"- {holiday['name']} ({holiday['date']}) - {holiday.get('days_until', 'N/A')} days")
        
        if not holiday_data and not upcoming_holidays:
            print("No upcoming holidays found")
            
    except Exception as e:
        print(f"Error testing holiday integration: {e}")

def show_system_status():
    """Show system status and configuration"""
    print("\n" + "-"*40)
    print("SYSTEM STATUS")
    print("-"*40)
    
    # Check database connection
    try:
        from config.database import get_db_connection
        conn = get_db_connection()
        conn.close()
        db_status = "✓ Connected"
    except Exception as e:
        db_status = f"✗ Error: {e}"
    
    # Check API configurations
    openai_status = "✓ Configured" if settings.openai.api_key else "✗ Missing API key"
    weather_status = "✓ Configured" if settings.weather.api_key else "✗ Missing API key"
    brevo_status = "✓ Configured" if settings.brevo.api_key else "✗ Missing API key"
    
    print(f"Database: {db_status}")
    print(f"OpenAI API: {openai_status}")
    print(f"Weather API: {weather_status}")
    print(f"Brevo API: {brevo_status}")
    print(f"Environment: {settings.environment}")
    print(f"Log Level: {settings.log_level}")
    print(f"Default Location: {settings.weather.default_location}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Smart After-Sales Campaigns System')
    parser.add_argument('--mode', choices=['single', 'batch', 'multi', 'interactive'], 
                       default='interactive', help='Execution mode')
    parser.add_argument('--location', type=str, help='Location for single campaign')
    parser.add_argument('--trigger', choices=['scheduled', 'weather', 'holiday', 'lifecycle'],
                       default='scheduled', help='Campaign trigger type')
    parser.add_argument('--min-customers', type=int, default=1, 
                       help='Minimum customers per location for multi-mode')
    parser.add_argument('--stats-only', action='store_true', 
                       help='Show location statistics only')
    parser.add_argument('--setup', action='store_true', help='Setup environment only')
    
    args = parser.parse_args()
    
    # Setup environment
    if not setup_environment():
        logger.error("Environment setup failed. Exiting.")
        sys.exit(1)
    
    if args.setup:
        logger.info("Environment setup completed successfully")
        return
    
    if args.stats_only:
        view_location_statistics()
        return
    
    # Execute based on mode
    try:
        if args.mode == 'single':
            location = args.location or settings.weather.default_location
            run_campaign(location=location, trigger=args.trigger)
            
        elif args.mode == 'batch':
            run_scheduled_campaigns()
            
        elif args.mode == 'multi':
            run_multi_location_campaigns(trigger=args.trigger, min_customers=args.min_customers)
            
        elif args.mode == 'interactive':
            interactive_mode()
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()