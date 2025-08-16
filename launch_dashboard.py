#!/usr/bin/env python3
"""
Launch script for Smart Campaign Dashboard
"""
import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing dashboard dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "streamlit==1.28.2", "plotly==5.17.0"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    try:
        dashboard_path = Path(__file__).parent / "frontend_dashboard.py"
        
        print("🚀 Starting Smart Campaign Dashboard...")
        print("📱 Dashboard will open at: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the dashboard")
        print("-" * 50)
        
        # Launch streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port=8501",
            "--server.address=localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found. Installing...")
        if install_requirements():
            launch_dashboard()
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")

if __name__ == "__main__":
    # Check if streamlit is installed
    try:
        import streamlit
        launch_dashboard()
    except ImportError:
        print("📦 Streamlit not found. Installing required packages...")
        if install_requirements():
            launch_dashboard()
        else:
            print("❌ Could not install required packages.")
            sys.exit(1)
