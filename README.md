# Smart After-Sales Campaigns System

A multi-agent AI system for generating and sending targeted automotive after-sales campaigns using LangGraph and Brevo email service.

## Overview

This system leverages artificial intelligence and multi-agent workflows to create personalized, contextual campaigns for automotive service customers. It analyzes customer data, weather conditions, holidays, and vehicle lifecycle information to generate highly targeted marketing campaigns.

## Key Features

- **Multi-Agent Architecture**: Uses LangGraph to orchestrate specialized AI agents
- **Contextual Campaign Generation**: Considers weather, holidays, and customer lifecycle
- **Personalized Content**: Creates tailored messages for each customer
- **Automated Email Delivery**: Integrates with Brevo for professional email marketing
- **Comprehensive Analytics**: Tracks campaign performance and customer engagement
- **Scalable Database Design**: PostgreSQL-based customer and vehicle management

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Weather       │    │    Holiday      │    │   Customer      │
│   Agent         │    │    Agent        │    │   Targeting     │
│                 │    │                 │    │   Agent         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │            LangGraph Workflow Engine            │
         └─────────────────────────────────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │   Campaign      │    │ Personalization │    │   Email         │
         │   Generator     │    │    Agent        │    │   Sender        │
         │   Agent         │    │                 │    │   Agent         │
         └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- OpenAI API key
- OpenWeatherMap API key
- Brevo (formerly SendinBlue) API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Smart After Sales Campgin"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   copy .env.example .env
   # Edit .env with your API keys and database credentials
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb car_campaigns
   
   # Initialize database tables
   python -c "from config.database import init_db; init_db()"
   ```

6. **Test Installation**
   ```bash
   python main.py --help
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=car_campaigns
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Weather API
WEATHER_API_KEY=your_openweather_key
DEFAULT_LOCATION=Mumbai

# Brevo Email Service
BREVO_API_KEY=your_brevo_key
BREVO_SENDER_EMAIL=campaigns@yourcompany.com
BREVO_SENDER_NAME=Your Service Team

# Campaign Settings
CAMPAIGN_BATCH_SIZE=50
LOG_LEVEL=INFO
```

### Database Schema

The system uses the following main tables:

- **customers**: Customer information and contact details
- **vehicles**: Vehicle details linked to customers
- **service_history**: Service records for each vehicle
- **campaigns**: Campaign execution tracking
- **campaign_metrics**: Performance analytics

## Usage

### Command Line Interface

```bash
# Run a single campaign for a location
python main.py --location "Mumbai" --trigger scheduled

# Run with specific campaign type
python main.py --location "Delhi" --trigger weather_alert

# Batch mode for multiple locations
python main.py --batch --config batch_config.json

# Test mode (dry run)
python main.py --test --location "Pune"
```

### Python API

```python
from workflows.campaign_workflow import CampaignWorkflow

# Initialize workflow
workflow = CampaignWorkflow()

# Run campaign
result = workflow.run_campaign(
    location="Mumbai",
    campaign_trigger="scheduled"
)

print(f"Campaign Status: {result.status}")
print(f"Customers Targeted: {result.total_targeted}")
print(f"Campaigns Sent: {result.campaigns_sent}")
```

## System Components

### Agents

1. **WeatherAgent**: Fetches current weather data and generates weather-based recommendations
2. **HolidayAgent**: Identifies current/upcoming holidays and creates themed campaigns
3. **TargetingAgent**: Selects appropriate customers based on various criteria
4. **CampaignGeneratorAgent**: Uses AI to create compelling campaign content
5. **PersonalizationAgent**: Customizes campaigns for individual customers
6. **EmailSenderAgent**: Delivers campaigns via Brevo email service
7. **DataAnalystAgent**: Provides insights and customer segmentation

### Services

- **WeatherService**: OpenWeatherMap API integration
- **HolidayService**: Holiday data management
- **BrevoService**: Email delivery and tracking
- **DatabaseService**: PostgreSQL data operations

### Workflows

The main workflow orchestrates all agents using LangGraph:

1. **Weather Analysis** → Get current weather conditions
2. **Holiday Analysis** → Check for relevant holidays
3. **Customer Targeting** → Select appropriate customers
4. **Campaign Generation** → Create campaign content with AI
5. **Personalization** → Customize for each customer
6. **Email Delivery** → Send campaigns via Brevo

## Campaign Types

The system generates various campaign types:

- **Seasonal**: Weather-based maintenance recommendations
- **Holiday**: Festival and celebration-themed offers
- **Lifecycle**: Vehicle age and warranty-based campaigns
- **Geographic**: Location-specific promotions
- **Service Reminders**: Overdue maintenance alerts
- **Warranty Alerts**: Expiring warranty notifications

## Testing

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/test_agents.py
python -m pytest tests/test_services.py
python -m pytest tests/test_workflows.py

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

## Monitoring and Logging

The system provides comprehensive logging:

- **Application logs**: `logs/campaign_system_YYYY-MM-DD.log`
- **Error logs**: `logs/errors_YYYY-MM-DD.log`
- **Campaign metrics**: `logs/campaigns_YYYY-MM-DD.log`
- **Performance logs**: `logs/performance_YYYY-MM-DD.log`

### Log Levels

- **DEBUG**: Detailed execution information
- **INFO**: General workflow progress
- **WARNING**: Non-critical issues
- **ERROR**: Serious problems requiring attention
- **CRITICAL**: System failures

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for better query performance
CREATE INDEX idx_customers_location ON customers(preferred_location);
CREATE INDEX idx_vehicles_customer_id ON vehicles(customer_id);
CREATE INDEX idx_vehicles_last_service ON vehicles(last_service_date);
CREATE INDEX idx_campaigns_customer_id ON campaigns(customer_id);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at);
```

### Caching

The system implements caching for:
- Weather data (1 hour TTL)
- Holiday information (24 hour TTL)
- Customer segments (6 hour TTL)

## API Integration

### Webhook Support

Configure webhooks to receive campaign status updates:

```python
from workflows.api_models import WebhookPayload

# Example webhook payload
payload = WebhookPayload(
    event_type="campaign_completed",
    workflow_id="workflow_123",
    data={
        "campaigns_sent": 25,
        "total_targeted": 30,
        "success_rate": 83.3
    }
)
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists and is accessible

2. **API Key Issues**
   - Verify OpenAI API key has sufficient credits
   - Check Brevo API key permissions
   - Validate OpenWeatherMap API key

3. **Email Delivery Problems**
   - Verify Brevo sender email is authenticated
   - Check email content for spam triggers
   - Monitor Brevo dashboard for delivery issues

4. **Performance Issues**
   - Monitor database query performance
   - Check OpenAI API rate limits
   - Review memory usage during batch operations

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python main.py --location "Mumbai" --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Standards

- Follow PEP 8 style guide
- Add type hints for all functions
- Include docstrings for classes and methods
- Write unit tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

## Changelog

### Version 1.0.0
- Initial release
- Multi-agent workflow implementation
- Brevo email integration
- Comprehensive campaign types
- PostgreSQL database support
- Weather and holiday context integration

---

**Note**: This system is designed for automotive service businesses but can be adapted for other industries by modifying the campaign templates and targeting criteria.
