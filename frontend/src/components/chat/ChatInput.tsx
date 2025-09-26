import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import { useAdaptiveColors } from '../../utils/colorUtils';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  disabled = false,
  placeholder = "Ask a health-related question..."
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const colors = useAdaptiveColors(containerRef);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  return (
    <div 
      ref={containerRef}
      className="p-4" 
      style={{ 
        borderTop: 'none', 
        backgroundColor: 'transparent' 
      }}
    >
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full px-4 py-3 rounded-lg focus:outline-none focus:ring-2 resize-none max-h-32 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm placeholder-opacity-70"
            style={{ 
              minHeight: '48px',
              backgroundColor: 'transparent',
              border: 'none',
              color: 'rgba(0, 0, 0, 0.9)',
              mixBlendMode: 'normal'
            }}
          />
          <div 
            className="absolute bottom-2 right-2 text-xs" 
            style={{ color: 'rgba(0, 0, 0, 0.6)' }}
          >
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
        
        <button
          type="submit"
          disabled={!message.trim() || disabled}
          className="p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-80 backdrop-blur-sm"
          style={{
            backgroundColor: 'transparent',
            color: 'rgba(59, 130, 246, 0.9)',
            border: 'none'
          }}
        >
          <PaperAirplaneIcon className="h-5 w-5" />
        </button>
      </form>
      
      <div 
        className="mt-2 text-xs text-center" 
        style={{ color: 'rgba(0, 0, 0, 0.7)' }}
      >
        This AI assistant provides general health information only. Always consult healthcare professionals for medical advice.
      </div>
    </div>
  );
};

export default ChatInput;