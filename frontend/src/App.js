import React, { useState, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import InterviewSetup from './pages/InterviewSetup';
import Interview from './pages/Interview';
import Feedback from './pages/Feedback';
import History from './pages/History';
import Dashboard from './pages/Dashboard';

// Create context for global state
const AppContext = createContext();

export const useApp = () => useContext(AppContext);

function App() {
  const [userId] = useState(() => `user_${Date.now()}`);
  const [currentSession, setCurrentSession] = useState(null);
  const [interviewData, setInterviewData] = useState(null);

  const value = {
    userId,
    currentSession,
    setCurrentSession,
    interviewData,
    setInterviewData
  };

  return (
    <AppContext.Provider value={value}>
      <Router>
        <div className="app">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/interview-setup" element={<InterviewSetup />} />
            <Route path="/interview" element={<Interview />} />
            <Route path="/feedback" element={<Feedback />} />
            <Route path="/history" element={<History />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </Router>
    </AppContext.Provider>
  );
}

export default App;