import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'

export default function SettingsPage() {
  const { user, theme, toggleTheme } = useAuthStore()
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [loading, setLoading] = useState(false)

  const handleChangePassword = async () => {
    if (!form.current_password || !form.new_password || !form.confirm_password) {
      toast.error('Please fill all fields')
      return
    }
    if (form.new_password !== form.confirm_password) {
      toast.error('New passwords do not match')
      return
    }
    if (form.new_password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      await authAPI.changePassword({ current_password: form.current_password, new_password: form.new_password })
      toast.success('✅ Password changed successfully!')
      setForm({ current_password: '', new_password: '', confirm_password: '' })
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || err?.userMessage || 'Failed to change password')
    } finally {
      setLoading(false)
    }
  }

  const cardStyle: React.CSSProperties = {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: '1.5rem',
    maxWidth: 520,
    marginBottom: '1rem',
  }

  const headingStyle: React.CSSProperties = {
    fontSize: '0.95rem',
    fontWeight: 700,
    color: 'var(--primary)',
    marginBottom: '1rem',
    marginTop: 0,
  }

  return (
    <div className="page-container">
      <h1 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1.5rem', color: 'var(--text-primary)' }}>
        ⚙️ Settings
      </h1>

      {/* Profile */}
      <div style={cardStyle}>
        <h2 style={headingStyle}>👤 Profile</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Email: <strong style={{ color: 'var(--text-primary)' }}>{(user as any)?.email || 'N/A'}</strong>
          </p>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Name: <strong style={{ color: 'var(--text-primary)' }}>{(user as any)?.full_name || 'N/A'}</strong>
          </p>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Role: <strong style={{ color: 'var(--text-primary)' }}>{(user as any)?.role || 'user'}</strong>
          </p>
        </div>
      </div>

      {/* Theme */}
      <div style={cardStyle}>
        <h2 style={headingStyle}>🎨 Appearance</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={toggleTheme}
            style={{
              padding: '0.6rem 1.5rem', borderRadius: 8,
              border: '1px solid var(--border-bright)',
              background: 'var(--bg-surface)', color: 'var(--text-primary)',
              cursor: 'pointer', fontSize: '0.85rem', fontWeight: 500,
              display: 'flex', alignItems: 'center', gap: 8,
            }}
          >
            {theme === 'dark' ? '☀️ Switch to Light Mode' : '🌙 Switch to Dark Mode'}
          </button>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Currently: <strong>{theme === 'dark' ? 'Dark' : 'Light'}</strong>
          </span>
        </div>
      </div>

      {/* Change Password */}
      <div style={cardStyle}>
        <h2 style={headingStyle}>🔐 Change Password</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {(['current_password', 'new_password', 'confirm_password'] as const).map((field) => (
            <div key={field}>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>
                {field.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
              </label>
              <input
                type="password"
                className="input"
                value={form[field]}
                onChange={(e) => setForm((prev) => ({ ...prev, [field]: e.target.value }))}
                placeholder="••••••••"
                style={{ width: '100%', boxSizing: 'border-box' }}
              />
            </div>
          ))}
          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: '0.25rem 0' }}>
            Requirements: min 8 chars · 1 uppercase · 1 special character
          </p>
          <button
            onClick={handleChangePassword}
            disabled={loading}
            style={{
              padding: '0.65rem 1.5rem', borderRadius: 8,
              background: 'var(--gradient-primary)', color: '#13110e',
              border: 'none', cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 700, fontSize: '0.85rem', opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Changing...' : 'Update Password'}
          </button>
        </div>
      </div>

      {/* About */}
      <div style={cardStyle}>
        <h2 style={headingStyle}>ℹ️ About LegalAI</h2>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.8, margin: 0 }}>
          <strong style={{ color: 'var(--text-primary)' }}>LegalAI v2.0</strong> — AI-powered Indian Legal Assistant<br />
          Powered by <strong style={{ color: 'var(--text-primary)' }}>Gemini 3.5 Flash</strong> · 8 AI Agents · 20 real landmark cases<br />
          Languages: English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Punjabi<br />
          <br />
          For free legal aid: NALSA Helpline{' '}
          <a href="tel:15100" style={{ color: 'var(--success)', textDecoration: 'none', fontWeight: 700 }}>15100</a><br />
          Women Helpline: <a href="tel:181" style={{ color: 'var(--success)', textDecoration: 'none' }}>181</a>
          {' · '}Cyber Crime: <a href="tel:1930" style={{ color: 'var(--success)', textDecoration: 'none' }}>1930</a>
        </p>
      </div>
    </div>
  )
}
