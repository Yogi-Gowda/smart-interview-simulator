import React from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../App';
import { 
  Brain, 
  FileText, 
  MessageSquare, 
  BarChart3, 
  Clock, 
  Target,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import './Home.css';

const Home = () => {
  const { userId } = useApp();

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Questions',
      description: 'Smart question generation based on job role and difficulty level'
    },
    {
      icon: FileText,
      title: 'Resume Analysis',
      description: 'Upload your resume for personalized, skill-based questions'
    },
    {
      icon: MessageSquare,
      title: 'Text & Voice Input',
      description: 'Answer using text or voice input for flexibility'
    },
    {
      icon: BarChart3,
      title: 'Performance Analytics',
      description: 'Track your progress with detailed scores and insights'
    },
    {
      icon: Clock,
      title: 'Timed Practice',
      description: 'Simulate real interview conditions with answer timers'
    },
    {
      icon: Target,
      title: 'Weak Area Detection',
      description: 'Identify and improve your knowledge gaps'
    }
  ];

  const jobRoles = [
    'Software Developer',
    'Data Analyst',
    'Software Testing',
    'MCA Fresher'
  ];

  const difficulties = ['Easy', 'Medium', 'Hard'];

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-background">
          <div className="hero-gradient"></div>
          <div className="hero-pattern"></div>
        </div>
        
        <div className="container">
          <div className="hero-content">
            <div className="hero-badge">
              <Sparkles size={16} />
              <span>AI-Powered Interview Practice</span>
            </div>
            
            <h1 className="hero-title">
              Master Your
              <span className="hero-highlight"> Interview</span>
              Skills
            </h1>
            
            <p className="hero-subtitle">
              Practice with AI-generated questions, get instant feedback, 
              and track your progress to ace your next interview.
            </p>
            
            <div className="hero-actions">
              <Link to="/interview-setup" className="btn btn-primary btn-lg">
                Start Interview
                <ArrowRight size={20} />
              </Link>
              <Link to="/dashboard" className="btn btn-secondary btn-lg">
                View Dashboard
              </Link>
            </div>
            
            <div className="hero-stats">
              <div className="stat-item">
                <span className="stat-value">500+</span>
                <span className="stat-label">Questions</span>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <span className="stat-value">4</span>
                <span className="stat-label">Job Roles</span>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <span className="stat-value">3</span>
                <span className="stat-label">Difficulty Levels</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Powerful Features</h2>
            <p className="section-subtitle">
              Everything you need to prepare for your next big interview
            </p>
          </div>
          
          <div className="features-grid">
            {features.map((feature, index) => (
              <div 
                key={index} 
                className="feature-card"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="feature-icon">
                  <feature.icon size={24} />
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Job Roles Section */}
      <section className="job-roles">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Interview Roles</h2>
            <p className="section-subtitle">
              Choose your target role and start practicing
            </p>
          </div>
          
          <div className="roles-grid">
            {jobRoles.map((role, index) => (
              <div key={index} className="role-card">
                <div className="role-icon">
                  <Brain size={32} />
                </div>
                <h3 className="role-name">{role}</h3>
                <Link 
                  to="/interview-setup" 
                  className="role-link"
                  state={{ role: role.toLowerCase().replace(' ', '_') }}
                >
                  Practice Now <ArrowRight size={16} />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Difficulty Section */}
      <section className="difficulty-section">
        <div className="container">
          <div className="difficulty-cards">
            {difficulties.map((diff, index) => (
              <div key={index} className={`difficulty-card difficulty-${diff.toLowerCase()}`}>
                <h3 className="difficulty-title">{diff}</h3>
                <p className="difficulty-description">
                  {diff === 'Easy' && 'Perfect for beginners and freshers'}
                  {diff === 'Medium' && 'For intermediate practitioners'}
                  {diff === 'Hard' && 'Challenge yourself with advanced topics'}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2 className="cta-title">Ready to Ace Your Interview?</h2>
            <p className="cta-subtitle">
              Start practicing now and build confidence for your next opportunity
            </p>
            <Link to="/interview-setup" className="btn btn-primary btn-lg">
              Get Started
              <ArrowRight size={20} />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <p className="footer-text">
              Smart Interview Simulator — AI-Powered Interview Practice
            </p>
            <p className="footer-user">User ID: {userId}</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;