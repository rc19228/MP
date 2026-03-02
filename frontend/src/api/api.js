import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
let statsEndpointAvailable = true;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const askQuery = async (query) => {
  const response = await api.post('/query', { question: query });
  return response.data;
};

export const getStats = async () => {
  if (statsEndpointAvailable) {
    try {
      const response = await api.get('/stats');
      return response.data;
    } catch (error) {
      if (error?.response?.status !== 404) {
        throw error;
      }
      statsEndpointAvailable = false;
    }
  }

  const [healthResult, historyResult] = await Promise.allSettled([
    api.get('/health'),
    api.get('/history'),
  ]);

  const healthData = healthResult.status === 'fulfilled' ? healthResult.value.data : {};
  const historyData = historyResult.status === 'fulfilled' ? historyResult.value.data : {};
  const historyItems = Array.isArray(historyData.history) ? historyData.history : [];
  const queriesProcessed = typeof historyData.count === 'number' ? historyData.count : historyItems.length;
  const avgResponseTime = queriesProcessed
    ? historyItems.reduce((sum, item) => sum + (item?.response_time || 0), 0) / queriesProcessed
    : 0;

  return {
    total_documents: 0,
    total_chunks: healthData.documents_indexed || 0,
    queries_processed: queriesProcessed,
    avg_response_time: Number(avgResponseTime.toFixed(2)),
    status: 'fallback',
  };
};

export default api;
