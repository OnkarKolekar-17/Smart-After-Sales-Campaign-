#!/usr/bin/env python3
"""
EFFICIENT Smart After-Sales Campaign System
Token-saving version using GROUP-based campaigns instead of individual campaigns
"""

import os
import sys
import logging
import time
from datetime import datetime
import argparse
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import init_db
from config.settings import settings
from workflows.efficient_workflow import EfficientCampaignWorkflow
from services.location_service import LocationService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/efficient_campaigns.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment and initialize database"""
    try:
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        
        return True
    except Exception as e:
        logger.error(f"Environment setup failed: {e}")
        return False

def run_single_location_campaign(location: str, trigger: str):
    """Run campaign for single location with TOKEN EFFICIENCY"""
    logger.info(f"🚀 Starting EFFICIENT campaign for {location}")
    logger.info(f"💰 TOKEN SAVING MODE: Group-based campaigns")
    
    try:
        # Initialize efficient workflow
        workflow = EfficientCampaignWorkflow()
        
        # Run campaign
        start_time = time.time()
        result = workflow.run_campaign(location=location, campaign_trigger=trigger)
        execution_time = time.time() - start_time
        
        # Display results
        if result.success:
            logger.info(f"✅ EFFICIENT Campaign completed successfully!")
            logger.info(f"⏱️ Execution time: {execution_time:.2f} seconds")
            logger.info(f"🎯 Total Targeted: {result.customers_targeted}")
            logger.info(f"📝 Campaign Groups Created: {result.campaigns_created}")  # Groups, not individual campaigns
            logger.info(f"📧 Emails Sent: {result.campaigns_sent}")
            logger.info(f"💰 TOKEN EFFICIENCY: Created {result.campaigns_created} group campaigns instead of {result.customers_targeted} individual ones!")
            
            # Calculate token savings
            token_savings = result.customers_targeted - result.campaigns_created
            savings_percentage = (token_savings / result.customers_targeted * 100) if result.customers_targeted > 0 else 0
            logger.info(f"💡 Token Savings: {token_savings} campaigns ({savings_percentage:.1f}% reduction in LLM calls)")
            
            print(f"\n🎉 CAMPAIGN SUCCESS - {location}")
            print(f"Total Targeted: {result.customers_targeted}")
            print(f"Campaigns Created: {result.campaigns_created}")
            print(f"Campaigns Sent: {result.campaigns_sent}")
            
        else:
            logger.error(f"❌ Campaign failed: {result.error_message}")
            print(f"\n❌ CAMPAIGN FAILED - {location}")
            print(f"Error: {result.error_message}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Campaign execution failed: {e}")
        print(f"\n❌ CAMPAIGN ERROR - {location}")
        print(f"Error: {str(e)}")
        return None

def run_multi_location_campaign(trigger: str):
    """Run campaigns for all locations with GROUP EFFICIENCY"""
    logger.info(f"🌍 Starting EFFICIENT multi-location campaign")
    logger.info(f"💰 GROUP-BASED approach for maximum token efficiency")
    
    try:
        # Get all locations
        location_service = LocationService()
        all_locations = location_service.get_all_locations()
        
        if not all_locations:
            logger.warning("No locations found")
            print("No locations available for campaigns")
            return
        
        logger.info(f"🎯 Processing {len(all_locations)} locations with GROUP efficiency")
        
        total_targeted = 0
        total_created = 0
        total_sent = 0
        successful_locations = []
        failed_locations = []
        
        # Process each location
        for i, location in enumerate(all_locations, 1):
            logger.info(f"🌍 Location {i}/{len(all_locations)}: {location}")
            
            result = run_single_location_campaign(location, trigger)
            
            if result and result.success:
                successful_locations.append(location)
                total_targeted += result.customers_targeted
                total_created += result.campaigns_created  # Group count
                total_sent += result.campaigns_sent
            else:
                failed_locations.append(location)
            
            # Small delay between locations
            time.sleep(1)
        
        # Final summary
        logger.info(f"\n🏁 EFFICIENT Multi-Location Campaign Complete!")
        logger.info(f"✅ Successful locations: {len(successful_locations)}")
        logger.info(f"❌ Failed locations: {len(failed_locations)}")
        logger.info(f"🎯 Total customers targeted: {total_targeted}")
        logger.info(f"📝 Total campaign groups: {total_created}")
        logger.info(f"📧 Total emails sent: {total_sent}")
        
        # Token efficiency calculation
        if total_targeted > 0:
            token_savings = total_targeted - total_created
            savings_percentage = (token_savings / total_targeted * 100)
            logger.info(f"💰 MASSIVE TOKEN SAVINGS: {token_savings} campaigns ({savings_percentage:.1f}% reduction)")
        
        print(f"\n🎉 MULTI-LOCATION RESULTS")
        print(f"Locations processed: {len(all_locations)}")
        print(f"Successful: {len(successful_locations)}")
        print(f"Failed: {len(failed_locations)}")
        print(f"Total Targeted: {total_targeted}")
        print(f"Campaigns Created: {total_created}")
        print(f"Campaigns Sent: {total_sent}")
        
        if successful_locations:
            print(f"✅ Success: {', '.join(successful_locations)}")
        if failed_locations:
            print(f"❌ Failed: {', '.join(failed_locations)}")
            
    except Exception as e:
        logger.error(f"Multi-location campaign failed: {e}")
        print(f"❌ Multi-location campaign error: {str(e)}")

def main():
    """Main function with TOKEN-EFFICIENT campaign execution"""
    parser = argparse.ArgumentParser(description='EFFICIENT Smart After-Sales Campaign System (Token-Saving)')
    parser.add_argument('--mode', choices=['single', 'multi'], default='single',
                      help='Campaign execution mode')
    parser.add_argument('--location', type=str, default='Mumbai',
                      help='Target location (for single mode)')
    parser.add_argument('--trigger', choices=['weather', 'holiday', 'lifecycle', 'scheduled'], 
                      default='scheduled', help='Campaign trigger type')
    
    args = parser.parse_args()
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    logger.info(f"🚀 EFFICIENT Campaign System Starting...")
    logger.info(f"💰 Mode: Token-saving GROUP-based campaigns")
    logger.info(f"🎯 Execution: {args.mode} | Trigger: {args.trigger}")
    
    try:
        if args.mode == 'single':
            logger.info(f"📍 Single location: {args.location}")
            run_single_location_campaign(args.location, args.trigger)
        else:
            logger.info(f"🌍 Multi-location mode (all locations)")
            run_multi_location_campaign(args.trigger)
            
        logger.info("✅ EFFICIENT Campaign system execution completed")
        
    except KeyboardInterrupt:
        logger.info("Campaign execution interrupted by user")
        print("\n⚠️ Campaign interrupted")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ System error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
