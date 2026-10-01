import { Component, ReactNode } from 'react'

interface Props { children: ReactNode; fallback?: ReactNode }
interface State { hasError: boolean; error: Error | null }

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('LegalAI Error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', height: '100vh',
          background: 'var(--bg-primary, #0f1117)', color: 'var(--text-primary, #f1f5f9)',
          fontFamily: 'Inter, sans-serif', gap: '1rem', padding: '2rem', textAlign: 'center'
        }}>
          <div style={{ fontSize: '3rem' }}>⚖️</div>
          <h2 style={{ fontSize: '1.5rem', color: '#f59e0b' }}>Something went wrong</h2>
          <p style={{ color: '#94a3b8', maxWidth: 400 }}>
            LegalAI encountered an unexpected error. Your data is safe.
          </p>
          <code style={{
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: 8, padding: '0.5rem 1rem', fontSize: '0.75rem', color: '#fca5a5',
            maxWidth: 500, wordBreak: 'break-all'
          }}>
            {this.state.error?.message}
          </code>
          <button
            onClick={() => { this.setState({ hasError: false, error: null }); window.location.href = '/chat' }}
            style={{
              background: '#f59e0b', color: '#0f1117', border: 'none',
              borderRadius: 8, padding: '0.75rem 2rem', cursor: 'pointer',
              fontWeight: 700, fontSize: '0.95rem', marginTop: '0.5rem'
            }}
          >
            🔄 Reload App
          </button>
          <a href="tel:15100" style={{ color: '#34d399', fontSize: '0.8rem' }}>
            Need legal help? NALSA Free Aid: 15100
          </a>
        </div>
      )
    }
    return this.props.children
  }
}
