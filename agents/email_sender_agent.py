from typing import Dict, Any, List
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from agents.base_agent import BaseAgent
from config.settings import settings
from config.database import get_db_connection
from datetime import datetime
import time

class EmailSenderAgent(BaseAgent):
    """Agent responsible for sending emails via Brevo and tracking campaign performance"""
    
    def __init__(self):
        super().__init__(
            agent_name="EmailSenderAgent",
            system_prompt=self._get_default_system_prompt()
        )
        
        # Initialize Brevo API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.brevo.api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        
        # Log Brevo configuration (without exposing full API key)
        api_key_preview = settings.brevo.api_key[:8] + "..." if settings.brevo.api_key else "NONE"
        self._log_step(f"🔧 Brevo API initialized with key: {api_key_preview}")
        self._log_step(f"📧 Sender configured: {settings.brevo.sender_name} <{settings.brevo.sender_email}>")
        self._log_step(f"🎯 To track emails, visit: https://app.brevo.com/email/transactional")
    
    def _get_default_system_prompt(self) -> str:
        return """
        You are an Email Campaign Execution Agent responsible for delivering personalized email campaigns.
        
        Your role is to:
        1. Personalize email content for individual customers
        2. Send emails efficiently through Brevo API
        3. Track campaign performance and delivery status
        4. Handle errors and retries gracefully
        5. Maintain compliance with email marketing best practices
        
        Always ensure:
        - Proper personalization without errors
        - Respectful handling of customer data
        - Accurate tracking and reporting
        - Error handling and recovery
        - Rate limiting and API best practices
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process email sending for multiple targeted campaigns"""
        try:
            self._log_step("Starting comprehensive email campaign execution")
            
            # Get all generated campaigns
            generated_campaigns = state.get('generated_campaigns', [])
            campaign_content = state.get('campaign_content')  # Fallback for compatibility
            customer_segments = state.get('customer_segments', [])
            
            total_sent = 0
            total_created = 0
            all_campaign_records = []
            all_sent_campaigns = []
            
            # Process multiple campaigns if available
            if generated_campaigns:
                for campaign in generated_campaigns:
                    self._log_step(f"Processing campaign: {campaign.get('title', 'Unknown')}")
                    
                    # Get targeted customers for this specific campaign
                    target_customers = campaign.get('target_customers', customer_segments)
                    
                    if target_customers:
                        # Create campaign records for this specific campaign
                        campaign_records = self._create_campaign_records(
                            target_customers, campaign, state
                        )
                        
                        # Send emails for this campaign
                        sent_campaigns = self._send_email_batch(
                            campaign_records, campaign
                        )
                        
                        all_campaign_records.extend(campaign_records)
                        all_sent_campaigns.extend(sent_campaigns)
                        total_created += len(campaign_records)
                        total_sent += len(sent_campaigns)
                        
                        self._log_step(f"Campaign '{campaign.get('title')}': {len(campaign_records)} created, {len(sent_campaigns)} sent")
            
            # Fallback to single campaign if no multiple campaigns
            elif campaign_content and customer_segments:
                campaign_records = self._create_campaign_records(
                    customer_segments, campaign_content, state
                )
                sent_campaigns = self._send_email_batch(
                    campaign_records, campaign_content
                )
                all_campaign_records = campaign_records
                all_sent_campaigns = sent_campaigns
                total_created = len(campaign_records)
                total_sent = len(sent_campaigns)
            
            # Update state with comprehensive results
            state['campaigns_created'] = all_campaign_records
            state['campaigns_sent'] = all_sent_campaigns
            state['total_created'] = total_created
            state['total_sent'] = total_sent
            
            self._log_step(f"Email campaign execution completed: {total_created} campaigns created, {total_sent} emails sent")
            
        except Exception as e:
            return self._handle_error(e, state)
        
        return state
    
    def _create_campaign_records(self, customers, campaign_content, state) -> List[Dict[str, Any]]:
        """Create campaign records in database"""
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            campaign_records = []
            
            # Extract campaign data
            campaign_type = campaign_content.get('campaign_type', 'service') if isinstance(campaign_content, dict) else campaign_content.campaign_type
            title = campaign_content.get('title', 'Service Campaign') if isinstance(campaign_content, dict) else campaign_content.title
            content = campaign_content.get('content', '') if isinstance(campaign_content, dict) else campaign_content.content
            subject_line = campaign_content.get('subject_line', 'Service Reminder') if isinstance(campaign_content, dict) else campaign_content.subject_line
            
            for customer_data in customers:
                customer_record = None
                
                # Handle lifecycle campaign format with nested customer
                if isinstance(customer_data, dict) and 'customer' in customer_data:
                    customer = customer_data['customer']
                    customer_id = customer.get('customer_id')
                    customer_name = customer.get('name', '')
                    customer_email = customer.get('email', '')
                    vehicle_info = customer.get('vehicle', {})
                    
                    if customer_id and customer_email and vehicle_info:
                        customer_record = {
                            'customer_id': customer_id,
                            'customer_name': customer_name,
                            'customer_email': customer_email,
                            'vehicle_info': vehicle_info
                        }
                
                # Handle direct customer format (Pydantic models from weather/holiday campaigns)
                elif hasattr(customer_data, 'customer_id') or (isinstance(customer_data, dict) and customer_data.get('customer_id')):
                    # Pydantic model or direct dictionary
                    if hasattr(customer_data, 'dict'):
                        customer_dict = customer_data.dict()
                    else:
                        customer_dict = customer_data
                    
                    customer_id = customer_dict.get('customer_id')
                    customer_name = customer_dict.get('name', '')
                    customer_email = customer_dict.get('email', '')
                    vehicles = customer_dict.get('vehicles', [])
                    
                    # Create records for each vehicle, or create one record if no vehicles
                    if vehicles:
                        for vehicle in vehicles:
                            if customer_id and customer_email and vehicle:
                                customer_record = {
                                    'customer_id': customer_id,
                                    'customer_name': customer_name,
                                    'customer_email': customer_email,
                                    'vehicle_info': vehicle
                                }
                                
                                # Create campaign record for this customer-vehicle combination
                                self._create_single_campaign_record(
                                    customer_record, campaign_content, state, campaign_records, cur
                                )
                    else:
                        # Create campaign for customer even without vehicle data
                        if customer_id and customer_email:
                            customer_record = {
                                'customer_id': customer_id,
                                'customer_name': customer_name,
                                'customer_email': customer_email,
                                'vehicle_info': {}  # Empty vehicle info
                            }
                            
                            # Create campaign record for this customer
                            self._create_single_campaign_record(
                                customer_record, campaign_content, state, campaign_records, cur
                            )
                    continue  # Skip the single record creation below
                
                # Create single campaign record if we have valid customer data
                if customer_record:
                    self._create_single_campaign_record(
                        customer_record, campaign_content, state, campaign_records, cur
                    )
            
            conn.commit()
            cur.close()
            conn.close()
            
            self._log_step(f"Created {len(campaign_records)} campaign records")
            return campaign_records
            
        except Exception as e:
            self._log_step(f"Error creating campaign records: {e}", "error")
            raise e
            
    def _create_single_campaign_record(self, customer_record: Dict, campaign_content: Dict, 
                                     state: Dict, campaign_records: List, cur) -> None:
        """Create a single campaign record for a customer"""
        import uuid
        
        # Extract campaign data
        campaign_type = campaign_content.get('campaign_type', 'service') if isinstance(campaign_content, dict) else campaign_content.campaign_type
        title = campaign_content.get('title', 'Service Campaign') if isinstance(campaign_content, dict) else campaign_content.title
        content = campaign_content.get('content', '') if isinstance(campaign_content, dict) else campaign_content.content
        subject_line = campaign_content.get('subject_line', 'Service Reminder') if isinstance(campaign_content, dict) else campaign_content.subject_line
        
        unique_campaign_id = str(uuid.uuid4())
        vehicle_info = customer_record['vehicle_info']
        # Handle empty vehicle info for customers without vehicles
        vehicle_id = None
        if vehicle_info:
            vehicle_id = vehicle_info.get('id') or vehicle_info.get('vehicle_id')
        
        # Insert campaign record
        cur.execute("""
            INSERT INTO campaigns (
                campaign_id, vehicle_id, customer_id, campaign_type, 
                campaign_title, subject_line, content, status, 
                location, trigger_type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            unique_campaign_id,
            vehicle_id,
            customer_record['customer_id'],
            campaign_type,
            title,
            subject_line,
            content,
            'created',
            state.get('location', 'Mumbai'),
            state.get('campaign_trigger', 'lifecycle')
        ))
        
        db_campaign_id = cur.fetchone()['id']
        
        campaign_record = {
            'campaign_id': unique_campaign_id,
            'db_id': db_campaign_id,
            'customer_id': customer_record['customer_id'],
            'customer_name': customer_record['customer_name'],
            'customer_email': customer_record['customer_email'],
            'vehicle': vehicle_info,
            'personalized_content': self._personalize_content(
                campaign_content, customer_record, vehicle_info
            )
        }
        
        campaign_records.append(campaign_record)
    
    def _personalize_content(self, campaign_content, customer, vehicle) -> Dict[str, str]:
        """Personalize campaign content for individual customer and vehicle"""
        
        # Handle both dictionary and object formats
        subject_line = campaign_content.get('subject_line', 'Service Reminder') if isinstance(campaign_content, dict) else campaign_content.subject_line
        content = campaign_content.get('content', 'Dear Customer...') if isinstance(campaign_content, dict) else campaign_content.content
        
        personalized = {
            'subject_line': subject_line,
            'content': content
        }
        
        # Extract customer data (handle both dict and object)
        if isinstance(customer, dict):
            customer_name = customer.get('name', 'Valued Customer')
            customer_location = customer.get('preferred_location', 'your area')
        else:
            customer_name = getattr(customer, 'name', 'Valued Customer') 
            customer_location = getattr(customer, 'preferred_location', 'your area')
        
        # Define personalization mappings
        personalizations = {
            '{{customer_name}}': customer_name,
            '{{vehicle_info}}': f"{vehicle.get('year', '')} {vehicle.get('make', '')} {vehicle.get('model', '')}".strip(),
            '{{vehicle_make}}': vehicle.get('make', 'your vehicle'),
            '{{vehicle_model}}': vehicle.get('model', ''),
            '{{vehicle_year}}': str(vehicle.get('year', '')),
            '{{last_service_date}}': self._format_date(vehicle.get('last_service_date')),
            '{{next_service_due}}': self._format_date(vehicle.get('next_service_due')),
            '{{mileage}}': f"{vehicle.get('mileage', 'N/A')} km" if vehicle.get('mileage') else 'N/A',
            '{{warranty_status}}': self._get_warranty_status(vehicle),
            '{{customer_location}}': customer_location
        }
        
        # Apply personalizations
        for placeholder, value in personalizations.items():
            personalized['subject_line'] = personalized['subject_line'].replace(placeholder, str(value))
            personalized['content'] = personalized['content'].replace(placeholder, str(value))
        
        return personalized
    
    def _format_date(self, date_str) -> str:
        """Format date string for display"""
        if not date_str:
            return 'Not Available'
        
        try:
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime('%B %d, %Y')
            return str(date_str)
        except:
            return str(date_str) if date_str else 'Not Available'
    
    def _get_warranty_status(self, vehicle) -> str:
        """Determine warranty status"""
        warranty_end = vehicle.get('warranty_end')
        if not warranty_end:
            return 'Check with service center'
        
        try:
            if isinstance(warranty_end, str):
                warranty_date = datetime.fromisoformat(warranty_end.replace('Z', '+00:00'))
            else:
                warranty_date = warranty_end
            
            today = datetime.now()
            if warranty_date > today:
                days_left = (warranty_date - today).days
                if days_left <= 30:
                    return f'Expires in {days_left} days'
                else:
                    return 'Active'
            else:
                return 'Expired'
        except:
            return 'Check with service center'
    
    def _send_email_batch(self, campaign_records, campaign_content) -> List[Dict[str, Any]]:
        """Send emails in batches with rate limiting"""
        
        sent_campaigns = []
        batch_size = settings.campaigns.batch_size
        
        for i in range(0, len(campaign_records), batch_size):
            batch = campaign_records[i:i + batch_size]
            
            self._log_step(f"Sending batch {i//batch_size + 1}: {len(batch)} emails")
            
            for record in batch:
                try:
                    # Send individual email
                    success = self._send_individual_email(record, campaign_content)
                    
                    if success:
                        # Update campaign status
                        self._update_campaign_status(record['campaign_id'], 'sent')
                        sent_campaigns.append(record)
                    else:
                        self._update_campaign_status(record['campaign_id'], 'failed')
                    
                    # Rate limiting - small delay between emails
                    time.sleep(0.1)
                    
                except Exception as e:
                    self._log_step(f"Error sending email to {record.get('customer_email', 'unknown')}: {e}", "error")
                    self._update_campaign_status(record['campaign_id'], 'failed')
            
            # Longer delay between batches
            if i + batch_size < len(campaign_records):
                time.sleep(2)
        
        return sent_campaigns
    
    def _send_individual_email(self, record, campaign_content) -> bool:
        """Send individual email via Brevo API"""
        
        try:
            # Extract data from new record structure
            customer_email = record['customer_email']
            customer_name = record['customer_name']
            personalized = record['personalized_content']
            
            self._log_step(f"🔄 Attempting to send email to {customer_email} ({customer_name})")
            self._log_step(f"📧 Subject: {personalized['subject_line'][:50]}...")
            
            # Extract campaign type from campaign content
            campaign_type = campaign_content.get('campaign_type', 'campaign') if isinstance(campaign_content, dict) else campaign_content.campaign_type
            
            # Create email payload
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[sib_api_v3_sdk.SendSmtpEmailTo(
                    email=customer_email,
                    name=customer_name
                )],
                sender=sib_api_v3_sdk.SendSmtpEmailSender(
                    name=settings.brevo.sender_name,
                    email=settings.brevo.sender_email
                ),
                subject=personalized['subject_line'],
                html_content=self._convert_to_html(personalized['content']),
                text_content=personalized['content'],
                tags=[campaign_type, 'automated_campaign']
            )
            
            self._log_step(f"📤 Sending via Brevo API...")
            
            # Send email
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            
            self._log_step(f"✅ SUCCESS! Email sent to {customer_email}")
            self._log_step(f"📬 Brevo Message ID: {api_response.message_id}")
            self._log_step(f"🎯 You can track this email in Brevo dashboard using Message ID: {api_response.message_id}")
            
            return True
            
        except ApiException as e:
            self._log_step(f"❌ Brevo API error for {customer_email}: {e}", "error")
            self._log_step(f"🔍 Error details: Status {e.status}, Reason: {e.reason}", "error")
            if hasattr(e, 'body'):
                self._log_step(f"📄 Error body: {e.body}", "error")
            return False
        except Exception as e:
            self._log_step(f"❌ Email sending error for {customer_email}: {e}", "error")
            return False
    
    def _convert_to_html(self, text_content: str) -> str:
        """Convert plain text to basic HTML"""
        
        # Basic text to HTML conversion
        html_content = text_content.replace('\n\n', '</p><p>')
        html_content = html_content.replace('\n', '<br>')
        
        # Handle bullet points
        html_content = html_content.replace('• ', '<li>').replace('✓ ', '<li>')
        
        # Wrap in basic HTML structure
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Vehicle Service Reminder</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .cta-button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <p>{html_content}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _update_campaign_status(self, campaign_id: str, status: str):
        """Update campaign status in database"""
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            if status == 'sent':
                cur.execute("""
                    UPDATE campaigns 
                    SET status = %s, sent_at = CURRENT_TIMESTAMP 
                    WHERE campaign_id = %s
                """, (status, campaign_id))
            else:
                cur.execute("""
                    UPDATE campaigns 
                    SET status = %s 
                    WHERE campaign_id = %s
                """, (status, campaign_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            self._log_step(f"Error updating campaign status: {e}", "error")