import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../../services/api';
import './OnboardingFlow.css';

export default function OnboardingFlow({ userId }) {
  const [stage, setStage] = useState('checking');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userInfo, setUserInfo] = useState(null);

  const checkStatus = useCallback(async () => {
    try {
      const response = await api.checkStatus(userId);
      setUserInfo(response.data);
      
      if (response.data.can_login) {
        setStage('password');
      } else {
        setStage('waiting');
      }
    } catch (err) {
      setError('Failed to check status');
    }
  }, [userId]);

  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  // ... rest of the component stays the same
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.login(userId, password);
      
      if (response.data.status === '2fa_required') {
        setStage('2fa');
      } else if (response.data.status === 'challenge_required') {
        setStage('challenge');
      } else if (response.data.status === 'success') {
        setStage('success');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handle2FASubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.submit2FA(userId, code);
      
      if (response.data.status === 'success') {
        setStage('success');
      }
    } catch (err) {
      setError(err.response?.data?.detail || '2FA failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChallengeSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.submitChallenge(userId, code);
      
      if (response.data.status === 'success') {
        setStage('success');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  if (stage === 'checking') {
    return (
      <div className="onboarding-container">
        <div className="loading">Checking status...</div>
      </div>
    );
  }

  if (stage === 'waiting') {
    return (
      <div className="onboarding-container">
        <div className="onboarding-card">
          <div className="icon"></div>
          <h2>Application Submitted!</h2>
          <p>We'll approve within 24 hours.</p>
          <button onClick={checkStatus} className="btn-secondary">
            Check Status
          </button>
        </div>
      </div>
    );
  }

  if (stage === 'password') {
    return (
      <div className="onboarding-container">
        <div className="onboarding-card">
          <h2>Connect Your Instagram</h2>
          <p>Proxy in <strong>{userInfo.city}</strong> ready </p>
          
          <form onSubmit={handlePasswordSubmit}>
            <div className="form-group">
              <label>Instagram Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Connecting...' : 'Continue'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (stage === '2fa') {
    return (
      <div className="onboarding-container">
        <div className="onboarding-card">
          <div className="icon"></div>
          <h2>Two-Factor Authentication</h2>
          <p>Enter 6-digit code</p>
          
          <form onSubmit={handle2FASubmit}>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
              placeholder="000000"
              maxLength="6"
              className="code-input"
              required
            />

            {error && <div className="error-message">{error}</div>}

            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Verifying...' : 'Verify'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (stage === 'success') {
    return (
      <div className="onboarding-container">
        <div className="onboarding-card success">
          <div className="icon"></div>
          <h2>You're All Set!</h2>
          <p>Automation starting...</p>
        </div>
      </div>
    );
  }

  return null;
}
