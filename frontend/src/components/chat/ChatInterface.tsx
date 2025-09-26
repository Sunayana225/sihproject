import React, { useState, useRef, useEffect } from 'react';
import { TrashIcon, Bars3Icon } from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import { Message } from '../../types/chat';

interface ChatInterfaceProps {
  onBackToHome?: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onBackToHome }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { signOut, currentUser } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateMessageId = () => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: generateMessageId(),
      content,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Add typing indicator
    const typingMessage: Message = {
      id: 'typing',
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isTyping: true,
    };

    setMessages(prev => [...prev, typingMessage]);

    try {
      // Import chat service dynamically to avoid circular dependencies
      const { chatService } = await import('../../services/chatService');
      
      // Send message to backend
      const response = await chatService.sendMessage(content);
      
      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));
      
      // Add assistant response
      const assistantMessage: Message = {
        id: response.messageId,
        content: response.message,
        role: 'assistant',
        timestamp: new Date(response.timestamp),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));
      
      const errorMessage: Message = {
        id: generateMessageId(),
        content: error.message || "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear this conversation?')) {
      setMessages([]);
    }
  };

  const handleRegenerate = (messageId: string) => {
    // Find the user message that prompted this response
    const messageIndex = messages.findIndex(msg => msg.id === messageId);
    if (messageIndex > 0) {
      const userMessage = messages[messageIndex - 1];
      if (userMessage.role === 'user') {
        // Remove the assistant message and regenerate
        setMessages(prev => prev.filter(msg => msg.id !== messageId));
        handleSendMessage(userMessage.content);
      }
    }
  };

  return (
    <div className="flex h-screen" style={{ backgroundColor: 'transparent', background: 'transparent', backgroundImage: 'none' }}>
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`} style={{ backgroundColor: 'transparent' }}>
        <div className="flex items-center justify-between p-4" style={{ backgroundColor: 'transparent' }}>
          <h2 className="text-lg font-semibold" style={{ color: 'rgba(0, 0, 0, 0.9)' }}>Chat History</h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden hover:opacity-70 transition-opacity"
            style={{ color: 'rgba(0, 0, 0, 0.6)' }}
          >
            ×
          </button>
        </div>
        
        <div className="p-4">
          <button
            onClick={handleClearChat}
            className="w-full flex items-center justify-center px-3 py-2 text-sm rounded-md hover:opacity-80 transition-opacity"
            style={{ 
              color: 'rgba(0, 0, 0, 0.7)', 
              backgroundColor: 'transparent', 
              border: 'none'
            }}
          >
            <TrashIcon className="h-4 w-4 mr-2" />
            Clear Conversation
          </button>
        </div>
        
        <div className="flex-1 p-4">
          <div className="text-sm text-center" style={{ color: 'rgba(0, 0, 0, 0.6)' }}>
            Chat history will be displayed here
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col" style={{ backgroundColor: 'transparent', background: 'transparent' }}>
        {/* Header */}
        <header className="px-4 py-3" style={{ backgroundColor: 'transparent' }}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden hover:opacity-70 transition-opacity"
                style={{ color: 'rgba(0, 0, 0, 0.7)' }}
              >
                <Bars3Icon className="h-6 w-6" />
              </button>
              
              {onBackToHome && (
                <button
                  onClick={onBackToHome}
                  className="text-sm font-medium hover:opacity-70 transition-opacity"
                  style={{ color: 'rgba(0, 0, 0, 0.8)' }}
                >
                  ← Back to Home
                </button>
              )}
              
              <h1 className="text-xl font-semibold" style={{ color: 'rgba(0, 0, 0, 0.9)' }}>WellBot Assistant</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm" style={{ color: 'rgba(0, 0, 0, 0.7)' }}>
                {currentUser?.email}
              </span>
              <button
                onClick={signOut}
                className="text-sm hover:opacity-70 transition-opacity"
                style={{ color: 'rgba(0, 0, 0, 0.8)' }}
              >
                Sign Out
              </button>
            </div>
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4" style={{ backgroundColor: 'transparent' }}>
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <div className="rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center" style={{ backgroundColor: 'transparent', border: 'none' }}>
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: 'rgba(0, 0, 0, 0.8)' }}>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-2" style={{ color: 'rgba(0, 0, 0, 0.9)' }}>Welcome to WellBot Assistant</h3>
                <p className="mb-4" style={{ color: 'rgba(0, 0, 0, 0.75)' }}>
                  I'm here to help answer your health-related questions. Ask me about symptoms, general health advice, or wellness tips.
                </p>
                <div className="rounded-lg p-3 text-sm" style={{ backgroundColor: 'transparent', border: 'none', color: 'rgba(0, 0, 0, 0.8)' }}>
                  <strong>Important:</strong> This is for informational purposes only and should not replace professional medical advice.
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto">
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  onRegenerate={message.role === 'assistant' && !message.isTyping ? () => handleRegenerate(message.id) : undefined}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Chat Input */}
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          placeholder="Ask a health-related question..."
        />
      </div>

      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default ChatInterface;