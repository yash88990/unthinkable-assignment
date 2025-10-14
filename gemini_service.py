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
        
        return f"""You are a helpful customer support AI assistant. Your role is to:

1. Answer customer questions based on the provided FAQ knowledge base
2. Be friendly, professional, and helpful
3. If you cannot find a relevant answer in the FAQs, politely escalate to human support
4. Keep responses concise but informative
5. Always maintain a helpful tone

FAQ Knowledge Base:
{faq_context}

Instructions:
- If the customer's question matches or is similar to any FAQ, provide the relevant answer
- If the question is not covered in the FAQs or you're unsure, respond with: "I understand your question, but I need to connect you with a human support agent for the best assistance. Please hold while I transfer you."
- Always be polite and professional
- If asked about topics not related to customer support, politely redirect to support-related questions

Remember: When in doubt, escalate to human support rather than providing potentially incorrect information."""

    def _determine_escalation(self, query: str, response: str) -> bool:
        """Determine if the query should be escalated based on response content"""
        escalation_indicators = [
            "connect you with a human support agent",
            "transfer you",
            "escalate",
            "human support",
            "I need to connect you"
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
                response_text = "I understand your question, but I need to connect you with a human support agent for the best assistance. Please hold while I transfer you."
            
            # Determine if escalation is needed
            is_escalated = self._determine_escalation(query, response_text)
            
            return response_text, is_escalated
            
        except Exception as e:
            # Fallback response in case of API errors
            error_response = "I apologize, but I'm experiencing technical difficulties. Please let me connect you with a human support agent who can assist you better."
            return error_response, True
    
    def get_faqs(self) -> List[Dict]:
        """Return the loaded FAQs"""
        return self.faqs
