import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import { 
  LayoutDashboard, 
  TrendingUp, 
  TrendingDown, 
  Award, 
  AlertTriangle,
  Target,
  BookOpen,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import * as api from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { userId } = useApp();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboard();
  }, [userId]);

  const fetchDashboard = async () => {
    try {
      setIsLoading(true);
      const data = await api.getUserDashboard(userId);
      setDashboardData(data);
    } catch (err) {
      console.error('Failed to fetch dashboard:', err);
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const COLORS = ['#8b8bf5', '#34d399', '#fbbf24', '#f87171', '#60a5fa', '#a78bfa'];

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <RefreshCw size={32} className="spin" />
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  // Mock data for demonstration if no real data
  const data = dashboardData || {
    total_interviews: 0,
    average_score: 0,
    total_questions: 0,
    weak_areas: [],
    strengths: [],
    recent_interviews: [],
    performance_trend: []
  };

  const performanceData = data.performance_trend.length > 0 
    ? data.performance_trend.map((item, index) => ({
        name: `Interview ${index + 1}`,
        score: Math.round(item.score)
      }))
    : [
        { name: 'Sample 1', score: 65 },
        { name: 'Sample 2', score: 72 },
        { name: 'Sample 3', score: 58 },
        { name: 'Sample 4', score: 78 },
        { name: 'Sample 5', score: 82 }
      ];

  const categoryData = data.strengths.length > 0 
    ? data.strengths.map(s => ({ name: s.category, value: s.score }))
    : [
        { name: 'Programming', value: 75 },
        { name: 'Database', value: 65 },
        { name: 'Web', value: 80 },
        { name: 'OOP', value: 70 }
      ];

  return (
    <div className="dashboard">
      <div className="container">
        {/* Header */}
        <div className="dashboard-header">
          <div className="header-content">
            <h1>
              <LayoutDashboard size={28} />
              Performance Dashboard
            </h1>
            <p>Track your interview preparation progress</p>
          </div>
          <button className="btn btn-primary" onClick={() => navigate('/interview-setup')}>
            Start Interview
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">{error}</div>
        )}

        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card primary">
            <div className="stat-icon">
              <Award size={24} />
            </div>
            <div className="stat-info">
              <span className="stat-value">{data.total_interviews}</span>
              <span className="stat-label">Total Interviews</span>
            </div>
          </div>
          
          <div className="stat-card success">
            <div className="stat-icon">
              <TrendingUp size={24} />
            </div>
            <div className="stat-info">
              <span className="stat-value">{data.average_score}%</span>
              <span className="stat-label">Average Score</span>
            </div>
          </div>
          
          <div className="stat-card info">
            <div className="stat-icon">
              <Target size={24} />
            </div>
            <div className="stat-info">
              <span className="stat-value">{data.total_questions}</span>
              <span className="stat-label">Questions Answered</span>
            </div>
          </div>
          
          <div className="stat-card warning">
            <div className="stat-icon">
              <AlertTriangle size={24} />
            </div>
            <div className="stat-info">
              <span className="stat-value">{data.weak_areas.length}</span>
              <span className="stat-label">Areas to Improve</span>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="charts-grid">
          {/* Performance Trend */}
          <div className="chart-card">
            <h2>
              <TrendingUp size={20} />
              Performance Trend
            </h2>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="name" stroke="#424249" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="#424249" fontSize={11} domain={[0, 100]} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ 
                      background: '#19191f', 
                      border: '1px solid rgba(255,255,255,0.08)',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#8b8bf5" 
                    strokeWidth={2}
                    dot={{ fill: '#8b8bf5', strokeWidth: 0, r: 3 }}
                    activeDot={{ r: 5, strokeWidth: 0 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Skills Distribution */}
          <div className="chart-card">
            <h2>
              <BookOpen size={20} />
              Skills Distribution
            </h2>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      background: '#19191f', 
                      border: '1px solid rgba(255,255,255,0.08)',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="chart-legend">
                {categoryData.map((entry, index) => (
                  <div key={index} className="legend-item">
                    <span 
                      className="legend-color" 
                      style={{ background: COLORS[index % COLORS.length] }}
                    ></span>
                    <span className="legend-label">{entry.name}</span>
                    <span className="legend-value">{entry.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Weak Areas & Strengths */}
        <div className="analysis-grid">
          {/* Weak Areas */}
          <div className="analysis-card weak">
            <h2>
              <AlertTriangle size={20} />
              Areas to Improve
            </h2>
            {data.weak_areas.length > 0 ? (
              <div className="analysis-list">
                {data.weak_areas.map((area, index) => (
                  <div key={index} className="analysis-item">
                    <div className="item-info">
                      <span className="item-name">{area.category}</span>
                      <span className="item-score" style={{ color: '#f87171' }}>
                        {area.score}%
                      </span>
                    </div>
                    <div className="item-bar">
                      <div 
                        className="bar-fill" 
                        style={{ width: `${area.score}%`, background: '#f87171' }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-analysis">
                <p>No weak areas identified yet.</p>
                <p className="hint">Complete more interviews to get personalized recommendations.</p>
              </div>
            )}
          </div>

          {/* Strengths */}
          <div className="analysis-card strong">
            <h2>
              <Award size={20} />
              Your Strengths
            </h2>
            {data.strengths.length > 0 ? (
              <div className="analysis-list">
                {data.strengths.map((strength, index) => (
                  <div key={index} className="analysis-item">
                    <div className="item-info">
                      <span className="item-name">{strength.category}</span>
                      <span className="item-score" style={{ color: '#34d399' }}>
                        {strength.score}%
                      </span>
                    </div>
                    <div className="item-bar">
                      <div 
                        className="bar-fill" 
                        style={{ width: `${strength.score}%`, background: '#34d399' }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-analysis">
                <p>No strengths identified yet.</p>
                <p className="hint">Complete interviews to discover your strong areas.</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Interviews */}
        <div className="recent-section">
          <h2>
            <Award size={20} />
            Recent Interviews
          </h2>
          {data.recent_interviews.length > 0 ? (
            <div className="recent-grid">
              {data.recent_interviews.map((interview, index) => (
                <div 
                  key={index} 
                  className="recent-card"
                  onClick={() => navigate('/feedback', { state: { report: interview } })}
                >
                  <div className="recent-info">
                    <span className="recent-role">{interview.job_role?.replace('_', ' ')}</span>
                    <span className="recent-date">
                      {new Date(interview.date).toLocaleDateString()}
                    </span>
                  </div>
                  <div 
                    className="recent-score"
                    style={{ 
                      background: interview.average_score >= 70 ? '#34d399' : 
                                 interview.average_score >= 50 ? '#fbbf24' : '#f87171' 
                    }}
                  >
                    {Math.round(interview.average_score)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-recent">
              <p>No recent interviews</p>
              <button className="btn btn-primary" onClick={() => navigate('/interview-setup')}>
                Start Your First Interview
              </button>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <button className="action-btn" onClick={() => navigate('/history')}>
            <Award size={20} />
            View History
          </button>
          <button className="action-btn" onClick={() => navigate('/interview-setup')}>
            <Target size={20} />
            Practice Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;