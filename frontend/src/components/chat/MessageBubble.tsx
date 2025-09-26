import React, { useState, useRef } from 'react';
import { ClipboardIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { CheckIcon } from '@heroicons/react/24/solid';
import { Message } from '../../types/chat';
import { useAdaptiveColors } from '../../utils/colorUtils';

interface MessageBubbleProps {
  message: Message;
  onRegenerate?: () => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onRegenerate }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const bubbleRef = useRef<HTMLDivElement>(null);
  const colors = useAdaptiveColors(bubbleRef);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy message:', error);
    }
  };

  const formatTime = (timestamp: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).format(timestamp);
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`} ref={bubbleRef}>
      <div className={`max-w-3xl ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className="px-4 py-3 rounded-lg"
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            color: isUser ? 'rgba(255, 255, 255, 0.95)' : 'rgba(0, 0, 0, 0.9)',
            mixBlendMode: 'normal'
          }}
        >
          {message.isTyping ? (
            <div className="flex items-center space-x-1">
              <div className="flex space-x-1">
                <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}></div>
                <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-sm ml-2" style={{ color: 'rgba(0, 0, 0, 0.6)' }}>AI is typing...</span>
            </div>
          ) : (
            <div className="whitespace-pre-wrap">{message.content}</div>
          )}
        </div>
        
        <div className={`flex items-center mt-1 space-x-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span className="text-xs" style={{ color: 'rgba(0, 0, 0, 0.6)' }}>
            {formatTime(message.timestamp)}
          </span>
          
          {!message.isTyping && (
            <div className="flex items-center space-x-1">
              <button
                onClick={handleCopy}
                className="p-1 rounded hover:opacity-70 transition-opacity"
                title="Copy message"
                style={{ color: 'rgba(0, 0, 0, 0.6)' }}
              >
                {copied ? (
                  <CheckIcon className="h-4 w-4" style={{ color: 'rgba(34, 197, 94, 0.8)' }} />
                ) : (
                  <ClipboardIcon className="h-4 w-4" />
                )}
              </button>
              
              {!isUser && onRegenerate && (
                <button
                  onClick={onRegenerate}
                  className="p-1 rounded hover:opacity-70 transition-opacity"
                  title="Regenerate response"
                  style={{ color: 'rgba(0, 0, 0, 0.6)' }}
                >
                  <ArrowPathIcon className="h-4 w-4" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;