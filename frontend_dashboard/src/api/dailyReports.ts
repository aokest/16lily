// src/api/dailyReports.ts
import api from './index';

export const getDailyReports = (params?: any) => api.get('daily-reports/', { params });

export const getDailyReport = (id: number) => api.get(`daily-reports/${id}/`);

export const createDailyReport = (data: any) => api.post('daily-reports/', data);

export const updateDailyReport = (id: number, data: any) => api.patch(`daily-reports/${id}/`, data);

export const deleteDailyReport = (id: number) => api.delete(`daily-reports/${id}/`);

export const polishDailyReport = (id: number) => api.post(`daily-reports/${id}/polish/`);
