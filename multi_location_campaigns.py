#!/usr/bin/env python3
"""
Multi-Location Campaign Runner
Automatically fetches locations from database and runs campaigns for each
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
        logging.FileHandler('logs/multi_location_campaigns.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MultiLocationCampaignRunner:
    """Runs campaigns across multiple locations automatically"""
    
    def __init__(self):
        self.location_service = LocationService()
        self.workflow = None
    
    def initialize(self):
        """Initialize the campaign system"""
        try:
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            
            # Initialize database
            logger.info("Initializing database...")
            init_db()
            logger.info("Database initialized successfully")
            
            # Initialize workflow
            self.workflow = CampaignWorkflow()
            logger.info("Campaign workflow initialized")
            
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def run_single_location_campaign(self, location: str, trigger: str = "auto") -> dict:
        """Run campaign for a single location"""
        
        logger.info(f"Starting campaign for location: {location}")
        
        try:
            # Get customer count for this location
            customers = self.location_service.get_customers_by_location(location)
            customer_count = len(customers)
            
            logger.info(f"Found {customer_count} customers in {location}")
            
            if customer_count == 0:
                logger.warning(f"No customers found in {location}, skipping")
                return {
                    'location': location,
                    'status': 'skipped',
                    'reason': 'no_customers',
                    'customers_targeted': 0,
                    'campaigns_created': 0,
                    'campaigns_sent': 0
                }
            
            # Execute campaign
            result = self.workflow.run_campaign(location=location, campaign_trigger=trigger)
            
            # Return structured result
            return {
                'location': location,
                'status': result.status,
                'workflow_id': result.workflow_id,
                'execution_time': result.execution_time,
                'customers_targeted': result.total_targeted,
                'campaigns_created': result.campaigns_created,
                'campaigns_sent': result.campaigns_sent,
                'errors': result.errors,
                'summary': result.summary
            }
            
        except Exception as e:
            logger.error(f"Campaign failed for {location}: {e}")
            return {
                'location': location,
                'status': 'failed',
                'error': str(e),
                'customers_targeted': 0,
                'campaigns_created': 0,
                'campaigns_sent': 0
            }
    
    def run_all_location_campaigns(self, trigger: str = "auto", min_customers: int = 1):
        """Run campaigns for all locations in database"""
        
        logger.info("=" * 80)
        logger.info("MULTI-LOCATION CAMPAIGN EXECUTION STARTED")
        logger.info("=" * 80)
        
        # Get all locations
        locations = self.location_service.get_unique_locations()
        
        if not locations:
            logger.error("No locations found in database")
            return []
        
        logger.info(f"Found {len(locations)} locations to process")
        
        # Filter locations by minimum customer count
        filtered_locations = [loc for loc in locations if loc['customer_count'] >= min_customers]
        
        if len(filtered_locations) < len(locations):
            logger.info(f"Filtered to {len(filtered_locations)} locations (min {min_customers} customers)")
        
        # Show location overview
        logger.info("Location Overview:")
        for loc in filtered_locations:
            logger.info(f"  • {loc['location']}: {loc['customer_count']} customers")
        
        # Run campaigns for each location
        results = []
        successful_campaigns = 0
        total_customers = 0
        total_campaigns_sent = 0
        
        for i, location_info in enumerate(filtered_locations, 1):
            location = location_info['location']
            customer_count = location_info['customer_count']
            
            logger.info(f"\\n[{i}/{len(filtered_locations)}] Processing {location}...")
            
            result = self.run_single_location_campaign(location, trigger)
            results.append(result)
            
            if result['status'] == 'success':
                successful_campaigns += 1
                total_customers += result['customers_targeted']
                total_campaigns_sent += result['campaigns_sent']
                
                logger.info(f"✅ {location}: {result['campaigns_sent']} campaigns sent to {result['customers_targeted']} customers")
            else:
                logger.warning(f"❌ {location}: Campaign failed - {result.get('error', 'Unknown error')}")
        
        # Final summary
        logger.info("\\n" + "=" * 80)
        logger.info("MULTI-LOCATION CAMPAIGN EXECUTION COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Locations Processed: {len(filtered_locations)}")
        logger.info(f"Successful Campaigns: {successful_campaigns}")
        logger.info(f"Failed Campaigns: {len(filtered_locations) - successful_campaigns}")
        logger.info(f"Total Customers Targeted: {total_customers}")
        logger.info(f"Total Campaigns Sent: {total_campaigns_sent}")
        
        if total_customers > 0:
            success_rate = (total_campaigns_sent / total_customers) * 100
            logger.info(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Show per-location results
        logger.info("\\nPer-Location Results:")
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            logger.info(f"  {status_icon} {result['location']}: "
                       f"{result['campaigns_sent']} sent / {result['customers_targeted']} targeted")
        
        logger.info("=" * 80)
        
        return results
    
    def show_location_statistics(self):
        """Show detailed location statistics"""
        
        logger.info("\\n" + "=" * 60)
        logger.info("LOCATION STATISTICS")
        logger.info("=" * 60)
        
        stats = self.location_service.get_location_statistics()
        
        logger.info(f"Total Customers: {stats['total_customers']}")
        logger.info(f"Total Locations: {stats['total_locations']}")
        logger.info("\\nLocation Breakdown:")
        
        for loc in stats['locations']:
            logger.info(f"  • {loc['location']:<15}: {loc['customer_count']:>3} customers ({loc['percentage']:>5.1f}%)")
        
        logger.info("=" * 60)

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description='Multi-Location Campaign Runner')
    parser.add_argument('--trigger', 
                       choices=['weather', 'holiday', 'lifecycle', 'auto'], 
                       default='auto',
                       help='Campaign trigger type')
    parser.add_argument('--location', 
                       type=str,
                       help='Run for specific location only')
    parser.add_argument('--min-customers', 
                       type=int, 
                       default=1,
                       help='Minimum customers required per location')
    parser.add_argument('--stats-only', 
                       action='store_true',
                       help='Show location statistics only')
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = MultiLocationCampaignRunner()
    
    if not runner.initialize():
        logger.error("Failed to initialize campaign system")
        return 1
    
    # Show statistics if requested
    if args.stats_only:
        runner.show_location_statistics()
        return 0
    
    # Run campaigns
    try:
        if args.location:
            # Single location
            result = runner.run_single_location_campaign(args.location, args.trigger)
            logger.info(f"Campaign completed for {args.location}: {result['status']}")
        else:
            # All locations
            runner.show_location_statistics()
            results = runner.run_all_location_campaigns(args.trigger, args.min_customers)
            
        logger.info("Campaign execution completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Campaign execution interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Campaign execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
