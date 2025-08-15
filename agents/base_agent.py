from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, agent_name: str, system_prompt: str = None):
        self.agent_name = agent_name
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=settings.openai.api_key,
            model=settings.openai.model,
            temperature=settings.openai.temperature,
            max_tokens=settings.openai.max_tokens
        )
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}")
        ])
        
        self.chain = self.prompt_template | self.llm
        
        logger.info(f"Initialized {self.agent_name} agent")
    
    @abstractmethod
    def _get_default_system_prompt(self) -> str:
        """Return the default system prompt for this agent"""
        pass
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method that each agent must implement"""
        pass
    
    def _invoke_llm(self, input_text: str, **kwargs) -> str:
        """Helper method to invoke LLM with error handling"""
        try:
            response = self.chain.invoke({
                "input": input_text,
                **kwargs
            })
            return response.content
        except Exception as e:
            logger.error(f"LLM invocation error in {self.agent_name}: {e}")
            raise
    
    def _log_step(self, message: str, level: str = "info"):
        """Log agent steps with consistent formatting"""
        import re
        # Remove emojis for clean console output
        emoji_pattern = re.compile("["
                                 u"\U0001f600-\U0001f64f"  # emoticons
                                 u"\U0001f300-\U0001f5ff"  # symbols & pictographs
                                 u"\U0001f680-\U0001f6ff"  # transport & map
                                 u"\U0001f1e0-\U0001f1ff"  # flags (iOS)
                                 u"\U00002702-\U000027b0"
                                 u"\U000024c2-\U0001f251"
                                 u"\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
                                 "]+", flags=re.UNICODE)
        clean_message = emoji_pattern.sub('', message).strip()
        
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(f"[{self.agent_name}] {clean_message}")
    
    def _validate_input(self, state: Dict[str, Any], required_fields: list) -> bool:
        """Validate that required fields are present in state"""
        missing_fields = [field for field in required_fields if field not in state or state[field] is None]
        
        if missing_fields:
            error_msg = f"Missing required fields: {missing_fields}"
            self._log_step(error_msg, "error")
            return False
        
        return True
    
    def _handle_error(self, error: Exception, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors consistently across agents"""
        error_msg = f"Error in {self.agent_name}: {str(error)}"
        self._log_step(error_msg, "error")
        
        # Add error to state
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(error_msg)
        
        return state