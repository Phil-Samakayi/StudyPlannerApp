// src/components/AvailabilityGrid.jsx
import React, { useState, useEffect } from 'react';
import api from '../services/api';

// Days matching DayOfWeek IntegerChoices (0 = Monday, ..., 6 = Sunday)
const DAYS = [
  { id: 0, label: 'Monday' },
  { id: 1, label: 'Tuesday' },
  { id: 2, label: 'Wednesday' },
  { id: 3, label: 'Thursday' },
  { id: 4, label: 'Friday' },
  { id: 5, label: 'Saturday' },
  { id: 6, label: 'Sunday' },
];

// Time slots from 08:00 to 20:00 in 2-hour blocks
const TIME_SLOTS = [
  { start: '08:00:00', end: '10:00:00', label: '8 AM - 10 AM' },
  { start: '10:00:00', end: '12:00:00', label: '10 AM - 12 PM' },
  { start: '12:00:00', end: '14:00:00', label: '12 PM - 2 PM' },
  { start: '14:00:00', end: '16:00:00', label: '2 PM - 4 PM' },
  { start: '16:00:00', end: '18:00:00', label: '4 PM - 6 PM' },
  { start: '18:00:00', end: '20:00:00', label: '6 PM - 8 PM' },
];

const AvailabilityGrid = () => {
  // Key format: "day_of_week-start_time" e.g., "1-14:00:00"
  const [selectedSlots, setSelectedSlots] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Load current schedule slots from backend
  useEffect(() => {
    setLoading(true);
    api.get('/scheduling/slots/')
      .then((res) => {
        const activeSet = new Set();
        res.data.forEach((slot) => {
          activeSet.add(`${slot.day_of_week}-${slot.start_time}`);
        });
        setSelectedSlots(activeSet);
      })
      .catch(() => setMessage({ type: 'error', text: 'Failed to load existing schedule.' }))
      .finally(() => setLoading(false));
  }, []);

  const toggleSlot = (dayId, startTime) => {
    const key = `${dayId}-${startTime}`;
    setSelectedSlots((prev) => {
      const updated = new Set(prev);
      if (updated.has(key)) {
        updated.delete(key);
      } else {
        updated.add(key);
      }
      return updated;
    });
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    // Transform selectedSet into array payload for ScheduleSlot model
    const slotsPayload = [];
    selectedSlots.forEach((key) => {
      const [dayStr, startTime] = key.split('-');
      const dayId = parseInt(dayStr, 10);
      const slotDef = TIME_SLOTS.find((t) => t.start === startTime);

      if (slotDef) {
        slotsPayload.push({
          day_of_week: dayId,
          start_time: slotDef.start,
          end_time: slotDef.end,
        });
      }
    });

    try {
      await api.post('/scheduling/slots/bulk-update/', { slots: slotsPayload });
      setMessage({ type: 'success', text: 'Weekly availability updated successfully!' });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to save availability schedule.',
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '2rem' }}>Loading schedule...</div>;
  }

  return (
    <div style={{ maxWidth: '900px', margin: '2rem auto', padding: '1.5rem', backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
      <h2>Weekly Recurring Availability</h2>
      <p style={{ color: '#718096', fontSize: '0.95rem' }}>
        Select the times you are free for group study. The AI matching algorithm uses these blocks to match you with available peers.
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

      {/* Grid Table */}
      <div style={{ overflowX: 'auto', marginBottom: '1.5rem' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center' }}>
          <thead>
            <tr style={{ backgroundColor: '#f7fafc' }}>
              <th style={{ padding: '0.75rem', border: '1px solid #e2e8f0' }}>Time</th>
              {DAYS.map((day) => (
                <th key={day.id} style={{ padding: '0.75rem', border: '1px solid #e2e8f0' }}>
                  {day.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {TIME_SLOTS.map((slot) => (
              <tr key={slot.start}>
                <td style={{ padding: '0.5rem', border: '1px solid #e2e8f0', fontWeight: 'bold', fontSize: '0.85rem', backgroundColor: '#f7fafc' }}>
                  {slot.label}
                </td>
                {DAYS.map((day) => {
                  const key = `${day.id}-${slot.start}`;
                  const isSelected = selectedSlots.has(key);
                  return (
                    <td
                      key={key}
                      onClick={() => toggleSlot(day.id, slot.start)}
                      style={{
                        padding: '0.75rem',
                        border: '1px solid #e2e8f0',
                        backgroundColor: isSelected ? '#3182ce' : '#ffffff',
                        color: isSelected ? '#ffffff' : '#a0aec0',
                        cursor: 'pointer',
                        userSelect: 'none',
                        transition: 'background-color 0.15s ease'
                      }}
                    >
                      {isSelected ? 'Available' : '—'}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        style={{
          padding: '0.75rem 2rem',
          backgroundColor: saving ? '#a0aec0' : '#2b6cb0',
          color: '#fff',
          fontWeight: 'bold',
          border: 'none',
          borderRadius: '4px',
          cursor: saving ? 'not-allowed' : 'pointer'
        }}
      >
        {saving ? 'Saving...' : 'Save Availability'}
      </button>
    </div>
  );
};

export default AvailabilityGrid;