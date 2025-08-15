import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import uuid

# Import workflow components to test
from workflows.campaign_workflow import CampaignWorkflow
from workflows.states import CampaignState, WorkflowResult
from workflows.api_models import CampaignRequest, CampaignResponse


class TestCampaignWorkflow(unittest.TestCase):
    """Test cases for CampaignWorkflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('workflows.campaign_workflow.WeatherAgent'), \
             patch('workflows.campaign_workflow.HolidayAgent'), \
             patch('workflows.campaign_workflow.TargetingAgent'), \
             patch('workflows.campaign_workflow.CampaignGeneratorAgent'), \
             patch('workflows.campaign_workflow.EmailSenderAgent'):
            self.workflow = CampaignWorkflow()
    
    def test_workflow_initialization(self):
        """Test workflow initialization"""
        self.assertIsNotNone(self.workflow.weather_agent)
        self.assertIsNotNone(self.workflow.holiday_agent)
        self.assertIsNotNone(self.workflow.targeting_agent)
        self.assertIsNotNone(self.workflow.campaign_generator_agent)
        self.assertIsNotNone(self.workflow.email_sender_agent)
        self.assertIsNotNone(self.workflow.workflow)
    
    @patch('workflows.campaign_workflow.uuid.uuid4')
    def test_run_campaign_success(self, mock_uuid):
        """Test successful campaign workflow execution"""
        # Mock UUID generation
        mock_uuid.return_value = uuid.UUID('12345678-1234-5678-9abc-123456789abc')
        
        # Mock the workflow execution
        mock_final_state = {
            'campaigns_created': ['campaign1', 'campaign2'],
            'campaigns_sent': ['campaign1'],
            'total_targeted': 10,
            'errors': []
        }
        
        with patch.object(self.workflow.workflow, 'invoke', return_value=mock_final_state):
            result = self.workflow.run_campaign('Mumbai', 'scheduled')
        
        self.assertIsInstance(result, WorkflowResult)
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.campaigns_created, 2)
        self.assertEqual(result.campaigns_sent, 1)
        self.assertEqual(result.total_targeted, 10)
    
    @patch('workflows.campaign_workflow.uuid.uuid4')
    def test_run_campaign_with_errors(self, mock_uuid):
        """Test campaign workflow with partial errors"""
        mock_uuid.return_value = uuid.UUID('12345678-1234-5678-9abc-123456789abc')
        
        # Mock the workflow execution with errors
        mock_final_state = {
            'campaigns_created': ['campaign1'],
            'campaigns_sent': [],
            'total_targeted': 5,
            'errors': ['Email service unavailable']
        }
        
        with patch.object(self.workflow.workflow, 'invoke', return_value=mock_final_state):
            result = self.workflow.run_campaign('Mumbai', 'weather_alert')
        
        self.assertEqual(result.status, 'partial_success')
        self.assertEqual(len(result.errors), 1)
    
    @patch('workflows.campaign_workflow.uuid.uuid4')
    def test_run_campaign_failure(self, mock_uuid):
        """Test campaign workflow complete failure"""
        mock_uuid.return_value = uuid.UUID('12345678-1234-5678-9abc-123456789abc')
        
        # Mock the workflow execution failure
        with patch.object(self.workflow.workflow, 'invoke', side_effect=Exception("Workflow failed")):
            result = self.workflow.run_campaign('Mumbai', 'scheduled')
        
        self.assertEqual(result.status, 'failed')
        self.assertEqual(result.campaigns_created, 0)
        self.assertEqual(result.campaigns_sent, 0)
    
    def test_weather_node(self):
        """Test weather analysis node"""
        state = {
            'location': 'Mumbai',
            'workflow_id': 'test_123'
        }
        
        # Mock weather agent response
        mock_weather_data = {
            'temperature': 28,
            'condition': 'Sunny',
            'recommendation': 'Good weather for travel'
        }
        
        with patch.object(self.workflow.weather_agent, 'process', 
                         return_value={**state, 'weather_data': mock_weather_data}):
            result = self.workflow._weather_node(state)
        
        self.assertIn('weather_data', result)
        self.assertEqual(result['weather_data']['temperature'], 28)
    
    def test_holiday_node(self):
        """Test holiday analysis node"""
        state = {
            'location': 'Mumbai',
            'workflow_id': 'test_123',
            'weather_data': {'condition': 'Sunny'}
        }
        
        # Mock holiday agent response
        mock_holiday_data = {
            'current_holidays': [
                {'name': 'Diwali', 'date': '2024-11-01', 'type': 'religious'}
            ]
        }
        
        with patch.object(self.workflow.holiday_agent, 'process',
                         return_value={**state, 'holiday_data': mock_holiday_data}):
            result = self.workflow._holiday_node(state)
        
        self.assertIn('holiday_data', result)
        self.assertEqual(len(result['holiday_data']['current_holidays']), 1)
    
    def test_targeting_node(self):
        """Test customer targeting node"""
        state = {
            'location': 'Mumbai',
            'workflow_id': 'test_123',
            'weather_data': {'condition': 'Sunny'},
            'holiday_data': {'current_holidays': []}
        }
        
        # Mock targeting agent response
        mock_customers = [
            {
                'customer_id': 1,
                'name': 'John Doe',
                'email': 'john@example.com',
                'vehicles': [{'make': 'Toyota', 'model': 'Camry'}]
            }
        ]
        
        with patch.object(self.workflow.targeting_agent, 'process',
                         return_value={**state, 'targeted_customers': mock_customers}):
            result = self.workflow._targeting_node(state)
        
        self.assertIn('targeted_customers', result)
        self.assertEqual(len(result['targeted_customers']), 1)
    
    def test_campaign_generation_node(self):
        """Test campaign generation node"""
        state = {
            'location': 'Mumbai',
            'workflow_id': 'test_123',
            'weather_data': {'condition': 'Sunny'},
            'holiday_data': {'current_holidays': []},
            'targeted_customers': [{'customer_id': 1, 'name': 'John'}]
        }
        
        # Mock campaign generator response
        mock_campaigns = [
            {
                'campaign_title': 'Summer Service Special',
                'subject_line': 'Beat the Heat - AC Service',
                'content': 'Keep your AC running smoothly...',
                'campaign_type': 'seasonal',
                'cta_text': 'Book Service Now'
            }
        ]
        
        with patch.object(self.workflow.campaign_generator_agent, 'process',
                         return_value={**state, 'generated_campaigns': mock_campaigns}):
            result = self.workflow._campaign_generation_node(state)
        
        self.assertIn('generated_campaigns', result)
        self.assertEqual(len(result['generated_campaigns']), 1)
    
    def test_email_sending_node(self):
        """Test email sending node"""
        state = {
            'location': 'Mumbai',
            'workflow_id': 'test_123',
            'personalized_campaigns': [
                {
                    'customer_id': 1,
                    'customer_email': 'john@example.com',
                    'subject_line': 'Test Subject',
                    'content': 'Test Content'
                }
            ]
        }
        
        # Mock email sender response
        mock_email_results = [
            {
                'customer_id': 1,
                'status': 'sent',
                'message_id': 'msg_123'
            }
        ]
        
        with patch.object(self.workflow.email_sender_agent, 'process',
                         return_value={**state, 'email_results': mock_email_results}):
            result = self.workflow._email_sending_node(state)
        
        self.assertIn('email_results', result)
        self.assertEqual(len(result['email_results']), 1)
    
    def test_finalize_node(self):
        """Test workflow finalization node"""
        state = {
            'workflow_id': 'test_123',
            'location': 'Mumbai',
            'campaigns_created': ['campaign1', 'campaign2'],
            'campaigns_sent': ['campaign1'],
            'total_targeted': 10,
            'errors': []
        }
        
        result = self.workflow._finalize_node(state)
        
        self.assertIn('final_summary', result)
        self.assertIn('completion_timestamp', result)
        self.assertEqual(result['status'], 'completed')
    
    def test_generate_summary(self):
        """Test workflow summary generation"""
        final_state = {
            'campaigns_created': ['c1', 'c2', 'c3'],
            'campaigns_sent': ['c1', 'c2'],
            'total_targeted': 15,
            'errors': ['Minor error'],
            'location': 'Mumbai'
        }
        
        summary = self.workflow._generate_summary(final_state)
        
        self.assertIn('campaigns', summary.lower())
        self.assertIn('customers', summary.lower())
        self.assertIn('mumbai', summary.lower())


class TestCampaignState(unittest.TestCase):
    """Test cases for CampaignState"""
    
    def test_campaign_state_creation(self):
        """Test CampaignState creation"""
        state = CampaignState(
            workflow_id='test_123',
            location='Mumbai',
            campaign_trigger='scheduled',
            current_step='start'
        )
        
        self.assertEqual(state.workflow_id, 'test_123')
        self.assertEqual(state.location, 'Mumbai')
        self.assertEqual(state.campaign_trigger, 'scheduled')
        self.assertEqual(state.current_step, 'start')
    
    def test_campaign_state_defaults(self):
        """Test CampaignState with default values"""
        state = CampaignState(
            workflow_id='test_123'
        )
        
        self.assertEqual(state.workflow_id, 'test_123')
        self.assertEqual(state.location, 'Mumbai')  # Default
        self.assertEqual(state.campaign_trigger, 'scheduled')  # Default
        self.assertIsInstance(state.metadata, dict)


class TestWorkflowResult(unittest.TestCase):
    """Test cases for WorkflowResult"""
    
    def test_workflow_result_creation(self):
        """Test WorkflowResult creation"""
        result = WorkflowResult(
            workflow_id='test_123',
            status='success',
            campaigns_created=5,
            campaigns_sent=4,
            total_targeted=20,
            errors=[],
            execution_time=15.5,
            summary='Test summary'
        )
        
        self.assertEqual(result.workflow_id, 'test_123')
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.campaigns_created, 5)
        self.assertEqual(result.campaigns_sent, 4)
        self.assertEqual(result.total_targeted, 20)
        self.assertEqual(result.execution_time, 15.5)
    
    def test_workflow_result_with_errors(self):
        """Test WorkflowResult with errors"""
        errors = ['Error 1', 'Error 2']
        result = WorkflowResult(
            workflow_id='test_123',
            status='partial_success',
            campaigns_created=2,
            campaigns_sent=1,
            total_targeted=10,
            errors=errors,
            execution_time=8.2,
            summary='Partial success with errors'
        )
        
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(result.status, 'partial_success')


class TestIntegration(unittest.TestCase):
    """Integration tests for workflow components"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        with patch('workflows.campaign_workflow.WeatherAgent'), \
             patch('workflows.campaign_workflow.HolidayAgent'), \
             patch('workflows.campaign_workflow.TargetingAgent'), \
             patch('workflows.campaign_workflow.CampaignGeneratorAgent'), \
             patch('workflows.campaign_workflow.EmailSenderAgent'):
            self.workflow = CampaignWorkflow()
    
    def test_state_flow_through_nodes(self):
        """Test state flowing through all nodes"""
        initial_state = {
            'workflow_id': 'integration_test',
            'location': 'Mumbai',
            'campaign_trigger': 'scheduled',
            'current_step': 'start'
        }
        
        # Mock each agent to add its expected data
        with patch.object(self.workflow.weather_agent, 'process') as mock_weather, \
             patch.object(self.workflow.holiday_agent, 'process') as mock_holiday, \
             patch.object(self.workflow.targeting_agent, 'process') as mock_targeting, \
             patch.object(self.workflow.campaign_generator_agent, 'process') as mock_generator, \
             patch.object(self.workflow.email_sender_agent, 'process') as mock_sender:
            
            # Configure mock responses
            mock_weather.return_value = {**initial_state, 'weather_data': {'condition': 'Sunny'}}
            mock_holiday.return_value = {**initial_state, 'weather_data': {'condition': 'Sunny'}, 'holiday_data': {'current_holidays': []}}
            mock_targeting.return_value = {**initial_state, 'weather_data': {'condition': 'Sunny'}, 'holiday_data': {'current_holidays': []}, 'targeted_customers': [{'customer_id': 1}]}
            mock_generator.return_value = {**initial_state, 'weather_data': {'condition': 'Sunny'}, 'holiday_data': {'current_holidays': []}, 'targeted_customers': [{'customer_id': 1}], 'generated_campaigns': [{'campaign_title': 'Test'}]}
            mock_sender.return_value = {**initial_state, 'weather_data': {'condition': 'Sunny'}, 'holiday_data': {'current_holidays': []}, 'targeted_customers': [{'customer_id': 1}], 'generated_campaigns': [{'campaign_title': 'Test'}], 'campaigns_sent': [{'customer_id': 1}]}
            
            # Test each node in sequence
            state = self.workflow._weather_node(initial_state)
            self.assertIn('weather_data', state)
            
            state = self.workflow._holiday_node(state)
            self.assertIn('holiday_data', state)
            
            state = self.workflow._targeting_node(state)
            self.assertIn('targeted_customers', state)
            
            state = self.workflow._campaign_generation_node(state)
            self.assertIn('generated_campaigns', state)
            
            state = self.workflow._email_sending_node(state)
            self.assertIn('campaigns_sent', state)
    
    def test_error_handling_across_nodes(self):
        """Test error handling propagation across nodes"""
        initial_state = {
            'workflow_id': 'error_test',
            'location': 'Mumbai',
            'errors': []
        }
        
        # Mock weather agent to add an error
        with patch.object(self.workflow.weather_agent, 'process') as mock_weather:
            mock_weather.return_value = {
                **initial_state, 
                'weather_data': {'condition': 'Unknown'},
                'errors': ['Weather service unavailable']
            }
            
            result_state = self.workflow._weather_node(initial_state)
            
            self.assertIn('errors', result_state)
            self.assertEqual(len(result_state['errors']), 1)
            self.assertIn('Weather service unavailable', result_state['errors'])


if __name__ == '__main__':
    unittest.main()