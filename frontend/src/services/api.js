import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL.replace(/\/+$/, '')}/api`
  : '/api';

export const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

export async function fetchHealth() {
  const url = import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL.replace(/\/+$/, '')}/health`
    : '/health';
  const { data } = await axios.get(url, { timeout: 10000 });
  return data;
}

export async function fetchMatches() {
  const { data } = await api.get('/matches');
  return data;
}

export async function fetchPredictions() {
  const { data } = await api.get('/predictions');
  return data;
}

export async function createPrediction(payload) {
  const { data } = await api.post('/predictions', payload);
  return data;
}
