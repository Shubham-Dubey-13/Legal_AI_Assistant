import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { chatAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  citations?: any[]
  ipc_sections?: string[]
  bns_sections?: string[]
  agent_pipeline?: any[]
  confidence_score?: number
}

const SUGGESTED_QUERIES = [
  'What are my rights if police arrest me without warrant?',
  'How to file FIR for cybercrime / online fraud?',
  'What is BNS 316? How does it replace IPC 420 (cheating)?',
  'How to apply for anticipatory bail under BNSS 2023?',
  'My employer is not paying salary. What legal action can I take?',
  'How to file consumer complaint against Amazon/Flipkart?',
  'What is Article 21 and how does it protect me?',
  'My landlord is illegally evicting me. What are my rights?',
]

const AGENT_EMOJIS: Record<string, string> = {
  'Orchestrator Agent': '🎯',
  'Retrieval Agent': '🔍',
  'Research Agent': '📚',
  'Verification Agent': '✅',
  'Summarization Agent': '📝',
  'Drafting Agent': '✍️',
  'Citation Agent': '📎',
  'Memory Agent': '🧠',
  'Direct LLM': '⚡',
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [thinkingStep, setThinkingStep] = useState(0)
  const [language, setLanguage] = useState('en')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { user } = useAuthStore()

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  useEffect(() => scrollToBottom(), [messages, loading])

  const THINKING_STEPS = [
    '🔍 Searching Indian law database…',
    '📚 Analyzing IPC / BNS sections…',
    '⚖️ Cross-referencing case laws…',
    '✅ Verifying legal accuracy…',
    '📝 Drafting your response…',
  ]

  // Cycle through thinking steps while loading
  useEffect(() => {
    if (!loading) { setThinkingStep(0); return }
    const interval = setInterval(() => setThinkingStep(s => (s + 1) % THINKING_STEPS.length), 1800)
    return () => clearInterval(interval)
  }, [loading])

  const handleSend = async (queryText?: string) => {
    const q = queryText || input.trim()
    if (!q || loading) return

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: q,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setThinkingStep(0)

    // Auto-resize textarea
    if (textareaRef.current) textareaRef.current.style.height = 'auto'

    try {
      const { data } = await chatAPI.query({
        message: q,
        conversation_id: conversationId,
        language,
        include_citations: true,
      })

      if (!conversationId) setConversationId(data.conversation_id)

      const aiMsg: Message = {
        id: data.message_id,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        citations: data.citations,
        ipc_sections: data.ipc_sections,
        bns_sections: data.bns_sections,
        agent_pipeline: data.agent_pipeline,
        confidence_score: data.confidence_score,
      }
      setMessages(prev => [...prev, aiMsg])
    } catch (err: any) {
      setAgentThinking([])
      const errMsg = err?.response?.data?.detail || 'Connection error. Please check your API configuration.'

      // Show helpful fallback
      const fallbackMsg: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `**⚠️ Service Notice**\n\n${errMsg}\n\n**💡 If it says "Could not validate credentials", you need to LOG OUT and LOG IN again!**\n\n**💡 Otherwise, to fully enable AI responses:**\n1. Configure \`GOOGLE_API_KEY\` in \`backend/.env\`\n2. Start the FastAPI backend: \`uvicorn app.main:app --reload\`\n3. The full 8-agent pipeline will then be active\n\n**🆘 Need immediate legal help?**\n- **NALSA Free Legal Aid**: Call **15100**\n- **Women Helpline**: 181\n- **Child Helpline**: 1098\n- **Website**: [nalsa.gov.in](https://nalsa.gov.in)`,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, fallbackMsg])
      toast.error('Check your API Key or Log in again')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`
  }

  const LANGS = [
    { code: 'en', label: '🇬🇧 English' },
    { code: 'hi', label: '🇮🇳 हिंदी' },
    { code: 'ta', label: 'தமிழ்' },
    { code: 'te', label: 'తెలుగు' },
    { code: 'bn', label: 'বাংলা' },
    { code: 'mr', label: 'मराठी' },
  ]

  return (
    <div className="chat-layout">
      {/* Left: Conversation History */}
      <div className="chat-history-panel">
        <div style={{ padding: '1rem', borderBottom: '1px solid var(--border)' }}>
          <button className="btn btn-primary" style={{ width: '100%', fontSize: '0.8rem' }}
            onClick={() => { setMessages([]); setConversationId(null) }}>
            ✚ New Consultation
          </button>
        </div>
        <div style={{ padding: '0.75rem', flex: 1, overflowY: 'auto' }}>
          <div className="nav-section-label">Quick Queries</div>
          {SUGGESTED_QUERIES.map((q, i) => (
            <div key={i}
              className="nav-item"
              style={{ fontSize: '0.72rem', lineHeight: 1.4, marginBottom: 4, cursor: 'pointer' }}
              onClick={() => handleSend(q)}
            >
              <span>💬</span>
              <span style={{ overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>{q}</span>
            </div>
          ))}
        </div>
        {/* Language selector */}
        <div style={{ padding: '0.75rem', borderTop: '1px solid var(--border)' }}>
          <div className="nav-section-label">Response Language</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 6 }}>
            {LANGS.map(l => (
              <button key={l.code} onClick={() => setLanguage(l.code)}
                className="lang-chip"
                style={l.code === language ? { background: 'rgba(99,102,241,0.15)', borderColor: 'var(--primary)', color: 'var(--primary-light)' } : {}}>
                {l.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Right: Chat main */}
      <div className="chat-main">
        {/* Messages */}
        <div className="chat-messages">
          {messages.length === 0 && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="hero" style={{ padding: '2rem 1rem' }}>
              <div className="hero-badge">🤖 8 AI Agents · RAG Pipeline · GPT-4o</div>
              <h1 style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>
                India's Most Advanced<br />Legal AI Assistant
              </h1>
              <p className="hero-sub" style={{ fontSize: '0.9rem' }}>
                Powered by LangGraph multi-agent orchestration, ChromaDB RAG, and GPT-4o.
                Get instant guidance on IPC, BNS, Constitution, Consumer law, and 50+ Indian acts.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', marginBottom: '2rem' }}>
                {['⚖️ IPC/BNS Sections', '📚 Case Law Search', '✍️ Draft FIR/Notice', '🔮 Judgment Prediction', '🌐 6 Languages', '🎤 Voice Support'].map(f => (
                  <span key={f} className="badge badge-primary">{f}</span>
                ))}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, maxWidth: 600, margin: '0 auto' }}>
                {SUGGESTED_QUERIES.slice(0, 4).map((q, i) => (
                  <motion.div key={i} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                    className="case-card" style={{ padding: '0.875rem', cursor: 'pointer', textAlign: 'left' }}
                    onClick={() => handleSend(q)}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>💬 {q}</div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {messages.map((msg) => (
            <motion.div key={msg.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className={`message-wrapper ${msg.role}`}>
              <div className={`message-avatar ${msg.role === 'assistant' ? 'ai' : 'user'}`}>
                {msg.role === 'assistant' ? '⚖️' : (user?.full_name?.[0] || 'U')}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className={`message-bubble ${msg.role === 'assistant' ? 'ai' : 'user'}`}>
                  {msg.role === 'assistant' ? (
                    <div className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                    </div>
                  ) : msg.content}

                  {/* Agent pipeline */}
                  {msg.agent_pipeline && msg.agent_pipeline.length > 0 && (
                    <div className="agent-pipeline">
                      {msg.agent_pipeline.map((a, i) => (
                        <span key={i} className="agent-pill">
                          {AGENT_EMOJIS[a.agent_name] || '🤖'} {a.agent_name}
                        </span>
                      ))}
                      {msg.confidence_score && (
                        <span className="confidence-meter">
                          🎯 {Math.round(msg.confidence_score * 100)}% confidence
                        </span>
                      )}
                    </div>
                  )}

                  {/* IPC/BNS sections */}
                  {((msg.ipc_sections?.length || 0) + (msg.bns_sections?.length || 0)) > 0 && (
                    <div className="sections-row" style={{ marginTop: 10 }}>
                      {msg.bns_sections?.map((s, i) => (
                        <span key={i} className="badge badge-primary">📜 {s}</span>
                      ))}
                      {msg.ipc_sections?.slice(0, 3).map((s, i) => (
                        <span key={i} className="badge badge-info">⚖️ {s}</span>
                      ))}
                    </div>
                  )}

                  {/* Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="citations-list">
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: 4 }}>📎 CASE CITATIONS</div>
                      {msg.citations.slice(0, 3).map((c, i) => (
                        <div key={i} className="citation-item">
                          <div className="citation-name">{c.case_name}</div>
                          <div className="citation-ref">{c.citation} · {c.court} · {c.year}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="message-time">{format(msg.timestamp, 'HH:mm')}</div>
              </div>
            </motion.div>
          ))}

          {/* Agent thinking animation */}
          <AnimatePresence>
            {loading && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                className="message-wrapper">
                <div className="message-avatar ai">⚖️</div>
                <div className="message-bubble ai">
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 10 }}>
                    {THINKING_STEPS[thinkingStep]}
                  </div>
                  <div className="agent-pipeline">
                    {['Orchestrator Agent', 'Retrieval Agent', 'Research Agent'].map((a, i) => (
                      <motion.span key={i} initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: i * 0.1 }}
                        className="agent-pill thinking">
                        {AGENT_EMOJIS[a] || '🤖'} {a}
                      </motion.span>
                    ))}
                  </div>
                  <div className="typing-indicator" style={{ marginTop: 10 }}>
                    <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="chat-input-area">
          <div className="chat-tools">
            {['📄 Upload Doc', '🔍 Case Search', '✍️ Draft', '🎤 Voice', '🌐 Translate'].map(tool => (
              <button key={tool} className="tool-chip">{tool}</button>
            ))}
            <span style={{ marginLeft: 'auto', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
              Shift+Enter for new line
            </span>
          </div>
          <div className="chat-input-wrapper">
            <textarea
              ref={textareaRef}
              className="chat-textarea"
              placeholder="Ask about Indian law — IPC sections, how to file FIR, your legal rights, BNS 2023..."
              value={input}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={loading}
            />
            <button className="chat-send-btn" onClick={() => handleSend()} disabled={loading || !input.trim()}>
              {loading ? '⏳' : '➤'}
            </button>
          </div>
          <div style={{ textAlign: 'center', marginTop: 8, fontSize: '0.65rem', color: 'var(--text-muted)' }}>
            ⚠️ AI-generated responses are for informational purposes only. Not a substitute for professional legal advice.
          </div>
        </div>
      </div>
    </div>
  )
}
