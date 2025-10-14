import json
import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

class GeminiService:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        self.api_key = api_key
        
        # Load FAQs
        self.faqs = self._load_faqs()
    
    def _load_faqs(self) -> List[Dict]:
        """Load FAQs from JSON file"""
        try:
            with open('faqs.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI assistant"""
        faq_context = "\n".join([
            f"Q: {faq['question']}\nA: {faq['answer']}\n"
            for faq in self.faqs
        ])
        
        return f"""You are an experienced and knowledgeable customer support representative. Your role is to:

1. Provide comprehensive, helpful, and accurate assistance to customers
2. Use the FAQ knowledge base as a reference, but don't limit yourself to only FAQ answers
3. Think like a human support agent who has extensive product/service knowledge
4. Be empathetic, professional, and solution-oriented
5. Provide detailed explanations and step-by-step guidance when appropriate
6. Offer multiple solutions or alternatives when possible
7. Ask clarifying questions if needed to better understand the customer's issue

FAQ Knowledge Base (use as reference):
{faq_context}

Your Approach as a Support Agent:
- Start by understanding the customer's specific situation and needs
- Provide comprehensive answers that go beyond simple FAQ responses
- Offer practical solutions, troubleshooting steps, and best practices
- Be proactive in suggesting related information that might be helpful
- Use a warm, professional tone that makes customers feel valued
- If you encounter a complex issue beyond your knowledge, acknowledge it honestly and offer to escalate: "This is a specialized issue that requires expert attention. Let me connect you with a senior support agent who can provide the detailed assistance you need."

Guidelines:
- Always prioritize customer satisfaction and problem resolution
- Provide actionable advice and clear next steps
- Be thorough but concise in your explanations
- Show empathy for customer frustrations
- Maintain a positive, solution-focused attitude
- Only escalate when absolutely necessary for complex technical issues or policy matters

Remember: You are a knowledgeable support professional who can handle most customer inquiries with expertise and care."""

    def _determine_escalation(self, query: str, response: str) -> bool:
        """Determine if the query should be escalated based on response content"""
        escalation_indicators = [
            "connect you with a human support agent",
            "connect you with a senior support agent",
            "transfer you",
            "escalate",
            "human support",
            "senior support agent",
            "I need to connect you",
            "specialized issue that requires expert attention"
        ]
        
        return any(indicator.lower() in response.lower() for indicator in escalation_indicators)
    
    def generate_response(self, query: str, conversation_history: List[Dict] = None) -> Tuple[str, bool]:
        """
        Generate a response using Gemini AI
        
        Args:
            query: User's question
            conversation_history: Previous messages in the conversation
            
        Returns:
            Tuple of (response_text, is_escalated)
        """
        try:
            # Build context from conversation history
            context = ""
            if conversation_history:
                context = "\n".join([
                    f"{msg['role'].title()}: {msg['content']}"
                    for msg in conversation_history[-5:]  # Last 5 messages for context
                ])
                context = f"Previous conversation:\n{context}\n\n"
            
            # Create the full prompt
            full_prompt = f"{self._build_system_prompt()}\n\n{context}Customer Question: {query}\n\nPlease provide a helpful response:"
            
            # Generate response via REST API (text-only)
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ]
            }
            resp = requests.post(
                GEMINI_API_URL,
                params={"key": self.api_key},
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            response_text = ""
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    response_text = parts[0].get("text", "").strip()
            if not response_text:
                response_text = "I apologize, but I'm experiencing some technical difficulties right now. Let me connect you with a senior support agent who can provide the assistance you need."
            
            # Determine if escalation is needed
            is_escalated = self._determine_escalation(query, response_text)
            
            return response_text, is_escalated
            
        except Exception as e:
            # Fallback response in case of API errors
            error_response = "I apologize, but I'm experiencing some technical difficulties right now. Let me connect you with a senior support agent who can provide the assistance you need."
            return error_response, True
    
    def get_faqs(self) -> List[Dict]:
        """Return the loaded FAQs"""
        return self.faqs
