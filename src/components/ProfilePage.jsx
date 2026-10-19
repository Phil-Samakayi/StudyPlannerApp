// src/components/ProfilePage.jsx
// Lets a student view and complete their academic profile (student number,
// programme, year of study) via PATCH /api/accounts/profile/. Name, email
// and role come from the account itself and are shown read-only here.
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProfile, updateProfile } from '../services/authService';

// New accounts get a placeholder student number ("PENDING-<id>") until the
// student fills in their real one.
export const PENDING_PREFIX = 'PENDING-';

export const isProfileIncomplete = (profile) =>
  !!profile && (!profile.program || String(profile.student_number || '').startsWith(PENDING_PREFIX));

const YEARS = [1, 2, 3, 4, 5, 6, 7];

const labelStyle = { display: 'block', marginBottom: '0.35rem', fontSize: '0.85rem', fontWeight: 'bold', color: '#4a5568' };
const inputStyle = {
  width: '100%',
  boxSizing: 'border-box',
  padding: '0.5rem',
  fontSize: '0.95rem',
  borderRadius: '4px',
  border: '1px solid #cbd5e0',
};
const fieldErrorStyle = { color: '#c53030', fontSize: '0.75rem', marginTop: '0.25rem' };

const ReadOnlyRow = ({ label, value }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #edf2f7', fontSize: '0.9rem' }}>
    <span style={{ color: '#718096' }}>{label}</span>
    <span style={{ color: '#2d3748', fontWeight: '500' }}>{value || '—'}</span>
  </div>
);

const ProfilePage = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [studentNumber, setStudentNumber] = useState('');
  const [program, setProgram] = useState('');
  const [yearOfStudy, setYearOfStudy] = useState(1);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [saveError, setSaveError] = useState(null);
  const [saved, setSaved] = useState(false);

  const fillForm = (data) => {
    setProfile(data);
    const number = data.student_number || '';
    setStudentNumber(number.startsWith(PENDING_PREFIX) ? '' : number);
    setProgram(data.program || '');
    setYearOfStudy(data.year_of_study || 1);
  };

  useEffect(() => {
    getProfile()
      .then(fillForm)
      .catch(() => setLoadError('Failed to load your profile. Please try again.'))
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    setFieldErrors({});
    setSaveError(null);
    try {
      const updated = await updateProfile({
        student_number: studentNumber.trim(),
        program: program.trim(),
        year_of_study: Number(yearOfStudy),
      });
      fillForm(updated);
      setSaved(true);
    } catch (err) {
      const data = err.response?.data;
      if (data && typeof data === 'object' && !data.detail) {
        const errors = {};
        Object.entries(data).forEach(([field, messages]) => {
          errors[field] = Array.isArray(messages) ? messages[0] : String(messages);
        });
        setFieldErrors(errors);
      } else {
        setSaveError(data?.detail || 'Could not save your profile.');
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: '#718096' }}>Loading profile...</div>;
  }

  if (loadError) {
    return (
      <div style={{ maxWidth: '600px', margin: '2rem auto', padding: '1rem', backgroundColor: '#fff5f5', color: '#c53030', borderRadius: '6px' }}>
        {loadError}
      </div>
    );
  }

  const user = profile?.user || {};
  const incomplete = isProfileIncomplete(profile);

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', padding: '0 1rem' }}>
      <div style={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.5rem' }}>
        <h2 style={{ marginTop: 0, color: '#2d3748' }}>👤 My Profile</h2>

        {incomplete && (
          <div style={{ padding: '0.75rem', backgroundColor: '#fffaf0', border: '1px solid #fbd38d', color: '#975a16', borderRadius: '6px', marginBottom: '1.25rem', fontSize: '0.85rem' }}>
            Your profile isn't complete yet. Add your student number and programme so peers and admins can identify you.
          </div>
        )}

        <h4 style={{ margin: '0 0 0.25rem', color: '#4a5568', fontSize: '0.9rem' }}>Account</h4>
        <div style={{ marginBottom: '1.5rem' }}>
          <ReadOnlyRow label="Full name" value={user.full_name} />
          <ReadOnlyRow label="Email" value={user.email} />
          <ReadOnlyRow label="Role" value={user.role === 'ADMIN' ? 'Admin' : 'Student'} />
        </div>

        <h4 style={{ margin: '0 0 0.75rem', color: '#4a5568', fontSize: '0.9rem' }}>Academic details</h4>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="student_number" style={labelStyle}>Student number</label>
            <input
              id="student_number"
              type="text"
              value={studentNumber}
              onChange={(e) => setStudentNumber(e.target.value)}
              placeholder="e.g. 2021439488"
              maxLength={20}
              required
              style={inputStyle}
            />
            {fieldErrors.student_number && <div style={fieldErrorStyle}>{fieldErrors.student_number}</div>}
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="program" style={labelStyle}>Programme / course of study</label>
            <input
              id="program"
              type="text"
              value={program}
              onChange={(e) => setProgram(e.target.value)}
              placeholder="e.g. BSc Computer Science"
              maxLength={150}
              required
              style={inputStyle}
            />
            {fieldErrors.program && <div style={fieldErrorStyle}>{fieldErrors.program}</div>}
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label htmlFor="year_of_study" style={labelStyle}>Year of study</label>
            <select
              id="year_of_study"
              value={yearOfStudy}
              onChange={(e) => setYearOfStudy(e.target.value)}
              style={inputStyle}
            >
              {YEARS.map((y) => (
                <option key={y} value={y}>Year {y}</option>
              ))}
            </select>
            {fieldErrors.year_of_study && <div style={fieldErrorStyle}>{fieldErrors.year_of_study}</div>}
          </div>

          {saveError && <div style={{ ...fieldErrorStyle, fontSize: '0.85rem', marginBottom: '0.75rem' }}>{saveError}</div>}
          {saved && (
            <div style={{ color: '#276749', fontSize: '0.85rem', marginBottom: '0.75rem' }}>✓ Profile saved.</div>
          )}

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              type="submit"
              disabled={saving}
              style={{
                padding: '0.5rem 1.25rem',
                backgroundColor: saving ? '#a0aec0' : '#2b6cb0',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                fontWeight: 'bold',
                cursor: saving ? 'not-allowed' : 'pointer',
              }}
            >
              {saving ? 'Saving...' : 'Save Profile'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              style={{
                padding: '0.5rem 1.25rem',
                backgroundColor: '#edf2f7',
                color: '#2d3748',
                border: '1px solid #cbd5e0',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Back to Dashboard
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfilePage;
