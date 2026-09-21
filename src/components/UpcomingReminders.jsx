// src/components/UpcomingReminders.jsx
import React from 'react';

const REMINDER_WINDOW_MS = 24 * 60 * 60 * 1000; // 24 hours

const formatTimeUntil = (date) => {
  const diffMins = Math.round((date - new Date()) / 60000);
  if (diffMins < 60) return `in ${Math.max(diffMins, 0)} min`;
  return `in ${Math.round(diffMins / 60)}h`;
};

// Builds the "starting soon" list from the two independent session
// sources the dashboard already loads: personal StudySessions
// (scheduling app) and matched GroupStudySessions (matching app). This
// is purely a view over data the dashboard has already fetched -- no
// extra API calls, no backend changes. Cancelled/completed group
// sessions are excluded; StudySession has no such lifecycle, so every
// personal session inside the window counts.
const buildUpcomingItems = (personalSessions, groupSessions) => {
  const now = new Date();
  const windowEnd = new Date(now.getTime() + REMINDER_WINDOW_MS);

  const personalItems = (personalSessions || [])
    .filter((s) => {
      const t = new Date(s.start_time);
      return t >= now && t <= windowEnd;
    })
    .map((s) => ({
      key: `personal-${s.id}`,
      time: new Date(s.start_time),
      label: `${s.subject_name || 'Study session'}${s.goal ? ` — ${s.goal}` : ''}`,
      type: 'Personal',
    }));

  const groupItems = (groupSessions || [])
    .filter((s) => {
      if (s.status !== 'scheduled') return false;
      const t = new Date(s.scheduled_time);
      return t >= now && t <= windowEnd;
    })
    .map((s) => ({
      key: `group-${s.id}`,
      time: new Date(s.scheduled_time),
      label: 'GroupStudy session',
      type: 'GroupStudy',
    }));

  return [...personalItems, ...groupItems].sort((a, b) => a.time - b.time);
};

const UpcomingReminders = ({ personalSessions, groupSessions }) => {
  const items = buildUpcomingItems(personalSessions, groupSessions);

  if (items.length === 0) return null;

  return (
    <div
      style={{
        backgroundColor: '#fffaf0',
        border: '1px solid #fbd38d',
        borderRadius: '8px',
        padding: '1rem 1.25rem',
        marginBottom: '1.5rem',
      }}
    >
      <div style={{ fontWeight: 'bold', color: '#9c4221', marginBottom: '0.5rem' }}>
        🔔 Coming up in the next 24 hours
      </div>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {items.map((item) => (
          <li
            key={item.key}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '0.5rem',
              padding: '0.3rem 0',
              fontSize: '0.85rem',
              color: '#744210',
            }}
          >
            <span><strong>{item.type}</strong> — {item.label}</span>
            <span>
              {item.time.toLocaleString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' })}
              {' '}({formatTimeUntil(item.time)})
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UpcomingReminders;
