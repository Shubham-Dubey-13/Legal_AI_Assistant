import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/authStore'

const FEATURES = [
  { icon: '🤖', title: '8 AI Agents', desc: 'LangGraph orchestrated multi-agent system' },
  { icon: '🔍', title: 'RAG Pipeline', desc: 'ChromaDB hybrid search over legal corpus' },
  { icon: '📜', title: 'IPC/BNS Mapping', desc: 'Full IPC to BNS 2023 section mapping' },
  { icon: '⚖️', title: 'Case Law Search', desc: 'Supreme Court & High Court judgments' },
  { icon: '✍️', title: 'Draft Maker', desc: 'FIR, notices, petitions, affidavits' },
  { icon: '🔮', title: 'Judgment AI', desc: 'ML-based case outcome prediction' },
  { icon: '🌐', title: '6 Languages', desc: 'Hindi, Tamil, Telugu, Bengali, Marathi' },
  { icon: '🎤', title: 'Voice Support', desc: 'Whisper ASR + TTS responses' },
  { icon: '📊', title: 'Analytics', desc: 'Agent performance dashboard' },
]

const STATS = [
  { value: '50+', label: 'Indian Legal Acts' },
  { value: '8', label: 'AI Agents' },
  { value: '~1.4s', label: 'Avg Response' },
  { value: '95%', label: 'Accuracy Rate' },
]

const TECH_STACK = [
  { name: 'LangGraph', color: '#6366f1', desc: 'Agent Orchestration' },
  { name: 'GPT-4o', color: '#10b981', desc: 'LLM Backend' },
  { name: 'ChromaDB', color: '#f59e0b', desc: 'Vector Database' },
  { name: 'FastAPI', color: '#06b6d4', desc: 'REST + WebSocket' },
  { name: 'React 18', color: '#61dafb', desc: 'Frontend' },
  { name: 'LangChain', color: '#8b5cf6', desc: 'AI Framework' },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()

  return (
    <div style={{ minHeight: '100vh', overflowX: 'hidden' }}>
      {/* Nav */}
      <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1.25rem 3rem', borderBottom: '1px solid var(--border)', backdropFilter: 'blur(16px)', position: 'sticky', top: 0, zIndex: 50, background: 'var(--bg-glass)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 36, height: 36, background: 'var(--gradient-primary)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', boxShadow: 'var(--shadow-glow-sm)' }}>⚖️</div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '1rem', background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>LegalAI</div>
            <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>Multi-Agent Indian Law AI</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          {isAuthenticated ? (
            <button className="btn btn-primary" onClick={() => navigate('/chat')}>Open App →</button>
          ) : (
            <>
              <button className="btn btn-ghost" onClick={() => navigate('/auth')}>Login</button>
              <button className="btn btn-primary" onClick={() => navigate('/auth')}>Get Started Free →</button>
            </>
          )}
        </div>
      </nav>

      {/* Hero */}
      <section style={{ maxWidth: 900, margin: '0 auto', padding: '6rem 2rem 3rem', textAlign: 'center' }}>
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="hero-badge" style={{ display: 'inline-flex', margin: '0 auto 2rem' }}>
          🚀 Enterprise-Grade Legal Tech · Multi-Agent AI System
        </motion.div>
        <motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          style={{ fontSize: 'clamp(2.5rem, 6vw, 4.5rem)', background: 'linear-gradient(135deg, #e2e8f0 30%, #a5b4fc 70%, #c4b5fd 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: '1.5rem', lineHeight: 1.1, fontFamily: "'Playfair Display', serif", fontWeight: 700 }}>
          India's Most Advanced<br />AI Legal Assistant
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
          style={{ fontSize: '1.15rem', color: 'var(--text-secondary)', maxWidth: 650, margin: '0 auto 2.5rem', lineHeight: 1.7 }}>
          A multi-agent AI system built with <strong style={{ color: 'var(--primary-light)' }}>LangGraph</strong>, <strong style={{ color: 'var(--primary-light)' }}>RAG</strong>, and <strong style={{ color: 'var(--primary-light)' }}>GPT-4o</strong>
          that democratizes access to Indian legal knowledge — IPC, BNS 2023, Constitution, 50+ acts.
        </motion.p>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="hero-actions">
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/auth')}>
            ⚖️ Start Legal Consultation Free
          </button>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="btn btn-ghost btn-lg">
            📂 View on GitHub
          </a>
        </motion.div>

        {/* Stats */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          style={{ display: 'flex', justifyContent: 'center', gap: '3rem', marginTop: '3.5rem', flexWrap: 'wrap' }}>
          {STATS.map((s) => (
            <div key={s.label} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2.25rem', fontWeight: 900, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{s.value}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Agent Architecture Visual */}
      <section style={{ maxWidth: 900, margin: '0 auto', padding: '2rem', textAlign: 'center' }}>
        <div className="card" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-muted)', fontSize: '0.8rem', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            🤖 LangGraph Multi-Agent Architecture
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
            {[
              { icon: '🎯', name: 'Orchestrator', role: 'StateGraph router' },
              { icon: '📚', name: 'Research', role: 'Indian Kanoon API' },
              { icon: '🔍', name: 'Retrieval', role: 'ChromaDB RAG' },
              { icon: '✅', name: 'Verification', role: 'Hallucination check' },
              { icon: '📝', name: 'Summarization', role: 'PDF analysis' },
              { icon: '✍️', name: 'Drafting', role: 'Legal docs AI' },
              { icon: '📎', name: 'Citation', role: 'SCC/AIR format' },
              { icon: '🧠', name: 'Memory', role: 'Conversation ctx' },
            ].map((a, i) => (
              <motion.div key={i} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.05 * i }}
                className="agent-status-card" style={{ flexDirection: 'column', textAlign: 'center', padding: '0.875rem 0.5rem' }}>
                <div style={{ fontSize: '1.5rem', marginBottom: 6 }}>{a.icon}</div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{a.name}</div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 3 }}>{a.role}</div>
                <div className="agent-dot online" style={{ margin: '6px auto 0' }} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section style={{ maxWidth: 1100, margin: '2rem auto', padding: '2rem' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '1.75rem' }}>
          Everything You Need for Indian Legal Research
        </h2>
        <div className="feature-grid">
          {FEATURES.map((f, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 * i }}
              className="feature-item">
              <div className="feature-icon">{f.icon}</div>
              <div className="feature-title">{f.title}</div>
              <div className="feature-desc">{f.desc}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Tech Stack */}
      <section style={{ maxWidth: 900, margin: '2rem auto', padding: '2rem' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', fontSize: '1.25rem', color: 'var(--text-secondary)' }}>
          🛠️ Built With Industry-Grade AI Stack
        </h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, justifyContent: 'center' }}>
          {TECH_STACK.map((t) => (
            <div key={t.name} style={{ background: 'var(--bg-card)', border: `1px solid ${t.color}40`, borderRadius: 'var(--radius-md)', padding: '10px 18px', textAlign: 'center', minWidth: 110 }}>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: t.color }}>{t.name}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 2 }}>{t.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{ textAlign: 'center', padding: '4rem 2rem', maxWidth: 700, margin: '0 auto' }}>
        <div className="card" style={{ padding: '3rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>Ready to Explore Indian Law?</h2>
          <p style={{ marginBottom: '2rem' }}>Get instant AI-powered legal guidance in your language.</p>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/auth')}>
            ⚖️ Start Free — No Credit Card Needed
          </button>
          <div style={{ marginTop: '1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            🆘 Emergency: NALSA Free Legal Aid Helpline <strong style={{ color: '#10b981' }}>15100</strong>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
        <p>⚖️ LegalAI — Multi-Agent AI Legal Assistant for Indian Law</p>
        <p style={{ marginTop: 6 }}>Built with LangGraph, ChromaDB, GPT-4o, FastAPI, React</p>
        <p style={{ marginTop: 6, color: '#ef4444' }}>⚠️ Not legal advice. Always consult a qualified Indian lawyer for legal matters.</p>
      </footer>
    </div>
  )
}
