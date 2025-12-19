import React, { useState } from 'react';
import { api } from '../../services/api';
import './ApplicationForm.css';

export default function ApplicationForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    email: '',
    instagram_username: '',
    city: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const cities = [
    'Paris', 'London', 'New York', 'Los Angeles', 'Miami',
    'Berlin', 'Amsterdam', 'Barcelona', 'Dubai', 'Tokyo'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.apply(
        formData.email,
        formData.instagram_username,
        formData.city
      );
      
      onSuccess(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Application failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="application-form-container">
      <div className="application-card">
        <h1>Join GES Nightlife Automation </h1>
        <p className="subtitle">
          Connect your Instagram and start automating your nightlife business
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              placeholder="your@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Instagram Username</label>
            <input
              type="text"
              value={formData.instagram_username}
              onChange={(e) => setFormData({...formData, instagram_username: e.target.value})}
              placeholder="@your_instagram"
              required
            />
            <small>Your business Instagram account</small>
          </div>

          <div className="form-group">
            <label>City</label>
            <select
              value={formData.city}
              onChange={(e) => setFormData({...formData, city: e.target.value})}
              required
            >
              <option value="">Select your city</option>
              {cities.map(city => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
            <small>We'll set up a dedicated proxy in your city</small>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Submitting...' : 'Apply Now'}
          </button>
        </form>

        <div className="info-box">
          <p> Dedicated mobile proxy in your city</p>
          <p> Automatic DM automation</p>
          <p> 24/7 customer support</p>
        </div>
      </div>
    </div>
  );
}
