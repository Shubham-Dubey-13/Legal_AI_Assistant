import { useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

const pageInfo: Record<string, { title: string; desc: string; icon: string }> = {
  '/chat': { title: 'Legal Q&A Assistant', desc: 'Ask any question about Indian Law — powered by 8 AI agents', icon: '⚖️' },
  '/documents': { title: 'Legal Document Analysis', desc: 'Upload PDFs for AI-powered summarization and section detection', icon: '📄' },
  '/search': { title: 'Case Law Search', desc: 'Semantic + BM25 hybrid search over Indian court judgments', icon: '🔍' },
  '/drafts': { title: 'AI Legal Draft Maker', desc: 'Generate FIRs, notices, petitions, and affidavits using AI', icon: '✍️' },
  '/prediction': { title: 'Judgment Predictor', desc: 'ML-powered case outcome prediction with confidence scoring', icon: '🔮' },
  '/agents': { title: 'Agent Control Panel', desc: 'Monitor and control all 8 AI agents in real-time', icon: '🤖' },
  '/analytics': { title: 'Analytics Dashboard', desc: 'System metrics, query trends, and agent performance', icon: '📊' },
}

const LANGUAGES = [
  { code: 'en', label: '🇬🇧 EN' },
  { code: 'hi', label: '🇮🇳 हिंदी' },
  { code: 'ta', label: '🏛️ தமிழ்' },
  { code: 'te', label: '🌿 తెలుగు' },
  { code: 'bn', label: '🐟 বাংলা' },
]

export default function Header() {
  const location = useLocation()
  const { user } = useAuthStore()
  const info = pageInfo[location.pathname] || { title: 'LegalAI', desc: '', icon: '⚖️' }

  return (
    <header className="header">
      <div className="header-title">
        <h2>{info.icon} {info.title}</h2>
        {info.desc && <p>{info.desc}</p>}
      </div>
      <div className="header-actions">
        {/* Language chip */}
        <div style={{ display: 'flex', gap: 6 }}>
          {LANGUAGES.slice(0,3).map(lang => (
            <button
              key={lang.code}
              className="lang-chip"
              style={lang.code === 'en' ? { background: 'rgba(99,102,241,0.15)', borderColor: 'var(--primary)', color: 'var(--primary-light)' } : {}}
            >
              {lang.label}
            </button>
          ))}
        </div>
        {/* Divider */}
        <div style={{ width: 1, height: 24, background: 'var(--border)' }} />
        {/* Disclaimer badge */}
        <span className="badge badge-gold">⚠️ Not Legal Advice</span>
        {/* NALSA */}
        <a
          href="https://nalsa.gov.in"
          target="_blank"
          rel="noreferrer"
          className="btn btn-ghost btn-sm"
          style={{ fontSize: '0.7rem' }}
        >
          🆘 Free Legal Aid: 15100
        </a>
      </div>
    </header>
  )
}
