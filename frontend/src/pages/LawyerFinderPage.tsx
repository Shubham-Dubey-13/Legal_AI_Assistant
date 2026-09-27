import { useState } from 'react'
import { motion } from 'framer-motion'

const HELPLINES = [
  { label: 'NALSA Free Legal Aid', number: '15100', icon: '⚖️' },
  { label: 'Women Helpline', number: '181', icon: '👩' },
  { label: 'Child Helpline', number: '1098', icon: '🧒' },
  { label: 'Cyber Crime', number: '1930', icon: '🖥️' },
  { label: 'Supreme Court of India', number: '011-23116400', icon: '🏛️' },
  { label: 'Bar Council of India', number: '011-23073038', icon: '📜' },
]

const AID_TYPES = [
  { title: 'District Legal Services Authority', desc: 'Free legal aid, Lok Adalats, mediation', icon: '🏢' },
  { title: 'Lok Adalat', desc: 'Out-of-court settlement, no court fees', icon: '⚖️' },
  { title: 'High Court Legal Services', desc: 'Appellate legal aid at High Court level', icon: '🏛️' },
  { title: 'Supreme Court Legal Services', desc: 'Free legal services at Supreme Court', icon: '🔱' },
  { title: 'Taluk Legal Services Committee', desc: 'Local-level free legal assistance', icon: '🌾' },
  { title: 'NALSA Schemes', desc: 'National legal aid schemes for marginalised', icon: '🤝' },
  { title: 'Women & Child Cell', desc: 'Dedicated support for women & children', icon: '👨‍👩‍👧' },
  { title: 'Legal Literacy Camps', desc: 'Community awareness & free guidance', icon: '📚' },
]

export default function LawyerFinderPage() {
  const [city, setCity] = useState('India')
  const [search, setSearch] = useState('')

  const mapSrc = `https://maps.google.com/maps?q=District+Legal+Services+Authority+${encodeURIComponent(city)}&output=embed`

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = search.trim()
    if (trimmed) setCity(trimmed)
  }

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1100, margin: '0 auto' }}>
      {/* Page heading */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: '0.25rem' }}>
          <span style={{ fontSize: '1.8rem' }}>🗺️</span>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 700, margin: 0 }}>Find Legal Aid Near You</h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1.5rem' }}>
          Locate NALSA / DLSA offices, Lok Adalats, and legal services committees across India.
        </p>
      </motion.div>

      {/* Search bar */}
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: 10, marginBottom: '1.25rem' }}>
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Enter city or state (e.g. Mumbai, Kerala, Delhi)…"
          style={{
            flex: 1,
            padding: '0.6rem 1rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border)',
            background: 'var(--surface)',
            color: 'var(--text-primary)',
            fontSize: '0.9rem',
            outline: 'none',
          }}
        />
        <button
          type="submit"
          className="btn btn-primary"
          style={{ padding: '0.6rem 1.2rem', fontSize: '0.85rem' }}
        >
          🔍 Search
        </button>
      </form>

      {/* Currently showing label */}
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
        Showing: <strong style={{ color: 'var(--text-secondary)' }}>District Legal Services Authority — {city}</strong>
      </div>

      {/* Map */}
      <div
        style={{
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          border: '1px solid var(--border)',
          marginBottom: '2rem',
          boxShadow: '0 4px 20px rgba(0,0,0,0.25)',
        }}
      >
        <iframe
          title="Legal Aid Map"
          src={mapSrc}
          width="100%"
          height="420"
          style={{ border: 0, display: 'block' }}
          allowFullScreen
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        />
      </div>

      {/* Helplines */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
        <h2 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.75rem' }}>
          📞 Important Legal Helplines
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: 10,
            marginBottom: '2rem',
          }}
        >
          {HELPLINES.map(h => (
            <div
              key={h.number}
              className="case-card"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 14,
                padding: '0.85rem 1rem',
              }}
            >
              <span style={{ fontSize: '1.5rem' }}>{h.icon}</span>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{h.label}</div>
                <div style={{ color: 'var(--primary-light)', fontWeight: 700, fontSize: '1rem', letterSpacing: 0.5 }}>
                  {h.number}
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Aid Types */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }}>
        <h2 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.75rem' }}>
          🏛️ Types of Legal Aid Available
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(230px, 1fr))',
            gap: 10,
          }}
        >
          {AID_TYPES.map(a => (
            <motion.div
              key={a.title}
              whileHover={{ scale: 1.02 }}
              className="case-card"
              style={{ padding: '1rem' }}
            >
              <div style={{ fontSize: '1.4rem', marginBottom: 6 }}>{a.icon}</div>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: 4 }}>{a.title}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{a.desc}</div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
