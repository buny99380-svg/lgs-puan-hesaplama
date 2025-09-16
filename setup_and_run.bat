@echo off
echo ========================================
echo LGS Puan Hesaplama Sistemi - Setup
echo ========================================

echo Installing required packages...
python -m pip install Flask==2.3.3 Flask-SQLAlchemy==3.0.5 Werkzeug==2.3.7 requests==2.31.0 python-dotenv==1.0.0

if %errorlevel% neq 0 (
    echo Failed to install packages. Please check your Python installation.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting LGS Puan Hesaplama Sistemi...
echo ========================================
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo ========================================

python run.py

pause
