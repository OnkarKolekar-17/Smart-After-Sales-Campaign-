#!/usr/bin/env python3
"""
Setup script for Smart After-Sales Campaign System
This script helps with initial system setup and configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("="*60)
    print("  Smart After-Sales Campaign System - Setup")
    print("="*60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_postgresql():
    """Check if PostgreSQL is installed"""
    print("Checking PostgreSQL installation...")
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, check=True)
        print("✅ PostgreSQL is installed")
        print(f"   {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PostgreSQL not found")
        print("   Please install PostgreSQL 12+ before continuing")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directory structure...")
    dirs = ['logs', 'data/backups', 'config/templates']
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def setup_environment_file():
    """Setup .env file from template"""
    print("Setting up environment configuration...")
    
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping .env file setup")
            return True
    
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from template")
    print("   Please edit .env file with your API keys and configuration")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def test_imports():
    """Test if key modules can be imported"""
    print("Testing module imports...")
    
    test_modules = [
        'psycopg2',
        'langchain',
        'langgraph', 
        'sib_api_v3_sdk',
        'requests',
        'pydantic'
    ]
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - import failed")
            return False
    
    return True

def create_database():
    """Instructions for manual database creation"""
    print("Database Setup Instructions...")
    print("=" * 50)
    print("📋 MANUAL DATABASE SETUP REQUIRED")
    print("=" * 50)
    print()
    print("Please follow these steps in pgAdmin:")
    print("1. Open pgAdmin and connect to PostgreSQL")
    print("2. Right-click 'Databases' → 'Create' → 'Database'")
    print("3. Database name: car_campaigns")
    print("4. Click 'Save' to create the database")
    print()
    print("✅ Then proceed to the next step (Database Tables)")
    return True

def initialize_database_tables():
    """Instructions for manual database table creation"""
    print("Database Tables Setup Instructions...")
    print("=" * 50)
    print("📋 MANUAL TABLE CREATION REQUIRED")
    print("=" * 50)
    print()
    print("Please follow these steps in pgAdmin:")
    print("1. Open pgAdmin and navigate to your 'car_campaigns' database")
    print("2. Right-click the database → 'Query Tool'")
    print("3. Open the file: database_setup.sql")
    print("4. Copy all contents into the Query Tool")
    print("5. Click the Execute button (▶️) to run the script")
    print()
    print("📁 The database_setup.sql file contains:")
    print("   - All table schemas (customers, vehicles, service_history, campaigns)")
    print("   - 15 sample customers with vehicles")
    print("   - Service history records")
    print("   - Sample campaign data")
    print()
    print("✅ After running the SQL script, all tables and data will be ready!")
    return True

def run_basic_test():
    """Run a basic system test"""
    print("Running basic system test...")
    try:
        # Test configuration loading
        sys.path.append('.')
        from config.settings import settings
        
        print(f"✅ Configuration loaded (DB: {settings.database.database})")
        return True
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("  Setup Complete! Next Steps:")
    print("="*60)
    print()
    print("🗄️ IMPORTANT - Complete Database Setup:")
    print("   1. Open pgAdmin")
    print("   2. Create database: car_campaigns") 
    print("   3. Run database_setup.sql in Query Tool")
    print()
    print("⚙️ Then configure your API keys:")
    print("   1. Edit the .env file with your API keys:")
    print("      - OpenAI API key")
    print("      - OpenWeatherMap API key") 
    print("      - Brevo (SendinBlue) API key")
    print("      - Database connection details")
    print()
    print("🧪 Test the system:")
    print("   python main.py --help")
    print()
    print("🚀 Run a test campaign:")
    print("   python main.py --location Mumbai --test")
    print()
    print("📖 Check the README.md for detailed usage instructions")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Track success of each step
    steps = [
        ("Python Version", check_python_version),
        ("PostgreSQL", check_postgresql),
        ("Directories", create_directories),
        ("Environment File", setup_environment_file),
        ("Dependencies", install_dependencies),
        ("Module Imports", test_imports),
        ("Database Creation", create_database),
        ("Database Tables", initialize_database_tables),
        ("Basic Test", run_basic_test)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n--- {step_name} ---")
        try:
            if not step_function():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
            failed_steps.append(step_name)
    
    print("\n" + "="*60)
    if failed_steps:
        print(f"⚠️  Setup completed with {len(failed_steps)} issue(s):")
        for step in failed_steps:
            print(f"   - {step}")
        print()
        print("Please resolve these issues before using the system.")
    else:
        print("✅ Setup completed successfully!")
        print_next_steps()

if __name__ == "__main__":
    main()
