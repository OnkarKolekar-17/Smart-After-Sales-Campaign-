"""
Smart After-Sales Campaign Dashboard
Interactive frontend for campaign management and monitoring
"""

import streamlit as st
import subprocess
import asyncio
import threading
import time
import psycopg2
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="Smart Campaign Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DatabaseConnection:
    """Handle database connections"""
    
    @staticmethod
    def get_connection():
        """Get database connection"""
        return psycopg2.connect(
            host='localhost',
            database='car_campaigns',
            user='Retailer',
            password='Kolekar@3234',
            port='5432'
        )

class CampaignStats:
    """Handle campaign statistics and data"""
    
    @staticmethod
    def get_campaign_stats() -> Dict:
        """Get overall campaign statistics"""
        try:
            conn = DatabaseConnection.get_connection()
            cur = conn.cursor()
            
            # Total campaigns
            cur.execute("SELECT COUNT(*) FROM campaigns")
            total_campaigns = cur.fetchone()[0]
            
            # Campaigns by type/trigger
            cur.execute("""
                SELECT 
                    CASE 
                        WHEN campaign_title ILIKE '%weather%' THEN 'Weather'
                        WHEN campaign_title ILIKE '%holiday%' OR campaign_title ILIKE '%festival%' THEN 'Holiday'
                        WHEN campaign_title ILIKE '%warranty%' OR campaign_title ILIKE '%service%' OR campaign_title ILIKE '%maintenance%' THEN 'Lifecycle'
                        ELSE 'Other'
                    END as campaign_type,
                    COUNT(*) as count
                FROM campaigns 
                GROUP BY 
                    CASE 
                        WHEN campaign_title ILIKE '%weather%' THEN 'Weather'
                        WHEN campaign_title ILIKE '%holiday%' OR campaign_title ILIKE '%festival%' THEN 'Holiday'
                        WHEN campaign_title ILIKE '%warranty%' OR campaign_title ILIKE '%service%' OR campaign_title ILIKE '%maintenance%' THEN 'Lifecycle'
                        ELSE 'Other'
                    END
                ORDER BY count DESC
            """)
            campaigns_by_type = {row[0]: row[1] for row in cur.fetchall()}
            
            # Recent campaigns (last 24 hours)
            cur.execute("""
                SELECT COUNT(*) FROM campaigns 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
            recent_campaigns = cur.fetchone()[0]
            
            # Total customers
            cur.execute("SELECT COUNT(*) FROM customers")
            total_customers = cur.fetchone()[0]
            
            # Campaigns per location
            cur.execute("""
                SELECT c.preferred_location, COUNT(camp.id) as campaign_count
                FROM customers c
                LEFT JOIN campaigns camp ON c.id = camp.customer_id
                GROUP BY c.preferred_location
                ORDER BY campaign_count DESC
            """)
            campaigns_by_location = {row[0]: row[1] for row in cur.fetchall()}
            
            conn.close()
            
            return {
                'total_campaigns': total_campaigns,
                'total_customers': total_customers,
                'recent_campaigns': recent_campaigns,
                'campaigns_by_type': campaigns_by_type,
                'campaigns_by_location': campaigns_by_location
            }
            
        except psycopg2.Error as e:
            st.error(f"Database connection error: {str(e)}")
            return {
                'total_campaigns': 0,
                'total_customers': 0,
                'recent_campaigns': 0,
                'campaigns_by_type': {},
                'campaigns_by_location': {}
            }
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return {
                'total_campaigns': 0,
                'total_customers': 0,
                'recent_campaigns': 0,
                'campaigns_by_type': {},
                'campaigns_by_location': {}
            }
    
    @staticmethod
    def get_sample_campaigns() -> Dict[str, Dict]:
        """Get sample campaigns for each trigger type"""
        try:
            conn = DatabaseConnection.get_connection()
            cur = conn.cursor()
            
            samples = {}
            
            # Weather campaign sample
            cur.execute("""
                SELECT campaign_title, content, customer_id, created_at
                FROM campaigns 
                WHERE campaign_title ILIKE '%weather%'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            weather_result = cur.fetchone()
            if weather_result:
                # Get customer info
                cur.execute("SELECT name, email FROM customers WHERE id = %s", (weather_result[2],))
                customer = cur.fetchone()
                samples['weather'] = {
                    'title': weather_result[0],
                    'content': weather_result[1][:200] + "...",
                    'customer_name': customer[0] if customer else "N/A",
                    'customer_email': customer[1] if customer else "N/A",
                    'created_at': weather_result[3]
                }
            
            # Holiday campaign sample  
            cur.execute("""
                SELECT campaign_title, content, customer_id, created_at
                FROM campaigns 
                WHERE campaign_title ILIKE '%holiday%' OR campaign_title ILIKE '%festival%'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            holiday_result = cur.fetchone()
            if holiday_result:
                cur.execute("SELECT name, email FROM customers WHERE id = %s", (holiday_result[2],))
                customer = cur.fetchone()
                samples['holiday'] = {
                    'title': holiday_result[0],
                    'content': holiday_result[1][:200] + "...",
                    'customer_name': customer[0] if customer else "N/A", 
                    'customer_email': customer[1] if customer else "N/A",
                    'created_at': holiday_result[3]
                }
            
            # Lifecycle campaign samples (different service types)
            lifecycle_types = [
                ('%warranty%', 'Warranty'),
                ('%service%', 'Service'),
                ('%maintenance%', 'Maintenance')
            ]
            
            lifecycle_samples = []
            for pattern, service_type in lifecycle_types:
                cur.execute("""
                    SELECT campaign_title, content, customer_id, created_at
                    FROM campaigns 
                    WHERE campaign_title ILIKE %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (pattern,))
                result = cur.fetchone()
                if result:
                    cur.execute("SELECT name, email FROM customers WHERE id = %s", (result[2],))
                    customer = cur.fetchone()
                    lifecycle_samples.append({
                        'service_type': service_type,
                        'title': result[0],
                        'content': result[1][:200] + "...",
                        'customer_name': customer[0] if customer else "N/A",
                        'customer_email': customer[1] if customer else "N/A", 
                        'created_at': result[3]
                    })
            
            samples['lifecycle'] = lifecycle_samples
            
            conn.close()
            return samples
            
        except Exception as e:
            st.error(f"Error fetching sample campaigns: {str(e)}")
            return {}

class CampaignExecutor:
    """Handle campaign execution"""
    
    @staticmethod
    def execute_campaign(trigger_type: str, location: Optional[str] = None) -> Dict:
        """Execute campaign and return results"""
        try:
            # Build command - always run multi-location campaigns
            cmd = [
                sys.executable, 
                str(project_root / "main.py"),
                "--mode", "single",
                "--trigger", trigger_type
            ]
            
            # Note: Never pass location - we want to process ALL locations for weather/holiday
            
            # Execute command
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=str(project_root),
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Parse output for campaign stats - ONLY use the FINAL summary
                output = result.stdout
                
                # Find the FINAL CAMPAIGN EXECUTION RESULTS section
                lines = output.split('\n')
                final_summary_started = False
                campaigns_created = 0
                campaigns_sent = 0
                customers_targeted = 0
                
                # Look for the final summary section only
                for line in lines:
                    if 'CAMPAIGN EXECUTION RESULTS' in line:
                        final_summary_started = True
                        continue
                    
                    if final_summary_started:
                        if 'Total Targeted:' in line:
                            customers_targeted = int(line.split(':')[1].strip())
                        elif 'Campaigns Created:' in line:
                            campaigns_created = int(line.split(':')[1].strip())
                        elif 'Campaigns Sent:' in line:
                            campaigns_sent = int(line.split(':')[1].strip())
                
                # DEBUG: Show what we parsed
                st.write("**🔍 DEBUG - Final Summary Results:**")
                st.write(f"- **Total Targeted:** {customers_targeted}")
                st.write(f"- **Campaigns Created:** {campaigns_created}")
                st.write(f"- **Campaigns Sent:** {campaigns_sent}")
                
                return {
                    'success': True,
                    'campaigns_created': campaigns_created,
                    'campaigns_sent': campaigns_sent, 
                    'customers_targeted': customers_targeted,
                    'output': output,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'campaigns_created': 0,
                    'campaigns_sent': 0,
                    'customers_targeted': 0,
                    'output': result.stdout,
                    'error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Campaign execution timed out (5 minutes)',
                'campaigns_created': 0,
                'campaigns_sent': 0,
                'customers_targeted': 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'campaigns_created': 0,
                'campaigns_sent': 0,
                'customers_targeted': 0
            }

def main():
    """Main dashboard function"""
    
    # Header
    st.title("🚀 Smart After-Sales Campaign Dashboard")
    st.markdown("---")
    
    # Initialize session state
    if 'campaign_running' not in st.session_state:
        st.session_state.campaign_running = False
    if 'last_execution_result' not in st.session_state:
        st.session_state.last_execution_result = None
    
    # Sidebar - Campaign Statistics
    st.sidebar.header("📊 Campaign Overview")
    
    # Get current stats
    stats = CampaignStats.get_campaign_stats()
    
    if stats:
        st.sidebar.metric("Total Campaigns", stats.get('total_campaigns', 0))
        st.sidebar.metric("Total Customers", stats.get('total_customers', 0))
        st.sidebar.metric("Recent Campaigns (24h)", stats.get('recent_campaigns', 0))
        
        # Campaign type breakdown
        if stats.get('campaigns_by_type'):
            st.sidebar.subheader("Campaigns by Type")
            for campaign_type, count in stats['campaigns_by_type'].items():
                st.sidebar.write(f"• **{campaign_type}**: {count}")
    
    # Main content area - Three columns for trigger buttons
    col1, col2, col3 = st.columns(3)
    
    # Lifecycle Campaign Button
    with col1:
        st.subheader("🔄 Lifecycle Campaigns")
        st.write("Service-need based targeting")
        st.write("• Warranty expiring alerts")
        st.write("• Service due reminders") 
        st.write("• Maintenance notifications")
        
        if st.button("🚀 Launch Lifecycle Campaign", 
                    disabled=st.session_state.campaign_running,
                    key="lifecycle_btn"):
            execute_campaign_with_progress("lifecycle")
    
    # Weather Campaign Button
    with col2:
        st.subheader("🌤️ Weather Campaigns") 
        st.write("Multi-location weather targeting")
        st.write("• Weather-based maintenance for all locations")
        st.write("• Seasonal vehicle care")
        st.write("• Climate protection tips")
        st.write("• Processes all 9 locations automatically")
        
        if st.button("🌦️ Launch Weather Campaign",
                    disabled=st.session_state.campaign_running,
                    key="weather_btn"):
            execute_campaign_with_progress("weather")
    
    # Holiday Campaign Button  
    with col3:
        st.subheader("🎉 Holiday Campaigns")
        st.write("Multi-location festival targeting")
        st.write("• Festival travel preparation for all locations")
        st.write("• Holiday vehicle checks")
        st.write("• Special occasion care")
        st.write("• Processes all 9 locations automatically")
        
        if st.button("🎊 Launch Holiday Campaign",
                    disabled=st.session_state.campaign_running,
                    key="holiday_btn"):
            execute_campaign_with_progress("holiday")
    
    st.markdown("---")
    
    # Campaign Execution Results
    if st.session_state.last_execution_result:
        display_execution_results(st.session_state.last_execution_result)
    
    # Sample Campaigns Section
    st.header("📝 Sample Campaign Preview")
    display_sample_campaigns()
    
    # Analytics Dashboard
    st.header("📈 Campaign Analytics")
    display_analytics_dashboard(stats)

def execute_campaign_with_progress(trigger_type: str, location: Optional[str] = None):
    """Execute campaign with progress indicator"""
    st.session_state.campaign_running = True
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text(f"🚀 Launching {trigger_type} campaign...")
    progress_bar.progress(20)
    
    # Execute campaign
    executor = CampaignExecutor()
    result = executor.execute_campaign(trigger_type, location)
    
    progress_bar.progress(100)
    status_text.text(f"✅ {trigger_type.title()} campaign completed!")
    
    # Store result
    st.session_state.last_execution_result = {
        'trigger_type': trigger_type,
        'location': location,
        'result': result,
        'timestamp': datetime.now()
    }
    
    st.session_state.campaign_running = False
    
    # Auto-refresh page to show updated stats
    time.sleep(2)
    st.rerun()

def display_execution_results(execution_data: Dict):
    """Display campaign execution results"""
    result = execution_data['result']
    trigger_type = execution_data['trigger_type']
    timestamp = execution_data['timestamp']
    
    # Display multi-location info for weather and holiday campaigns
    location_info = ""
    if trigger_type in ['weather', 'holiday']:
        location_info = " (All Locations)"
    
    st.subheader(f"🎯 Latest Campaign Results - {trigger_type.title()}{location_info}")
    
    if result['success']:
        # Simple success message
        st.success("✅ **Campaign completed successfully!** All emails have been sent.")
        
        # Get list of customers who received emails from recent campaigns
        customers_list = get_recent_campaign_recipients(trigger_type)
        
        if customers_list:
            st.write(f"� **Emails sent to {len(customers_list)} customers:**")
            
            # Display customers in a nice format
            for i, customer in enumerate(customers_list, 1):
                col1, col2, col3 = st.columns([1, 3, 2])
                with col1:
                    st.write(f"**{i}.**")
                with col2:
                    st.write(f"**{customer['name']}**")
                with col3:
                    st.write(f"� {customer['location']}")
        else:
            st.info("No customer details available for this campaign.")
        
        st.caption(f"Executed at: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
    else:
        st.error(f"❌ Campaign failed: {result.get('error', 'Unknown error')}")
        
        if result.get('output'):
            with st.expander("View Execution Log"):
                st.text(result['output'])

def get_recent_campaign_recipients(trigger_type: str):
    """Get list of customers who received emails in recent campaigns"""
    try:
        conn = DatabaseConnection.get_connection()
        cur = conn.cursor()
        
        # Get customers from recent campaigns of this type
        # Look for campaigns created in the last 5 minutes
        cur.execute("""
            SELECT DISTINCT c.name, c.preferred_location
            FROM campaigns camp
            JOIN customers c ON camp.customer_id = c.id
            WHERE camp.trigger_type = %s 
            AND camp.created_at >= NOW() - INTERVAL '5 minutes'
            AND camp.status = 'sent'
            ORDER BY c.name
        """, (trigger_type,))
        
        results = cur.fetchall()
        conn.close()
        
        return [{'name': name, 'location': location} for name, location in results]
        
    except Exception as e:
        st.error(f"Error getting customer list: {str(e)}")
        return []

def display_sample_campaigns():
    """Display sample campaigns for each trigger type"""
    samples = CampaignStats.get_sample_campaigns()
    
    if not samples:
        st.warning("No sample campaigns available. Run some campaigns first!")
        return
    
    # Create tabs for each campaign type
    tabs = st.tabs(["🔄 Lifecycle", "🌤️ Weather", "🎉 Holiday"])
    
    # Lifecycle samples
    with tabs[0]:
        lifecycle_samples = samples.get('lifecycle', [])
        if lifecycle_samples:
            for i, sample in enumerate(lifecycle_samples):
                with st.expander(f"📋 {sample['service_type']} Campaign Sample"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Title:** {sample['title']}")
                        st.write(f"**Content Preview:** {sample['content']}")
                    
                    with col2:
                        st.write(f"**Customer:** {sample['customer_name']}")
                        st.write(f"**Email:** {sample['customer_email']}")
                        st.write(f"**Created:** {sample['created_at'].strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No lifecycle campaign samples available.")
    
    # Weather samples
    with tabs[1]:
        weather_sample = samples.get('weather')
        if weather_sample:
            with st.expander("🌦️ Weather Campaign Sample"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Title:** {weather_sample['title']}")
                    st.write(f"**Content Preview:** {weather_sample['content']}")
                
                with col2:
                    st.write(f"**Customer:** {weather_sample['customer_name']}")
                    st.write(f"**Email:** {weather_sample['customer_email']}")
                    st.write(f"**Created:** {weather_sample['created_at'].strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No weather campaign samples available.")
    
    # Holiday samples
    with tabs[2]:
        holiday_sample = samples.get('holiday')
        if holiday_sample:
            with st.expander("🎊 Holiday Campaign Sample"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Title:** {holiday_sample['title']}")
                    st.write(f"**Content Preview:** {holiday_sample['content']}")
                
                with col2:
                    st.write(f"**Customer:** {holiday_sample['customer_name']}")
                    st.write(f"**Email:** {holiday_sample['customer_email']}")
                    st.write(f"**Created:** {holiday_sample['created_at'].strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No holiday campaign samples available.")

def display_analytics_dashboard(stats: Dict):
    """Display analytics charts and insights"""
    if not stats:
        st.warning("No analytics data available.")
        return
    
    col1, col2 = st.columns(2)
    
    # Campaign type pie chart
    with col1:
        if stats.get('campaigns_by_type'):
            fig_pie = px.pie(
                values=list(stats['campaigns_by_type'].values()),
                names=list(stats['campaigns_by_type'].keys()),
                title="Campaigns by Type"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Campaign location bar chart
    with col2:
        if stats.get('campaigns_by_location'):
            fig_bar = px.bar(
                x=list(stats['campaigns_by_location'].keys()),
                y=list(stats['campaigns_by_location'].values()),
                title="Campaigns by Location"
            )
            fig_bar.update_xaxes(title="Location")
            fig_bar.update_yaxes(title="Number of Campaigns")
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Summary insights
    if stats.get('total_campaigns', 0) > 0:
        st.subheader("💡 Key Insights")
        
        total = stats['total_campaigns']
        recent = stats.get('recent_campaigns', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📈 Campaign Growth", f"{recent}", f"in last 24h")
        
        with col2:
            most_active_type = max(stats.get('campaigns_by_type', {}), 
                                 key=stats.get('campaigns_by_type', {}).get, default="N/A")
            st.metric("🏆 Top Campaign Type", most_active_type)
        
        with col3:
            most_active_location = max(stats.get('campaigns_by_location', {}),
                                     key=stats.get('campaigns_by_location', {}).get, default="N/A")
            st.metric("📍 Most Active Location", most_active_location)

if __name__ == "__main__":
    main()
