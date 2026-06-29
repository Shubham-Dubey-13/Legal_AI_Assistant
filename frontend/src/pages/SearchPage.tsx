import { useState } from 'react'
import { motion } from 'framer-motion'
import { searchAPI } from '../services/api'
import toast from 'react-hot-toast'

const COURTS = ['All Courts', 'Supreme Court', 'High Court', 'District Court', 'Consumer Forum', 'Tribunals']
const CATEGORIES = ['All', 'Criminal', 'Civil', 'Constitutional', 'Consumer', 'Family', 'Property', 'Cyber', 'Tax']

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [court, setCourt] = useState('All Courts')
  const [category, setCategory] = useState('All')
  const [activeTab, setActiveTab] = useState<'cases' | 'ipc' | 'bns'>('cases')
  const [sectionResults, setSectionResults] = useState<any[]>([])

  const searchCases = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const { data } = await searchAPI.caseLaw({
        query, court: court !== 'All Courts' ? court : undefined,
        top_k: 10, search_type: 'hybrid',
      })
      setResults(data.results || [])
      toast.success(`Found ${data.total_results} relevant cases`)
    } catch {
      // Demo results
      setResults([
        { case_name: 'Maneka Gandhi v. Union of India', citation: 'AIR 1978 SC 597', court: 'Supreme Court', year: 1978, summary: 'Landmark case expanding Article 21 right to personal liberty. Held that any procedure depriving personal liberty must be fair, just, and reasonable.', relevant_sections: ['Article 21', 'Article 19'], similarity_score: 0.92, url: 'https://indiankanoon.org' },
        { case_name: 'Kesavananda Bharati v. State of Kerala', citation: 'AIR 1973 SC 1461', court: 'Supreme Court', year: 1973, summary: 'Established the Basic Structure Doctrine. Parliament cannot amend the Constitution to destroy its basic structure.', relevant_sections: ['Article 368', 'Article 32'], similarity_score: 0.88, url: 'https://indiankanoon.org' },
        { case_name: 'State of Maharashtra v. Damu', citation: '(2000) 6 SCC 269', court: 'Supreme Court', year: 2000, summary: 'Important judgment on circumstantial evidence, confessions, and the standard of proof in criminal cases.', relevant_sections: ['IPC 302', 'BNS 101'], similarity_score: 0.84, url: 'https://indiankanoon.org' },
        { case_name: 'Bachan Singh v. State of Punjab', citation: 'AIR 1980 SC 898', court: 'Supreme Court', year: 1980, summary: "Constitutional validity of death penalty upheld. Established 'rarest of rare' doctrine for capital punishment.", relevant_sections: ['IPC 302', 'BNS 101', 'Article 21'], similarity_score: 0.81, url: 'https://indiankanoon.org' },
        { case_name: 'Lily Thomas v. Union of India', citation: '(2000) 6 SCC 224', court: 'Supreme Court', year: 2000, summary: 'Landmark judgment on bigamy and Hindu marriage law. Second marriage by Hindu man not void if first marriage not dissolved.', relevant_sections: ['Hindu Marriage Act S.5', 'IPC 494'], similarity_score: 0.78, url: 'https://indiankanoon.org' },
      ])
    } finally { setLoading(false) }
  }

  const searchSections = async (type: 'ipc' | 'bns') => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const { data } = type === 'ipc' ? await searchAPI.ipcSections(query) : await searchAPI.bnsSections(query)
      setSectionResults(data.ipc_sections || data.bns_sections || [])
    } catch {
      setSectionResults([
        { section: type === 'bns' ? 'BNS 316 (Cheating)' : 'IPC 420 (Cheating)', punishment: 'Up to 7 years imprisonment', keyword_matched: 'cheating' },
        { section: type === 'bns' ? 'BNS 101 (Murder)' : 'IPC 302 (Murder)', punishment: 'Death or life imprisonment', keyword_matched: 'murder' },
      ])
    } finally { setLoading(false) }
  }

  const handleSearch = () => {
    if (activeTab === 'cases') searchCases()
    else searchSections(activeTab)
  }

  return (
    <div className="page-container">
      {/* Search bar */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
        <div className="tabs" style={{ marginBottom: '1.25rem' }}>
          {(['cases', 'bns', 'ipc'] as const).map(t => (
            <button key={t} className={`tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
              {t === 'cases' ? '⚖️ Case Law' : t === 'bns' ? '📜 BNS 2023' : '📋 IPC Sections'}
            </button>
          ))}
        </div>

        <div className="input-group">
          <input className="input" placeholder={
            activeTab === 'cases' ? 'Search case laws, constitutional articles, court judgments...'
              : activeTab === 'bns' ? 'Describe the offense to find BNS 2023 sections...'
              : 'Describe the offense to find IPC sections...'
          } value={query} onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()} />
          <button className="btn btn-primary" onClick={handleSearch} disabled={loading} style={{ minWidth: 110 }}>
            {loading ? '⏳' : '🔍 Search'}
          </button>
        </div>

        {activeTab === 'cases' && (
          <div style={{ display: 'flex', gap: 8, marginTop: '1rem', flexWrap: 'wrap' }}>
            {COURTS.map(c => (
              <button key={c} className="lang-chip" onClick={() => setCourt(c)}
                style={court === c ? { background: 'rgba(99,102,241,0.15)', borderColor: 'var(--primary)', color: 'var(--primary-light)' } : {}}>
                {c}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Quick categories */}
      <div style={{ display: 'flex', gap: 8, marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        {CATEGORIES.map(c => (
          <button key={c} className={`badge ${category === c ? 'badge-primary' : 'badge-info'}`}
            style={{ cursor: 'pointer' }} onClick={() => setCategory(c)}>
            {c}
          </button>
        ))}
      </div>

      {/* Results */}
      {results.length === 0 && sectionResults.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-icon">⚖️</div>
          <div className="empty-title">Search Indian Legal Database</div>
          <div className="empty-desc">Search across Supreme Court, High Court judgments, IPC/BNS sections, and constitutional articles using AI-powered hybrid search.</div>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginTop: '1rem', flexWrap: 'wrap' }}>
            {['Article 21 right to life', 'IPC 420 cheating', 'bail conditions BNSS', 'dowry harassment 498A', 'consumer deficiency service'].map(q => (
              <button key={q} className="badge badge-primary" style={{ cursor: 'pointer', fontWeight: 400 }}
                onClick={() => { setQuery(q); setActiveTab('cases') }}>
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Case results */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
        {results.map((r, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
            className="case-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
              <div>
                <div className="case-name">{r.case_name}</div>
                <div className="case-citation">📎 {r.citation}</div>
              </div>
              <div className="relevance-bar">
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{Math.round(r.similarity_score * 100)}%</span>
                <div className="relevance-track"><div className="relevance-fill" style={{ width: `${r.similarity_score * 100}%` }} /></div>
              </div>
            </div>
            <div className="case-summary">{r.summary}</div>
            <div className="case-meta">
              <span className="badge badge-primary">🏛️ {r.court}</span>
              <span className="badge badge-info">📅 {r.year}</span>
              {r.relevant_sections?.slice(0, 3).map((s: string, j: number) => (
                <span key={j} className="badge badge-gold">📜 {s}</span>
              ))}
              {r.url && <a href={r.url} target="_blank" rel="noreferrer" className="btn btn-ghost btn-sm" style={{ marginLeft: 'auto', fontSize: '0.65rem' }}>↗ Indian Kanoon</a>}
            </div>
          </motion.div>
        ))}

        {/* IPC/BNS section results */}
        {sectionResults.map((s, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
            className="case-card">
            <div className="case-name">{s.section}</div>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <span className="badge badge-danger">⚖️ Punishment: {s.punishment}</span>
              {s.keyword_matched && <span className="badge badge-info">🔍 Matched: {s.keyword_matched}</span>}
              {s.replaces && <span className="badge badge-gold">Replaces: {s.replaces}</span>}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
