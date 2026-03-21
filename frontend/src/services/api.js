import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // FastAPI default

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = () => api.get('/health');

export const predictAll = (data) => api.post('/predict/all', data);

export const getSimilarPatients = (caseId) => api.post('/similar-patients', { case_id: caseId });

export default api;
