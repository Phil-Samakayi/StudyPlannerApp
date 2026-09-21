// src/services/scheduleService.js
// Calls against the `scheduling` app's own endpoints. Kept separate from
// matchService.js (which wraps the `matching` app) so scheduling-owned
// resources -- slots, sessions, subject goals -- have one home instead of
// growing inside a file named after a different app.
import api from './api';

export const getMyGoals = async () => {
  const response = await api.get('/scheduling/goals/');
  return response.data;
};

export const createGoal = async ({ subject, description, target_date }) => {
  const response = await api.post('/scheduling/goals/', {
    subject,
    description,
    target_date,
  });
  return response.data;
};

export const deleteGoal = async (goalId) => {
  await api.delete(`/scheduling/goals/${goalId}/`);
};

export const markGoalAchieved = async (goalId) => {
  const response = await api.post(`/scheduling/goals/${goalId}/mark-achieved/`);
  return response.data;
};
