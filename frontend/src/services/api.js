// API Service for Smart Interview Simulator
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// ==================== Health Check ====================
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'unhealthy', error: error.message };
  }
};

// ==================== Interview Setup ====================
export const startInterview = async (userId, jobRole, difficulty) => {
  try {
    const response = await api.post('/interview/start', {
      user_id: userId,
      job_role: jobRole,
      difficulty: difficulty,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const getJobRoles = async () => {
  try {
    const response = await api.get('/roles');
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// ==================== Resume Upload ====================
export const uploadResume = async (sessionId, file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/resume/upload?session_id=${sessionId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// ==================== Questions ====================
export const getNextQuestion = async (sessionId) => {
  try {
    const response = await api.get(`/question/${sessionId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const getFollowUpQuestion = async (sessionId, originalQuestion, originalAnswer) => {
  try {
    const response = await api.post('/question/follow-up', {
      session_id: sessionId,
      original_question: originalQuestion,
      original_answer: originalAnswer,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// ==================== Answer Submission ====================
export const submitAnswer = async (sessionId, questionId, answerText, answerType = 'text') => {
  try {
    const response = await api.post('/answer/submit', {
      session_id: sessionId,
      question_id: questionId,
      answer_text: answerText,
      answer_type: answerType,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// ==================== Session Management ====================
export const getSessionStatus = async (sessionId) => {
  try {
    const response = await api.get(`/session/${sessionId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const endInterview = async (sessionId) => {
  try {
    const response = await api.post('/interview/end', null, {
      params: { session_id: sessionId },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// ==================== History & Dashboard ====================
export const getInterviewHistory = async (userId) => {
  try {
    const response = await api.get(`/history/${userId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const getUserDashboard = async (userId) => {
  try {
    const response = await api.get(`/dashboard/${userId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const getSessionAnalytics = async (sessionId) => {
  try {
    const response = await api.get(`/analytics/${sessionId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export default api;