// Chatbot Frontend Application
class ChatbotApp {
    constructor() {
        this.sessionId = null;
        this.isLoading = false;
        
        // DOM elements
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.useRagCheckbox = document.getElementById('use-rag');
        this.clearChatButton = document.getElementById('clear-chat');
        this.newSessionButton = document.getElementById('new-session');
        this.sessionIdSpan = document.getElementById('session-id');
        this.activeSessionsSpan = document.getElementById('active-sessions');
        
        this.init();
    }
    
    async init() {
        // Create initial session
        await this.createSession();
        
        // Set up event listeners
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.clearChatButton.addEventListener('click', () => this.clearChat());
        this.newSessionButton.addEventListener('click', () => this.createSession());
        
        // Auto-resize textarea
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = this.userInput.scrollHeight + 'px';
        });
        
        // Update stats periodically
        setInterval(() => this.updateStats(), 30000); // Every 30 seconds
    }
    
    async createSession() {
        try {
            const response = await fetch('/api/session/create', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.session_id) {
                this.sessionId = data.session_id;
                this.sessionIdSpan.textContent = `Session: ${this.sessionId.substring(0, 8)}...`;
                
                // Clear chat display
                this.clearChatDisplay();
                
                this.showWelcomeMessage();
                await this.updateStats();
            }
        } catch (error) {
            console.error('Error creating session:', error);
            this.showError('Failed to create session');
        }
    }
    
    async sendMessage() {
        const message = this.userInput.value.trim();
        
        if (!message || this.isLoading) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        
        // Show loading indicator
        this.showLoading();
        this.isLoading = true;
        this.sendButton.disabled = true;
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    query: message,
                    use_rag: this.useRagCheckbox.checked
                })
            });
            
            const data = await response.json();
            
            // Remove loading indicator
            this.hideLoading();
            
            if (data.response) {
                this.addMessage('assistant', data.response, data.sources);
            } else if (data.error) {
                this.showError(data.error);
            }
        } catch (error) {
            this.hideLoading();
            console.error('Error sending message:', error);
            this.showError('Failed to send message');
        } finally {
            this.isLoading = false;
            this.sendButton.disabled = false;
            this.userInput.focus();
        }
    }
    
    addMessage(role, content, sources = []) {
        // Remove welcome message if present
        const welcomeMsg = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const label = role === 'user' ? 'You' : 'Assistant';
        
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="sources">
                    <div class="sources-title">📄 Sources:</div>
                    ${sources.map(source => `<div class="source-item">• ${source}</div>`).join('')}
                </div>
            `;
        }
        
        messageDiv.innerHTML = `
            <div class="message-label">${label}</div>
            <div class="message-content">${this.formatContent(content)}</div>
            ${sourcesHtml}
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatContent(content) {
        // Basic formatting: preserve line breaks and convert URLs to links
        return content
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    }
    
    showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant-message loading-message';
        loadingDiv.innerHTML = `
            <div class="loading">
                <span>Thinking</span>
                <div class="loading-dots">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(loadingDiv);
        this.scrollToBottom();
    }
    
    hideLoading() {
        const loadingMsg = this.chatMessages.querySelector('.loading-message');
        if (loadingMsg) {
            loadingMsg.remove();
        }
    }
    
    showWelcomeMessage() {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <h2>Welcome! 👋</h2>
            <p>I can help you find information from your uploaded PDF documents.</p>
            <p>Start by asking a question about your documents.</p>
        `;
        
        this.chatMessages.appendChild(welcomeDiv);
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message assistant-message';
        errorDiv.innerHTML = `
            <div class="message-label">Error</div>
            <div class="message-content" style="background: #fee2e2; color: #991b1b;">
                ⚠️ ${message}
            </div>
        `;
        
        this.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
    }
    
    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/session/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.clearChatDisplay();
                this.showWelcomeMessage();
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
            this.showError('Failed to clear chat');
        }
    }
    
    clearChatDisplay() {
        this.chatMessages.innerHTML = '';
    }
    
    async updateStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.active_sessions !== undefined) {
                this.activeSessionsSpan.textContent = `Active Sessions: ${data.active_sessions}`;
            }
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatbotApp();
});
