import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auth
export const auth = {
    login: (username: string, password: string) =>
        api.post('/auth/login', { username, password }),
    register: (data: any) => api.post('/auth/register', data),
};

// Dashboard
export const dashboard = {
    getStats: () => api.get('/stats/dashboard'),
};

// Error Groups
export const errorGroups = {
    list: (platform?: string, limit = 50) =>
        api.get('/error-groups', { params: { platform, limit } }),
};

// Proposals
export const proposals = {
    create: (error_group_id: number, platform: string) =>
        api.post('/proposals/create', null, { params: { error_group_id, platform } }),
    get: (id: number) => api.get(`/proposals/${id}`),
    approve: (id: number, pattern_index: number, user: string) =>
        api.post(`/proposals/${id}/approve`, { pattern_index, user }),
    reject: (id: number) => api.post(`/proposals/${id}/reject`),
};

// Apply/Rollback
export const actions = {
    apply: (proposal_id: number) => api.post(`/apply/${proposal_id}`),
    rollback: (rule_id: number) => api.post(`/rollback/${rule_id}`),
};

// Validation
export const validation = {
    getReport: (proposal_id: number) => api.get(`/validation/${proposal_id}`),
};

// SIEM Connectors
export const connectors = {
    test: (connector_id: number) => api.post(`/connectors/test`, { connector_id }),
};

export default api;
