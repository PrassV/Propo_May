import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { supabase } from '../lib/supabase';

// Create a base API instance
const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api: AxiosInstance = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the auth token
api.interceptors.request.use(
  async (config) => {
    const session = await supabase.auth.getSession();
    const token = session?.data?.session?.access_token;
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If the error is due to an expired token (401) and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt to refresh the token
        const { error: refreshError } = await supabase.auth.refreshSession();
        
        if (refreshError) {
          // If refresh fails, redirect to login
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Retry the original request with the new token
        const session = await supabase.auth.getSession();
        const token = session?.data?.session?.access_token;
        
        if (token) {
          originalRequest.headers.Authorization = `Bearer ${token}`;
        }
        
        return api(originalRequest);
      } catch (refreshError) {
        console.error('Error refreshing token:', refreshError);
        // Redirect to login
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

// Type-safe wrapper methods
const apiService = {
  get: <T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return api.get<T>(url, config);
  },
  
  post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return api.post<T>(url, data, config);
  },
  
  put: <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return api.put<T>(url, data, config);
  },
  
  patch: <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return api.patch<T>(url, data, config);
  },
  
  delete: <T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return api.delete<T>(url, config);
  },
};

export default apiService; 