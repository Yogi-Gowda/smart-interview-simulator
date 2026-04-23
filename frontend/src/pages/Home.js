import React from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../App';
import { motion } from 'framer-motion';
import {
  Brain,
  Zap,
  BarChart3,
  Mic,
  Target,
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import './Home.css';

const container = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] }
  }
};

const Home = () => {
  const { userId } = useApp();

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Questions',
      description: 'Intelligent question generation tailored to your role and skill level'
    },
    {
      icon: Mic,
      title: 'Voice & Text Input',
      description: 'Practice answering with both voice recording and text for flexibility'
    },
    {
      icon: BarChart3,
      title: 'Real-Time Analytics',
      description: 'Detailed performance metrics with actionable improvement insights'
    },
    {
      icon: Target,
      title: 'Weak Area Detection',
      description: 'Pinpoint knowledge gaps and focus your preparation effectively'
    },
    {
      icon: TrendingUp,
      title: 'Progress Tracking',
      description: 'Watch your interview skills improve across sessions over time'
    },
    {
      icon: Zap,
      title: 'Instant Feedback',
      description: 'Get immediate AI-powered analysis on every response you give'
    }
  ];

  const jobRoles = [
    { name: 'Software Developer', icon: '💻', desc: 'Full-stack, backend, frontend' },
    { name: 'Data Analyst', icon: '📊', desc: 'SQL, Python, visualization' },
    { name: 'QA Engineer', icon: '🧪', desc: 'Testing, automation, CI/CD' },
    { name: 'MCA Fresher', icon: '🎓', desc: 'Core CS, aptitude, basics' }
  ];

  return (
    <div className="home">
      {/* Ambient background */}
      <div className="home__ambient" aria-hidden="true">
        <div className="home__glow home__glow--1" />
        <div className="home__glow home__glow--2" />
      </div>

      {/* Hero */}
      <motion.section
        className="hero"
        variants={container}
        initial="hidden"
        animate="visible"
      >
        <div className="hero__content">
          <motion.div className="hero__badge" variants={item}>
            <span className="hero__badge-dot" />
            <span>AI-Powered Interview Platform</span>
          </motion.div>

          <motion.h1 className="hero__title" variants={item}>
            Master Your
            <br />
            <span className="hero__title-accent">Interview Skills</span>
          </motion.h1>

          <motion.p className="hero__subtitle" variants={item}>
            Practice with AI-generated questions, get instant feedback,
            and track your improvement over time.
          </motion.p>

          <motion.div className="hero__actions" variants={item}>
            <Link to="/interview-setup" className="btn btn-primary btn-lg">
              Start Interview
              <ArrowRight size={18} />
            </Link>
            <Link to="/dashboard" className="btn btn-secondary btn-lg">
              View Dashboard
            </Link>
          </motion.div>

          <motion.div className="hero__stats" variants={item}>
            <div className="hero__stat">
              <span className="hero__stat-value">500+</span>
              <span className="hero__stat-label">Questions</span>
            </div>
            <div className="hero__stat-sep" />
            <div className="hero__stat">
              <span className="hero__stat-value">4</span>
              <span className="hero__stat-label">Job Roles</span>
            </div>
            <div className="hero__stat-sep" />
            <div className="hero__stat">
              <span className="hero__stat-value">3</span>
              <span className="hero__stat-label">Difficulty Levels</span>
            </div>
          </motion.div>
        </div>
      </motion.section>

      {/* Features */}
      <section className="features">
        <div className="container">
          <motion.div
            className="section-header"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          >
            <p className="section-label">Features</p>
            <h2 className="section-title">Everything you need to ace your interview</h2>
          </motion.div>

          <motion.div
            className="features__grid"
            variants={container}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-60px" }}
          >
            {features.map((feature, index) => (
              <motion.div key={index} className="feature-card" variants={item}>
                <div className="feature-card__icon">
                  <feature.icon size={20} />
                </div>
                <h3 className="feature-card__title">{feature.title}</h3>
                <p className="feature-card__desc">{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Roles */}
      <section className="roles">
        <div className="container">
          <motion.div
            className="section-header"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          >
            <p className="section-label">Roles</p>
            <h2 className="section-title">Practice for your target role</h2>
          </motion.div>

          <motion.div
            className="roles__grid"
            variants={container}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-60px" }}
          >
            {jobRoles.map((role, index) => (
              <motion.div key={index} className="role-card" variants={item}>
                <span className="role-card__icon">{role.icon}</span>
                <div className="role-card__info">
                  <span className="role-card__name">{role.name}</span>
                  <span className="role-card__desc">{role.desc}</span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta">
        <div className="container">
          <motion.div
            className="cta__inner"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          >
            <h2 className="cta__title">Ready to begin?</h2>
            <p className="cta__subtitle">Start your first mock interview and get personalized feedback in minutes.</p>
            <Link to="/interview-setup" className="btn btn-primary btn-lg">
              Get Started <ArrowRight size={18} />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <div className="container">
          <p>Smart Interview Simulator &middot; Session {userId?.split('_')[1]?.slice(-6)}</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;