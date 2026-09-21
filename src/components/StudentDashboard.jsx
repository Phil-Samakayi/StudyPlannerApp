// src/components/StudentDashboard.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { getProfile } from '../services/authService';
import FeedbackModal from './FeedbackModal';
import PeerMatchRequest from './PeerMatchRequest';
import SubjectGoals from './SubjectGoals';
import { scheduleSession, completeSession, cancelSession } from '../services/matchService';

// Lets a student pick a time and turn one of their Matches into a
// scheduled GroupStudySession. Each row owns its own input state, so this
// lives outside the list `.map()` as its own component.
const ScheduleSessionForm = ({ matchId, onScheduled }) => {
  const [scheduledTime, setScheduledTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSchedule = async () => {
    if (!scheduledTime) return;
    setLoading(true);
    setError(null);
    try {
      await scheduleSession(matchId, new Date(scheduledTime).toISOString());
      onScheduled();
    } catch (err) {
      const data = err.response?.data;
      const detail = data?.scheduled_time?.[0] || data?.match?.[0] || data?.detail || 'Could not schedule session.';
      setError(String(detail));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: '0.5rem' }}>
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <input
          type="datetime-local"
          value={scheduledTime}
          onChange={(e) => setScheduledTime(e.target.value)}
          style={{ padding: '0.3rem', fontSize: '0.8rem', borderRadius: '4px', border: '1px solid #cbd5e0' }}
        />
        <button
          onClick={handleSchedule}
          disabled={loading || !scheduledTime}
          style={{
            padding: '0.3rem 0.75rem',
            fontSize: '0.8rem',
            backgroundColor: loading || !scheduledTime ? '#a0aec0' : '#38a169',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: loading || !scheduledTime ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Scheduling...' : 'Schedule Session'}
        </button>
      </div>
      {error && <div style={{ color: '#c53030', fontSize: '0.75rem', marginTop: '0.25rem' }}>{error}</div>}
    </div>
  );
};

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

  // Active view tab state within dashboard: 'overview' | 'match' | 'goals'
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

  // Refetches just matches/sessions without touching `loading` -- flipping
  // `loading` unmounts the whole tab content (including PeerMatchRequest
  // and its just-created match result, or the feedback modal), so this is
  // what every post-action refresh below uses instead of fetchDashboardData.
  const refreshMatchesAndSessions = async () => {
    try {
      const [matchesRes, sessionsRes] = await Promise.all([
        api.get('/matching/matches/'),
        api.get('/matching/sessions/'),
      ]);
      setMatches(matchesRes.data);
      setSessions(sessionsRes.data);
    } catch (err) {
      setError('Failed to refresh matches and sessions.');
    }
  };

  const handleOpenFeedback = (session) => {
    setSelectedSessionForFeedback(session);
    setIsFeedbackOpen(true);
  };

  const handleCompleteSession = async (sessionId) => {
    try {
      await completeSession(sessionId);
      refreshMatchesAndSessions();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to mark session as completed.';
      setError(String(detail));
    }
  };

  const handleCancelSession = async (sessionId) => {
    if (!window.confirm('Cancel this GroupStudy session?')) return;
    try {
      await cancelSession(sessionId);
      refreshMatchesAndSessions();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to cancel session.';
      setError(String(detail));
    }
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
        <button
          onClick={() => setActiveTab('goals')}
          style={{
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderBottom: activeTab === 'goals' ? '3px solid #3182ce' : 'none',
            backgroundColor: 'transparent',
            fontWeight: activeTab === 'goals' ? 'bold' : 'normal',
            color: activeTab === 'goals' ? '#3182ce' : '#4a5568',
            cursor: 'pointer',
            fontSize: '1rem'
          }}
        >
          My Goals
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'match' ? (
        <PeerMatchRequest onMatchCreated={refreshMatchesAndSessions} />
      ) : activeTab === 'goals' ? (
        <SubjectGoals />
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
                {matches.map((m) => {
                  const existingSession = sessions.find((s) => s.match === m.id);
                  return (
                    <li key={m.id} style={{ padding: '0.75rem 0', borderBottom: '1px solid #edf2f7' }}>
                      <div style={{ fontWeight: 'bold', color: '#2b6cb0' }}>Match #{m.id}</div>
                      <div style={{ fontSize: '0.85rem', color: '#718096' }}>
                        Relevance Score: {(m.relevance_score * 100).toFixed(0)}%
                      </div>
                      {existingSession ? (
                        <div style={{ fontSize: '0.8rem', color: '#718096', marginTop: '0.25rem' }}>
                          Session {existingSession.status} for {new Date(existingSession.scheduled_time).toLocaleString()}
                        </div>
                      ) : (
                        <ScheduleSessionForm matchId={m.id} onScheduled={refreshMatchesAndSessions} />
                      )}
                    </li>
                  );
                })}
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
                      {s.status === 'scheduled' && (
                        <div style={{ display: 'flex', gap: '0.4rem' }}>
                          <button
                            onClick={() => handleCompleteSession(s.id)}
                            style={{
                              padding: '0.35rem 0.75rem',
                              fontSize: '0.8rem',
                              backgroundColor: '#38a169',
                              color: '#fff',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}
                          >
                            Mark Complete
                          </button>
                          <button
                            onClick={() => handleCancelSession(s.id)}
                            style={{
                              padding: '0.35rem 0.75rem',
                              fontSize: '0.8rem',
                              backgroundColor: '#fff5f5',
                              color: '#c53030',
                              border: '1px solid #feb2b2',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}
                          >
                            Cancel
                          </button>
                        </div>
                      )}
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
          refreshMatchesAndSessions();
        }}
      />
    </div>
  );
};

export default StudentDashboard;
