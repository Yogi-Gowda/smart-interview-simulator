import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import { 
  MessageSquare, 
  Mic, 
  MicOff, 
  Send, 
  Clock, 
  SkipForward,
  Loader,
  AlertCircle,
  Volume2
} from 'lucide-react';
import * as api from '../services/api';
import './Interview.css';

const Interview = () => {
  const navigate = useNavigate();
  const { currentSession, setInterviewData, interviewData } = useApp();
  
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [timeLeft, setTimeLeft] = useState(120);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [questionNumber, setQuestionNumber] = useState(1);
  const [feedback, setFeedback] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  
  const recognitionRef = useRef(null);
  const timerRef = useRef(null);
  const textareaRef = useRef(null);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        if (finalTranscript) {
          setTranscript(prev => prev + ' ' + finalTranscript);
          setAnswer(prev => prev + ' ' + finalTranscript);
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };
      
      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // Fetch first question
  useEffect(() => {
    if (!currentSession?.sessionId) {
      navigate('/interview-setup');
      return;
    }
    
    fetchQuestion();
  }, [currentSession]);

  // Timer
  useEffect(() => {
    if (currentQuestion && !showFeedback) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            handleSubmitAnswer();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [currentQuestion, showFeedback]);

  const fetchQuestion = async () => {
    try {
      setIsLoading(true);
      setError('');
      const question = await api.getNextQuestion(currentSession.sessionId);
      setCurrentQuestion(question);
      setTimeLeft(question.time_limit || 120);
      setAnswer('');
      setTranscript('');
      setShowFeedback(false);
      setFeedback(null);
    } catch (err) {
      console.error('Failed to fetch question:', err);
      setError('Failed to load question. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      setError('Please provide an answer');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const result = await api.submitAnswer(
        currentSession.sessionId,
        currentQuestion.question_id,
        answer,
        isRecording ? 'voice' : 'text'
      );
      
      setFeedback(result);
      setShowFeedback(true);
      
      // Update interview data
      setInterviewData(prev => ({
        ...prev,
        questionsAnswered: (prev?.questionsAnswered || 0) + 1,
        lastScore: result.scores.total_score
      }));
    } catch (err) {
      console.error('Failed to submit answer:', err);
      setError(err.message || 'Failed to submit answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNextQuestion = () => {
    setQuestionNumber(prev => prev + 1);
    fetchQuestion();
  };

  const handleEndInterview = async () => {
    try {
      const report = await api.endInterview(currentSession.sessionId);
      setInterviewData(prev => ({
        ...prev,
        finalReport: report
      }));
      navigate('/feedback', { state: { report } });
    } catch (err) {
      console.error('Failed to end interview:', err);
      navigate('/feedback');
    }
  };

  const toggleVoiceInput = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
    } else {
      try {
        recognitionRef.current?.start();
        setIsRecording(true);
      } catch (err) {
        console.error('Failed to start voice recognition:', err);
      }
    }
  };

  const speakQuestion = () => {
    if ('speechSynthesis' in window && currentQuestion) {
      const utterance = new SpeechSynthesisUtterance(currentQuestion.question);
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="interview-loading">
        <Loader size={48} className="spin" />
        <p>Loading your first question...</p>
      </div>
    );
  }

  return (
    <div className="interview">
      <div className="container">
        {/* Header */}
        <div className="interview-header">
          <div className="interview-info">
            <h1>Interview Session</h1>
            <div className="interview-meta">
              <span className="meta-item">
                Role: {currentSession?.jobRole?.replace('_', ' ')}
              </span>
              <span className="meta-item">
                Difficulty: {currentSession?.difficulty}
              </span>
              <span className="meta-item">
                Question #{questionNumber}
              </span>
            </div>
          </div>
          
          <div className="timer-display" style={{ 
            '--timer-color': timeLeft < 30 ? '#EF4444' : timeLeft < 60 ? '#F59E0B' : '#10B981' 
          }}>
            <Clock size={20} />
            <span className="timer-value">{formatTime(timeLeft)}</span>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-banner">
            <AlertCircle size={20} />
            <span>{error}</span>
            <button onClick={() => setError('')}>×</button>
          </div>
        )}

        {/* Question Section */}
        {currentQuestion && (
          <div className="question-section">
            <div className="question-card">
              <div className="question-header">
                <span className="question-label">Question</span>
                <button className="speak-btn" onClick={speakQuestion} title="Read aloud">
                  <Volume2 size={18} />
                </button>
              </div>
              <p className="question-text">{currentQuestion.question}</p>
              <div className="question-meta">
                <span className="category-tag">{currentQuestion.category}</span>
                {currentQuestion.skills && currentQuestion.skills.length > 0 && (
                  <div className="skills-hint">
                    {currentQuestion.skills.slice(0, 3).map((skill, i) => (
                      <span key={i} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Answer Section */}
        <div className="answer-section">
          <div className="answer-header">
            <h2>
              <MessageSquare size={20} />
              Your Answer
            </h2>
            <div className="answer-tools">
              <button 
                className={`voice-btn ${isRecording ? 'recording' : ''}`}
                onClick={toggleVoiceInput}
                disabled={!recognitionRef.current}
                title={isRecording ? 'Stop recording' : 'Start voice input'}
              >
                {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
                {isRecording ? 'Stop' : 'Voice'}
              </button>
            </div>
          </div>
          
          <textarea
            ref={textareaRef}
            className="answer-input"
            placeholder="Type your answer here... or use voice input"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={showFeedback}
          />
          
          {isRecording && (
            <div className="recording-indicator">
              <span className="recording-dot"></span>
              <span>Recording... Speak now</span>
            </div>
          )}
        </div>

        {/* Feedback Section */}
        {showFeedback && feedback && (
          <div className="feedback-section">
            <div className="feedback-card">
              <h3>Answer Feedback</h3>
              
              <div className="score-display">
                <div className="main-score">
                  <span className="score-value">{feedback.scores.total_score}</span>
                  <span className="score-grade">{feedback.scores.grade}</span>
                </div>
                <div className="score-breakdown">
                  <div className="score-item">
                    <span className="score-label">Content</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: `${feedback.scores.content_score}%` }}></div>
                    </div>
                    <span className="score-num">{feedback.scores.content_score}</span>
                  </div>
                  <div className="score-item">
                    <span className="score-label">Technical</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: `${feedback.scores.technical_score}%` }}></div>
                    </div>
                    <span className="score-num">{feedback.scores.technical_score}</span>
                  </div>
                  <div className="score-item">
                    <span className="score-label">Grammar</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: `${feedback.scores.grammar_score}%` }}></div>
                    </div>
                    <span className="score-num">{feedback.scores.grammar_score}</span>
                  </div>
                  <div className="score-item">
                    <span className="score-label">Confidence</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: `${feedback.scores.confidence_score}%` }}></div>
                    </div>
                    <span className="score-num">{feedback.scores.confidence_score}</span>
                  </div>
                </div>
              </div>
              
              <div className="feedback-content">
                <div className="feedback-item">
                  <strong>Overall:</strong> {feedback.feedback.overall}
                </div>
                
                {feedback.feedback.strengths.length > 0 && (
                  <div className="feedback-item">
                    <strong>Strengths:</strong>
                    <ul>
                      {feedback.feedback.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {feedback.feedback.weaknesses.length > 0 && (
                  <div className="feedback-item">
                    <strong>Areas to Improve:</strong>
                    <ul>
                      {feedback.feedback.weaknesses.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="interview-actions">
          {!showFeedback ? (
            <>
              <button
                className="btn btn-primary"
                onClick={handleSubmitAnswer}
                disabled={isSubmitting || !answer.trim()}
              >
                {isSubmitting ? (
                  <>
                    <Loader size={20} className="spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Send size={20} />
                    Submit Answer
                  </>
                )}
              </button>
              
              <button
                className="btn btn-secondary"
                onClick={handleEndInterview}
              >
                End Interview
              </button>
            </>
          ) : (
            <>
              <button
                className="btn btn-primary"
                onClick={handleNextQuestion}
              >
                <SkipForward size={20} />
                Next Question
              </button>
              
              <button
                className="btn btn-secondary"
                onClick={handleEndInterview}
              >
                End Interview & View Results
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Interview;