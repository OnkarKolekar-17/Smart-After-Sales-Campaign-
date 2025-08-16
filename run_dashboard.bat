@echo off
echo Installing required packages for dashboard...
pip install streamlit==1.28.2 plotly==5.17.0

echo.
echo Starting Smart Campaign Dashboard...
echo Open your browser to: http://localhost:8501
echo.

streamlit run frontend_dashboard.py
