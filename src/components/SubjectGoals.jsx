// src/components/SubjectGoals.jsx
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { getMyGoals, createGoal, deleteGoal, markGoalAchieved } from '../services/scheduleService';

const todayISO = () => new Date().toISOString().slice(0, 10);

const NewGoalForm = ({ subjects, onCreated }) => {
  const [subjectId, setSubjectId] = useState('');
  const [description, setDescription] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!subjectId || !description.trim() || !targetDate) return;
    setLoading(true);
    setError(null);
    try {
      await createGoal({ subject: subjectId, description: description.trim(), target_date: targetDate });
      setDescription('');
      setTargetDate('');
      setSubjectId('');
      onCreated();
    } catch (err) {
      const data = err.response?.data;
      const detail =
        data?.description?.[0] || data?.target_date?.[0] || data?.subject?.[0] || data?.detail ||
        'Could not create goal.';
      setError(String(detail));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        display: 'flex',
        gap: '0.5rem',
        flexWrap: 'wrap',
        alignItems: 'center',
        marginBottom: '1.25rem',
        padding: '1rem',
        backgroundColor: '#f7fafc',
        borderRadius: '6px',
        border: '1px solid #e2e8f0',
      }}
    >
      <select
        value={subjectId}
        onChange={(e) => setSubjectId(e.target.value)}
        required
        style={{ padding: '0.4rem', fontSize: '0.85rem', borderRadius: '4px', border: '1px solid #cbd5e0' }}
      >
        <option value="">Subject...</option>
        {subjects.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>
      <input
        type="text"
        placeholder="What are you aiming to achieve?"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
        style={{ flex: 1, minWidth: '200px', padding: '0.4rem', fontSize: '0.85rem', borderRadius: '4px', border: '1px solid #cbd5e0' }}
      />
      <input
        type="date"
        value={targetDate}
        min={todayISO()}
        onChange={(e) => setTargetDate(e.target.value)}
        required
        style={{ padding: '0.4rem', fontSize: '0.85rem', borderRadius: '4px', border: '1px solid #cbd5e0' }}
      />
      <button
        type="submit"
        disabled={loading}
        style={{
          padding: '0.4rem 1rem',
          fontSize: '0.85rem',
          backgroundColor: loading ? '#a0aec0' : '#2b6cb0',
          color: '#fff',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontWeight: 'bold',
        }}
      >
        {loading ? 'Adding...' : 'Add Goal'}
      </button>
      {error && <div style={{ width: '100%', color: '#c53030', fontSize: '0.75rem' }}>{error}</div>}
    </form>
  );
};

const GoalRow = ({ goal, onChanged }) => {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const overdue = !goal.achieved && goal.target_date < todayISO();

  const handleMarkAchieved = async () => {
    setBusy(true);
    setError(null);
    try {
      await markGoalAchieved(goal.id);
      onChanged();
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update goal.');
    } finally {
      setBusy(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this goal? This cannot be undone.')) return;
    setBusy(true);
    setError(null);
    try {
      await deleteGoal(goal.id);
      onChanged();
    } catch (err) {
      setError('Could not delete goal.');
      setBusy(false);
    }
  };

  return (
    <li style={{ padding: '0.75rem 0', borderBottom: '1px solid #edf2f7', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.75rem' }}>
      <div>
        <div style={{ fontWeight: 'bold', color: '#2b6cb0' }}>{goal.subject_name}</div>
        <div style={{ fontSize: '0.85rem', color: '#2d3748' }}>{goal.description}</div>
        <div style={{ fontSize: '0.75rem', marginTop: '0.15rem', color: overdue ? '#c53030' : '#718096' }}>
          {goal.achieved ? '✓ Achieved' : overdue ? `Overdue since ${goal.target_date}` : `Target: ${goal.target_date}`}
        </div>
        {error && <div style={{ color: '#c53030', fontSize: '0.7rem', marginTop: '0.15rem' }}>{error}</div>}
      </div>
      <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
        {!goal.achieved && (
          <button
            onClick={handleMarkAchieved}
            disabled={busy}
            style={{
              padding: '0.35rem 0.75rem', fontSize: '0.8rem', backgroundColor: '#38a169',
              color: '#fff', border: 'none', borderRadius: '4px', cursor: busy ? 'not-allowed' : 'pointer',
            }}
          >
            Mark Achieved
          </button>
        )}
        <button
          onClick={handleDelete}
          disabled={busy}
          style={{
            padding: '0.35rem 0.75rem', fontSize: '0.8rem', backgroundColor: '#fff5f5',
            color: '#c53030', border: '1px solid #feb2b2', borderRadius: '4px', cursor: busy ? 'not-allowed' : 'pointer',
          }}
        >
          Delete
        </button>
      </div>
    </li>
  );
};

const SubjectGoals = () => {
  const [subjects, setSubjects] = useState([]);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAll = async () => {
    try {
      const [subjectsRes, goalsData] = await Promise.all([
        api.get('/subjects/'),
        getMyGoals(),
      ]);
      setSubjects(subjectsRes.data);
      setGoals(goalsData);
    } catch (err) {
      setError('Failed to load subject goals.');
    } finally {
      setLoading(false);
    }
  };

  const refreshGoals = async () => {
    try {
      setGoals(await getMyGoals());
    } catch (err) {
      setError('Failed to refresh goals.');
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>Loading goals...</div>;
  }

  const pending = goals.filter((g) => !g.achieved);
  const achieved = goals.filter((g) => g.achieved);

  return (
    <div style={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.5rem' }}>
      <h3 style={{ marginTop: 0, color: '#2d3748' }}>🎯 My Subject Goals</h3>

      {error && (
        <div style={{ padding: '0.75rem', backgroundColor: '#fff5f5', color: '#c53030', borderRadius: '6px', marginBottom: '1rem', fontSize: '0.85rem' }}>
          {error}
        </div>
      )}

      <NewGoalForm subjects={subjects} onCreated={refreshGoals} />

      {goals.length === 0 ? (
        <p style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
          No subject goals yet. Add one above to start tracking what you're aiming for in each subject.
        </p>
      ) : (
        <>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {pending.map((g) => (
              <GoalRow key={g.id} goal={g} onChanged={refreshGoals} />
            ))}
          </ul>
          {achieved.length > 0 && (
            <>
              <h4 style={{ color: '#718096', fontSize: '0.85rem', marginTop: '1.5rem', marginBottom: '0.5rem' }}>
                Achieved ({achieved.length})
              </h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {achieved.map((g) => (
                  <GoalRow key={g.id} goal={g} onChanged={refreshGoals} />
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default SubjectGoals;
