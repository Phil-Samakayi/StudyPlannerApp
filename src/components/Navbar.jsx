// src/components/Navbar.jsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../services/authService';

const Navbar = ({ isAuthenticated, setIsAuthenticated }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    setIsAuthenticated(false);
    navigate('/login');
  };

  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      backgroundColor: '#1a202c',
      color: '#ffffff',
      padding: '1rem 2rem',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div style={{ fontWeight: 'bold', fontSize: '1.25rem', cursor: 'pointer' }} onClick={() => navigate('/')}>
        📚 StudyPlannerApp
      </div>

      {isAuthenticated && (
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <Link to="/dashboard" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: '500' }}>
            Dashboard
          </Link>
          <Link to="/availability" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: '500' }}>
            Availability
          </Link>
          <Link to="/assessment" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: '500' }}>
            Self Assessment
          </Link>
          <button
            onClick={handleLogout}
            style={{
              padding: '0.4rem 0.8rem',
              backgroundColor: '#e53e3e',
              color: '#ffffff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;