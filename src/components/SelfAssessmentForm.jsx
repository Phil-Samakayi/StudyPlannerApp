// src/components/SelfAssessmentForm.jsx
import React, { useState, useEffect } from 'react';
import api from '../services/api';

const SelfAssessmentForm = ({ onAssessmentSaved }) => {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [strengthScore, setStrengthScore] = useState(3);
  const [weaknessScore, setWeaknessScore] = useState(3);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    // Fetch available course subjects from API
    api.get('/subjects/')
      .then((res) => setSubjects(res.data))
      .catch(() => setMessage({ type: 'error', text: 'Failed to load course subjects.' }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedSubject) {
      setMessage({ type: 'error', text: 'Please select a subject.' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const payload = {
        subject: parseInt(selectedSubject, 10),
        strength_score: parseInt(strengthScore, 10),
        weakness_score: parseInt(weaknessScore, 10),
      };

      await api.post('/assessments/', payload);

      setMessage({ type: 'success', text: 'Self-assessment submitted successfully!' });
      
      if (onAssessmentSaved) {
        onAssessmentSaved();
      }
    } catch (err) {
      const errorDetail = err.response?.data?.detail 
        || Object.values(err.response?.data || {})[0] 
        || 'Failed to submit self-assessment.';
      setMessage({ type: 'error', text: String(errorDetail) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: '600px',
      margin: '2rem auto',
      padding: '2rem',
      backgroundColor: '#ffffff',
      borderRadius: '8px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      border: '1px solid #e2e8f0'
    }}>
      <h2 style={{ marginTop: 0, color: '#1a202c' }}>Subject Self-Assessment</h2>
      <p style={{ color: '#718096', fontSize: '0.95rem' }}>
        Rate your understanding on a scale of 1 to 5 for each subject.
        These ratings are used by the AI matcher to pair you with complementary study partners.
      </p>

      {message.text && (
        <div style={{
          padding: '0.75rem 1rem',
          borderRadius: '4px',
          marginBottom: '1rem',
          backgroundColor: message.type === 'error' ? '#fff5f5' : '#f0fff4',
          color: message.type === 'error' ? '#c53030' : '#276749',
          border: `1px solid ${message.type === 'error' ? '#feb2b2' : '#9ae6b4'}`
        }}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Subject Dropdown */}
        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#2d3748' }}>
            Select Subject:
          </label>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            style={{
              width: '100%',
              padding: '0.6rem',
              borderRadius: '4px',
              border: '1px solid #cbd5e0',
              fontSize: '1rem'
            }}
            required
          >
            <option value="">-- Select Course --</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.code} - {s.name}
              </option>
            ))}
          </select>
        </div>

        {/* Strength Rating (1-5) */}
        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.25rem', color: '#2d3748' }}>
            Strength Score (1 - Weak to 5 - Mastered): <span style={{ color: '#3182ce' }}>{strengthScore}</span>
          </label>
          <input
            type="range"
            min="1"
            max="5"
            value={strengthScore}
            onChange={(e) => setStrengthScore(e.target.value)}
            style={{ width: '100%', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#a0aec0' }}>
            <span>1 (Beginner)</span>
            <span>3 (Intermediate)</span>
            <span>5 (Expert)</span>
          </div>
        </div>

        {/* Weakness Rating (1-5) */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.25rem', color: '#2d3748' }}>
            Need for Support / Weakness (1 - None to 5 - High): <span style={{ color: '#e53e3e' }}>{weaknessScore}</span>
          </label>
          <input
            type="range"
            min="1"
            max="5"
            value={weaknessScore}
            onChange={(e) => setWeaknessScore(e.target.value)}
            style={{ width: '100%', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#a0aec0' }}>
            <span>1 (No help needed)</span>
            <span>3 (Moderate support)</span>
            <span>5 (Urgent help needed)</span>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !selectedSubject}
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: loading || !selectedSubject ? '#a0aec0' : '#3182ce',
            color: '#ffffff',
            fontWeight: 'bold',
            border: 'none',
            borderRadius: '4px',
            cursor: loading || !selectedSubject ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
            transition: 'background-color 0.2s'
          }}
        >
          {loading ? 'Saving Assessment...' : 'Save Self-Assessment'}
        </button>
      </form>
    </div>
  );
};

export default SelfAssessmentForm;