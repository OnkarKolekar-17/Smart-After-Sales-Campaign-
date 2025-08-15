"""
Brevo API Service for email campaign management
"""

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from typing import Dict, List, Any, Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class BrevoService:
    """Service class for Brevo email operations"""
    
    def __init__(self):
        # Initialize Brevo API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.brevo.api_key
        
        self.transactional_api = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        self.contacts_api = sib_api_v3_sdk.ContactsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
    
    def send_transactional_email(self, 
                                to_email: str, 
                                to_name: str,
                                subject: str,
                                html_content: str,
                                text_content: str = None,
                                tags: List[str] = None) -> Optional[str]:
        """Send a transactional email via Brevo"""
        
        try:
            # Create email payload
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[sib_api_v3_sdk.SendSmtpEmailTo(
                    email=to_email,
                    name=to_name
                )],
                sender=sib_api_v3_sdk.SendSmtpEmailSender(
                    name=settings.brevo.sender_name,
                    email=settings.brevo.sender_email
                ),
                subject=subject,
                html_content=html_content,
                text_content=text_content or self._html_to_text(html_content),
                tags=tags or ['campaign', 'automotive']
            )
            
            # Send email
            api_response = self.transactional_api.send_transac_email(send_smtp_email)
            
            logger.info(f"Email sent to {to_email}: {api_response.message_id}")
            return api_response.message_id
            
        except ApiException as e:
            logger.error(f"Brevo API error sending email to {to_email}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return None
    
    def create_or_update_contact(self, 
                               email: str, 
                               attributes: Dict[str, Any] = None,
                               list_ids: List[int] = None) -> bool:
        """Create or update a contact in Brevo"""
        
        try:
            create_contact = sib_api_v3_sdk.CreateContact(
                email=email,
                attributes=attributes or {},
                list_ids=list_ids or []
            )
            
            try:
                # Try to create contact
                self.contacts_api.create_contact(create_contact)
                logger.info(f"Contact created: {email}")
                return True
            except ApiException as e:
                if e.status == 400 and "Contact already exist" in str(e):
                    # Contact exists, update it
                    update_contact = sib_api_v3_sdk.UpdateContact(
                        attributes=attributes or {},
                        list_ids=list_ids or []
                    )
                    self.contacts_api.update_contact(email, update_contact)
                    logger.info(f"Contact updated: {email}")
                    return True
                else:
                    raise e
                    
        except ApiException as e:
            logger.error(f"Brevo API error managing contact {email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error managing contact {email}: {e}")
            return False
    
    def get_email_events(self, message_id: str) -> List[Dict[str, Any]]:
        """Get events for a specific email message"""
        
        try:
            # Note: This is a simplified version - Brevo API has specific endpoints for events
            # You might need to use webhooks or other endpoints depending on your needs
            logger.info(f"Fetching events for message {message_id}")
            
            # This is a placeholder - implement based on your specific tracking needs
            return []
            
        except ApiException as e:
            logger.error(f"Error fetching email events for {message_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching email events: {e}")
            return []
    
    def create_email_template(self, 
                            template_name: str,
                            subject: str,
                            html_content: str,
                            sender_name: str = None,
                            sender_email: str = None) -> Optional[int]:
        """Create an email template in Brevo"""
        
        try:
            template = sib_api_v3_sdk.CreateSmtpTemplate(
                template_name=template_name,
                subject=subject,
                html_content=html_content,
                sender=sib_api_v3_sdk.CreateSmtpTemplateSender(
                    name=sender_name or settings.brevo.sender_name,
                    email=sender_email or settings.brevo.sender_email
                ),
                is_active=True
            )
            
            api_response = self.transactional_api.create_smtp_template(template)
            logger.info(f"Template created: {template_name} (ID: {api_response.id})")
            return api_response.id
            
        except ApiException as e:
            logger.error(f"Error creating template {template_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating template: {e}")
            return None
    
    def send_template_email(self, 
                           template_id: int,
                           to_email: str,
                           to_name: str,
                           params: Dict[str, Any] = None,
                           tags: List[str] = None) -> Optional[str]:
        """Send an email using a template"""
        
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[sib_api_v3_sdk.SendSmtpEmailTo(
                    email=to_email,
                    name=to_name
                )],
                template_id=template_id,
                params=params or {},
                tags=tags or ['template', 'automotive']
            )
            
            api_response = self.transactional_api.send_transac_email(send_smtp_email)
            logger.info(f"Template email sent to {to_email}: {api_response.message_id}")
            return api_response.message_id
            
        except ApiException as e:
            logger.error(f"Error sending template email to {to_email}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error sending template email: {e}")
            return None
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text (basic implementation)"""
        
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Convert HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def validate_connection(self) -> bool:
        """Validate Brevo API connection"""
        
        try:
            # Try to get account info as a connection test
            account_api = sib_api_v3_sdk.AccountApi(
                sib_api_v3_sdk.ApiClient(self.transactional_api.api_client.configuration)
            )
            account_info = account_api.get_account()
            logger.info(f"Brevo connection validated - Account: {account_info.email}")
            return True
            
        except ApiException as e:
            logger.error(f"Brevo connection validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error validating Brevo connection: {e}")
            return False