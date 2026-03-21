import axios from 'axios';

// Use the environment variable if available (e.g., set in Vercel/Netlify), otherwise default to our live Render API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://cancer-ai-api.onrender.com';

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
