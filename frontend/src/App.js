import React, { useState } from 'react';
import ApplicationForm from './components/Apply/ApplicationForm';
import OnboardingFlow from './components/Onboarding/OnboardingFlow';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('apply');
  const [userId, setUserId] = useState(null);

  const handleApplicationSuccess = (data) => {
    setUserId(data.user_id);
    setCurrentView('onboarding');
  };

  return (
    <div className="App">
      {currentView === 'apply' && (
        <ApplicationForm onSuccess={handleApplicationSuccess} />
      )}
      
      {currentView === 'onboarding' && userId && (
        <OnboardingFlow userId={userId} />
      )}
    </div>
  );
}

export default App;
