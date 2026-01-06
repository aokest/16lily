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
    timeout: 60000,
});

// Add Token for requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

/**
 * 响应拦截器：统一处理未授权（401）与禁止访问（403）
 * 清除本地令牌并跳转登录页，避免页面长时间空白或重复失败
 */
// Handle Response Errors (e.g., 401/403)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const status = error?.response?.status;
        if (status === 401 || status === 403) {
            // Clear token and redirect to login for unauthorized/forbidden
            localStorage.removeItem('auth_token');
            if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export const fetchStats = (params: any) => api.get('dashboard/stats/', { params });
export const fetchActivities = () => api.get('dashboard/activities/');

export default api;

export const fetchPerformanceReport = (params: any) => api.get('reports/performance/', { params });
