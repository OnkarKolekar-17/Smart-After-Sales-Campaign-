from typing import Dict, Any
from langgraph.graph import StateGraph, END
from workflows.states import CampaignState, WorkflowResult
from agents.weather_agent import WeatherAgent
from agents.holiday_agent import HolidayAgent
from agents.targeting_agent import TargetingAgent
from agents.group_campaign_generator import GroupBasedCampaignGenerator
from agents.group_email_sender import GroupBasedEmailSender
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EfficientCampaignWorkflow:
    """Token-efficient workflow using group-based campaigns"""
    
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.holiday_agent = HolidayAgent()
        self.targeting_agent = TargetingAgent()
        self.group_campaign_generator = GroupBasedCampaignGenerator()
        self.group_email_sender = GroupBasedEmailSender()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the efficient LangGraph workflow"""
        
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("customer_targeting", self._targeting_node)
        workflow.add_node("weather_analysis", self._weather_node)
        workflow.add_node("holiday_analysis", self._holiday_node)
        workflow.add_node("group_campaign_generation", self._group_campaign_node)
        workflow.add_node("group_email_sending", self._group_email_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Set entry point
        workflow.set_entry_point("customer_targeting")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "customer_targeting",
            self._route_after_targeting,
            {
                "weather": "weather_analysis",
                "holiday": "holiday_analysis", 
                "lifecycle": "group_campaign_generation",  # Skip context agents for lifecycle
                "scheduled": "group_campaign_generation"
            }
        )
        
        # Weather and holiday paths
        workflow.add_edge("weather_analysis", "group_campaign_generation")
        workflow.add_edge("holiday_analysis", "group_campaign_generation")
        
        # Final path
        workflow.add_edge("group_campaign_generation", "group_email_sending")
        workflow.add_edge("group_email_sending", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def run_campaign(self, location: str = "Mumbai", campaign_trigger: str = "scheduled") -> WorkflowResult:
        """Execute efficient group-based campaign workflow"""
        
        workflow_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Initialize state
        initial_state = {
            "workflow_id": workflow_id,
            "location": location,
            "campaign_trigger": campaign_trigger,
            "current_step": "start",
            "completed_steps": [],
            "errors": [],
            "weather_data": None,
            "holiday_data": None,
            "targeted_customers": [],
            "grouped_campaigns": [],
            "campaign_summary": []
        }
        
        logger.info(f"🚀 Starting EFFICIENT campaign workflow {workflow_id} for {location}")
        logger.info(f"📊 Trigger: {campaign_trigger} | Token-saving: GROUP-BASED campaigns")
        
        try:
            # Execute workflow
            result = self.workflow.invoke(initial_state)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create result summary
            campaign_summary = result.get('campaign_summary', [])
            total_groups = len(campaign_summary)
            total_customers = sum(group['customers_targeted'] for group in campaign_summary)
            total_sent = sum(group['emails_sent'] for group in campaign_summary)
            
            logger.info(f"✅ EFFICIENT workflow completed in {execution_time:.2f}s")
            logger.info(f"📈 Results: {total_groups} campaign groups, {total_customers} customers, {total_sent} emails sent")
            logger.info(f"💰 Token Savings: Generated {total_groups} campaigns instead of {total_customers} individual campaigns!")
            
            return WorkflowResult(
                success=True,
                workflow_id=workflow_id,
                execution_time=execution_time,
                customers_targeted=total_customers,
                campaigns_created=total_groups,  # Group count, not individual campaigns
                campaigns_sent=total_sent,
                error_message=None,
                campaign_details=campaign_summary
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            
            logger.error(f"❌ Efficient workflow failed after {execution_time:.2f}s: {error_msg}")
            
            return WorkflowResult(
                success=False,
                workflow_id=workflow_id,
                execution_time=execution_time,
                customers_targeted=0,
                campaigns_created=0,
                campaigns_sent=0,
                error_message=error_msg,
                campaign_details=[]
            )
    
    def _targeting_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Customer targeting node"""
        logger.info("🎯 Executing customer targeting...")
        state['current_step'] = 'targeting'
        result = self.targeting_agent.process(state)
        state['completed_steps'].append('targeting')
        return result
    
    def _weather_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Weather analysis node"""
        logger.info("🌤️ Executing weather analysis...")
        state['current_step'] = 'weather'
        result = self.weather_agent.process(state)
        state['completed_steps'].append('weather')
        return result
    
    def _holiday_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Holiday analysis node"""
        logger.info("🎉 Executing holiday analysis...")
        state['current_step'] = 'holiday'
        result = self.holiday_agent.process(state)
        state['completed_steps'].append('holiday')
        return result
    
    def _group_campaign_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Group-based campaign generation node"""
        logger.info("📝 Executing GROUP campaign generation (Token-Efficient)...")
        state['current_step'] = 'group_campaigns'
        result = self.group_campaign_generator.process(state)
        state['completed_steps'].append('group_campaigns')
        
        groups_created = len(result.get('grouped_campaigns', []))
        total_customers = sum(len(group['customers']) for group in result.get('grouped_campaigns', []))
        logger.info(f"💰 TOKEN SAVINGS: {groups_created} group campaigns instead of {total_customers} individual ones!")
        
        return result
    
    def _group_email_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Group-based email sending node"""
        logger.info("📧 Executing GROUP email sending...")
        state['current_step'] = 'group_emails'
        result = self.group_email_sender.process(state)
        state['completed_steps'].append('group_emails')
        return result
    
    def _finalize_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize workflow"""
        logger.info("🏁 Finalizing efficient campaign workflow...")
        state['current_step'] = 'complete'
        state['completed_steps'].append('finalize')
        return state
    
    def _route_after_targeting(self, state: Dict[str, Any]) -> str:
        """Route based on campaign trigger"""
        trigger = state.get('campaign_trigger', 'scheduled')
        logger.info(f"🔀 Routing to: {trigger}")
        return trigger
