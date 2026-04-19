import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../App';
import { 
  Award, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  BookOpen,
  ArrowRight,
  Home,
  BarChart3
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import './Feedback.css';

const Feedback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { interviewData } = useApp();
  
  const [report, setReport] = useState(location.state?.report || interviewData?.finalReport || null);

  useEffect(() => {
    if (!report) {
      // Try to get from session storage
      const savedReport = sessionStorage.getItem('interviewReport');
      if (savedReport) {
        setReport(JSON.parse(savedReport));
      }
    } else {
      sessionStorage.setItem('interviewReport', JSON.stringify(report));
    }
  }, [report]);

  if (!report) {
    return (
      <div className="feedback-empty">
        <h2>No Interview Report Found</h2>
        <p>Complete an interview to see your results here.</p>
        <button className="btn btn-primary" onClick={() => navigate('/interview-setup')}>
          Start New Interview
        </button>
      </div>
    );
  }

  const scoreData = [
    { subject: 'Content', value: report?.scores_breakdown?.content ?? 0, fullMark: 100 },
    { subject: 'Technical', value: report?.scores_breakdown?.technical ?? 0, fullMark: 100 },
    { subject: 'Grammar', value: report?.scores_breakdown?.grammar ?? 0, fullMark: 100 },
    { subject: 'Confidence', value: report?.scores_breakdown?.confidence ?? 0, fullMark: 100 }
  ];

  const getGradeColor = (grade) => {
    if (!grade) return '#64748B';
    if (grade.startsWith('A')) return '#10B981';
    if (grade.startsWith('B')) return '#3B82F6';
    if (grade === 'C') return '#F59E0B';
    return '#EF4444';
  };

  // Safe access to report properties
  const averageScore = report?.average_score ?? 0;
  const totalQuestions = report?.total_questions ?? 0;
  const jobRole = report?.job_role ?? 'Interview';
  const difficulty = report?.difficulty ?? 'N/A';
  const weakAreas = report?.weak_areas ?? [];
  const strengths = report?.strengths ?? [];
  const improvementSuggestions = report?.improvement_suggestions ?? [];
  const overallFeedback = report?.overall_feedback ?? 'No feedback available.';

  return (
    <div className="feedback">
      <div className="container">
        {/* Header */}
        <div className="feedback-header">
          <div className="header-content">
            <h1>Interview Complete!</h1>
            <p>Here's your performance summary</p>
          </div>
          <div className="header-actions">
            <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
              <BarChart3 size={18} />
              Dashboard
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/interview-setup')}>
              <ArrowRight size={18} />
              Practice Again
            </button>
          </div>
        </div>

        {/* Main Score Card */}
        <div className="score-card">
          <div className="score-main">
            <div className="score-circle" style={{ '--score-color': getGradeColor(report?.scores_breakdown?.content > 70 ? 'A' : report?.scores_breakdown?.content > 50 ? 'B' : 'C') }}>
              <svg viewBox="0 0 100 100">
                <circle className="score-bg" cx="50" cy="50" r="45" />
                <circle 
                  className="score-progress" 
                  cx="50" 
                  cy="50" 
                  r="45"
                  style={{ 
                    strokeDasharray: `${(averageScore / 100) * 283} 283`,
                    stroke: getGradeColor(report?.scores_breakdown?.content > 70 ? 'A' : report?.scores_breakdown?.content > 50 ? 'B' : 'C')
                  }}
                />
              </svg>
              <div className="score-text">
                <span className="score-number">{averageScore}</span>
                <span className="score-label">Average</span>
              </div>
            </div>
          </div>
          
          <div className="score-details">
            <div className="detail-item">
              <span className="detail-label">Total Questions</span>
              <span className="detail-value">{totalQuestions}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Job Role</span>
              <span className="detail-value">{jobRole.replace('_', ' ')}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Difficulty</span>
              <span className="detail-value">{difficulty}</span>
            </div>
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="breakdown-section">
          <h2>Score Breakdown</h2>
          <div className="breakdown-grid">
            <div className="breakdown-card">
              <div className="breakdown-header">
                <span className="breakdown-title">Content</span>
                <span className="breakdown-score" style={{ color: getGradeColor(scoreData[0].value >= 70 ? 'A' : scoreData[0].value >= 50 ? 'B' : 'C') }}>
                  {scoreData[0].value}
                </span>
              </div>
              <div className="breakdown-bar">
                <div className="bar-fill" style={{ width: `${scoreData[0].value}%`, background: getGradeColor(scoreData[0].value >= 70 ? 'A' : scoreData[0].value >= 50 ? 'B' : 'C') }}></div>
              </div>
              <p className="breakdown-desc">Quality and depth of your answers</p>
            </div>
            
            <div className="breakdown-card">
              <div className="breakdown-header">
                <span className="breakdown-title">Technical</span>
                <span className="breakdown-score" style={{ color: getGradeColor(scoreData[1].value >= 70 ? 'A' : scoreData[1].value >= 50 ? 'B' : 'C') }}>
                  {scoreData[1].value}
                </span>
              </div>
              <div className="breakdown-bar">
                <div className="bar-fill" style={{ width: `${scoreData[1].value}%`, background: getGradeColor(scoreData[1].value >= 70 ? 'A' : scoreData[1].value >= 50 ? 'B' : 'C') }}></div>
              </div>
              <p className="breakdown-desc">Technical knowledge demonstrated</p>
            </div>
            
            <div className="breakdown-card">
              <div className="breakdown-header">
                <span className="breakdown-title">Grammar</span>
                <span className="breakdown-score" style={{ color: getGradeColor(scoreData[2].value >= 70 ? 'A' : scoreData[2].value >= 50 ? 'B' : 'C') }}>
                  {scoreData[2].value}
                </span>
              </div>
              <div className="breakdown-bar">
                <div className="bar-fill" style={{ width: `${scoreData[2].value}%`, background: getGradeColor(scoreData[2].value >= 70 ? 'A' : scoreData[2].value >= 50 ? 'B' : 'C') }}></div>
              </div>
              <p className="breakdown-desc">Language and grammar quality</p>
            </div>
            
            <div className="breakdown-card">
              <div className="breakdown-header">
                <span className="breakdown-title">Confidence</span>
                <span className="breakdown-score" style={{ color: getGradeColor(scoreData[3].value >= 70 ? 'A' : scoreData[3].value >= 50 ? 'B' : 'C') }}>
                  {scoreData[3].value}
                </span>
              </div>
              <div className="breakdown-bar">
                <div className="bar-fill" style={{ width: `${scoreData[3].value}%`, background: getGradeColor(scoreData[3].value >= 70 ? 'A' : scoreData[3].value >= 50 ? 'B' : 'C') }}></div>
              </div>
              <p className="breakdown-desc">Confidence in communication</p>
            </div>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="chart-section">
          <h2>Skills Radar</h2>
          <div className="radar-container">
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={scoreData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94A3B8', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748B' }} />
                <Radar
                  name="Score"
                  dataKey="value"
                  stroke="#4F46E5"
                  fill="#4F46E5"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weak Areas */}
        {weakAreas.length > 0 && (
          <div className="areas-section weak-areas">
            <h2>
              <AlertTriangle size={20} />
              Areas to Improve
            </h2>
            <div className="areas-grid">
              {weakAreas.map((area, index) => (
                <div key={index} className="area-card">
                  <div className="area-header">
                    <span className="area-name">{area.category}</span>
                    <span className="area-score">{area.average_score}%</span>
                  </div>
                  <p className="area-recommendation">{area.recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Strengths */}
        {strengths.length > 0 && (
          <div className="areas-section strengths">
            <h2>
              <CheckCircle size={20} />
              Your Strengths
            </h2>
            <div className="areas-grid">
              {strengths.map((strength, index) => (
                <div key={index} className="area-card strength-card">
                  <div className="area-header">
                    <span className="area-name">{strength.category}</span>
                    <span className="area-score">{strength.average_score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Overall Feedback */}
        <div className="overall-feedback">
          <h2>
            <Award size={20} />
            Overall Feedback
          </h2>
          <p>{overallFeedback}</p>
        </div>

        {/* Improvement Plan */}
        {improvementSuggestions.length > 0 && (
          <div className="improvement-section">
            <h2>
              <BookOpen size={20} />
              Improvement Plan
            </h2>
            <div className="improvement-list">
              {improvementSuggestions.map((item, index) => (
                <div key={index} className="improvement-item">
                  <div className="improvement-priority" data-priority={item.priority}>
                    {item.priority}
                  </div>
                  <div className="improvement-content">
                    <h3>{item.area}</h3>
                    <p>{item.action}</p>
                    <div className="improvement-resources">
                      <span className="resources-label">Resources:</span>
                      {item.resources.map((res, i) => (
                        <span key={i} className="resource-tag">{res}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="feedback-nav">
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            <Home size={18} />
            Home
          </button>
          <button className="btn btn-primary" onClick={() => navigate('/interview-setup')}>
            <ArrowRight size={18} />
            Practice Again
          </button>
        </div>
      </div>
    </div>
  );
};

export default Feedback;