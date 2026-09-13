// src/components/PeerMatchRequest.jsx
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { requestMatch } from '../services/matchService';

const PeerMatchRequest = ({ onMatchCreated }) => {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [matchResult, setMatchResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [infoMessage, setInfoMessage] = useState(null);

  useEffect(() => {
    // Load enrolled subjects
    api.get('/subjects/')
      .then((res) => setSubjects(res.data))
      .catch((err) => setError('Failed to load course catalog.'));
  }, []);

  const handleMatchRequest = async (e) => {
    e.preventDefault();
    if (!selectedSubject) return;

    setLoading(true);
    setError(null);
    setInfoMessage(null);
    setMatchResult(null);

    try {
      const data = await requestMatch(selectedSubject);
      // A real match is a 201 with a Match object (has an id). "No candidates
      // found" comes back as a 200 with just {"detail": "..."} -- treat that
      // as informational, not as a match to render.
      if (data && data.id) {
        setMatchResult(data);
        // The dashboard's own "Active Peer Matches" list only fetches on
        // mount, so it won't otherwise pick up a match created here.
        onMatchCreated && onMatchCreated();
      } else {
        setInfoMessage(data?.detail || 'No candidate study peers found for this subject yet.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'No candidate study peers found.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', padding: '1.5rem', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Find a Study Partner (AI Peer Matcher)</h2>
      
      <form onSubmit={handleMatchRequest}>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Select Subject:
          </label>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            style={{ width: '100%', padding: '0.5rem' }}
            required
          >
            <option value="">-- Choose a Course --</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.code} - {s.name}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={loading || !selectedSubject}
          style={{ padding: '0.75rem 1.5rem', backgroundColor: '#007bff', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          {loading ? 'Finding Match...' : 'Find Matching Peer'}
        </button>
      </form>

      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}

      {infoMessage && (
        <p style={{ color: '#4a5568', marginTop: '1rem', padding: '0.75rem', backgroundColor: '#f7fafc', border: '1px solid #e2e8f0', borderRadius: '4px' }}>
          {infoMessage}
        </p>
      )}

      {matchResult && (
        <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#e9f5ff', borderRadius: '6px' }}>
          <h3>Match Found! 🎉</h3>
          <p><strong>Match ID:</strong> #{matchResult.id}</p>
          <p><strong>Relevance Score:</strong> {(matchResult.relevance_score * 100).toFixed(0)}%</p>
          <h4>Participants:</h4>
          <ul>
            {matchResult.participants?.map((p) => (
              <li key={p.id}>{p.full_name || p.student_email}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PeerMatchRequest;