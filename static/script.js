let sessionId = null;
let isEscalated = false;

// Initialize the chat
document.addEventListener('DOMContentLoaded', function() {
    createNewSession();
    loadFAQs();
    
    // Add enter key support
    document.getElementById('user-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});

async function createNewSession() {
    try {
        const response = await fetch('/new_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            sessionId = data.session_id;
            console.log('New session created:', sessionId);
        } else {
            console.error('Failed to create session');
        }
    } catch (error) {
        console.error('Error creating session:', error);
    }
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message || isEscalated) return;
    
    // Add user message to chat
    addMessageToChat('user', message);
    input.value = '';
    
    // Disable input while processing
    const sendButton = document.getElementById('send-button');
    sendButton.disabled = true;
    input.disabled = true;
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                query: message
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Remove typing indicator
            hideTypingIndicator();
            
            // Add bot response to chat
            addMessageToChat('bot', data.response);
            
            // Check if escalated
            if (data.escalated) {
                isEscalated = true;
                showEscalationNotice();
            }
        } else {
            hideTypingIndicator();
            addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        hideTypingIndicator();
        addMessageToChat('bot', 'Sorry, I encountered a network error. Please check your connection and try again.');
        console.error('Error sending message:', error);
    } finally {
        // Re-enable input
        sendButton.disabled = false;
        input.disabled = false;
        input.focus();
    }
}

function addMessageToChat(role, content) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (role === 'user') {
        contentDiv.textContent = content;
    } else {
        contentDiv.innerHTML = `<strong>AI Assistant:</strong> ${content}`;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typing-indicator';
    
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span>AI Assistant is typing</span>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function showEscalationNotice() {
    const escalationNotice = document.getElementById('escalation-notice');
    escalationNotice.style.display = 'flex';
}

async function loadFAQs() {
    try {
        const response = await fetch('/faqs');
        if (response.ok) {
            const faqs = await response.json();
            displayFAQs(faqs);
        }
    } catch (error) {
        console.error('Error loading FAQs:', error);
    }
}

function displayFAQs(faqs) {
    const faqList = document.getElementById('faq-list');
    faqList.innerHTML = '';
    
    faqs.forEach(faq => {
        const faqItem = document.createElement('div');
        faqItem.className = 'faq-item';
        faqItem.onclick = () => askFAQ(faq.question);
        
        faqItem.innerHTML = `
            <div class="faq-question">${faq.question}</div>
            <div class="faq-answer">${faq.answer}</div>
            <span class="faq-category">${faq.category}</span>
        `;
        
        faqList.appendChild(faqItem);
    });
}

function askFAQ(question) {
    if (isEscalated) return;
    
    const input = document.getElementById('user-input');
    input.value = question;
    sendMessage();
}
