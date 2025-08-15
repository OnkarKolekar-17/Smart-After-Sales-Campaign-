import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import requests

# Import services to test
from services.weather_service import WeatherService
from services.holiday_service import HolidayService
from services.brevo_service import BrevoService
from services.database_service import DatabaseService


class TestWeatherService(unittest.TestCase):
    """Test cases for WeatherService"""
    
    def setUp(self):
        self.service = WeatherService()
    
    @patch('services.weather_service.requests.get')
    def test_get_current_weather_success(self, mock_get):
        """Test successful weather data retrieval"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'name': 'Mumbai',
            'main': {
                'temp': 28.5,
                'humidity': 65
            },
            'weather': [
                {
                    'main': 'Clouds',
                    'description': 'scattered clouds'
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.service.get_current_weather('Mumbai')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['location'], 'Mumbai')
        self.assertEqual(result['temperature'], 28.5)
        self.assertEqual(result['humidity'], 65)
        self.assertIn('recommendation', result)
    
    @patch('services.weather_service.requests.get')
    def test_get_current_weather_api_error(self, mock_get):
        """Test weather service with API error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.service.get_current_weather('InvalidCity')
        
        self.assertIsNone(result)
    
    @patch('services.weather_service.requests.get')
    def test_get_current_weather_network_error(self, mock_get):
        """Test weather service with network error"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = self.service.get_current_weather('Mumbai')
        
        self.assertIsNone(result)
    
    def test_get_weather_recommendation(self):
        """Test weather recommendation logic"""
        # Test hot weather
        hot_weather = {
            'temperature': 40,
            'condition': 'Clear',
            'humidity': 30
        }
        recommendation = self.service._get_weather_recommendation(hot_weather)
        self.assertIn('AC', recommendation.lower())
        
        # Test rainy weather
        rainy_weather = {
            'temperature': 25,
            'condition': 'Rain',
            'humidity': 85
        }
        recommendation = self.service._get_weather_recommendation(rainy_weather)
        self.assertIn('wiper', recommendation.lower() or 'brake', recommendation.lower())


class TestHolidayService(unittest.TestCase):
    """Test cases for HolidayService"""
    
    def setUp(self):
        self.service = HolidayService()
    
    @patch('services.holiday_service.os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, 
           read_data='[{"name": "Diwali", "date": "2024-11-01", "type": "religious"}]')
    def test_get_current_holidays_success(self, mock_open, mock_exists):
        """Test successful holiday retrieval"""
        mock_exists.return_value = True
        
        holidays = self.service.get_current_holidays()
        
        self.assertIsInstance(holidays, list)
        if holidays:  # If holidays are returned
            self.assertIn('name', holidays[0])
            self.assertIn('date', holidays[0])
    
    @patch('services.holiday_service.os.path.exists')
    def test_get_current_holidays_file_not_found(self, mock_exists):
        """Test holiday service when file doesn't exist"""
        mock_exists.return_value = False
        
        holidays = self.service.get_current_holidays()
        
        self.assertEqual(holidays, [])
    
    def test_is_current_holiday(self):
        """Test current holiday detection logic"""
        # Test with today's date
        today_holiday = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'name': 'Test Holiday'
        }
        self.assertTrue(self.service._is_current_holiday(today_holiday))
        
        # Test with past date
        past_holiday = {
            'date': '2020-01-01',
            'name': 'Past Holiday'
        }
        self.assertFalse(self.service._is_current_holiday(past_holiday))
    
    def test_get_holiday_campaigns(self):
        """Test holiday campaign generation"""
        holiday = {
            'name': 'Diwali',
            'type': 'religious',
            'date': '2024-11-01'
        }
        
        campaigns = self.service.get_holiday_campaigns([holiday])
        
        self.assertIsInstance(campaigns, list)
        if campaigns:
            self.assertIn('discount', campaigns[0])
            self.assertIn('message', campaigns[0])


class TestBrevoService(unittest.TestCase):
    """Test cases for BrevoService"""
    
    def setUp(self):
        with patch('services.brevo_service.sib_api_v3_sdk.Configuration'):
            self.service = BrevoService()
    
    @patch('services.brevo_service.sib_api_v3_sdk.TransactionalEmailsApi')
    def test_send_transactional_email_success(self, mock_api):
        """Test successful email sending"""
        # Mock API response
        mock_response = Mock()
        mock_response.message_id = 'msg_123456'
        mock_api.return_value.send_transac_email.return_value = mock_response
        
        self.service.transactional_api = mock_api.return_value
        
        result = self.service.send_transactional_email(
            to_email='test@example.com',
            to_name='Test User',
            subject='Test Subject',
            html_content='<p>Test content</p>'
        )
        
        self.assertEqual(result, 'msg_123456')
    
    @patch('services.brevo_service.sib_api_v3_sdk.TransactionalEmailsApi')
    def test_send_transactional_email_api_error(self, mock_api):
        """Test email sending with API error"""
        from sib_api_v3_sdk.rest import ApiException
        
        mock_api.return_value.send_transac_email.side_effect = ApiException("API Error")
        self.service.transactional_api = mock_api.return_value
        
        result = self.service.send_transactional_email(
            to_email='invalid@example.com',
            to_name='Test User',
            subject='Test Subject',
            html_content='<p>Test content</p>'
        )
        
        self.assertIsNone(result)
    
    def test_html_to_text(self):
        """Test HTML to text conversion"""
        html_content = '<h1>Title</h1><p>This is a <b>test</b> paragraph.</p>'
        text_content = self.service._html_to_text(html_content)
        
        self.assertNotIn('<', text_content)
        self.assertNotIn('>', text_content)
        self.assertIn('Title', text_content)
        self.assertIn('test', text_content)
    
    @patch('services.brevo_service.sib_api_v3_sdk.ContactsApi')
    def test_create_contact_success(self, mock_api):
        """Test successful contact creation"""
        self.service.contacts_api = mock_api.return_value
        
        result = self.service.create_or_update_contact(
            email='newuser@example.com',
            attributes={'NAME': 'New User'}
        )
        
        self.assertTrue(result)
    
    @patch('services.brevo_service.sib_api_v3_sdk.ContactsApi')
    def test_update_existing_contact(self, mock_api):
        """Test updating existing contact"""
        from sib_api_v3_sdk.rest import ApiException
        
        # Mock contact already exists error
        error = ApiException("Contact already exist")
        error.status = 400
        
        mock_api.return_value.create_contact.side_effect = error
        self.service.contacts_api = mock_api.return_value
        
        result = self.service.create_or_update_contact(
            email='existing@example.com',
            attributes={'NAME': 'Existing User'}
        )
        
        self.assertTrue(result)


class TestDatabaseService(unittest.TestCase):
    """Test cases for DatabaseService"""
    
    def setUp(self):
        self.service = DatabaseService()
    
    @patch('services.database_service.psycopg2.connect')
    def test_get_connection_success(self, mock_connect):
        """Test successful database connection"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        connection = self.service.get_connection()
        
        self.assertEqual(connection, mock_connection)
    
    @patch('services.database_service.psycopg2.connect')
    def test_get_connection_error(self, mock_connect):
        """Test database connection error handling"""
        mock_connect.side_effect = Exception("Connection failed")
        
        connection = self.service.get_connection()
        
        self.assertIsNone(connection)
    
    @patch.object(DatabaseService, 'get_connection')
    def test_execute_query_success(self, mock_get_connection):
        """Test successful query execution"""
        # Mock connection and cursor
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test'}]
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection
        
        result = self.service.execute_query("SELECT * FROM test")
        
        self.assertEqual(result, [{'id': 1, 'name': 'Test'}])
    
    @patch.object(DatabaseService, 'get_connection')
    def test_execute_query_error(self, mock_get_connection):
        """Test query execution with error"""
        mock_get_connection.return_value = None
        
        result = self.service.execute_query("SELECT * FROM test")
        
        self.assertEqual(result, [])
    
    @patch.object(DatabaseService, 'execute_query')
    def test_get_customers_by_location(self, mock_execute):
        """Test getting customers by location"""
        mock_execute.return_value = [
            {
                'customer_id': 1,
                'name': 'John Doe',
                'email': 'john@example.com',
                'preferred_location': 'Mumbai'
            }
        ]
        
        customers = self.service.get_customers_by_location('Mumbai')
        
        self.assertIsInstance(customers, list)
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0]['name'], 'John Doe')
    
    @patch.object(DatabaseService, 'execute_query')
    def test_get_customers_needing_service(self, mock_execute):
        """Test getting customers needing service"""
        mock_execute.return_value = [
            {
                'customer_id': 1,
                'name': 'Jane Doe',
                'last_service_date': date(2024, 1, 1),
                'days_since_service': 200
            }
        ]
        
        customers = self.service.get_customers_needing_service(180)
        
        self.assertIsInstance(customers, list)
        self.assertEqual(len(customers), 1)
        self.assertGreater(customers[0]['days_since_service'], 180)
    
    @patch.object(DatabaseService, 'get_connection')
    def test_save_campaign_success(self, mock_get_connection):
        """Test successful campaign saving"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {'id': 1}
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_connection
        
        campaign_data = {
            'campaign_id': 'test_campaign_123',
            'customer_id': 1,
            'campaign_type': 'test',
            'subject_line': 'Test Subject',
            'content': 'Test Content'
        }
        
        result = self.service.save_campaign(campaign_data)
        
        self.assertEqual(result, 1)
    
    @patch.object(DatabaseService, 'get_connection')
    def test_save_campaign_error(self, mock_get_connection):
        """Test campaign saving with error"""
        mock_get_connection.return_value = None
        
        campaign_data = {
            'campaign_id': 'test_campaign_123',
            'customer_id': 1,
            'campaign_type': 'test'
        }
        
        result = self.service.save_campaign(campaign_data)
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()