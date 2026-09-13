// src/components/StudentDashboard.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { getProfile } from '../services/authService';
import FeedbackModal from './FeedbackModal';
import PeerMatchRequest from './PeerMatchRequest';

const StudentDashboard = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modal State for submitting session feedback
  const [selectedSessionForFeedback, setSelectedSessionForFeedback] = useState(null);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  // Active view tab state within dashboard: 'overview' | 'match'
  const [activeTab, setActiveTab] = useState('overview');

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [profileData, matchesRes, sessionsRes] = await Promise.all([
        getProfile(),
        api.get('/matching/matches/'),
        api.get('/matching/sessions/'),
      ]);

      setProfile(profileData);
      setMatches(matchesRes.data);
      setSessions(sessionsRes.data);
    } catch (err) {
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleOpenFeedback = (session) => {
    setSelectedSessionForFeedback(session);
    setIsFeedbackOpen(true);
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem' }}>Loading Student Dashboard...</div>;
  }

  return (
    <div style={{ maxWidth: '1000px', margin: '2rem auto', padding: '0 1rem' }}>
      {/* Header Banner */}
      <header style={{
        backgroundColor: '#2b6cb0',
        color: '#fff',
        padding: '1.5rem 2rem',
        borderRadius: '8px',
        marginBottom: '2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '1.75rem' }}>
            Welcome back, {profile?.user?.full_name || profile?.user?.email || 'Student'}!
          </h1>
          <p style={{ margin: '0.5rem 0 0 0', opacity: 0.9, fontSize: '0.95rem' }}>
            {profile?.program ? `${profile.program} (Year ${profile.year_of_study})` : 'Student Portal'}
          </p>
        </div>
        <div>
          <button
            onClick={() => navigate('/availability')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#ffffff',
              color: '#2b6cb0',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 'bold',
              cursor: 'pointer',
              marginRight: '0.5rem'
            }}
          >
            Availability Grid
          </button>
          <button
            onClick={() => navigate('/assessment')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#ebf8ff',
              color: '#2b6cb0',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            Self Assessments
          </button>
        </div>
      </header>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: '#fff5f5', color: '#c53030', borderRadius: '6px', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '2px solid #e2e8f0', marginBottom: '1.5rem' }}>
        <button
          onClick={() => setActiveTab('overview')}
          style={{
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderBottom: activeTab === 'overview' ? '3px solid #3182ce' : 'none',
            backgroundColor: 'transparent',
            fontWeight: activeTab === 'overview' ? 'bold' : 'normal',
            color: activeTab === 'overview' ? '#3182ce' : '#4a5568',
            cursor: 'pointer',
            fontSize: '1rem'
          }}
        >
          Dashboard Overview
        </button>
        <button
          onClick={() => setActiveTab('match')}
          style={{
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderBottom: activeTab === 'match' ? '3px solid #3182ce' : 'none',
            backgroundColor: 'transparent',
            fontWeight: activeTab === 'match' ? 'bold' : 'normal',
            color: activeTab === 'match' ? '#3182ce' : '#4a5568',
            cursor: 'pointer',
            fontSize: '1rem'
          }}
        >
          Find AI Peer Match
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'match' ? (
        <PeerMatchRequest />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          {/* Active Peer Matches */}
          <div style={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0, color: '#2d3748' }}>🤝 Active Peer Matches</h3>
            {matches.length === 0 ? (
              <p style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
                No active matches yet. Click "Find AI Peer Match" above to request a study partner!
              </p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {matches.map((m) => (
                  <li key={m.id} style={{ padding: '0.75rem 0', borderBottom: '1px solid #edf2f7' }}>
                    <div style={{ fontWeight: 'bold', color: '#2b6cb0' }}>Match #{m.id}</div>
                    <div style={{ fontSize: '0.85rem', color: '#718096' }}>
                      Relevance Score: {(m.relevance_score * 100).toFixed(0)}%
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Group Study Sessions (AI-matched) */}
          <div style={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0, color: '#2d3748' }}>📅 Group Study Sessions</h3>
            {sessions.length === 0 ? (
              <p style={{ color: '#a0aec0', fontSize: '0.9rem' }}>No group study sessions scheduled yet.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {sessions.map((s) => {
                  const otherNames = (s.participants || [])
                    .filter((p) => p.email !== profile?.user?.email)
                    .map((p) => p.full_name || p.email)
                    .join(', ');
                  return (
                    <li key={s.id} style={{ padding: '0.75rem 0', borderBottom: '1px solid #edf2f7', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 'bold' }}>{otherNames || 'Group Study Session'}</div>
                        <div style={{ fontSize: '0.8rem', color: '#718096' }}>
                          {new Date(s.scheduled_time).toLocaleString()} · {s.status}
                        </div>
                      </div>
                      {s.status === 'completed' && (
                        <button
                          onClick={() => handleOpenFeedback(s)}
                          style={{
                            padding: '0.35rem 0.75rem',
                            fontSize: '0.8rem',
                            backgroundColor: '#edf2f7',
                            border: '1px solid #cbd5e0',
                            borderRadius: '4px',
                            cursor: 'pointer'
                          }}
                        >
                          Rate
                        </button>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      )}

      {/* Feedback Modal Trigger */}
      <FeedbackModal
        session={selectedSessionForFeedback}
        isOpen={isFeedbackOpen}
        onClose={() => setIsFeedbackOpen(false)}
        onFeedbackSubmitted={() => {
          fetchDashboardData();
        }}
      />
    </div>
  );
};

export default StudentDashboard;