import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = {
  // User Application
  apply: (email, instagram_username, city) =>
    axios.post(`${API_URL}/api/onboarding/apply`, {
      email,
      instagram_username,
      city
    }),
  
  // Check status
  checkStatus: (userId) =>
    axios.get(`${API_URL}/api/onboarding/status/${userId}`),
  
  // Login
  login: (userId, password) =>
    axios.post(`${API_URL}/api/onboarding/login`, {
      user_id: userId,
      password
    }),
  
  // Submit 2FA
  submit2FA: (userId, code) =>
    axios.post(`${API_URL}/api/onboarding/submit-2fa`, {
      user_id: userId,
      code
    }),
  
  // Submit Challenge
  submitChallenge: (userId, code) =>
    axios.post(`${API_URL}/api/onboarding/submit-challenge`, {
      user_id: userId,
      code
    }),
  
  // Admin - Get pending users
  getPendingUsers: () =>
    axios.get(`${API_URL}/api/admin/pending-users`),
  
  // Admin - Approve user
  approveUser: (userId, useMockProxy = false) =>
    axios.post(`${API_URL}/api/admin/approve/${userId}`, {
      use_mock_proxy: useMockProxy
    })
};
