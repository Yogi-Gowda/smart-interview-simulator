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
      description: 'Intelligent question generation based on job role and difficulty level',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: Mic,
      title: 'Voice & Text Input',
      description: 'Practice with both voice and text answers for flexibility',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: BarChart3,
      title: 'Real-Time Analytics',
      description: 'Detailed performance metrics and improvement insights',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: Target,
      title: 'Weak Area Detection',
      description: 'Identify knowledge gaps and focus on improvement areas',
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: TrendingUp,
      title: 'Progress Tracking',
      description: 'Watch your interview skills improve over time',
      color: 'from-indigo-500 to-blue-500'
    },
    {
      icon: Zap,
      title: 'Instant Feedback',
      description: 'Get immediate AI-powered feedback on your responses',
      color: 'from-yellow-500 to-orange-500'
    }
  ];

  const jobRoles = [
    { name: 'Software Developer', icon: Code2, color: 'from-blue-500 to-blue-600' },
    { name: 'Data Analyst', icon: BarChart3, color: 'from-green-500 to-green-600' },
    { name: 'QA Engineer', icon: CheckCircle2, color: 'from-purple-500 to-purple-600' },
    { name: 'MCA Fresher', icon: Sparkles, color: 'from-pink-500 to-pink-600' }
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
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.5, ease: 'easeOut' },
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Hero Section - Modern */}
      <motion.section 
        className="relative min-h-screen flex items-center justify-center pt-20 pb-20 px-4 overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        {/* Animated Background Elements */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-20 left-1/4 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
          <div className="absolute top-40 right-1/4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute bottom-20 left-1/3 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>

        <motion.div 
          className="max-w-4xl mx-auto text-center space-y-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Badge */}
          <motion.div 
            variants={itemVariants}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 rounded-full backdrop-blur-xl"
          >
            <Sparkles size={16} className="text-indigo-400" />
            <span className="text-sm font-semibold text-indigo-200">AI-Powered Interview Platform</span>
          </motion.div>

          {/* Main Headline */}
          <motion.div variants={itemVariants} className="space-y-4">
            <h1 className="text-6xl md:text-7xl font-bold tracking-tight">
              <span className="text-white">Master Your</span>
              <br />
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 text-transparent bg-clip-text">
                Interview Skills
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
              Practice with AI-generated questions, get instant feedback, and build confidence for your next opportunity.
            </p>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div 
            variants={itemVariants}
            className="flex flex-col sm:flex-row gap-4 justify-center pt-4"
          >
            <Link
              to="/interview-setup"
              className="btn btn-primary btn-lg group"
            >
              <span>Start Interview</span>
              <motion.div
                animate={{ x: [0, 4, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <ArrowRight size={20} />
              </motion.div>
            </Link>
            <Link
              to="/dashboard"
              className="btn btn-secondary btn-lg"
            >
              View Dashboard
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div 
            variants={itemVariants}
            className="grid grid-cols-3 gap-4 pt-8"
          >
            {[
              { value: '500+', label: 'Questions' },
              { value: '4', label: 'Job Roles' },
              { value: '3', label: 'Difficulty Levels' }
            ].map((stat, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xl hover:bg-white/10 transition-all duration-300">
                <div className="text-2xl font-bold text-indigo-400">{stat.value}</div>
                <div className="text-xs text-slate-400 mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </motion.div>
      </motion.section>

      {/* Features Section - Modern Grid */}
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
            <h2 className="text-4xl md:text-5xl font-bold text-white">Powerful Features</h2>
            <p className="text-xl text-slate-400">Everything you need to ace your interviews</p>
          </motion.div>

          <motion.div 
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
            variants={containerVariants}
            initial="hidden"
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