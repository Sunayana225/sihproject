import { ChatResponse } from '../types/chat';

class ChatService {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async sendMessage(content: string, sessionId?: string): Promise<ChatResponse> {
    try {
      // Get auth token
      const token = await this.getAuthToken();
      
      const response = await this.makeRequest<ChatResponse>('/chat/message', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          content,
          role: 'user',
          session_id: sessionId,
        }),
      });

      return response;
    } catch (error) {
      console.error('Chat service error:', error);
      throw error;
    }
  }

  async validateQuery(content: string): Promise<{
    is_health_related: boolean;
    confidence: number;
    reason: string;
    rejection_message?: string;
  }> {
    try {
      const token = await this.getAuthToken();
      
      return await this.makeRequest('/chat/validate-query', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          content,
          role: 'user',
        }),
      });
    } catch (error) {
      console.error('Query validation error:', error);
      throw error;
    }
  }

  async checkChatHealth(): Promise<{
    status: string;
    services: Record<string, string>;
  }> {
    try {
      return await this.makeRequest('/chat/health-check');
    } catch (error) {
      console.error('Chat health check error:', error);
      throw error;
    }
  }

  private async getAuthToken(): Promise<string> {
    // This will be implemented to get the Firebase ID token
    // For now, we'll use a placeholder
    const { authService } = await import('./authService');
    const token = await authService.getIdToken();
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    return token;
  }
}

export const chatService = new ChatService();