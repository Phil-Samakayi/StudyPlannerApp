// src/services/authService.js
import api from './api';

export const login = async (email, password) => {
  const response = await api.post('/auth/token/', { email, password });
  if (response.data.access) {
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
  }
  return response.data;
};

export const register = async (userData) => {
  const response = await api.post('/accounts/register/', userData);
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
};

export const getProfile = async () => {
  const response = await api.get('/accounts/profile/');
  return response.data;
};