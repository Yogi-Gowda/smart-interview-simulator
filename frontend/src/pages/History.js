import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import { 
  History as HistoryIcon, 
  Calendar, 
  Award, 
  ChevronRight,
  Clock,
  Briefcase,
  BarChart3
} from 'lucide-react';
import * as api from '../services/api';
import './History.css';

const HistoryPage = () => {
  const navigate = useNavigate();
  const { userId } = useApp();
  
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, [userId]);

  const fetchHistory = async () => {
    try {
      setIsLoading(true);
      const data = await api.getInterviewHistory(userId);
      setHistory(data.history || []);
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError('Failed to load interview history');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#34d399';
    if (score >= 60) return '#8b8bf5';
    if (score >= 40) return '#fbbf24';
    return '#f87171';
  };

  const getGrade = (score) => {
    if (score >= 90) return 'A+';
    if (score >= 80) return 'A';
    if (score >= 70) return 'B+';
    if (score >= 60) return 'B';
    if (score >= 50) return 'C';
    if (score >= 40) return 'D';
    return 'F';
  };

  if (isLoading) {
    return (
      <div className="history-loading">
        <div className="spinner"></div>
        <p>Loading history...</p>
      </div>
    );
  }

  return (
    <div className="history">
      <div className="container">
        {/* Header */}
        <div className="history-header">
          <div className="header-content">
            <h1>
              <HistoryIcon size={28} />
              Interview History
            </h1>
            <p>View your past interview sessions and performance</p>
          </div>
          <button className="btn btn-primary" onClick={() => navigate('/interview-setup')}>
            Start New Interview
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">{error}</div>
        )}

        {/* Empty State */}
        {history.length === 0 && !error && (
          <div className="empty-state">
            <HistoryIcon size={64} />
            <h2>No Interview History</h2>
            <p>You haven't completed any interviews yet. Start practicing to build your history.</p>
            <button className="btn btn-primary" onClick={() => navigate('/interview-setup')}>
              Start Your First Interview
            </button>
          </div>
        )}

        {/* History List */}
        {history.length > 0 && (
          <div className="history-list">
            {history.map((session, index) => (
              <div 
                key={session.session_id || index} 
                className="history-card"
                onClick={() => navigate('/feedback', { state: { report: session } })}
              >
                <div className="card-main">
                  <div className="card-icon">
                    <Briefcase size={24} />
                  </div>
                  <div className="card-info">
                    <h3 className="card-title">
                      {session.job_role?.replace('_', ' ') || 'Interview'}
                    </h3>
                    <div className="card-meta">
                      <span className="meta-item">
                        <Calendar size={14} />
                        {formatDate(session.completed_at || session.last_updated)}
                      </span>
                      <span className="meta-item">
                        <Clock size={14} />
                        {session.total_questions || session.answers?.length || 0} questions
                      </span>
                      <span className="meta-item difficulty">
                        {session.difficulty}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="card-score">
                  <div 
                    className="score-badge"
                    style={{ background: getScoreColor(session.average_score) }}
                  >
                    <span className="score-value">{Math.round(session.average_score || 0)}</span>
                    <span className="score-grade">{getGrade(session.average_score)}</span>
                  </div>
                  <ChevronRight size={20} className="arrow-icon" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Stats Summary */}
        {history.length > 0 && (
          <div className="history-stats">
            <div className="stat-card">
              <span className="stat-icon"><Award size={20} /></span>
              <div className="stat-content">
                <span className="stat-value">{history.length}</span>
                <span className="stat-label">Total Interviews</span>
              </div>
            </div>
            <div className="stat-card">
              <span className="stat-icon"><BarChart3 size={20} /></span>
              <div className="stat-content">
                <span className="stat-value">
                  {Math.round(history.reduce((acc, s) => acc + (s.average_score || 0), 0) / history.length) || 0}
                </span>
                <span className="stat-label">Average Score</span>
              </div>
            </div>
            <div className="stat-card">
              <span className="stat-icon"><Clock size={20} /></span>
              <div className="stat-content">
                <span className="stat-value">
                  {history.reduce((acc, s) => acc + (s.total_questions || s.answers?.length || 0), 0)}
                </span>
                <span className="stat-label">Questions Answered</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;