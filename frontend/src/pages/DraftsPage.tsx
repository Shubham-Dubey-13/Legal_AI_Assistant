import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { draftsAPI } from '../services/api'
import toast from 'react-hot-toast'

const DRAFT_TYPES = [
  { value: 'fir', label: 'FIR', icon: '🚨', desc: 'First Information Report' },
  { value: 'legal_notice', label: 'Legal Notice', icon: '📨', desc: 'Formal legal notice' },
  { value: 'petition', label: 'Petition', icon: '📜', desc: 'Court petition / writ' },
  { value: 'affidavit', label: 'Affidavit', icon: '📋', desc: 'Sworn statement' },
  { value: 'bail_application', label: 'Bail Application', icon: '⚖️', desc: 'Bail request' },
  { value: 'consumer_complaint', label: 'Consumer Complaint', icon: '🛒', desc: 'Forum complaint' },
  { value: 'contract', label: 'Agreement', icon: '🤝', desc: 'Legal contract' },
  { value: 'will', label: 'Will/Testament', icon: '📝', desc: 'Legal will' },
]

const LANGUAGES = [
  { code: 'en', label: '🇬🇧 English' },
  { code: 'hi', label: '🇮🇳 Hindi' },
  { code: 'ta', label: 'Tamil' },
  { code: 'te', label: 'Telugu' },
  { code: 'bn', label: 'Bengali' },
]

export default function DraftsPage() {
  const [selectedType, setSelectedType] = useState('fir')
  const [form, setForm] = useState({ description: '', facts: '', relief_sought: '', language: 'en', parties: { complainant: '', accused: '', petitioner: '', respondent: '' } })
  const [loading, setLoading] = useState(false)
  const [draft, setDraft] = useState<any>(null)
  const [templates, setTemplates] = useState<any[]>([])

  useEffect(() => {
    draftsAPI.templates().then(({ data }) => setTemplates(data.templates || [])).catch(() => {})
  }, [])

  const generateDraft = async () => {
    if (!form.description.trim()) { toast.error('Please describe the situation'); return }
    setLoading(true)
    try {
      const { data } = await draftsAPI.generate({
        draft_type: selectedType,
        description: form.description,
        parties: form.parties,
        facts: form.facts,
        relief_sought: form.relief_sought,
        language: form.language,
      })
      setDraft(data)
      toast.success('✅ AI draft generated successfully!')
    } catch {
      // Fallback demo draft
      setDraft({
        draft_id: 'demo-draft',
        title: `${DRAFT_TYPES.find(t => t.value === selectedType)?.label} — AI Generated Draft`,
        content: `[DEMO MODE — Configure OpenAI API key for full AI drafting]\n\n${DRAFT_TYPES.find(t => t.value === selectedType)?.label.toUpperCase()}\n\nDate: ${new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' })}\n\nTO,\nThe Station House Officer\n[Police Station Name]\n[City, State]\n\nSUBJECT: ${form.description}\n\nRESPECTFULLY SUBMITTED THAT:\n\n1. The complainant/petitioner is filing this ${selectedType.replace('_', ' ')} regarding: ${form.description}\n\n2. FACTS OF THE CASE:\n${form.facts || '[Facts to be detailed here]'}\n\n3. RELIEF SOUGHT:\n${form.relief_sought || '[List specific reliefs requested]'}\n\nPRAYER:\nIn view of the above facts and circumstances, it is respectfully prayed that appropriate action be taken.\n\nVerified that the contents of this ${selectedType.replace('_', ' ')} are true to my knowledge.\n\n\nSignature: _______________\nDate: ${new Date().toLocaleDateString()}\nPlace: _______________\n\n⚠️ DISCLAIMER: This is an AI-generated template. Review with a qualified advocate before submission.\nFree Legal Aid: NALSA Helpline 15100 | nalsa.gov.in`,
        sections_used: ['BNS 173', 'BNSS 173'],
        word_count: 180,
      })
      toast.success('Demo draft generated! Add OpenAI key for full AI drafting.')
    } finally { setLoading(false) }
  }

  const currentType = DRAFT_TYPES.find(t => t.value === selectedType)

  return (
    <div className="page-container">
      <div style={{ display: 'grid', gridTemplateColumns: draft ? '380px 1fr' : '380px 1fr', gap: '1.5rem' }}>
        {/* Left Panel: Form */}
        <div>
          {/* Type selector */}
          <div className="card" style={{ marginBottom: '1.25rem', padding: '1.25rem' }}>
            <h4 style={{ marginBottom: '0.875rem', fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Document Type</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {DRAFT_TYPES.map(t => (
                <motion.button key={t.value} whileTap={{ scale: 0.96 }}
                  onClick={() => setSelectedType(t.value)}
                  style={{ background: selectedType === t.value ? 'rgba(99,102,241,0.15)' : 'transparent', border: `1px solid ${selectedType === t.value ? 'var(--primary)' : 'var(--border)'}`, borderRadius: 'var(--radius-md)', padding: '0.625rem', cursor: 'pointer', textAlign: 'left', transition: 'var(--transition)', color: selectedType === t.value ? 'var(--primary-light)' : 'var(--text-secondary)' }}>
                  <div style={{ fontSize: '1.1rem', marginBottom: 3 }}>{t.icon}</div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700 }}>{t.label}</div>
                  <div style={{ fontSize: '0.6rem', opacity: 0.7, marginTop: 1 }}>{t.desc}</div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Form */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h4 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 6 }}>
              {currentType?.icon} {currentType?.label} Details
            </h4>

            <div className="form-group">
              <label className="form-label">📝 Situation Description *</label>
              <textarea className="textarea" placeholder={`Describe the situation for which you need a ${currentType?.label}...`}
                value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={3} />
            </div>

            <div className="form-group">
              <label className="form-label">👤 Complainant / Petitioner</label>
              <input className="input" placeholder="Full name" value={form.parties.complainant}
                onChange={e => setForm(f => ({ ...f, parties: { ...f.parties, complainant: e.target.value } }))} />
            </div>

            <div className="form-group">
              <label className="form-label">👥 Accused / Respondent</label>
              <input className="input" placeholder="Name or 'Unknown person'" value={form.parties.accused}
                onChange={e => setForm(f => ({ ...f, parties: { ...f.parties, accused: e.target.value } }))} />
            </div>

            <div className="form-group">
              <label className="form-label">📋 Key Facts</label>
              <textarea className="textarea" placeholder="What happened? When? Where? Add all important facts..." rows={3}
                value={form.facts} onChange={e => setForm(f => ({ ...f, facts: e.target.value }))} />
            </div>

            <div className="form-group">
              <label className="form-label">⚖️ Relief / Action Sought</label>
              <input className="input" placeholder="What do you want as outcome / relief?" value={form.relief_sought}
                onChange={e => setForm(f => ({ ...f, relief_sought: e.target.value }))} />
            </div>

            <div className="form-group">
              <label className="form-label">🌐 Draft Language</label>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {LANGUAGES.map(l => (
                  <button key={l.code} className="lang-chip" onClick={() => setForm(f => ({ ...f, language: l.code }))}
                    style={form.language === l.code ? { background: 'rgba(99,102,241,0.15)', borderColor: 'var(--primary)', color: 'var(--primary-light)' } : {}}>
                    {l.label}
                  </button>
                ))}
              </div>
            </div>

            <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
              className="btn btn-primary" style={{ width: '100%', padding: '0.875rem', fontSize: '0.95rem' }}
              onClick={generateDraft} disabled={loading}>
              {loading ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                  AI Drafting Agent Working...
                </span>
              ) : `✍️ Generate ${currentType?.label} with AI`}
            </motion.button>
          </div>
        </div>

        {/* Right: Draft Output */}
        <div>
          {!draft ? (
            <div className="empty-state" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div className="empty-icon">✍️</div>
              <div className="empty-title">AI Draft will appear here</div>
              <div className="empty-desc">Fill in the form and click Generate to create a professional legal document using the AI Drafting Agent powered by GPT-4o.</div>
              <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 300, width: '100%' }}>
                {templates.slice(0, 3).map((t: any, i: number) => (
                  <div key={i} className="case-card" style={{ padding: '0.875rem', cursor: 'pointer' }}
                    onClick={() => setSelectedType(t.type)}>
                    <div className="case-name" style={{ fontSize: '0.82rem' }}>{t.name}</div>
                    <div className="case-summary" style={{ fontSize: '0.72rem', marginTop: 3 }}>{t.description}</div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div className="draft-editor">
                <div className="draft-toolbar">
                  <h4 style={{ flex: 1, fontSize: '0.85rem' }}>{draft.title}</h4>
                  <span className="badge badge-success">✅ Generated</span>
                  <span className="badge badge-info">📝 {draft.word_count} words</span>
                  <button className="btn btn-ghost btn-sm" onClick={() => { navigator.clipboard.writeText(draft.content); toast.success('Copied!') }}>📋 Copy</button>
                  <button className="btn btn-secondary btn-sm" onClick={() => {
                    const blob = new Blob([draft.content], { type: 'text/plain' })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url; a.download = `${draft.title}.txt`; a.click()
                    toast.success('Downloaded!')
                  }}>⬇️ Download</button>
                </div>

                {draft.sections_used?.length > 0 && (
                  <div style={{ padding: '0.75rem 1.5rem', background: 'rgba(99,102,241,0.04)', borderBottom: '1px solid var(--border)', display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Applicable sections:</span>
                    {draft.sections_used.map((s: string, i: number) => <span key={i} className="badge badge-primary">{s}</span>)}
                  </div>
                )}

                <div className="draft-content">{draft.content}</div>
              </div>

              <div style={{ marginTop: '1rem', padding: '0.875rem', background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)', fontSize: '0.75rem', color: '#fca5a5' }}>
                ⚠️ This AI-generated draft is a starting template only. Always review with a qualified Indian advocate before submission to any court or authority.
              </div>
            </motion.div>
          )}
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
