// src/lib/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for generation
});

// Shots API
export const createShot = async (shotData) => {
  const response = await api.post('/api/shots/create', shotData);
  return response.data;
};

export const getShot = async (shotId) => {
  const response = await api.get(`/api/shots/${shotId}`);
  return response.data;
};

export const listShots = async () => {
  const response = await api.get('/api/shots');
  return response.data;
};

export const refineShot = async (shotId, refinementData) => {
  const response = await api.post(`/api/shots/${shotId}/refine`, refinementData);
  return response.data;
};

export const modifyParameter = async (shotId, parameterData) => {
  const response = await api.post(`/api/shots/${shotId}/modify`, parameterData);
  return response.data;
};

// Storyboards API
export const createStoryboard = async (storyboardData) => {
  const response = await api.post('/api/storyboards/create', storyboardData);
  return response.data;
};

export const getStoryboard = async (storyboardId) => {
  const response = await api.get(`/api/storyboards/${storyboardId}`);
  return response.data;
};

export const listStoryboards = async () => {
  const response = await api.get('/api/storyboards');
  return response.data;
};

// File downloads
export const getDownloadUrl = (filename) => {
  return `${API_BASE_URL}/api/download/${filename}`;
};

export const getOutputUrl = (path) => {
  return `${API_BASE_URL}/${path}`;
};

export default api;