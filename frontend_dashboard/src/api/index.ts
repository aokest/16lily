// src/api/index.ts
import axios from 'axios';

// Determine API Base URL
const getApiBase = () => {
    // In dev mode (Vite proxy), use relative path to trigger proxy
    if (import.meta.env.DEV) {
        return '/api'; // Append /api to match the vite proxy rule
    }
    // In production, assume same domain or specify env var
    return import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';
};

const api = axios.create({
    baseURL: getApiBase(),
    timeout: 10000,
});

// Add Token for requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    } else {
        // Fallback for Dashboard public access (if needed) or remove it
        // The dashboard currently relies on AllowAny in backend, so no token is fine for dashboard stats.
        // But for CRM it will need token.
    }
    return config;
});

export const fetchStats = (params: any) => api.get('dashboard/stats/', { params });
export const fetchActivities = () => api.get('dashboard/activities/');

export default api;
