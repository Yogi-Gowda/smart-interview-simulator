import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../App';
import {
  Briefcase,
  Upload,
  FileText,
  CheckCircle,
  ArrowRight,
  Loader
} from 'lucide-react';
import * as api from '../services/api';
import './InterviewSetup.css';

const jobRoles = [
  { id: 'software_developer', name: 'Software Developer', icon: '💻' },
  { id: 'data_analyst', name: 'Data Analyst', icon: '📊' },
  { id: 'software_testing', name: 'Software Testing', icon: '🧪' },
  { id: 'fresher', name: 'Fresher', icon: '🎓' }
];

const difficulties = [
  { id: 'easy', name: 'Easy', description: 'Basic concepts', color: '#34d399' },
  { id: 'medium', name: 'Medium', description: 'Intermediate topics', color: '#fbbf24' },
  { id: 'hard', name: 'Hard', description: 'Advanced concepts', color: '#f87171' }
];

const InterviewSetup = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { userId, setCurrentSession, setInterviewData } = useApp();

  const [selectedRole, setSelectedRole] = useState(location.state?.role || '');
  const [selectedDifficulty, setSelectedDifficulty] = useState('medium');
  const [resumeFile, setResumeFile] = useState(null);
  const [resumePreview, setResumePreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [resumeUploaded, setResumeUploaded] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!validTypes.includes(file.type)) {
        setError('Please upload a PDF or DOCX file');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }
      setResumeFile(file);
      setResumePreview({
        name: file.name,
        size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
        type: file.type.includes('pdf') ? 'PDF' : 'DOCX'
      });
      setError('');
    }
  };

  const handleStartInterview = async () => {
    if (!selectedRole) {
      setError('Please select a job role');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Start interview session
      const sessionResponse = await api.startInterview(
        userId,
        selectedRole,
        selectedDifficulty
      );

      const sessionId = sessionResponse.session_id;

      // Upload resume if provided
      if (resumeFile) {
        try {
          await api.uploadResume(sessionId, resumeFile);
          setResumeUploaded(true);
        } catch (resumeError) {
          console.warn('Resume upload failed, continuing without resume:', resumeError);
        }
      }

      // Set current session
      setCurrentSession({
        sessionId,
        jobRole: selectedRole,
        difficulty: selectedDifficulty,
        resumeUploaded
      });

      setInterviewData({
        jobRole: selectedRole,
        difficulty: selectedDifficulty,
        startTime: new Date().toISOString()
      });

      // Navigate to interview page
      navigate('/interview');
    } catch (err) {
      console.error('Failed to start interview:', err);
      setError(err.message || 'Failed to start interview. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="interview-setup">
      <div className="container">
        <div className="setup-header">
          <h1 className="setup-title">Setup Your Interview</h1>
          <p className="setup-subtitle">Choose your role, difficulty, and optionally upload your resume</p>
        </div>

        <div className="setup-content">
          {/* Job Role Selection */}
          <section className="setup-section">
            <h2 className="section-title">
              <Briefcase size={20} />
              Select Job Role
            </h2>
            <div className="role-grid">
              {jobRoles.map((role) => (
                <div
                  key={role.id}
                  className={`role-option ${selectedRole === role.id ? 'selected' : ''}`}
                  onClick={() => setSelectedRole(role.id)}
                >
                  <span className="role-icon">{role.icon}</span>
                  <span className="role-name">{role.name}</span>
                  {selectedRole === role.id && (
                    <CheckCircle size={20} className="check-icon" />
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Difficulty Selection */}
          <section className="setup-section">
            <h2 className="section-title">
              <span>🎯</span>
              Select Difficulty
            </h2>
            <div className="difficulty-grid">
              {difficulties.map((diff) => (
                <div
                  key={diff.id}
                  className={`difficulty-option ${selectedDifficulty === diff.id ? 'selected' : ''}`}
                  onClick={() => setSelectedDifficulty(diff.id)}
                  style={{ '--diff-color': diff.color }}
                >
                  <span className="difficulty-name">{diff.name}</span>
                  <span className="difficulty-desc">{diff.description}</span>
                  {selectedDifficulty === diff.id && (
                    <CheckCircle size={20} className="check-icon" />
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Resume Upload */}
          <section className="setup-section">
            <h2 className="section-title">
              <Upload size={20} />
              Upload Resume (Optional)
            </h2>
            <p className="section-description">
              Upload your resume to get personalized questions based on your skills
            </p>

            {!resumePreview ? (
              <div className="upload-area">
                <input
                  type="file"
                  id="resume-upload"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="file-input"
                />
                <label htmlFor="resume-upload" className="upload-label">
                  <FileText size={40} />
                  <span className="upload-text">Click to upload resume</span>
                  <span className="upload-hint">PDF or DOCX (max 5MB)</span>
                </label>
              </div>
            ) : (
              <div className="resume-preview">
                <div className="resume-info">
                  <FileText size={24} />
                  <div className="resume-details">
                    <span className="resume-name">{resumePreview.name}</span>
                    <span className="resume-meta">{resumePreview.type} • {resumePreview.size}</span>
                  </div>
                </div>
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    setResumeFile(null);
                    setResumePreview(null);
                  }}
                >
                  Remove
                </button>
              </div>
            )}
          </section>

          {/* Error Message */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Start Button */}
          <div className="setup-actions">
            <button
              className="btn btn-primary btn-lg"
              onClick={handleStartInterview}
              disabled={isLoading || !selectedRole}
            >
              {isLoading ? (
                <>
                  <Loader size={20} className="spin" />
                  Starting Interview...
                </>
              ) : (
                <>
                  Start Interview
                  <ArrowRight size={20} />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewSetup;