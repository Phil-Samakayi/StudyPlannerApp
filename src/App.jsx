// src/App.jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';

import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';

import StudentDashboard from './components/StudentDashboard';
import AvailabilityGrid from './components/AvailabilityGrid';
import SelfAssessmentForm from './components/SelfAssessmentForm';
import PeerMatchRequest from './components/PeerMatchRequest';
import { login } from './services/authService';

const LoginPage = ({ setIsAuthenticated }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      setIsAuthenticated(true);
      navigate('/dashboard');
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Login failed. Please check your email and password.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '4rem auto', padding: '2rem', border: '1px solid #e2e8f0', borderRadius: '8px', backgroundColor: '#fff' }}>
      <h2>Student Login</h2>
      {error && (
        <div style={{ padding: '0.75rem', backgroundColor: '#fff5f5', color: '#c53030', border: '1px solid #feb2b2', borderRadius: '4px', marginBottom: '1rem', fontSize: '0.9rem' }}>
          {error}
        </div>
      )}
      <form onSubmit={handleLogin}>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>Email Address</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #cbd5e0' }}
          />
        </div>
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #cbd5e0' }}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          style={{ width: '100%', padding: '0.75rem', backgroundColor: loading ? '#a0aec0' : '#3182ce', color: '#fff', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          {loading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if token exists in localStorage on startup
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  return (
    <Router>
      <div style={{ minHeight: '100vh', backgroundColor: '#f7fafc', fontFamily: 'Arial, sans-serif' }}>
        <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />

        <main style={{ paddingBottom: '3rem' }}>
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={
                isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage setIsAuthenticated={setIsAuthenticated} />
              }
            />

            {/* Protected Student Routes */}
            <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<StudentDashboard />} />
              <Route path="/availability" element={<AvailabilityGrid />} />
              <Route path="/assessment" element={<SelfAssessmentForm />} />
              <Route path="/match" element={<PeerMatchRequest />} />
            </Route>

            {/* Fallback Route */}
            <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;