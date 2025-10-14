# AI Customer Support Bot

A complete FastAPI-based backend system for an AI-powered customer support bot using Google Gemini API. This system provides intelligent FAQ responses and automatic escalation to human support when needed.

## 🚀 Features

- **AI-Powered Responses**: Uses Google Gemini API for intelligent customer support
- **Session Management**: Tracks conversation history per session
- **FAQ Database**: Pre-loaded with common customer questions
- **Automatic Escalation**: Escalates to human support when AI confidence is low
- **Modern Web UI**: Beautiful, responsive chat interface
- **RESTful API**: Complete FastAPI backend with auto-generated documentation
- **SQLite Database**: Persistent storage for sessions and messages

## 🏗️ Tech Stack

- **Backend**: FastAPI
- **AI Model**: Google Gemini API (`google-generativeai`)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Modern CSS with gradients and animations

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `env.example` to `.env`
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

4. **Get a Gemini API key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

## 🚀 Running the Application

1. **Start the server**:
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the application**:
   - **Web Interface**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ask` | Ask a question to the AI bot |
| `POST` | `/new_session` | Create a new chat session |
| `GET` | `/get_history/{session_id}` | Get conversation history |
| `GET` | `/faqs` | Get list of FAQs |
| `GET` | `/` | Serve the chat interface |
| `GET` | `/health` | Health check endpoint |

### Request/Response Examples

#### Ask a Question
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "query": "How do I reset my password?"
  }'
```

Response:
```json
{
  "response": "To reset your password, go to the login page and click 'Forgot Password'...",
  "escalated": false
}
```

#### Create New Session
```bash
curl -X POST "http://localhost:8000/new_session"
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## 🗄️ Database Schema

### Sessions Table
- `id` (String, Primary Key): Unique session identifier
- `created_at` (DateTime): Session creation timestamp

### Messages Table
- `id` (Integer, Primary Key): Message identifier
- `session_id` (String, Foreign Key): Reference to session
- `role` (String): "user" or "bot"
- `content` (Text): Message content
- `timestamp` (DateTime): Message timestamp

## 🧠 AI Integration

The system uses Google Gemini API with the following features:

- **Contextual Responses**: Maintains conversation history for better responses
- **FAQ-Based Knowledge**: Pre-loaded with common customer questions
- **Smart Escalation**: Automatically escalates when confidence is low
- **Professional Tone**: Maintains helpful, professional customer service tone

### System Prompt
The AI is configured with a comprehensive system prompt that includes:
- FAQ knowledge base
- Escalation guidelines
- Professional communication standards
- Context awareness instructions

## 🎨 Frontend Features

- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Chat**: Instant message sending and receiving
- **Typing Indicators**: Shows when AI is processing
- **FAQ Integration**: Clickable FAQ items for quick questions
- **Escalation Notices**: Clear indication when escalated to human support
- **Modern UI**: Beautiful gradients, animations, and smooth interactions

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)

### Customization
- **FAQs**: Edit `faqs.json` to add/modify FAQ entries
- **Styling**: Modify `static/style.css` for UI changes
- **AI Behavior**: Adjust prompts in `gemini_service.py`

## 📁 Project Structure

```
├── main.py                 # FastAPI application
├── database.py             # Database models and configuration
├── gemini_service.py       # Gemini AI integration
├── faqs.json              # FAQ dataset
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── README.md              # This file
├── templates/
│   └── chat.html          # Chat interface template
└── static/
    ├── style.css          # CSS styles
    └── script.js          # Frontend JavaScript
```

## 🚨 Troubleshooting

### Common Issues

1. **"Gemini service not available" error**:
   - Check that your `GEMINI_API_KEY` is set correctly
   - Verify the API key is valid and has proper permissions

2. **Database errors**:
   - Ensure SQLite can create files in the project directory
   - Check file permissions

3. **Frontend not loading**:
   - Verify static files are in the correct directories
   - Check browser console for JavaScript errors

### Health Check
Visit `http://localhost:8000/health` to verify:
- Server is running
- Gemini service is available

## 🔒 Security Considerations

- Store API keys in environment variables, never in code
- Consider implementing rate limiting for production use
- Add authentication if handling sensitive customer data
- Use HTTPS in production environments

## 🚀 Production Deployment

For production deployment:

1. **Use a production ASGI server**:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set up environment variables**:
   - Use a proper `.env` file or environment variable management
   - Never commit API keys to version control

3. **Database considerations**:
   - Consider using PostgreSQL for production
   - Implement proper database backups

4. **Security**:
   - Add CORS configuration if needed
   - Implement rate limiting
   - Use HTTPS

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For questions or issues:
- Check the troubleshooting section above
- Review the API documentation at `/docs`
- Open an issue in the project repository
