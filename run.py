#!/usr/bin/env python3
"""
LGS Puan Hesaplama Sistemi - Startup Script
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
    
    print("🚀 Starting LGS Puan Hesaplama Sistemi...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🤖 AI features powered by OpenRouter API")
    print("⚡ Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except ImportError as e:
    print("❌ Missing required packages. Please install them:")
    print("pip install Flask Flask-SQLAlchemy Werkzeug requests python-dotenv")
    print(f"Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1)
