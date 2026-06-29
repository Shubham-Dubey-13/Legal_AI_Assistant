import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'

const BalanceIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ width: 28, height: 28 }}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1M4.22 4.22l.707.707m12.728 12.728.707.707M1 12h2m18 0h2M4.22 19.778l.707-.707M18.95 5.636l.707-.707" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8a4 4 0 100 8 4 4 0 000-8z" />
  </svg>
)

const EyeIcon = ({ show }: { show: boolean }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ width: 18, height: 18 }}>
    {show ? (
      <>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </>
    ) : (
      <>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
      </>
    )}
  </svg>
)

export default function AuthPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [form, setForm] = useState({ email: '', password: '', full_name: '', preferred_language: 'en' })
  const { login } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Frontend password validation on register
    if (mode === 'register') {
      if (form.password.length < 8) {
        toast.error('Password must be at least 8 characters')
        return
      }
      if (!/[A-Z]/.test(form.password)) {
        toast.error('Password must contain at least 1 capital letter')
        return
      }
      if (!/[!@#$%^&*(),.?":{}|<>]/.test(form.password)) {
        toast.error('Password must contain at least 1 symbol (e.g. @#$!)')
        return
      }
    }

    setLoading(true)
    try {
      const { data } = mode === 'login'
        ? await authAPI.login({ email: form.email, password: form.password })
        : await authAPI.register(form)
      login(data.access_token, { user_id: data.user_id, email: data.email, full_name: data.full_name })
      toast.success(`Welcome, ${data.full_name}!`)
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        toast.error(detail[0]?.msg || 'Validation failed')
      } else {
        toast.error(detail || err.message || 'Authentication failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-root">
      {/* Background texture */}
      <div className="auth-bg" />

      {/* Split layout */}
      <div className="auth-split">
        {/* Left panel — branding */}
        <motion.div
          className="auth-brand"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="auth-brand-inner">
            <div className="auth-logo">
              <span>⚖</span>
            </div>
            <h1 className="auth-brand-title">LexAI</h1>
            <p className="auth-brand-subtitle">
              India's most advanced AI legal assistant — powered by multi-agent reasoning and comprehensive case law.
            </p>
            <div className="auth-features">
              {[
                { icon: '📋', text: 'Draft legal documents instantly' },
                { icon: '🔍', text: 'Search IPC, BNS & case law' },
                { icon: '🤖', text: 'AI-powered judgment prediction' },
                { icon: '🔒', text: 'Secure & confidential' },
              ].map((f, i) => (
                <motion.div
                  key={i}
                  className="auth-feature-item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.1 }}
                >
                  <span className="auth-feature-icon">{f.icon}</span>
                  <span>{f.text}</span>
                </motion.div>
              ))}
            </div>
            <div className="auth-brand-footer">
              <span className="auth-helpline">🆘 NALSA Free Legal Aid: <strong>15100</strong></span>
            </div>
          </div>
        </motion.div>

        {/* Right panel — form */}
        <div className="auth-form-panel">
          <motion.div
            className="auth-card"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {/* Tab switcher */}
            <div className="auth-tabs">
              <button
                className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
                onClick={() => setMode('login')}
                type="button"
              >
                Sign In
              </button>
              <button
                className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
                onClick={() => setMode('register')}
                type="button"
              >
                Register
              </button>
            </div>

            <AnimatePresence mode="wait">
              <motion.div
                key={mode}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <div className="auth-card-header">
                  <h2 className="auth-card-title">
                    {mode === 'login' ? 'Welcome back' : 'Create your account'}
                  </h2>
                  <p className="auth-card-desc">
                    {mode === 'login'
                      ? 'Sign in to continue to your workspace'
                      : 'Start your AI legal journey today'}
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                  {mode === 'register' && (
                    <div className="auth-field">
                      <label className="auth-label">Full Name</label>
                      <input
                        className="auth-input"
                        placeholder="e.g. Ramesh Kumar"
                        value={form.full_name}
                        onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
                        required
                        autoComplete="name"
                      />
                    </div>
                  )}

                  <div className="auth-field">
                    <label className="auth-label">Email Address</label>
                    <input
                      className="auth-input"
                      type="email"
                      placeholder="you@example.com"
                      value={form.email}
                      onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                      required
                      autoComplete="email"
                    />
                  </div>

                  <div className="auth-field">
                    <label className="auth-label">Password</label>
                    <div className="auth-input-wrap">
                      <input
                        className="auth-input"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        value={form.password}
                        onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                        required
                        minLength={8}
                        autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                      />
                      <button
                        type="button"
                        className="auth-eye-btn"
                        onClick={() => setShowPassword(s => !s)}
                        tabIndex={-1}
                      >
                        <EyeIcon show={showPassword} />
                      </button>
                    </div>
                    {mode === 'register' && (
                      <p className="auth-hint">Min 8 chars · 1 capital letter · 1 symbol</p>
                    )}
                  </div>

                  <button
                    type="submit"
                    className="auth-submit-btn"
                    disabled={loading}
                  >
                    {loading
                      ? <span className="auth-spinner" />
                      : mode === 'login' ? 'Sign In' : 'Create Account'}
                  </button>

                  <div className="auth-divider"><span>or</span></div>

                  <button
                    type="button"
                    className="auth-demo-btn"
                    onClick={() => {
                      login('demo-token', { user_id: 'demo', email: 'demo@legalai.in', full_name: 'Demo User' })
                      toast.success('Running in demo mode')
                    }}
                  >
                    Try Demo — No signup needed
                  </button>
                </form>
              </motion.div>
            </AnimatePresence>
          </motion.div>

          <p className="auth-footer-note">
            By continuing, you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  )
}
