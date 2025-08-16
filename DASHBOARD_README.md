# Smart After-Sales Campaign Dashboard 🚀

## Overview
Interactive frontend dashboard for the Smart After-Sales Campaign system. Provides one-click campaign execution, real-time monitoring, and comprehensive analytics.

## Features

### 🎯 Campaign Triggers
- **Lifecycle Campaigns**: Service-need based targeting (warranty, maintenance, service reminders)
- **Weather Campaigns**: Location-specific weather-based vehicle care recommendations  
- **Holiday Campaigns**: Festival and holiday-based travel preparation campaigns

### 📊 Real-time Monitoring
- Live campaign statistics
- Execution progress tracking
- Success/failure notifications
- Campaign distribution analytics

### 📈 Analytics Dashboard
- Campaign type breakdown (pie chart)
- Location-wise campaign distribution (bar chart)
- Key performance metrics
- Campaign growth tracking

### 📝 Sample Campaign Preview
- Real campaign examples for each trigger type
- Content preview for generated campaigns
- Customer targeting information
- Creation timestamps

## Quick Start

### Method 1: Using Launch Script
```bash
python launch_dashboard.py
```

### Method 2: Using Batch File (Windows)
```bash
run_dashboard.bat
```

### Method 3: Manual Launch
```bash
# Install dependencies
pip install streamlit==1.28.2 plotly==5.17.0

# Launch dashboard
python -m streamlit run frontend_dashboard.py --server.port=8501
```

## Dashboard Access
- **Local URL**: http://localhost:8501
- **Network URL**: http://your-ip:8501

## Dashboard Sections

### 1. Campaign Control Panel
Three main campaign buttons with location selectors:
- 🔄 **Lifecycle Campaign**: Targets all customers based on service needs
- 🌤️ **Weather Campaign**: Select location for weather-based targeting
- 🎉 **Holiday Campaign**: Select location for festival-based campaigns

### 2. Campaign Statistics Sidebar
- Total campaigns created
- Total customers in system
- Recent campaigns (24h)
- Campaign breakdown by type

### 3. Execution Results
Real-time display of:
- Campaign execution status
- Customers targeted
- Campaigns created
- Emails sent
- Success/failure rates

### 4. Sample Campaign Preview
- **Lifecycle Tab**: Different service type samples (warranty, service, maintenance)
- **Weather Tab**: Weather-based campaign examples
- **Holiday Tab**: Festival campaign samples

### 5. Analytics Dashboard
- Interactive charts showing campaign distribution
- Location-wise performance metrics
- Key insights and trends

## Technical Details

### Database Integration
- Real-time connection to PostgreSQL database
- Live statistics and campaign data
- Sample campaign retrieval

### Campaign Execution
- Subprocess-based campaign launching
- 5-minute timeout protection
- Real-time progress tracking
- Error handling and reporting

### Data Visualization
- Plotly-based interactive charts
- Responsive design
- Real-time data updates

## Dependencies
```
streamlit==1.28.2
plotly==5.17.0
psycopg2-binary (for database)
pandas (for data handling)
```

## Usage Tips

1. **Monitor Database**: Check sidebar statistics before launching campaigns
2. **Location Selection**: Choose appropriate locations for weather/holiday campaigns
3. **Progress Tracking**: Watch the progress bar during campaign execution
4. **Sample Preview**: Review sample campaigns to understand content generation
5. **Analytics**: Use charts to identify trends and optimal campaign types

## Troubleshooting

### Dashboard Won't Start
```bash
# Reinstall dependencies
pip install --upgrade streamlit plotly

# Check Python version
python --version  # Should be 3.8+
```

### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials in config/settings.py
- Ensure database schema is initialized

### Campaign Execution Fails
- Check that main.py works independently
- Verify all agents and services are configured
- Check log files for detailed error messages

## Security Notes
- Dashboard runs on localhost by default
- Database credentials are managed through settings
- No sensitive data is logged or displayed
- Campaign content is truncated in previews

## Development
To extend the dashboard:
1. Modify `frontend_dashboard.py` 
2. Add new database queries in `CampaignStats` class
3. Create new visualizations with Plotly
4. Extend campaign execution in `CampaignExecutor` class
