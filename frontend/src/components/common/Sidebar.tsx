import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

const navItems = [
  { to: '/chat', icon: '⚖️', label: 'Legal Q&A', badge: null },
  { to: '/documents', icon: '📄', label: 'Documents', badge: null },
  { to: '/search', icon: '🔍', label: 'Case Search', badge: null },
  { to: '/drafts', icon: '✍️', label: 'Draft Maker', badge: 'AI' },
  { to: '/prediction', icon: '🔮', label: 'Judgment AI', badge: 'ML' },
  { to: '/agents', icon: '🤖', label: 'Agents', badge: '8' },
  { to: '/analytics', icon: '📊', label: 'Analytics', badge: null },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">⚖️</div>
        <div>
          <div className="sidebar-logo-text">LegalAI</div>
          <div className="sidebar-logo-sub">Multi-Agent Indian Law AI</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Main</div>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span className="nav-item-icon">{item.icon}</span>
            <span style={{ flex: 1 }}>{item.label}</span>
            {item.badge && <span className="nav-item-badge">{item.badge}</span>}
          </NavLink>
        ))}

        <div className="nav-section-label" style={{ marginTop: '0.75rem' }}>Framework</div>
        <div className="nav-item" style={{ cursor: 'default', gap: '8px' }}>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            🔗 LangChain · LangGraph<br />
            📦 ChromaDB · GPT-4o<br />
            🐍 FastAPI · PostgreSQL
          </span>
        </div>
      </nav>

      <div className="sidebar-footer">
        {/* System status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '0.75rem', padding: '6px 8px', background: 'rgba(16,185,129,0.06)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16,185,129,0.15)' }}>
          <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 6px #10b981', animation: 'agentPulse 2s infinite' }} />
          <span style={{ fontSize: '0.7rem', color: '#34d399', fontWeight: 600 }}>8 Agents Online</span>
        </div>

        <div className="user-card" onClick={() => {}}>
          <div className="user-avatar">
            {user?.full_name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="user-name" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {user?.full_name || 'Demo User'}
            </div>
            <div className="user-role">{user?.email || 'demo@legalai.in'}</div>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); logout(); navigate('/') }}
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: '1rem', padding: '2px' }}
            title="Logout"
          >
            🚪
          </button>
        </div>
      </div>
    </aside>
  )
}
