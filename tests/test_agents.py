import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import json

# Import agents to test
from agents.weather_agent import WeatherAgent
from agents.holiday_agent import HolidayAgent
from agents.targeting_agent import TargetingAgent
from agents.campaign_generator_agent import CampaignGeneratorAgent
from agents.email_sender_agent import EmailSenderAgent
from agents.data_analyst_agent import DataAnalystAgent
from agents.personalization_agent import PersonalizationAgent


class TestWeatherAgent(unittest.TestCase):
    """Test cases for WeatherAgent"""
    
    def setUp(self):
        self.agent = WeatherAgent()
    
    @patch('agents.weather_agent.WeatherService')
    def test_process_success(self, mock_weather_service):
        """Test successful weather data processing"""
        # Mock weather service response
        mock_weather_service.return_value.get_current_weather.return_value = {
            'location': 'Mumbai',
            'temperature': 28.5,
            'condition': 'Partly Cloudy',
            'humidity': 65,
            'description': 'Pleasant weather with some clouds'
        }
        
        state = {'location': 'Mumbai'}
        result = self.agent.process(state)
        
        self.assertIn('weather_data', result)
        self.assertEqual(result['weather_data']['location'], 'Mumbai')
        self.assertEqual(result['weather_data']['temperature'], 28.5)
    
    def test_process_missing_location(self):
        """Test processing with missing location"""
        state = {}
        result = self.agent.process(state)
        
        # Should use default location
        self.assertIn('weather_data', result)
        self.assertIsInstance(result['weather_data'], dict)


class TestHolidayAgent(unittest.TestCase):
    """Test cases for HolidayAgent"""
    
    def setUp(self):
        self.agent = HolidayAgent()
    
    @patch('agents.holiday_agent.HolidayService')
    def test_process_success(self, mock_holiday_service):
        """Test successful holiday data processing"""
        mock_holiday_service.return_value.get_current_holidays.return_value = [
            {
                'name': 'Diwali',
                'date': '2024-11-01',
                'type': 'religious',
                'description': 'Festival of Lights'
            }
        ]
        
        state = {'location': 'Mumbai'}
        result = self.agent.process(state)
        
        self.assertIn('holiday_data', result)
        self.assertIn('current_holidays', result['holiday_data'])
        self.assertEqual(len(result['holiday_data']['current_holidays']), 1)
    
    def test_process_no_holidays(self):
        """Test processing when no holidays are found"""
        with patch('agents.holiday_agent.HolidayService') as mock_service:
            mock_service.return_value.get_current_holidays.return_value = []
            
            state = {'location': 'Mumbai'}
            result = self.agent.process(state)
            
            self.assertIn('holiday_data', result)
            self.assertEqual(len(result['holiday_data']['current_holidays']), 0)


class TestTargetingAgent(unittest.TestCase):
    """Test cases for TargetingAgent"""
    
    def setUp(self):
        self.agent = TargetingAgent()
    
    @patch('agents.targeting_agent.DatabaseService')
    def test_process_success(self, mock_db_service):
        """Test successful customer targeting"""
        # Mock database response
        mock_db_service.return_value.execute_query.return_value = [
            {
                'customer_id': 1,
                'name': 'John Doe',
                'email': 'john@example.com',
                'phone': '+919876543210',
                'preferred_location': 'Mumbai',
                'vehicle_id': 1,
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2020,
                'last_service_date': date(2024, 6, 15),
                'warranty_end': date(2025, 12, 31)
            }
        ]
        
        state = {
            'location': 'Mumbai',
            'campaign_trigger': 'scheduled'
        }
        result = self.agent.process(state)
        
        self.assertIn('targeted_customers', result)
        self.assertIn('targeting_summary', result)
        self.assertGreater(len(result['targeted_customers']), 0)
    
    def test_process_no_customers(self):
        """Test processing when no customers match criteria"""
        with patch('agents.targeting_agent.DatabaseService') as mock_service:
            mock_service.return_value.execute_query.return_value = []
            
            state = {'location': 'NonExistentCity'}
            result = self.agent.process(state)
            
            self.assertIn('targeted_customers', result)
            self.assertEqual(len(result['targeted_customers']), 0)


class TestCampaignGeneratorAgent(unittest.TestCase):
    """Test cases for CampaignGeneratorAgent"""
    
    def setUp(self):
        self.agent = CampaignGeneratorAgent()
    
    @patch.object(CampaignGeneratorAgent, '_invoke_llm')
    def test_process_success(self, mock_llm):
        """Test successful campaign generation"""
        # Mock LLM response
        mock_llm.return_value = json.dumps({
            'campaigns': [
                {
                    'campaign_title': 'Winter Service Special',
                    'subject_line': 'Prepare Your Vehicle for Winter',
                    'content': 'Winter is coming...',
                    'cta_text': 'Book Winter Service',
                    'campaign_type': 'seasonal'
                }
            ]
        })
        
        state = {
            'weather_data': {'condition': 'Cold', 'temperature': 15},
            'holiday_data': {'current_holidays': []},
            'targeted_customers': [{'customer_id': 1, 'name': 'John'}],
            'location': 'Mumbai'
        }
        
        result = self.agent.process(state)
        
        self.assertIn('generated_campaigns', result)
        self.assertGreater(len(result['generated_campaigns']), 0)
    
    @patch.object(CampaignGeneratorAgent, '_invoke_llm')
    def test_process_llm_error(self, mock_llm):
        """Test campaign generation with LLM error"""
        mock_llm.side_effect = Exception("LLM Error")
        
        state = {
            'weather_data': {'condition': 'Sunny'},
            'targeted_customers': [{'customer_id': 1}]
        }
        
        result = self.agent.process(state)
        
        self.assertIn('errors', result)
        self.assertIn('generated_campaigns', result)


class TestEmailSenderAgent(unittest.TestCase):
    """Test cases for EmailSenderAgent"""
    
    def setUp(self):
        self.agent = EmailSenderAgent()
    
    @patch('agents.email_sender_agent.BrevoService')
    def test_process_success(self, mock_brevo_service):
        """Test successful email sending"""
        # Mock Brevo service
        mock_brevo_service.return_value.send_transactional_email.return_value = 'msg_123'
        
        state = {
            'personalized_campaigns': [
                {
                    'customer_id': 1,
                    'customer_name': 'John Doe',
                    'customer_email': 'john@example.com',
                    'subject_line': 'Test Subject',
                    'content': 'Test Content',
                    'campaign_type': 'test'
                }
            ]
        }
        
        result = self.agent.process(state)
        
        self.assertIn('campaigns_sent', result)
        self.assertIn('email_results', result)
        self.assertGreater(len(result['campaigns_sent']), 0)
    
    def test_process_no_campaigns(self):
        """Test processing with no campaigns to send"""
        state = {'personalized_campaigns': []}
        result = self.agent.process(state)
        
        self.assertIn('campaigns_sent', result)
        self.assertEqual(len(result['campaigns_sent']), 0)


class TestDataAnalystAgent(unittest.TestCase):
    """Test cases for DataAnalystAgent"""
    
    def setUp(self):
        self.agent = DataAnalystAgent()
    
    @patch('agents.data_analyst_agent.DatabaseService')
    def test_process_success(self, mock_db_service):
        """Test successful data analysis"""
        # Mock database response
        mock_db_service.return_value.execute_query.return_value = [
            {
                'customer_id': 1,
                'name': 'John Doe',
                'email': 'john@example.com',
                'preferred_location': 'Mumbai',
                'vehicle_id': 1,
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2020,
                'registration_date': date(2020, 1, 1),
                'last_service_date': date(2024, 6, 15),
                'warranty_end': date(2025, 12, 31),
                'last_service_cost': 5000.0
            }
        ]
        
        state = {'location': 'Mumbai'}
        result = self.agent.process(state)
        
        self.assertIn('data_analysis', result)
        self.assertIn('customer_segments', result['data_analysis'])
        self.assertIn('analysis_summary', result['data_analysis'])
    
    def test_customer_segmentation(self):
        """Test customer segmentation logic"""
        customers_data = [
            {
                'customer_id': 1,
                'name': 'John Doe',
                'vehicles': [
                    {
                        'registration_date': date(2024, 1, 1),  # New vehicle
                        'last_service_date': date(2024, 8, 1),   # Recent service
                        'warranty_end': date(2025, 1, 1),        # Active warranty
                        'last_service_cost': 15000.0             # High value
                    }
                ]
            }
        ]
        
        segments = self.agent._segment_customers(customers_data)
        
        self.assertIn('new_customers', segments)
        self.assertIn('regular_customers', segments)
        self.assertIn('high_value_customers', segments)


class TestPersonalizationAgent(unittest.TestCase):
    """Test cases for PersonalizationAgent"""
    
    def setUp(self):
        self.agent = PersonalizationAgent()
    
    def test_process_success(self):
        """Test successful content personalization"""
        state = {
            'generated_campaigns': [
                {
                    'campaign_title': 'Test Campaign',
                    'subject_line': 'Hello {{ customer_name }}',
                    'content': 'Service for {{ vehicle_make }} {{ vehicle_model }}',
                    'campaign_type': 'test'
                }
            ],
            'targeted_customers': [
                {
                    'customer_id': 1,
                    'name': 'John Doe',
                    'email': 'john@example.com',
                    'vehicles': [
                        {
                            'make': 'Toyota',
                            'model': 'Camry',
                            'year': 2020,
                            'registration_date': date(2020, 1, 1),
                            'last_service_date': date(2024, 6, 15)
                        }
                    ]
                }
            ]
        }
        
        result = self.agent.process(state)
        
        self.assertIn('personalized_campaigns', result)
        self.assertGreater(len(result['personalized_campaigns']), 0)
    
    def test_get_primary_vehicle(self):
        """Test primary vehicle selection logic"""
        customer = {
            'vehicles': [
                {'year': 2018, 'last_service_date': '2024-01-01'},
                {'year': 2022, 'last_service_date': '2024-06-01'},  # Should be primary
                {'year': 2020, 'last_service_date': '2024-03-01'}
            ]
        }
        
        primary = self.agent._get_primary_vehicle(customer)
        self.assertEqual(primary['year'], 2022)
    
    def test_build_personalization_context(self):
        """Test personalization context building"""
        customer = {
            'customer_id': 1,
            'name': 'John Doe',
            'email': 'john@example.com',
            'vehicles': [
                {
                    'make': 'Toyota',
                    'model': 'Camry',
                    'year': 2020,
                    'registration_date': date(2020, 1, 1),
                    'last_service_date': date(2024, 6, 15)
                }
            ]
        }
        
        context = self.agent._build_personalization_context(customer)
        
        self.assertEqual(context['customer_name'], 'John Doe')
        self.assertEqual(context['vehicle_make'], 'Toyota')
        self.assertEqual(context['vehicle_model'], 'Camry')
        self.assertIn('vehicle_age', context)


if __name__ == '__main__':
    unittest.main()