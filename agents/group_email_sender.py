from typing import Dict, Any, List
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from agents.base_agent import BaseAgent
from config.settings import settings
from config.database import get_db_connection
from datetime import datetime
import time

class GroupBasedEmailSender(BaseAgent):
    """Efficient email sender that works with grouped campaigns"""
    
    def __init__(self):
        super().__init__(
            agent_name="GroupBasedEmailSender",
            system_prompt="Group-based email sender for efficient campaign delivery"
        )
        
        # Initialize Brevo API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.brevo.api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Send grouped campaigns efficiently"""
        try:
            self._log_step("Starting group-based email campaign execution")
            
            grouped_campaigns = state.get('grouped_campaigns', [])
            if not grouped_campaigns:
                self._log_step("No grouped campaigns found")
                return state
            
            total_sent = 0
            total_created = 0
            campaign_summary = []
            
            # Process each group
            for group in grouped_campaigns:
                group_type = group['group_type']
                customers = group['customers']
                template = group['campaign_template']
                
                self._log_step(f"Processing group: {group_type} ({len(customers)} customers)")
                
                # Create one campaign record per group (not per customer!)
                group_campaign_id = self._create_group_campaign_record(group, state)
                
                # Send personalized emails to all customers in the group
                sent_count = self._send_group_emails(customers, template, group_campaign_id)
                
                campaign_summary.append({
                    'group_type': group_type,
                    'customers_targeted': len(customers),
                    'emails_sent': sent_count,
                    'campaign_id': group_campaign_id
                })
                
                total_created += 1  # One campaign per group
                total_sent += sent_count
                
                self._log_step(f"Group {group_type}: 1 campaign created, {sent_count}/{len(customers)} emails sent")
            
            # Update state with results
            state['campaign_summary'] = campaign_summary
            state['emails_sent'] = total_sent
            state['campaigns_created'] = total_created
            state['customers_targeted'] = sum(len(group['customers']) for group in grouped_campaigns)
            
            self._log_step(f"✅ Group campaign execution completed: {total_created} campaigns, {total_sent} emails sent")
            
        except Exception as e:
            return self._handle_error(e, state)
        
        return state
    
    def _create_group_campaign_record(self, group: Dict, state: Dict) -> int:
        """Create ONE campaign record for the entire group"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Insert single campaign record for the group
            cur.execute("""
                INSERT INTO campaigns (
                    workflow_id, trigger_type, campaign_type, title, subject_line, 
                    content, target_location, target_count, status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                state.get('workflow_id'),
                state.get('campaign_trigger', 'group'),
                group['group_type'],
                group['campaign_template']['title'],
                group['campaign_template']['subject_line'],
                group['campaign_template']['content_template'],
                group.get('location', 'Multiple'),
                group['customer_count'],
                'created',
                datetime.now()
            ))
            
            campaign_id = cur.fetchone()[0]
            
            # Create campaign metrics record
            cur.execute("""
                INSERT INTO campaign_metrics (
                    campaign_id, customers_targeted, emails_sent, 
                    open_rate, click_rate, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                campaign_id, group['customer_count'], 0, 0.0, 0.0, datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            return campaign_id
            
        except Exception as e:
            self._log_step(f"Error creating group campaign record: {e}", "error")
            if conn:
                conn.close()
            return None
    
    def _send_group_emails(self, customers: List[Dict], template: Dict, campaign_id: int) -> int:
        """Send personalized emails to all customers in the group using the same template"""
        sent_count = 0
        
        for customer in customers:
            try:
                # Personalize the template for this customer
                personalized_content = self._personalize_template(template, customer)
                
                # Send email via Brevo
                success = self._send_single_email(customer, personalized_content)
                
                if success:
                    sent_count += 1
                    # Update individual customer record
                    self._update_customer_campaign_record(customer['id'], campaign_id)
                
                # Small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                self._log_step(f"Error sending email to {customer.get('name', 'Unknown')}: {e}", "error")
                continue
        
        # Update campaign metrics
        self._update_campaign_metrics(campaign_id, sent_count)
        
        return sent_count
    
    def _personalize_template(self, template: Dict, customer: Dict) -> Dict:
        """Personalize template content for individual customer"""
        
        # Get personalization data
        vehicle = customer.get('vehicle', {})
        
        # Prepare personalization mapping
        personalization = {
            'customer_name': customer.get('name', 'Valued Customer'),
            'vehicle_make': vehicle.get('make', 'Your Vehicle'),
            'vehicle_model': vehicle.get('model', ''),
            'warranty_end_date': vehicle.get('warranty_end_date', 'Soon'),
            'last_service_date': vehicle.get('last_service_date', 'Long ago'),
            'service_interval': '6'  # Default service interval
        }
        
        # Apply personalization to content
        personalized_subject = template['subject_line'].format(**personalization)
        personalized_content = template['content_template'].format(**personalization)
        
        return {
            'title': template['title'],
            'subject_line': personalized_subject,
            'content': personalized_content,
            'cta_text': template['cta_text']
        }
    
    def _send_single_email(self, customer: Dict, content: Dict) -> bool:
        """Send single personalized email via Brevo"""
        try:
            email_data = sib_api_v3_sdk.SendSmtpEmail(
                to=[sib_api_v3_sdk.SendSmtpEmailTo(
                    email=customer.get('email'),
                    name=customer.get('name')
                )],
                sender=sib_api_v3_sdk.SendSmtpEmailSender(
                    name=settings.brevo.sender_name,
                    email=settings.brevo.sender_email
                ),
                subject=content['subject_line'],
                html_content=self._format_html_content(content),
                text_content=content['content']
            )
            
            response = self.api_instance.send_transac_email(email_data)
            return True
            
        except ApiException as e:
            self._log_step(f"Brevo API error for {customer.get('email')}: {e}", "error")
            return False
        except Exception as e:
            self._log_step(f"Email error for {customer.get('email')}: {e}", "error")
            return False
    
    def _format_html_content(self, content: Dict) -> str:
        """Convert text content to HTML format"""
        html_content = content['content'].replace('\n', '<br>')
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                {html_content}
                <div style="margin-top: 30px; text-align: center;">
                    <a href="#" style="background-color: #007bff; color: white; padding: 12px 24px; 
                       text-decoration: none; border-radius: 5px; display: inline-block;">
                        {content['cta_text']}
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _update_customer_campaign_record(self, customer_id: int, campaign_id: int):
        """Link customer to the group campaign"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Create customer-campaign relationship
            cur.execute("""
                INSERT INTO customer_campaigns (customer_id, campaign_id, sent_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (customer_id, campaign_id) DO NOTHING
            """, (customer_id, campaign_id, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self._log_step(f"Error updating customer campaign record: {e}", "error")
            if conn:
                conn.close()
    
    def _update_campaign_metrics(self, campaign_id: int, sent_count: int):
        """Update campaign metrics with actual send count"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE campaign_metrics 
                SET emails_sent = %s, updated_at = %s
                WHERE campaign_id = %s
            """, (sent_count, datetime.now(), campaign_id))
            
            # Update campaign status
            cur.execute("""
                UPDATE campaigns 
                SET status = 'sent', sent_at = %s
                WHERE id = %s
            """, (datetime.now(), campaign_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self._log_step(f"Error updating campaign metrics: {e}", "error")
            if conn:
                conn.close()
