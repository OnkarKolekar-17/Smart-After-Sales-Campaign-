# Manual Setup Guide - Smart After-Sales Campaign System

## 📋 Prerequisites
- Python 3.8+
- PostgreSQL 12+ with pgAdmin
- Internet connection for API services

## 🚀 Quick Setup Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup (Manual)

#### Step 2a: Create Database
1. Open **pgAdmin**
2. Connect to your PostgreSQL server
3. Right-click **"Databases"** → **"Create"** → **"Database"**
4. Enter database name: `car_campaigns`
5. Click **"Save"**

#### Step 2b: Create Tables and Data
1. In pgAdmin, right-click your `car_campaigns` database
2. Select **"Query Tool"**
3. Open the file `database_setup.sql` in a text editor
4. **Copy all contents** from the SQL file
5. **Paste into the pgAdmin Query Tool**
6. Click the **Execute button (▶️)** to run the script
7. You should see confirmation messages for table creation and data insertion

### 3. Configure Environment Variables
1. Copy `.env.example` to `.env`
2. Edit the `.env` file with your credentials:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/car_campaigns

# API Keys (get these from respective services)
OPENAI_API_KEY=your_openai_api_key_here
BREVO_API_KEY=your_brevo_api_key_here
OPENWEATHERMAP_API_KEY=your_weather_api_key_here

# Email Configuration
FROM_EMAIL=your-email@company.com
FROM_NAME=Your Company Name
```

### 4. Verify Setup
Run the automated setup script to check everything:
```bash
python setup.py
```

### 5. Test the System
```bash
# Test basic functionality
python main.py --help

# Run a test campaign for Mumbai
python main.py --location Mumbai --test
```

## 🗄️ Database Verification

After running the SQL script, verify your setup:

1. In pgAdmin, navigate to your `car_campaigns` database
2. Check that these tables exist:
   - `customers` (15 sample customers)
   - `vehicles` (15 sample vehicles) 
   - `service_history` (service records)
   - `campaigns` (campaign data)
   - `campaign_metrics` (analytics)

3. Run this verification query in pgAdmin:
```sql
SELECT 
    'customers' as table_name, COUNT(*) as record_count 
FROM customers
UNION ALL
SELECT 
    'vehicles' as table_name, COUNT(*) as record_count 
FROM vehicles
UNION ALL
SELECT 
    'service_history' as table_name, COUNT(*) as record_count 
FROM service_history;
```

You should see:
- customers: 15 records
- vehicles: 15 records  
- service_history: 15+ records

## 🔑 API Keys Required

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create account and generate API key
3. Add to `.env` file

### Brevo (SendinBlue) API Key
1. Go to [Brevo](https://www.brevo.com/)
2. Create account → Go to API Keys
3. Generate a new API key
4. Add to `.env` file

### OpenWeatherMap API Key  
1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Create account and get free API key
3. Add to `.env` file

## 🧪 Testing Your Setup

### Test Database Connection
```bash
python -c "from config.database import test_connection; test_connection()"
```

### Test API Services
```bash
python -c "from services.weather_service import WeatherService; print('Weather API:', WeatherService().get_weather('Mumbai'))"
```

### Run Sample Campaign
```bash
python main.py --location Mumbai --test
```

## 📁 Project Structure
```
Smart After Sales Campaign/
├── main.py                    # Entry point
├── database_setup.sql         # Complete database setup
├── requirements.txt           # Python dependencies
├── setup.py                  # Automated setup script
├── .env.example              # Environment template
├── agents/                   # AI agents
├── services/                 # External services
├── workflows/                # LangGraph workflows
├── models/                   # Data models
├── utils/                    # Utilities
└── logs/                     # System logs
```

## ⚠️ Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running
- Verify credentials in `.env` file
- Ensure `car_campaigns` database exists

### Import Errors
- Run: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)

### API Errors
- Verify all API keys in `.env` file
- Check internet connectivity
- Validate API key formats

## 🎯 Ready to Use!

Once setup is complete, you can:
- Generate seasonal campaigns: `python main.py --location Mumbai`
- Analyze customer data: `python main.py --analyze`
- Send targeted emails based on service history
- Get weather-based campaign recommendations

For detailed usage, run: `python main.py --help`
