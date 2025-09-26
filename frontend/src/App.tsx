import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LandingPage from './components/LandingPage';

const AppContent: React.FC = () => {
  const { currentUser } = useAuth();

  const handleTryNowClick = () => {
    // This function is no longer used since the LandingPage handles redirection internally
    console.log('Try Now clicked from App component');
  };

  return (
    <LandingPage 
      onTryNowClick={handleTryNowClick}
      isAuthenticated={!!currentUser}
    />
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
