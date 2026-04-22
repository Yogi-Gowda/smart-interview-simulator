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
  Sparkles,
  CheckCircle2,
  TrendingUp,
  Code2
} from 'lucide-react';
import './Home.css';

const Home = () => {
  const { userId } = useApp();

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Questions',
      description: 'Intelligent question generation based on job role and difficulty level'
    },
    {
      icon: Mic,
      title: 'Voice & Text Input',
      description: 'Practice with both voice and text answers for flexibility'
    },
    {
      icon: BarChart3,
      title: 'Real-Time Analytics',
      description: 'Detailed performance metrics and improvement insights'
    },
    {
      icon: Target,
      title: 'Weak Area Detection',
      description: 'Identify knowledge gaps and focus on improvement areas'
    },
    {
      icon: TrendingUp,
      title: 'Progress Tracking',
      description: 'Watch your interview skills improve over time'
    },
    {
      icon: Zap,
      title: 'Instant Feedback',
      description: 'Get immediate AI-powered feedback on your responses'
    }
  ];

  const jobRoles = [
    { name: 'Software Developer', icon: '💻' },
    { name: 'Data Analyst', icon: '📊' },
    { name: 'QA Engineer', icon: '🧪' },
    { name: 'MCA Fresher', icon: '🎓' }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] },
    },
  };

  return (
    <div className="home">
      {/* Background Effects */}
      <div className="hero-bg">
        <div className="hero-grid"></div>
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      {/* Hero Section */}
      <motion.section 
        className="hero"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <div className="hero-content">
          {/* Badge */}
          <motion.div 
            className="hero-badge"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
          >
            <div className="hero-badge-icon">
              <Sparkles size={12} />
            </div>
            <span className="hero-badge-text">AI-Powered Interview Platform</span>
          </motion.div>

          {/* Title */}
          <motion.h1 
            className="hero-title"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
          >
            <span className="hero-title-line">Master Your</span>
            <span className="hero-title-line">Interview Skills</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p 
            className="hero-subtitle"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
          >
            Practice with AI-generated questions, get instant feedback, and build confidence for your next opportunity.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div 
            className="hero-actions"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
          >
            <Link to="/interview-setup" className="hero-cta-primary">
              Start Interview
              <ArrowRight size={20} />
            </Link>
            <Link to="/dashboard" className="hero-cta-secondary">
              View Dashboard
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div 
            className="hero-stats"
            variants={itemVariants}
            initial="hidden"
            animate="visible"
          >
            <div className="hero-stat">
              <div className="hero-stat-value">500+</div>
              <div className="hero-stat-label">Questions</div>
            </div>
            <div className="hero-stat-divider"></div>
            <div className="hero-stat">
              <div className="hero-stat-value">4</div>
              <div className="hero-stat-label">Job Roles</div>
            </div>
            <div className="hero-stat-divider"></div>
            <div className="hero-stat">
              <div className="hero-stat-value">3</div>
              <div className="hero-stat-label">Difficulty Levels</div>
            </div>
          </motion.div>
        </div>
      </motion.section>

      {/* Features Section */}
      <motion.section 
        className="features"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.6 }}
      >
        <div className="features-header">
          <h2 className="features-title">Powerful Features</h2>
          <p className="features-subtitle">Everything you need to ace your interviews</p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <motion.div 
              key={index}
              className="feature-card"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ 
                duration: 0.5, 
                delay: index * 0.1,
                ease: [0.16, 1, 0.3, 1]
              }}
            >
              <div className="feature-icon">
                <feature.icon size={28} />
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-desc">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Job Roles Section */}
      <motion.section 
        className="roles"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.6 }}
      >
        <div className="roles-header">
          <h2 className="roles-title">Choose Your Path</h2>
          <p className="roles-subtitle">Select a job role to start practicing</p>
        </div>

        <div className="roles-grid">
          {jobRoles.map((role, index) => (
            <motion.div 
              key={index}
              className="role-card"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ 
                duration: 0.4, 
                delay: index * 0.1,
                ease: [0.16, 1, 0.3, 1]
              }}
              whileHover={{ scale: 1.02 }}
            >
              <span className="role-icon">{role.icon}</span>
              <span className="role-name">{role.name}</span>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section 
        className="cta-section"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <div className="cta-content">
          <h2 className="cta-title">Ready to Begin?</h2>
          <p className="cta-subtitle">Start your interview practice journey today</p>
          <Link to="/interview-setup" className="cta-button">
            Get Started
            <ArrowRight size={20} />
          </Link>
        </div>
      </motion.section>
    </div>
  );
};

export default Home;
            whileInView="visible"
            viewport={{ once: true }}
          >
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={idx}
                  variants={itemVariants}
                  whileHover={{ y: -8, transition: { duration: 0.2 } }}
                  className="group card"
                >
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${feature.color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon size={24} className="text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-slate-400 text-sm leading-relaxed">{feature.description}</p>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </motion.section>

      {/* Job Roles Section */}
      <motion.section 
        className="py-24 px-4 relative"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
      >
        <div className="container-lg">
          <motion.div 
            className="text-center mb-16 space-y-4"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white">Choose Your Role</h2>
            <p className="text-xl text-slate-400">Select a job role and start practicing</p>
          </motion.div>

          <motion.div 
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {jobRoles.map((role, idx) => {
              const Icon = role.icon;
              return (
                <motion.div
                  key={idx}
                  variants={itemVariants}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="group"
                >
                  <Link
                    to="/interview-setup"
                    className="card h-full flex flex-col items-center justify-center text-center gap-4 cursor-pointer"
                  >
                    <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-r ${role.color} group-hover:scale-125 transition-transform duration-300`}>
                      <Icon size={32} className="text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-white">{role.name}</h3>
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      whileHover={{ opacity: 1, x: 0 }}
                      className="flex items-center gap-1 text-indigo-400 font-semibold mt-2"
                    >
                      Practice Now <ArrowRight size={16} />
                    </motion.div>
                  </Link>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </motion.section>

      {/* CTA Section - Final */}
      <motion.section 
        className="py-24 px-4 relative"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
      >
        <div className="container-lg">
          <motion.div 
            className="text-center space-y-8 py-16 px-8 rounded-3xl bg-gradient-to-r from-indigo-900/30 to-purple-900/30 border border-indigo-500/20 backdrop-blur-xl"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <motion.div variants={itemVariants}>
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Ready to Ace Your Interview?</h2>
              <p className="text-xl text-slate-300">Start practicing now and build unshakeable confidence</p>
            </motion.div>
            <motion.div variants={itemVariants}>
              <Link to="/interview-setup" className="btn btn-primary btn-lg">
                Begin Now <ArrowRight size={20} />
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </motion.section>
    </div>
  );
};

export default Home;
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