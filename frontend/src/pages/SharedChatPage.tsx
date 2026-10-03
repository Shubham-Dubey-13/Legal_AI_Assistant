import { useEffect, useState } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import axios from 'axios'

interface SharedMessage {
  role: string
  content: string
  created_at: string | null
}

export default function SharedChatPage() {
  const { conversationId } = useParams<{ conversationId: string }>()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [messages, setMessages] = useState<SharedMessage[]>([])
  const [title, setTitle] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!conversationId || !token) {
      setError('Invalid share link — missing token.')
      setLoading(false)
      return
    }
    axios
      .get<{ messages: SharedMessage[]; title: string }>(`/api/v1/chat/shared/${conversationId}?token=${encodeURIComponent(token)}`)
      .then(({ data }) => {
        setMessages(data.messages || [])
        setTitle(data.title || 'Shared Legal Consultation')
      })
      .catch(() => setError('This share link has expired or is invalid.'))
      .finally(() => setLoading(false))
  }, [conversationId, token])

  const base: React.CSSProperties = {
    minHeight: '100vh',
    background: '#13110e',
    color: '#f0ece4',
    fontFamily: 'Inter, sans-serif',
  }

  if (loading) {
    return (
      <div style={{ ...base, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem', color: '#7a746c' }}>
        Loading shared consultation…
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ ...base, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1rem', textAlign: 'center', padding: '2rem' }}>
        <div style={{ fontSize: '3rem' }}>⚖️</div>
        <h2 style={{ color: '#c8a96e', fontSize: '1.2rem', margin: 0 }}>{error}</h2>
        <Link to="/auth" style={{ color: '#5a9e78', textDecoration: 'none', fontSize: '0.9rem' }}>
          Start your own consultation →
        </Link>
      </div>
    )
  }

  return (
    <div style={base}>
      {/* Header */}
      <div style={{ background: '#1c1915', borderBottom: '1px solid rgba(200,169,110,0.12)', padding: '1rem 2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span style={{ fontSize: '1.4rem' }}>⚖️</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h1 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#c8a96e', margin: 0 }}>
            LegalAI — Shared Legal Consultation
          </h1>
          <p style={{ fontSize: '0.72rem', color: '#7a746c', margin: 0, marginTop: 2 }}>
            {title} · Read-only view
          </p>
        </div>
        <Link
          to="/auth"
          style={{
            background: 'linear-gradient(135deg, #c8a96e 0%, #e0c28a 100%)',
            color: '#13110e', padding: '0.5rem 1rem',
            borderRadius: 8, textDecoration: 'none',
            fontSize: '0.78rem', fontWeight: 700, whiteSpace: 'nowrap',
          }}
        >
          Start Yours →
        </Link>
      </div>

      {/* Messages */}
      <div style={{ maxWidth: 800, margin: '0 auto', padding: '2rem 1rem' }}>
        {messages.length === 0 && (
          <p style={{ color: '#7a746c', textAlign: 'center' }}>No messages in this conversation.</p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', marginBottom: '1rem' }}
          >
            {msg.role === 'assistant' && (
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: '#221f1a', border: '1px solid rgba(200,169,110,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', marginRight: 8, flexShrink: 0 }}>
                ⚖️
              </div>
            )}
            <div
              style={{
                maxWidth: '78%',
                padding: '0.75rem 1rem',
                borderRadius: msg.role === 'user' ? '12px 12px 4px 12px' : '4px 12px 12px 12px',
                background: msg.role === 'user' ? 'linear-gradient(135deg,#c8a96e,#e0c28a)' : '#221f1a',
                color: msg.role === 'user' ? '#13110e' : '#f0ece4',
                border: msg.role === 'user' ? 'none' : '1px solid rgba(200,169,110,0.12)',
                fontSize: '0.875rem',
                lineHeight: 1.65,
                whiteSpace: 'pre-wrap',
              }}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {/* Disclaimer */}
        <div style={{ marginTop: '3rem', padding: '1.25rem', background: '#1c1915', borderRadius: 10, border: '1px solid rgba(200,169,110,0.15)', textAlign: 'center' }}>
          <p style={{ color: '#7a746c', fontSize: '0.78rem', margin: 0, lineHeight: 1.7 }}>
            ⚠️ This is a read-only shared consultation for informational purposes only.<br />
            It does not constitute legal advice. Always consult a qualified advocate.<br />
            Free Legal Aid: NALSA Helpline{' '}
            <a href="tel:15100" style={{ color: '#5a9e78', textDecoration: 'none', fontWeight: 700 }}>15100</a>
          </p>
        </div>
      </div>
    </div>
  )
}
