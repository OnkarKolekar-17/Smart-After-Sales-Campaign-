from typing import Dict, Any
from langgraph.graph import StateGraph, END
from workflows.states import CampaignState, WorkflowResult
from agents.weather_agent import WeatherAgent
from agents.holiday_agent import HolidayAgent
from agents.targeting_agent import TargetingAgent
from agents.vehicle_lifecycle_agent import VehicleLifecycleAgent
from agents.campaign_generator_agent import CampaignGeneratorAgent
from agents.email_sender_agent import EmailSenderAgent
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CampaignWorkflow:
    """LangGraph workflow for orchestrating the multi-agent campaign system"""
    
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.holiday_agent = HolidayAgent()
        self.targeting_agent = TargetingAgent()
        self.vehicle_lifecycle_agent = VehicleLifecycleAgent()
        self.campaign_generator_agent = CampaignGeneratorAgent()
        self.email_sender_agent = EmailSenderAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create workflow graph with dict state instead of CampaignState
        workflow = StateGraph(dict)
        
        # Add nodes (agents)
        workflow.add_node("weather_analysis", self._weather_node)
        workflow.add_node("holiday_analysis", self._holiday_node)
        workflow.add_node("customer_targeting", self._targeting_node)
        workflow.add_node("vehicle_lifecycle_analysis", self._vehicle_lifecycle_node)
        workflow.add_node("campaign_generation", self._campaign_generation_node)
        workflow.add_node("email_sending", self._email_sending_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Set entry point based on trigger (will be handled in run_campaign)
        workflow.set_entry_point("customer_targeting")
        
        # Add conditional edges based on campaign trigger
        workflow.add_edge("customer_targeting", "weather_analysis")
        workflow.add_edge("weather_analysis", "holiday_analysis") 
        workflow.add_edge("holiday_analysis", "vehicle_lifecycle_analysis")
        workflow.add_edge("vehicle_lifecycle_analysis", "campaign_generation")
        workflow.add_edge("campaign_generation", "email_sending")
        workflow.add_edge("email_sending", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def run_campaign(self, location: str = "Mumbai", campaign_trigger: str = "scheduled") -> WorkflowResult:
        """Execute the complete campaign workflow"""
        
        # Initialize workflow state
        workflow_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Initialize workflow state as dictionary
        initial_state = {
            "workflow_id": workflow_id,
            "location": location,
            "campaign_trigger": campaign_trigger,
            "current_step": "start",
            "completed_steps": [],
            "errors": [],
            "weather_data": None,
            "holiday_data": None,
            "customer_segments": [],
            "targeting_criteria": None,
            "campaign_content": None
        }
        
        logger.info(f"Starting campaign workflow {workflow_id} for {location}")
        
        try:
            # Execute workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = WorkflowResult(
                workflow_id=workflow_id,
                status="success" if not final_state.get('errors') else "partial_success",
                campaigns_created=len(final_state.get('campaigns_created', [])),
                campaigns_sent=len(final_state.get('campaigns_sent', [])),
                total_targeted=final_state.get('total_targeted', 0),
                errors=final_state.get('errors', []),
                execution_time=execution_time,
                summary=self._generate_summary(final_state)
            )
            
            logger.info(f"Campaign workflow {workflow_id} completed: {result.status}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Campaign workflow {workflow_id} failed: {e}")
            
            return WorkflowResult(
                workflow_id=workflow_id,
                status="failed",
                campaigns_created=0,
                campaigns_sent=0,
                total_targeted=0,
                errors=[str(e)],
                execution_time=execution_time,
                summary=f"Workflow failed: {str(e)}"
            )
    
    def _weather_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Weather analysis node - skip for lifecycle campaigns"""
        state['current_step'] = 'weather_analysis'
        if 'completed_steps' not in state:
            state['completed_steps'] = []
        state['completed_steps'].append('weather_analysis')
        
        # Skip weather analysis for lifecycle-only campaigns
        if state.get('campaign_trigger') == 'lifecycle':
            logger.info("Skipping weather analysis for lifecycle campaign")
            state['weather_data'] = None
            return state
        
        return self.weather_agent.process(state)
    
    def _holiday_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Holiday analysis node - skip for lifecycle campaigns"""
        state['current_step'] = 'holiday_analysis'
        if 'completed_steps' not in state:
            state['completed_steps'] = []
        state['completed_steps'].append('holiday_analysis')
        
        # Skip holiday analysis for lifecycle-only campaigns  
        if state.get('campaign_trigger') == 'lifecycle':
            logger.info("Skipping holiday analysis for lifecycle campaign")
            state['holiday_data'] = None
            return state
        
        return self.holiday_agent.process(state)
    
    def _targeting_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Customer targeting node"""
        state['current_step'] = 'customer_targeting'
        if 'completed_steps' not in state:
            state['completed_steps'] = []
        state['completed_steps'].append('customer_targeting')
        
        return self.targeting_agent.process(state)
    
    def _vehicle_lifecycle_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Vehicle lifecycle analysis node"""
        state['current_step'] = 'vehicle_lifecycle_analysis'
        if 'completed_steps' not in state:
            state['completed_steps'] = []
        state['completed_steps'].append('vehicle_lifecycle_analysis')
        
        return self.vehicle_lifecycle_agent.process(state)
    
    def _campaign_generation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Campaign generation node"""
        state['current_step'] = 'campaign_generation'
        if 'completed_steps' not in state:
            state['completed_steps'] = []
        state['completed_steps'].append('campaign_generation')
        
        return self.campaign_generator_agent.process(state)
    
    def _email_sending_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Email sending node"""
        state['current_step'] = 'email_sending'
        if 'completed_steps' not in state:
            state['completed_steps'] = []
        state['completed_steps'].append('email_sending')
        
        return self.email_sender_agent.process(state)
    
    def _finalize_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalization node"""
        state['current_step'] = 'completed'
        if 'completed_steps' not in state:
            state['completed_steps'] = []
        state['completed_steps'].append('finalize')
        
        # Log final statistics
        logger.info(f"Workflow {state.get('workflow_id')} finalized:")
        logger.info(f"- Total targeted: {state.get('total_targeted', 0)}")
        logger.info(f"- Campaigns created: {len(state.get('campaigns_created', []))}")
        logger.info(f"- Campaigns sent: {len(state.get('campaigns_sent', []))}")
        logger.info(f"- Errors: {len(state.get('errors', []))}")
        
        return state
    
    def _generate_summary(self, final_state: Dict[str, Any]) -> str:
        """Generate a summary of the workflow execution"""
        
        total_targeted = final_state.get('total_targeted', 0)
        campaigns_created = len(final_state.get('campaigns_created', []))
        campaigns_sent = len(final_state.get('campaigns_sent', []))
        errors = len(final_state.get('errors', []))
        
        weather_data = final_state.get('weather_data')
        holiday_data = final_state.get('holiday_data')
        campaign_content = final_state.get('campaign_content')
        
        summary_parts = []
        
        # Basic metrics
        summary_parts.append(f"Campaign executed for {final_state.get('location', 'Unknown location')}")
        summary_parts.append(f"Targeted {total_targeted} customers")
        summary_parts.append(f"Created {campaigns_created} campaigns")
        summary_parts.append(f"Sent {campaigns_sent} emails")
        
        # Context information
        if weather_data:
            summary_parts.append(f"Weather context: {weather_data.get('condition', 'N/A')} at {weather_data.get('temperature', 'N/A')}°C")
        
        if holiday_data:
            summary_parts.append(f"Holiday context: {holiday_data.get('name', 'N/A')} on {holiday_data.get('date', 'N/A')}")
        
        if campaign_content:
            summary_parts.append(f"Campaign type: {campaign_content.get('campaign_type', 'N/A')}")
            summary_parts.append(f"Campaign title: {campaign_content.get('title', 'N/A')}")
        
        # Error information
        if errors > 0:
            summary_parts.append(f"Encountered {errors} errors during execution")
        
        return " | ".join(summary_parts)
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a running workflow (placeholder for future implementation)"""
        # This could be implemented with a workflow tracking system
        return {
            "workflow_id": workflow_id,
            "status": "unknown",
            "message": "Workflow tracking not implemented"
        }