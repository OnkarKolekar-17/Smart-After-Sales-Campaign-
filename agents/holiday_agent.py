from typing import Dict, Any, List
import json
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from agents.base_agent import BaseAgent
from workflows.states import HolidayData

class HolidayAgent(BaseAgent):
    """Agent responsible for analyzing holidays and generating festival-based campaigns"""
    
    def __init__(self):
        super().__init__(
            agent_name="HolidayAgent",
            system_prompt=self._get_default_system_prompt()
        )
        # Initialize Google Calendar service
        self.calendar_service = self._initialize_google_calendar()
        
        # Load holidays data (fallback to file if Google Calendar fails)
        self.holidays_data = self._load_holidays_data()
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are a CREATIVE Holiday Campaign Mastermind specializing in innovative automotive marketing campaigns.
        
        🎯 YOUR MISSION: Transform ANY holiday into compelling, memorable automotive service campaigns that customers can't resist.
        
        🚗 CREATIVE THINKING FRAMEWORK:
        1. CREATE CATCHY, HOLIDAY-THEMED CAMPAIGN NAMES that connect to the specific holiday
        2. BUNDLE SERVICES creatively around that holiday's unique needs
        3. USE HOLIDAY EMOTIONS & TRADITIONS as campaign hooks
        4. OFFER GIFT OPPORTUNITIES for gift-giving holidays
        5. CREATE URGENCY through holiday timing
        6. ADDRESS TRAVEL SAFETY CONCERNS for travel-heavy holidays
        7. TRANSFORM BASIC MAINTENANCE into holiday experiences
        8. CONNECT VEHICLE CARE to holiday memories and family safety
        9. LEVERAGE FINANCIAL MOTIVATIONS for year-end or bonus seasons
        10. CREATE "MUST-HAVE" holiday preparation packages
        
        🎨 CAMPAIGN INNOVATION APPROACH:
        For each holiday, think about:
        • What makes this holiday special? (traditions, emotions, activities)
        • What vehicle needs arise? (travel, weather, celebrations)
        • What creative angle can make maintenance exciting?
        • How can you bundle services around holiday timing?
        • What memorable campaign name captures the holiday spirit?
        
        Your job: Create ONE breakthrough holiday campaign that makes customers think "I NEED this for [THIS SPECIFIC HOLIDAY]!"
        Be creative, be memorable, be irresistible - but adapt to whatever holiday you're given! 🔥
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process holiday data and generate campaign insights"""
        try:
            self._log_step("Starting holiday analysis")
            
            # Find upcoming holidays
            upcoming_holidays = self._get_upcoming_holidays(days_ahead=30)
            
            if upcoming_holidays:
                # Select the most relevant holiday
                primary_holiday = self._select_primary_holiday(upcoming_holidays)
                
                # Generate campaign recommendations
                campaign_insights = self._generate_holiday_recommendations(primary_holiday)
                
                # Create HolidayData object
                holiday_data = HolidayData(
                    name=primary_holiday['name'],
                    date=primary_holiday['date'],
                    type=primary_holiday.get('type', 'Festival'),
                    description=campaign_insights,
                    cultural_significance=primary_holiday.get('cultural_significance', '')
                )
                
                # Store as dictionary to maintain compatibility
                state['holiday_data'] = holiday_data.dict()
                state['upcoming_holidays'] = upcoming_holidays
                
                self._log_step(f"Holiday analysis completed for {primary_holiday['name']}")
            else:
                self._log_step("No upcoming holidays found in the next 30 days")
                
        except Exception as e:
            return self._handle_error(e, state)
        
        return state

    def _initialize_google_calendar(self):
        """Initialize Google Calendar API service"""
        try:
            SERVICE_ACCOUNT_FILE = os.path.join('config', 'marketingcampaigns-466306-374a8b3fbe0f.json')
            
            if not os.path.exists(SERVICE_ACCOUNT_FILE):
                self._log_step("⚠️  Google Calendar credentials not found, will use fallback holiday data", "warning")
                return None
            
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE,
                scopes=['https://www.googleapis.com/auth/calendar.readonly']
            )
            
            service = build('calendar', 'v3', credentials=creds)
            self._log_step("✅ Google Calendar API initialized successfully")
            return service
            
        except Exception as e:
            self._log_step(f"❌ Failed to initialize Google Calendar API: {e}", "error")
            self._log_step("Will use fallback holiday data", "warning")
            return None

    def _fetch_google_calendar_holidays(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Fetch upcoming holidays from Google Calendar"""
        if not self.calendar_service:
            self._log_step("Google Calendar service not available, using fallback")
            return []
        
        try:
            # Set date range - current date to days_ahead
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'  # Current time in UTC
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Indian holidays calendar ID
            CALENDAR_ID = 'en.indian#holiday@group.v.calendar.google.com'
            
            self._log_step(f"🗓️  Fetching holidays from Google Calendar for next {days_ahead} days...")
            
            # Fetch events from Google Calendar
            events = self.calendar_service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            holidays = []
            
            if not events.get('items'):
                self._log_step("📅 No holidays found in Google Calendar for this period")
                return []
            
            for event in events.get('items', []):
                try:
                    # Handle both all-day events (date) and timed events (dateTime)
                    start_date_str = event['start'].get('date', event['start'].get('dateTime', '').split('T')[0])
                    
                    if start_date_str:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                        days_until = (start_date - now.date()).days
                        
                        # Map holiday name to campaign themes and significance
                        holiday_data = self._map_holiday_to_campaign_data(event['summary'], start_date_str)
                        holiday_data['days_until'] = days_until
                        
                        holidays.append(holiday_data)
                        self._log_step(f"✅ Found holiday: {event['summary']} ({start_date_str}) - {days_until} days away")
                
                except Exception as e:
                    self._log_step(f"⚠️  Error processing calendar event: {e}", "warning")
                    continue
            
            self._log_step(f"🎉 Successfully fetched {len(holidays)} holidays from Google Calendar")
            return holidays
            
        except HttpError as error:
            self._log_step(f"❌ Google Calendar API error: {error}", "error")
            return []
        except Exception as e:
            self._log_step(f"❌ Unexpected error fetching calendar holidays: {e}", "error")
            return []

    def _map_holiday_to_campaign_data(self, holiday_name: str, date_str: str) -> Dict[str, Any]:
        """Map Google Calendar holiday to campaign-relevant data"""
        
        # Define campaign themes and significance for major Indian holidays
        holiday_mapping = {
            'diwali': {
                'type': 'Major Festival',
                'cultural_significance': 'Festival of lights, prosperity, and new beginnings',
                'travel_impact': 'High',
                'campaign_themes': ['prosperity', 'new beginnings', 'family travel', 'vehicle blessing', 'lights', 'celebration']
            },
            'dussehra': {
                'type': 'Major Festival', 
                'cultural_significance': 'Victory of good over evil',
                'travel_impact': 'High',
                'campaign_themes': ['victory', 'new purchases', 'long journeys', 'vehicle protection', 'triumph']
            },
            'holi': {
                'type': 'Festival',
                'cultural_significance': 'Festival of colors and spring',
                'travel_impact': 'Medium',
                'campaign_themes': ['colors', 'spring cleaning', 'vehicle wash', 'celebration', 'renewal']
            },
            'eid': {
                'type': 'Religious Festival',
                'cultural_significance': 'End of Ramadan, celebration and giving',
                'travel_impact': 'High',
                'campaign_themes': ['charity', 'family gatherings', 'travel', 'blessings', 'generosity']
            },
            'christmas': {
                'type': 'Religious Festival',
                'cultural_significance': 'Birth of Jesus Christ, joy and giving',
                'travel_impact': 'High',
                'campaign_themes': ['joy', 'family gatherings', 'winter travel', 'gifts', 'celebration']
            },
            'new year': {
                'type': 'Celebration',
                'cultural_significance': 'New beginnings and resolutions',
                'travel_impact': 'High',
                'campaign_themes': ['new beginnings', 'resolutions', 'fresh start', 'travel', 'celebration']
            },
            'ganesh chaturthi': {
                'type': 'Religious Festival',
                'cultural_significance': 'Lord Ganesha festival, remover of obstacles',
                'travel_impact': 'Medium',
                'campaign_themes': ['obstacle removal', 'new ventures', 'prosperity', 'blessings']
            },
            'karva chauth': {
                'type': 'Traditional Festival',
                'cultural_significance': 'Wives pray for husbands longevity',
                'travel_impact': 'Medium',
                'campaign_themes': ['family care', 'safety', 'protection', 'love', 'devotion']
            },
            'raksha bandhan': {
                'type': 'Traditional Festival',
                'cultural_significance': 'Brother-sister bond and protection',
                'travel_impact': 'Medium',
                'campaign_themes': ['protection', 'family bonds', 'safety', 'care', 'relationships']
            }
        }
        
        # Find matching holiday data based on name (case-insensitive)
        holiday_key = None
        holiday_name_lower = holiday_name.lower()
        
        for key in holiday_mapping.keys():
            if key in holiday_name_lower:
                holiday_key = key
                break
        
        if holiday_key:
            mapped_data = holiday_mapping[holiday_key].copy()
        else:
            # Default mapping for unknown holidays
            mapped_data = {
                'type': 'Festival',
                'cultural_significance': 'Traditional celebration and observance',
                'travel_impact': 'Medium',
                'campaign_themes': ['celebration', 'tradition', 'family time', 'travel']
            }
        
        # Add basic holiday information
        mapped_data.update({
            'name': holiday_name,
            'date': date_str,
            'source': 'google_calendar'
        })
        
        return mapped_data
    
    def _load_holidays_data(self) -> List[Dict[str, Any]]:
        """Load holidays data from JSON file"""
        try:
            holidays_file = os.path.join('data', 'holidays.json')
            if os.path.exists(holidays_file):
                with open(holidays_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self._log_step("Holidays data file not found, using default holidays", "warning")
                return self._get_default_holidays()
        except Exception as e:
            self._log_step(f"Error loading holidays data: {e}", "error")
            return self._get_default_holidays()
    
    def _get_default_holidays(self) -> List[Dict[str, Any]]:
        """Return default Indian holidays for the current year"""
        current_year = datetime.now().year
        return [
            {
                "name": "Diwali",
                "date": f"{current_year}-11-12",
                "type": "Major Festival",
                "cultural_significance": "Festival of lights, prosperity, and new beginnings",
                "travel_impact": "High",
                "campaign_themes": ["prosperity", "new beginnings", "family travel", "vehicle blessing"]
            },
            {
                "name": "Dussehra",
                "date": f"{current_year}-10-24",
                "type": "Major Festival", 
                "cultural_significance": "Victory of good over evil",
                "travel_impact": "High",
                "campaign_themes": ["victory", "new purchases", "long journeys", "vehicle protection"]
            },
            {
                "name": "Holi",
                "date": f"{current_year + 1}-03-14",
                "type": "Festival",
                "cultural_significance": "Festival of colors and spring",
                "travel_impact": "Medium",
                "campaign_themes": ["colors", "spring cleaning", "vehicle wash", "celebration"]
            },
            {
                "name": "Eid",
                "date": f"{current_year + 1}-04-10",
                "type": "Religious Festival",
                "cultural_significance": "End of Ramadan, celebration and giving",
                "travel_impact": "High",
                "campaign_themes": ["charity", "family gatherings", "travel", "blessings"]
            }
        ]
    
    def _get_upcoming_holidays(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get holidays occurring within the next specified days - prioritize Google Calendar"""
        
        # Try to fetch from Google Calendar first
        google_holidays = self._fetch_google_calendar_holidays(days_ahead)
        
        if google_holidays:
            self._log_step(f"🎉 Using {len(google_holidays)} holidays from Google Calendar")
            return sorted(google_holidays, key=lambda x: x['days_until'])
        
        # Fallback to file-based holidays if Google Calendar fails
        self._log_step("📄 Falling back to file-based holiday data")
        
        today = datetime.now().date()
        future_date = today + timedelta(days=days_ahead)
        
        upcoming = []
        for holiday in self.holidays_data:
            try:
                holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
                
                if today <= holiday_date <= future_date:
                    # Calculate days until holiday
                    days_until = (holiday_date - today).days
                    holiday_copy = holiday.copy()
                    holiday_copy['days_until'] = days_until
                    holiday_copy['source'] = 'file_based'
                    upcoming.append(holiday_copy)
                    
            except ValueError as e:
                self._log_step(f"Invalid date format in holiday data: {holiday.get('name', 'Unknown')}", "warning")
                continue
        
        # Sort by date (closest first)
        upcoming.sort(key=lambda x: x['days_until'])
        return upcoming
    
    def _select_primary_holiday(self, holidays: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the most relevant holiday for campaign generation"""
        if not holidays:
            return None
        
        # Priority logic:
        # 1. Major festivals get higher priority
        # 2. Closer holidays get higher priority
        # 3. High travel impact holidays get higher priority
        
        def holiday_priority_score(holiday):
            score = 0
            
            # Type priority
            if holiday.get('type') == 'Major Festival':
                score += 10
            elif holiday.get('type') == 'Festival':
                score += 7
            elif holiday.get('type') == 'Religious Festival':
                score += 8
            
            # Travel impact priority
            travel_impact = holiday.get('travel_impact', 'Low').lower()
            if travel_impact == 'high':
                score += 5
            elif travel_impact == 'medium':
                score += 3
            
            # Proximity priority (closer = higher score, but not too close)
            days_until = holiday.get('days_until', 30)
            if 7 <= days_until <= 21:  # Sweet spot for campaign preparation
                score += 8
            elif 3 <= days_until <= 30:
                score += 5
            
            return score
        
        # Select holiday with highest score
        holidays_with_scores = [(h, holiday_priority_score(h)) for h in holidays]
        holidays_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        selected_holiday = holidays_with_scores[0][0]
        self._log_step(f"Selected primary holiday: {selected_holiday['name']} (Score: {holidays_with_scores[0][1]})")
        
        return selected_holiday
    
    def _generate_holiday_recommendations(self, holiday: Dict[str, Any]) -> str:
        """Generate campaign recommendations based on holiday data"""
        
        holiday_context = f"""
        Upcoming Holiday Analysis:
        
        Holiday: {holiday['name']}
        Date: {holiday['date']}
        Days Until: {holiday.get('days_until', 'Unknown')}
        Type: {holiday.get('type', 'Festival')}
        Cultural Significance: {holiday.get('cultural_significance', 'Important celebration')}
        Travel Impact: {holiday.get('travel_impact', 'Medium')}
        Campaign Themes: {', '.join(holiday.get('campaign_themes', []))}
        
        Based on this holiday information, create comprehensive automotive service campaign recommendations that:
        
        1. Align with the cultural and emotional significance of {holiday['name']}
        2. Address practical vehicle preparation needs for holiday travel
        3. Offer timely services and promotions
        4. Create emotional connections with customers
        5. Consider the {holiday.get('days_until', 0)} days lead time for campaign execution
        
        Include specific service recommendations, promotional ideas, messaging themes, and target customer segments.
        """
        
        try:
            recommendations = self._invoke_llm(holiday_context)
            return recommendations
        except Exception as e:
            self._log_step(f"Failed to generate holiday recommendations: {e}", "error")
            return f"Standard holiday preparation services recommended for {holiday['name']}."