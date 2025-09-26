import { authService } from './authService';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ApiService {
  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = await authService.getIdToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  // Authentication endpoints
  async verifyToken(): Promise<{ valid: boolean; uid: string; email: string }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/auth/verify`, {
      method: 'POST',
      headers,
    });
    return this.handleResponse(response);
  }

  async getCurrentUser(): Promise<any> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: 'GET',
      headers,
    });
    return this.handleResponse(response);
  }

  async getAuthStatus(): Promise<{ authenticated: boolean; user?: any }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/auth/status`, {
      method: 'GET',
      headers,
    });
    return this.handleResponse(response);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
    return this.handleResponse(response);
  }
}

export const apiService = new ApiService();