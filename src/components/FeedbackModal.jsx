// src/components/FeedbackModal.jsx
import React, { useState } from 'react';
import api from '../services/api';

const FeedbackModal = ({ session, isOpen, onClose, onFeedbackSubmitted }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen || !session) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await api.post('/matching/feedback/', {
        session: session.id,
        rating: parseInt(rating, 10),
        comment: comment.trim(),
      });

      if (onFeedbackSubmitted) {
        onFeedbackSubmitted();
      }
      onClose();
    } catch (err) {
      const errDetail = err.response?.data?.detail || 
                        err.response?.data?.non_field_errors?.[0] || 
                        'Failed to submit feedback.';
      setError(String(errDetail));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: '#ffffff',
        padding: '2rem',
        borderRadius: '8px',
        width: '100%',
        maxWidth: '500px',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
      }}>
        <h3 style={{ marginTop: 0, color: '#1a202c' }}>
          Session Feedback #{session.id}
        </h3>
        <p style={{ color: '#4a5568', fontSize: '0.9rem' }}>
          Please rate how helpful this study session was in improving your understanding.
        </p>

        {error && (
          <div style={{
            padding: '0.75rem',
            backgroundColor: '#fff5f5',
            color: '#c53030',
            border: '1px solid #feb2b2',
            borderRadius: '4px',
            marginBottom: '1rem',
            fontSize: '0.9rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Star Rating / Score Input */}
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#2d3748' }}>
              Rating (1 = Poor, 5 = Excellent):
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  type="button"
                  key={star}
                  onClick={() => setRating(star)}
                  style={{
                    flex: 1,
                    padding: '0.6rem 0',
                    border: '1px solid #cbd5e0',
                    borderRadius: '4px',
                    backgroundColor: rating >= star ? '#ecc94b' : '#edf2f7',
                    color: rating >= star ? '#744210' : '#718096',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    fontSize: '1rem'
                  }}
                >
                  ★ {star}
                </button>
              ))}
            </div>
          </div>

          {/* Comment Field */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#2d3748' }}>
              Comments (Optional):
            </label>
            <textarea
              rows="4"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Was your match helpful? Any suggestions for improvement?"
              style={{
                width: '100%',
                padding: '0.6rem',
                borderRadius: '4px',
                border: '1px solid #cbd5e0',
                boxSizing: 'border-box',
                fontSize: '0.95rem'
              }}
            />
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              style={{
                padding: '0.6rem 1.25rem',
                border: '1px solid #cbd5e0',
                backgroundColor: '#fff',
                borderRadius: '4px',
                cursor: 'pointer',
                color: '#4a5568'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '0.6rem 1.25rem',
                border: 'none',
                backgroundColor: loading ? '#a0aec0' : '#3182ce',
                color: '#fff',
                fontWeight: 'bold',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FeedbackModal;