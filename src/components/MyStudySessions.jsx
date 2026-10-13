// src/components/MyStudySessions.jsx
// Personal study schedule: lets a student book, view and remove their own
// study sessions (the `scheduling` app's StudySession). The session list is
// owned by StudentDashboard and passed in, so creating or deleting a session
// here also refreshes the UpcomingReminders banner straight away.
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { createStudySession, deleteStudySession } from '../services/scheduleService';

const todayISO = () => {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};

const formatDayHeading = (date) =>
  date.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' });

const formatTime = (date) =>
  date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });

const formatDuration = (start, end) => {
  const minutes = Math.round((end - start) / 60000);
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m} min`;
  return m === 0 ? `${h} h` : `${h} h ${m} min`;
};

// Pulls the most useful message out of a DRF validation error response.
const extractError = (err, fallback) => {
  const data = err.response?.data;
  if (!data) return fallback;
  const first = (v) => (Array.isArray(v) ? v[0] : v);
  return String(
    first(data.non_field_errors) ||
      first(data.end_time) ||
      first(data.start_time) ||
      first(data.subject) ||
      first(data.goal) ||
      data.detail ||
      fallback
  );
};

const NewSessionForm = ({ subjects, onCreated }) => {
  const [subjectId, setSubjectId] = useState('');
  const [date, setDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [goal, setGoal] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Date + time inputs are interpreted in the browser's local time zone.
    const start = new Date(`${date}T${startTime}`);
    const end = new Date(`${date}T${endTime}`);

    if (end <= start) {
      setError('End time must be after start time.');
      return;
    }
    if (start < new Date()) {
      setError('You can only plan sessions that start in the future.');
      return;
    }

    setLoading(true);
    try {
      await createStudySession({
        subject: subjectId,
        start_time: start.toISOString(),
        end_time: end.toISOString(),
        goal: goal.trim(),
      });
      setSubjectId('');
      setDate('');
      setStartTime('');
      setEndTime('');
      setGoal('');
      onCreated();
    } catch (err) {
      setError(extractError(err, 'Could not create study session.'));
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    padding: '0.4rem',
    fontSize: '0.85rem',
    borderRadius: '4px',
    border: '1px solid #cbd5e0',
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
      <select value={subjectId} onChange={(e) => setSubjectId(e.target.value)} required style={inputStyle}>
        <option value="">Subject...</option>
        {subjects.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>
      <input
        type="date"
        value={date}
        min={todayISO()}
        onChange={(e) => setDate(e.target.value)}
        required
        style={inputStyle}
      />
      <input
        type="time"
        value={startTime}
        onChange={(e) => setStartTime(e.target.value)}
        required
        aria-label="Start time"
        style={inputStyle}
      />
      <span style={{ color: '#718096', fontSize: '0.85rem' }}>to</span>
      <input
        type="time"
        value={endTime}
        onChange={(e) => setEndTime(e.target.value)}
        required
        aria-label="End time"
        style={inputStyle}
      />
      <input
        type="text"
        placeholder="Session goal (optional), e.g. 'Past paper Q1-Q5'"
        value={goal}
        maxLength={255}
        onChange={(e) => setGoal(e.target.value)}
        style={{ ...inputStyle, flex: 1, minWidth: '200px' }}
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
        {loading ? 'Adding...' : 'Add Session'}
      </button>
      {error && <div style={{ width: '100%', color: '#c53030', fontSize: '0.75rem' }}>{error}</div>}
    </form>
  );
};

const SessionRow = ({ session, onChanged, isPast }) => {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const start = new Date(session.start_time);
  const end = new Date(session.end_time);
  const inProgress = !isPast && start <= new Date();

  const handleDelete = async () => {
    if (!window.confirm('Remove this study session from your plan?')) return;
    setBusy(true);
    setError(null);
    try {
      await deleteStudySession(session.id);
      onChanged();
    } catch (err) {
      setError('Could not remove session.');
      setBusy(false);
    }
  };

  return (
    <li
      style={{
        padding: '0.75rem 0',
        borderBottom: '1px solid #edf2f7',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '0.75rem',
        opacity: isPast ? 0.65 : 1,
      }}
    >
      <div>
        <div style={{ fontWeight: 'bold', color: '#2b6cb0' }}>
          {session.subject_name}
          {inProgress && (
            <span
              style={{
                marginLeft: '0.5rem',
                fontSize: '0.7rem',
                padding: '0.1rem 0.4rem',
                backgroundColor: '#c6f6d5',
                color: '#22543d',
                borderRadius: '4px',
              }}
            >
              In progress
            </span>
          )}
        </div>
        <div style={{ fontSize: '0.8rem', color: '#718096' }}>
          {formatTime(start)} – {formatTime(end)} · {formatDuration(start, end)}
        </div>
        {session.goal && <div style={{ fontSize: '0.85rem', color: '#2d3748', marginTop: '0.15rem' }}>{session.goal}</div>}
        {error && <div style={{ color: '#c53030', fontSize: '0.7rem', marginTop: '0.15rem' }}>{error}</div>}
      </div>
      {!isPast && (
        <button
          onClick={handleDelete}
          disabled={busy}
          style={{
            padding: '0.35rem 0.75rem',
            fontSize: '0.8rem',
            backgroundColor: '#fff5f5',
            color: '#c53030',
            border: '1px solid #feb2b2',
            borderRadius: '4px',
            cursor: busy ? 'not-allowed' : 'pointer',
            flexShrink: 0,
          }}
        >
          Remove
        </button>
      )}
    </li>
  );
};

// Groups sessions under a heading per calendar day, preserving order.
const groupByDay = (sessions) => {
  const groups = [];
  sessions.forEach((s) => {
    const start = new Date(s.start_time);
    const key = start.toDateString();
    const last = groups[groups.length - 1];
    if (last && last.key === key) {
      last.sessions.push(s);
    } else {
      groups.push({ key, heading: formatDayHeading(start), sessions: [s] });
    }
  });
  return groups;
};

const PAST_SESSIONS_SHOWN = 10;

const MyStudySessions = ({ sessions, onChanged }) => {
  const [subjects, setSubjects] = useState([]);
  const [subjectsError, setSubjectsError] = useState(null);
  const [showPast, setShowPast] = useState(false);

  useEffect(() => {
    api
      .get('/subjects/')
      .then((res) => setSubjects(res.data))
      .catch(() => setSubjectsError('Failed to load subjects.'));
  }, []);

  const now = new Date();
  // A session stays in "upcoming" until it has ended, so one in progress
  // is still visible (and flagged) rather than jumping straight to "past".
  const upcoming = [...(sessions || [])]
    .filter((s) => new Date(s.end_time) > now)
    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
  const past = [...(sessions || [])]
    .filter((s) => new Date(s.end_time) <= now)
    .sort((a, b) => new Date(b.start_time) - new Date(a.start_time));

  return (
    <div style={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.5rem' }}>
      <h3 style={{ marginTop: 0, color: '#2d3748' }}>📚 My Study Sessions</h3>
      <p style={{ marginTop: 0, color: '#718096', fontSize: '0.85rem' }}>
        Plan your own study time for each subject. Sessions starting in the next 24 hours appear in your reminders.
      </p>

      {subjectsError && (
        <div style={{ padding: '0.75rem', backgroundColor: '#fff5f5', color: '#c53030', borderRadius: '6px', marginBottom: '1rem', fontSize: '0.85rem' }}>
          {subjectsError}
        </div>
      )}

      <NewSessionForm subjects={subjects} onCreated={onChanged} />

      {upcoming.length === 0 ? (
        <p style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
          No upcoming study sessions. Add one above to start building your study plan.
        </p>
      ) : (
        groupByDay(upcoming).map((group) => (
          <div key={group.key} style={{ marginBottom: '1rem' }}>
            <h4 style={{ color: '#4a5568', fontSize: '0.9rem', margin: '0.5rem 0 0' }}>{group.heading}</h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {group.sessions.map((s) => (
                <SessionRow key={s.id} session={s} onChanged={onChanged} isPast={false} />
              ))}
            </ul>
          </div>
        ))
      )}

      {past.length > 0 && (
        <div style={{ marginTop: '1.5rem' }}>
          <button
            onClick={() => setShowPast((v) => !v)}
            style={{
              background: 'none',
              border: 'none',
              padding: 0,
              color: '#718096',
              fontSize: '0.85rem',
              cursor: 'pointer',
              fontWeight: 'bold',
            }}
          >
            {showPast ? '▾' : '▸'} Past sessions ({past.length})
          </button>
          {showPast &&
            groupByDay(past.slice(0, PAST_SESSIONS_SHOWN)).map((group) => (
              <div key={group.key} style={{ marginTop: '0.5rem' }}>
                <h4 style={{ color: '#a0aec0', fontSize: '0.8rem', margin: '0.5rem 0 0' }}>{group.heading}</h4>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {group.sessions.map((s) => (
                    <SessionRow key={s.id} session={s} onChanged={onChanged} isPast />
                  ))}
                </ul>
              </div>
            ))}
        </div>
      )}
    </div>
  );
};

export default MyStudySessions;
