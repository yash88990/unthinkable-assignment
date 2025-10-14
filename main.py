from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db, create_tables, Session as DBSession, Message
from gemini_service import GeminiService

# Create FastAPI app
app = FastAPI(
    title="AI Customer Support Bot",
    description="AI-powered customer support system with Gemini integration",
    version="1.0.0"
)

# Initialize Gemini service
try:
    gemini_service = GeminiService()
except ValueError as e:
    print(f"Warning: {e}")
    gemini_service = None

# Create database tables
create_tables()

# Pydantic models for request/response
class AskRequest(BaseModel):
    session_id: str
    query: str

class AskResponse(BaseModel):
    response: str
    escalated: bool

class NewSessionResponse(BaseModel):
    session_id: str

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime

class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageResponse]

class FAQResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: str

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    """
    Ask a question to the AI customer support bot
    """
    if not gemini_service:
        raise HTTPException(status_code=500, detail="Gemini service not available")
    
    # Check if session exists
    session = db.query(DBSession).filter(DBSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get conversation history
    messages = db.query(Message).filter(Message.session_id == request.session_id).order_by(Message.timestamp).all()
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
    
    # Generate AI response
    response_text, is_escalated = gemini_service.generate_response(
        request.query, 
        conversation_history
    )
    
    # Save user message
    user_message = Message(
        session_id=request.session_id,
        role="user",
        content=request.query
    )
    db.add(user_message)
    
    # Save bot response
    bot_message = Message(
        session_id=request.session_id,
        role="bot",
        content=response_text
    )
    db.add(bot_message)
    
    db.commit()
    
    return AskResponse(response=response_text, escalated=is_escalated)

@app.post("/new_session", response_model=NewSessionResponse)
async def create_new_session(db: Session = Depends(get_db)):
    """
    Create a new chat session
    """
    session_id = str(uuid.uuid4())
    
    # Create new session in database
    new_session = DBSession(id=session_id)
    db.add(new_session)
    db.commit()
    
    return NewSessionResponse(session_id=session_id)

@app.get("/get_history/{session_id}", response_model=HistoryResponse)
async def get_conversation_history(session_id: str, db: Session = Depends(get_db)):
    """
    Get conversation history for a session
    """
    # Check if session exists
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get messages
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp).all()
    
    message_responses = [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in messages
    ]
    
    return HistoryResponse(session_id=session_id, messages=message_responses)

@app.get("/faqs", response_model=List[FAQResponse])
async def get_faqs():
    """
    Get list of frequently asked questions
    """
    if not gemini_service:
        raise HTTPException(status_code=500, detail="Gemini service not available")
    
    faqs = gemini_service.get_faqs()
    return [FAQResponse(**faq) for faq in faqs]

@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """
    Serve the chat interface
    """
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "gemini_available": gemini_service is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
