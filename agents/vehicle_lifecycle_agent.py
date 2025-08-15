from typing import Dict, Any, List
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent

class VehicleLifecycleAgent(BaseAgent):
    """Agent responsible for analyzing vehicle lifecycle data and generating data-driven campaign opportunities"""
    
    def __init__(self):
        super().__init__(
            agent_name="VehicleLifecycleAgent",
            system_prompt=self._get_default_system_prompt()
        )
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are a Vehicle Lifecycle Analysis Agent specialized in data-driven automotive service campaigns.
        
        Your role is to:
        1. Analyze vehicle ownership milestones, mileage patterns, and service history
        2. Identify lifecycle-based opportunities for targeted campaigns
        3. Generate personalized service recommendations based on vehicle age and usage
        4. Create urgency-driven campaigns for warranty expiration, major service intervals
        5. Segment customers based on vehicle lifecycle stage for targeted messaging
        
        Focus on creating value-driven campaigns that help customers maintain their vehicles properly while building long-term loyalty.
        
        Campaign Types to Generate:
        - Ownership Milestone Campaigns (0-12 months, 1-3 years, 3-5 years, 5+ years)
        - Mileage-Based Service Campaigns (10K, 50K, 100K+ km intervals)
        - Warranty Expiry Campaigns (approaching expiration)
        - Seasonal Service Reminders based on vehicle age
        - Loyalty Program Campaigns for long-term customers
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process vehicle lifecycle data and generate campaign opportunities"""
        
        try:
            self._log_step("Starting vehicle lifecycle analysis")
            
            # Get customer and vehicle data from state
            customers = state.get('targeted_customers', [])
            location = state.get('location', 'Unknown')
            
            if not customers:
                self._log_step("No customer data available for lifecycle analysis", "warning")
                return state
            
            # Analyze lifecycle patterns
            lifecycle_campaigns = self._analyze_vehicle_lifecycle(customers, location)
            
            # Update state with lifecycle campaign data
            state['lifecycle_campaigns'] = lifecycle_campaigns
            state['lifecycle_analysis_completed'] = True
            
            self._log_step(f"Vehicle lifecycle analysis completed: {len(lifecycle_campaigns)} campaign types identified")
            
            return state
            
        except Exception as e:
            self._log_step(f"Error in vehicle lifecycle analysis: {e}", "error")
            state['lifecycle_campaigns'] = []
            return state
    
    def _analyze_vehicle_lifecycle(self, customers: List[Dict], location: str) -> List[Dict[str, Any]]:
        """Analyze vehicle lifecycle data and generate targeted campaigns"""
        
        lifecycle_campaigns = []
        
        # Analyze each customer's vehicles
        ownership_segments = {
            'new_owners': [],      # 0-12 months
            'early_owners': [],    # 1-3 years  
            'mid_owners': [],      # 3-5 years
            'veteran_owners': [],  # 5+ years
            'high_mileage': [],    # 50K+ km
            'ultra_high_mileage': [], # 100K+ km
            'warranty_expiring': [],  # Warranty ending soon
            'service_due': []         # Service overdue
        }
        
        current_date = datetime.now()
        
        for customer in customers:
            vehicle = customer.get('vehicle', {})
            if not vehicle:
                continue
                
            # Calculate vehicle age
            purchase_date = self._parse_date(vehicle.get('purchase_date'))
            vehicle_age_years = self._calculate_years_since(purchase_date) if purchase_date else 0
            
            # Get mileage and service data
            mileage = vehicle.get('mileage', 0)
            last_service = self._parse_date(vehicle.get('last_service_date'))
            warranty_end = self._parse_date(vehicle.get('warranty_end'))
            
            customer_data = {
                'customer': customer,
                'vehicle_age_years': vehicle_age_years,
                'mileage': mileage,
                'days_since_service': self._calculate_days_since(last_service) if last_service else 365
            }
            
            # Categorize customers by lifecycle stage
            if vehicle_age_years <= 1:
                ownership_segments['new_owners'].append(customer_data)
            elif vehicle_age_years <= 3:
                ownership_segments['early_owners'].append(customer_data)
            elif vehicle_age_years <= 5:
                ownership_segments['mid_owners'].append(customer_data)
            else:
                ownership_segments['veteran_owners'].append(customer_data)
            
            # Mileage-based segmentation
            if mileage >= 100000:
                ownership_segments['ultra_high_mileage'].append(customer_data)
            elif mileage >= 50000:
                ownership_segments['high_mileage'].append(customer_data)
            
            # Warranty expiration (within 6 months)
            if warranty_end and self._days_until_date(warranty_end) <= 180:
                ownership_segments['warranty_expiring'].append(customer_data)
            
            # Service due (over 6 months since last service)
            if customer_data['days_since_service'] > 180:
                ownership_segments['service_due'].append(customer_data)
        
        # Generate campaigns for each segment
        lifecycle_campaigns.extend(self._generate_ownership_campaigns(ownership_segments, location))
        lifecycle_campaigns.extend(self._generate_mileage_campaigns(ownership_segments, location))
        lifecycle_campaigns.extend(self._generate_warranty_campaigns(ownership_segments, location))
        lifecycle_campaigns.extend(self._generate_service_due_campaigns(ownership_segments, location))
        
        return lifecycle_campaigns
    
    def _generate_ownership_campaigns(self, segments: Dict, location: str) -> List[Dict]:
        """Generate ownership milestone campaigns"""
        
        campaigns = []
        
        # New Owner Campaign (0-12 months)
        if segments['new_owners']:
            campaigns.append({
                'campaign_type': 'ownership_milestone',
                'segment': 'new_owners',
                'title': 'Welcome to the Family - Free First Service',
                'target_customers': segments['new_owners'],
                'priority': 'high',
                'urgency': 'medium',
                'benefits': [
                    'Complimentary first service check',
                    'Welcome to loyalty program',
                    'Vehicle health assessment',
                    'Maintenance schedule planning'
                ],
                'cta': 'Book Your Free First Service'
            })
        
        # Early Owner Campaign (1-3 years)
        if segments['early_owners']:
            campaigns.append({
                'campaign_type': 'ownership_milestone',
                'segment': 'early_owners',
                'title': 'Keep Your Vehicle Running Like New',
                'target_customers': segments['early_owners'],
                'priority': 'medium',
                'urgency': 'medium',
                'benefits': [
                    '20% off minor service packages',
                    'Brake and battery health check',
                    'Tire rotation and alignment',
                    'Loyalty points bonus'
                ],
                'cta': 'Maintain Peak Performance'
            })
        
        # Mid-Life Owner Campaign (3-5 years)
        if segments['mid_owners']:
            campaigns.append({
                'campaign_type': 'ownership_milestone', 
                'segment': 'mid_owners',
                'title': 'Mid-Life Vehicle Care Package',
                'target_customers': segments['mid_owners'],
                'priority': 'high',
                'urgency': 'medium',
                'benefits': [
                    'Comprehensive brake system check',
                    'Battery replacement service',
                    'Fluid system maintenance',
                    'AC system cleaning'
                ],
                'cta': 'Extend Vehicle Life'
            })
        
        # Veteran Owner Campaign (5+ years)
        if segments['veteran_owners']:
            campaigns.append({
                'campaign_type': 'ownership_milestone',
                'segment': 'veteran_owners', 
                'title': 'Veteran Vehicle Major Service Package',
                'target_customers': segments['veteran_owners'],
                'priority': 'high',
                'urgency': 'high',
                'benefits': [
                    'Major service inspection',
                    'Timing belt replacement',
                    'Suspension system check',
                    'Engine performance optimization'
                ],
                'cta': 'Schedule Major Service'
            })
        
        return campaigns
    
    def _generate_mileage_campaigns(self, segments: Dict, location: str) -> List[Dict]:
        """Generate mileage-based campaigns"""
        
        campaigns = []
        
        # High Mileage Campaign (50K+ km)
        if segments['high_mileage']:
            campaigns.append({
                'campaign_type': 'mileage_based',
                'segment': 'high_mileage',
                'title': 'High-Mileage Vehicle Care',
                'target_customers': segments['high_mileage'],
                'priority': 'high',
                'urgency': 'high',
                'benefits': [
                    'Tire replacement packages',
                    'Brake pad and disc service',
                    'Battery replacement options',
                    'Extended warranty plans'
                ],
                'cta': 'Protect Your Investment'
            })
        
        # Ultra High Mileage Campaign (100K+ km)
        if segments['ultra_high_mileage']:
            campaigns.append({
                'campaign_type': 'mileage_based',
                'segment': 'ultra_high_mileage',
                'title': 'Ultra High-Mileage Specialist Care',
                'target_customers': segments['ultra_high_mileage'],
                'priority': 'critical',
                'urgency': 'high',
                'benefits': [
                    'Complete engine overhaul packages',
                    'Transmission service specials',
                    'Cooling system replacement',
                    'Major component warranties'
                ],
                'cta': 'Comprehensive Care Package'
            })
        
        return campaigns
    
    def _generate_warranty_campaigns(self, segments: Dict, location: str) -> List[Dict]:
        """Generate warranty expiration campaigns"""
        
        campaigns = []
        
        if segments['warranty_expiring']:
            campaigns.append({
                'campaign_type': 'warranty_expiring',
                'segment': 'warranty_expiring',
                'title': 'Warranty Expiring - Extended Protection Available',
                'target_customers': segments['warranty_expiring'],
                'priority': 'critical',
                'urgency': 'high',
                'benefits': [
                    'Extended warranty options',
                    'Pre-expiry comprehensive inspection',
                    'Priority service booking',
                    'Special extended coverage rates'
                ],
                'cta': 'Secure Your Coverage'
            })
        
        return campaigns
    
    def _generate_service_due_campaigns(self, segments: Dict, location: str) -> List[Dict]:
        """Generate overdue service campaigns"""
        
        campaigns = []
        
        if segments['service_due']:
            campaigns.append({
                'campaign_type': 'service_overdue',
                'segment': 'service_due',
                'title': 'Important: Service Overdue - Book Now',
                'target_customers': segments['service_due'],
                'priority': 'critical',
                'urgency': 'high',
                'benefits': [
                    'Emergency service booking',
                    'Health and safety inspection',
                    'Preventive maintenance package',
                    'Same-day service options'
                ],
                'cta': 'Book Emergency Service'
            })
        
        return campaigns
    
    def _parse_date(self, date_str):
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y']:
                try:
                    return datetime.strptime(str(date_str)[:10], fmt)
                except:
                    continue
            return None
        except:
            return None
    
    def _calculate_years_since(self, date_obj):
        """Calculate years since given date"""
        if not date_obj:
            return 0
        return (datetime.now() - date_obj).days / 365.25
    
    def _calculate_days_since(self, date_obj):
        """Calculate days since given date"""
        if not date_obj:
            return 0
        return (datetime.now() - date_obj).days
    
    def _days_until_date(self, date_obj):
        """Calculate days until given date"""
        if not date_obj:
            return 999
        return (date_obj - datetime.now()).days
