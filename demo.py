#!/usr/bin/env python3
"""
Demo script showing how to use the AI Customer Support Bot API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def demo_api():
    print("🤖 AI Customer Support Bot - API Demo")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server is running")
            print(f"   Gemini Available: {health_data.get('gemini_available', False)}")
        else:
            print("❌ Server health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return
    
    print()
    
    # Create a new session
    print("1. Creating new session...")
    response = requests.post(f"{BASE_URL}/new_session")
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"   ✅ Session created: {session_id}")
    else:
        print("   ❌ Failed to create session")
        return
    
    print()
    
    # Get FAQs
    print("2. Loading FAQs...")
    response = requests.get(f"{BASE_URL}/faqs")
    if response.status_code == 200:
        faqs = response.json()
        print(f"   ✅ Loaded {len(faqs)} FAQs")
        print(f"   Sample FAQ: {faqs[0]['question']}")
    else:
        print("   ❌ Failed to load FAQs")
    
    print()
    
    # Demo questions
    demo_questions = [
        "How do I reset my password?",
        "What are your business hours?",
        "How can I track my order?",
        "Tell me about your return policy",
        "What's the weather like today?"  # This should trigger escalation
    ]
    
    print("3. Testing AI responses...")
    for i, question in enumerate(demo_questions, 1):
        print(f"\n   Question {i}: {question}")
        
        response = requests.post(f"{BASE_URL}/ask", json={
            "session_id": session_id,
            "query": question
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   🤖 Response: {data['response'][:100]}{'...' if len(data['response']) > 100 else ''}")
            print(f"   📞 Escalated: {data['escalated']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        time.sleep(1)  # Small delay between requests
    
    print()
    
    # Get conversation history
    print("4. Getting conversation history...")
    response = requests.get(f"{BASE_URL}/get_history/{session_id}")
    if response.status_code == 200:
        history = response.json()
        print(f"   ✅ Retrieved {len(history['messages'])} messages")
        print(f"   Session ID: {history['session_id']}")
    else:
        print("   ❌ Failed to get history")
    
    print()
    print("🎉 Demo completed!")
    print(f"🌐 Try the web interface at: {BASE_URL}")

if __name__ == "__main__":
    demo_api()
