import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  register: async (userData: { email: string; password: string; name: string }) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
  },
};

export const documentService = {
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  list: async () => {
    const response = await api.get('/documents');
    return response.data;
  },
  getById: async (id: string) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },
};

export const taxService = {
  analyze: async (documentId: string) => {
    const response = await api.post(`/tax/analyze/${documentId}`);
    return response.data;
  },
  validate: async (data: any) => {
    const response = await api.post('/tax/validate', data);
    return response.data;
  },
  submit: async (data: any) => {
    const response = await api.post('/tax/submit', data);
    return response.data;
  },
};

export default api; 