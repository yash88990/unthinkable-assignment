#!/usr/bin/env python3
"""
Simple startup script for the AI Customer Support Bot
"""

import uvicorn
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not found in environment variables.")
        print("   Please set your Gemini API key in a .env file or environment variable.")
        print("   The application will start but AI features will be disabled.")
        print()
    
    print("🚀 Starting AI Customer Support Bot...")
    print("📱 Web Interface: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
