// src/services/matchService.js
import api from './api';

export const requestMatch = async (subjectId) => {
  const response = await api.post('/matching/matches/request-match/', {
    subject_id: subjectId,
  });
  return response.data;
};

export const getMyMatches = async () => {
  const response = await api.get('/matching/matches/');
  return response.data;
};

export const submitFeedback = async (sessionId, rating, comment) => {
  const response = await api.post('/matching/feedback/', {
    session: sessionId,
    rating,
    comment,
  });
  return response.data;
};

export const getFeedbackMetrics = async () => {
  const response = await api.get('/matching/feedback/metrics/');
  return response.data;
};

export const scheduleSession = async (matchId, scheduledTime) => {
  const response = await api.post('/matching/sessions/', {
    match: matchId,
    scheduled_time: scheduledTime,
  });
  return response.data;
};

export const getMySessions = async () => {
  const response = await api.get('/matching/sessions/');
  return response.data;
};

export const completeSession = async (sessionId) => {
  const response = await api.post(`/matching/sessions/${sessionId}/complete/`);
  return response.data;
};
