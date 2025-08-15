"""
Logging configuration for the Smart After-Sales Campaign system.
"""

import os
import re
import logging
import logging.config
from datetime import datetime
from config.settings import settings

class EmojiStrippingFormatter(logging.Formatter):
    """Custom formatter that removes emojis for console output"""
    
    def format(self, record):
        # Remove emojis using regex
        emoji_pattern = re.compile("["
                                 u"\U0001f600-\U0001f64f"  # emoticons
                                 u"\U0001f300-\U0001f5ff"  # symbols & pictographs
                                 u"\U0001f680-\U0001f6ff"  # transport & map
                                 u"\U0001f1e0-\U0001f1ff"  # flags (iOS)
                                 u"\U00002702-\U000027b0"
                                 u"\U000024c2-\U0001f251"
                                 u"\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
                                 "]+", flags=re.UNICODE)
        
        # Format the message normally first
        formatted = super().format(record)
        # Then remove emojis
        return emoji_pattern.sub('', formatted)

def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Current date for log file naming
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'console': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'console',
                'stream': 'ext://sys.stdout'
            },
            'file_all': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.DEBUG,
                'formatter': 'detailed',
                'filename': f'{logs_dir}/campaign_system_{current_date}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'file_errors': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.ERROR,
                'formatter': 'detailed',
                'filename': f'{logs_dir}/errors_{current_date}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'file_campaigns': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.INFO,
                'formatter': 'json',
                'filename': f'{logs_dir}/campaigns_{current_date}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'encoding': 'utf8'
            },
            'file_performance': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.INFO,
                'formatter': 'json',
                'filename': f'{logs_dir}/performance_{current_date}.log',
                'maxBytes': 5242880,  # 5MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {  # Root logger
                'level': log_level,
                'handlers': ['console', 'file_all', 'file_errors'],
                'propagate': False
            },
            'agents': {
                'level': logging.INFO,
                'handlers': ['console', 'file_all', 'file_campaigns'],
                'propagate': False
            },
            'workflows': {
                'level': logging.INFO,
                'handlers': ['console', 'file_all', 'file_campaigns'],
                'propagate': False
            },
            'services': {
                'level': logging.INFO,
                'handlers': ['console', 'file_all'],
                'propagate': False
            },
            'performance': {
                'level': logging.INFO,
                'handlers': ['file_performance'],
                'propagate': False
            },
            'campaign_metrics': {
                'level': logging.INFO,
                'handlers': ['file_campaigns'],
                'propagate': False
            },
            # Third-party loggers
            'requests': {
                'level': logging.WARNING,
                'handlers': ['file_all'],
                'propagate': False
            },
            'urllib3': {
                'level': logging.WARNING,
                'handlers': ['file_all'],
                'propagate': False
            },
            'openai': {
                'level': logging.WARNING,
                'handlers': ['console', 'file_all'],
                'propagate': False
            },
            'langchain': {
                'level': logging.WARNING,
                'handlers': ['file_all'],
                'propagate': False
            },
            'langgraph': {
                'level': logging.INFO,
                'handlers': ['console', 'file_all', 'file_campaigns'],
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    
    # Apply emoji stripping formatter to ALL console handlers system-wide
    emoji_formatter = EmojiStrippingFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Apply to all loggers and their handlers - this fixes the issue completely
    def apply_emoji_formatter_to_all_handlers():
        # Get all existing loggers
        for name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(name)
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.StreamHandler) and hasattr(handler.stream, 'name'):
                    if handler.stream.name in ['<stdout>', '<stderr>']:
                        handler.setFormatter(emoji_formatter)
        
        # Also apply to root logger handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and hasattr(handler.stream, 'name'):
                if handler.stream.name in ['<stdout>', '<stderr>']:
                    handler.setFormatter(emoji_formatter)
    
    apply_emoji_formatter_to_all_handlers()
    
    # Set encoding for console output to handle Unicode gracefully  
    try:
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass  # Ignore encoding issues on some systems
    
    # Set up custom logger for application startup
    logger = logging.getLogger('system.startup')
    logger.info("Logging configuration initialized")
    logger.info(f"Log level set to: {settings.log_level}")
    logger.info(f"Logs directory: {os.path.abspath(logs_dir)}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

def log_campaign_metrics(workflow_id: str, metrics: dict):
    """Log campaign metrics to dedicated campaign log"""
    logger = logging.getLogger('campaign_metrics')
    logger.info(f"Campaign metrics for workflow {workflow_id}: {metrics}")

def log_performance_metric(operation: str, execution_time: float, additional_info: dict = None):
    """Log performance metrics"""
    logger = logging.getLogger('performance')
    info = additional_info or {}
    info.update({
        'operation': operation,
        'execution_time_seconds': execution_time
    })
    logger.info(f"Performance metric: {info}")

def log_agent_activity(agent_name: str, action: str, details: dict = None):
    """Log agent activity"""
    logger = logging.getLogger(f'agents.{agent_name}')
    details_str = f" - {details}" if details else ""
    logger.info(f"{agent_name} - {action}{details_str}")

def log_workflow_step(workflow_id: str, step: str, status: str, details: dict = None):
    """Log workflow step execution"""
    logger = logging.getLogger('workflows')
    details_str = f" - {details}" if details else ""
    logger.info(f"Workflow {workflow_id} - Step: {step} - Status: {status}{details_str}")

class CampaignLogFilter(logging.Filter):
    """Custom filter for campaign-related logs"""
    
    def filter(self, record):
        # Only allow records that contain campaign-related keywords
        campaign_keywords = ['campaign', 'workflow', 'agent', 'customer', 'email']
        message = record.getMessage().lower()
        return any(keyword in message for keyword in campaign_keywords)

class PerformanceLogFilter(logging.Filter):
    """Custom filter for performance-related logs"""
    
    def filter(self, record):
        # Only allow records that contain performance-related keywords
        performance_keywords = ['performance', 'execution_time', 'duration', 'latency']
        message = record.getMessage().lower()
        return any(keyword in message for keyword in performance_keywords)

# Custom exception handler
def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions by logging them"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow KeyboardInterrupt to be handled normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger('system.exceptions')
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Set the exception handler
import sys
sys.excepthook = handle_exception