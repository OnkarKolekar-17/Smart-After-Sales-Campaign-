#!/usr/bin/env python3
"""Test Google Calendar integration for holiday fetching"""

from agents.holiday_agent import HolidayAgent

def test_google_calendar():
    print("🧪 Testing Google Calendar Holiday Integration...")
    
    try:
        agent = HolidayAgent()
        
        # Test Google Calendar API initialization
        if agent.calendar_service:
            print("✅ Google Calendar API initialized successfully")
        else:
            print("❌ Google Calendar API initialization failed")
        
        # Fetch holidays from Google Calendar
        holidays = agent._fetch_google_calendar_holidays(15)
        
        if holidays:
            print(f"\n🎉 Found {len(holidays)} holidays from Google Calendar:")
            for holiday in holidays:
                print(f"  📅 {holiday['name']} ({holiday['date']}) - {holiday['days_until']} days away")
                print(f"      Type: {holiday.get('type', 'N/A')}")
                print(f"      Themes: {', '.join(holiday.get('campaign_themes', []))}")
                print()
        else:
            print("❌ No holidays fetched from Google Calendar")
            
        # Test the main get_upcoming_holidays method
        print("\n🔍 Testing main holiday fetching method...")
        upcoming_holidays = agent._get_upcoming_holidays(15)
        
        if upcoming_holidays:
            print(f"✅ Found {len(upcoming_holidays)} upcoming holidays:")
            for holiday in upcoming_holidays:
                source = holiday.get('source', 'unknown')
                print(f"  🎊 {holiday['name']} ({holiday['date']}) - {holiday['days_until']} days away [Source: {source}]")
        else:
            print("❌ No upcoming holidays found")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_google_calendar()
