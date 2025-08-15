from typing import Dict, Any, List
import json
import os
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from workflows.states import HolidayData

class HolidayAgent(BaseAgent):
    """Agent responsible for analyzing holidays and generating festival-based campaigns"""
    
    def __init__(self):
        super().__init__(
            agent_name="HolidayAgent",
            system_prompt=self._get_default_system_prompt()
        )
        self.holidays_data = self._load_holidays_data()
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are a Holiday Campaign Analysis Agent specializing in automotive marketing campaigns.
        
        Your role is to analyze upcoming holidays and festivals to create compelling automotive service campaigns.
        
        Consider these factors:
        - Cultural significance of holidays and festivals
        - Travel patterns during holiday seasons
        - Vehicle preparation needs for long journeys
        - Seasonal vehicle maintenance requirements
        - Gift and promotional opportunities
        - Regional customs and traditions
        
        Focus on creating campaigns that:
        1. Resonate with cultural values and traditions
        2. Address practical vehicle needs during holiday travel
        3. Offer value through timely services and promotions
        4. Build emotional connections with customers
        
        Always provide specific, actionable campaign ideas with clear value propositions.
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
        """Get holidays occurring within the next specified days"""
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