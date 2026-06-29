import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { analyticsAPI } from '../services/api'

const COLORS = ['#6366f1', '#8b5cf6', '#f59e0b', '#10b981', '#06b6d4', '#ef4444']

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '8px 14px', fontSize: '0.75rem' }}>
        <p style={{ color: 'var(--text-muted)', marginBottom: 4 }}>{label}</p>
        {payload.map((p: any, i: number) => (
          <p key={i} style={{ color: p.color || 'var(--text-primary)', fontWeight: 600 }}>{p.name}: {p.value}</p>
        ))}
      </div>
    )
  }
  return null
}

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    analyticsAPI.dashboard()
      .then(({ data }) => setData(data))
      .catch(() => {
        // Demo data
        setData({
          total_queries: 1247, total_documents: 89, total_drafts: 34, total_predictions: 56,
          avg_response_time_ms: 1420,
          query_trends: [
            { date: '05/12', count: 89 }, { date: '05/13', count: 102 }, { date: '05/14', count: 134 },
            { date: '05/15', count: 178 }, { date: '05/16', count: 156 }, { date: '05/17', count: 201 }, { date: '05/18', count: 187 },
          ],
          most_searched_sections: [
            { section: 'BNS 316 (Cheating)', count: 142 }, { section: 'Article 21', count: 98 },
            { section: 'BNS 74 (Assault)', count: 87 }, { section: 'Consumer Act S.35', count: 76 }, { section: 'BNS 63 (Rape)', count: 65 },
          ],
          agent_performance: {
            orchestrator: { avg_ms: 120, success_rate: 0.98 }, retrieval: { avg_ms: 340, success_rate: 0.97 },
            research: { avg_ms: 890, success_rate: 0.95 }, verification: { avg_ms: 210, success_rate: 0.99 },
            summarization: { avg_ms: 560, success_rate: 0.96 }, drafting: { avg_ms: 1200, success_rate: 0.94 },
            citation: { avg_ms: 90, success_rate: 0.98 }, memory: { avg_ms: 45, success_rate: 0.99 },
          },
          top_case_types: [
            { type: 'Criminal', percentage: 33.9 }, { type: 'Civil', percentage: 25.0 },
            { type: 'Consumer', percentage: 15.9 }, { type: 'Constitutional', percentage: 12.5 }, { type: 'Family', percentage: 12.7 },
          ],
          language_distribution: [
            { language: 'English', count: 789 }, { language: 'Hindi', count: 287 },
            { language: 'Bengali', count: 89 }, { language: 'Tamil', count: 56 }, { language: 'Telugu', count: 26 },
          ],
        })
      })
  }, [])

  if (!data) return <div className="page-container"><div style={{ textAlign: 'center', padding: '4rem' }}>Loading analytics...</div></div>

  const STATS = [
    { icon: '💬', value: data.total_queries.toLocaleString(), label: 'Total Queries', change: '+24% this week', color: '#6366f1' },
    { icon: '📄', value: data.total_documents, label: 'Documents Processed', change: '+12 this week', color: '#10b981' },
    { icon: '✍️', value: data.total_drafts, label: 'Drafts Generated', change: '+8 this week', color: '#f59e0b' },
    { icon: '🔮', value: data.total_predictions, label: 'Predictions Made', change: '+15 this week', color: '#8b5cf6' },
  ]

  const agentData = Object.entries(data.agent_performance).map(([name, perf]: any) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1), avg_ms: perf.avg_ms, success: Math.round(perf.success_rate * 100),
  }))

  return (
    <div className="page-container">
      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {STATS.map((s, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
            className="stat-card" style={{ borderColor: `${s.color}30` }}>
            <div className="stat-icon" style={{ background: `${s.color}15`, fontSize: '1.3rem' }}>{s.icon}</div>
            <div className="stat-content">
              <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
              <div className="stat-label">{s.label}</div>
              <div className="stat-change">{s.change}</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Avg response time */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Query trend */}
        <div className="chart-card">
          <div className="chart-title">📈 Query Volume (Last 7 Days)</div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={data.query_trends}>
              <defs>
                <linearGradient id="queryGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="count" name="Queries" stroke="#6366f1" fill="url(#queryGrad)" strokeWidth={2} dot={{ fill: '#6366f1', r: 3 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Case type distribution */}
        <div className="chart-card">
          <div className="chart-title">⚖️ Case Types</div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={data.top_case_types} cx="50%" cy="50%" outerRadius={75} dataKey="percentage" nameKey="type" label={({ type, percentage }) => `${type}: ${percentage}%`} labelLine={false} fontSize={10}>
                {data.top_case_types.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v: any) => `${v}%`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Agent performance */}
        <div className="chart-card">
          <div className="chart-title">🤖 Agent Response Times (ms)</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={agentData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} width={80} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="avg_ms" name="Avg ms" radius={[0, 4, 4, 0]}>
                {agentData.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Most searched sections */}
        <div className="chart-card">
          <div className="chart-title">📜 Most Queried Legal Sections</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {data.most_searched_sections.map((s: any, i: number) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 24, height: 24, borderRadius: '50%', background: `${COLORS[i]}20`, border: `1px solid ${COLORS[i]}40`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', color: COLORS[i], fontWeight: 700, flexShrink: 0 }}>{i + 1}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{s.section}</div>
                  <div className="progress-bar" style={{ height: 3 }}>
                    <div className="progress-fill" style={{ width: `${(s.count / data.most_searched_sections[0].count) * 100}%`, background: COLORS[i] }} />
                  </div>
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, minWidth: 35, textAlign: 'right' }}>{s.count}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Agent success rates */}
      <div className="chart-card">
        <div className="chart-title">✅ Agent Success Rates</div>
        <div className="agent-status-grid">
          {agentData.map((a, i) => (
            <div key={i} className="agent-status-card">
              <div className="agent-dot online" />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-primary)' }}>{a.name}</div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{a.avg_ms}ms avg · {a.success}% success</div>
                <div className="progress-bar" style={{ marginTop: 5 }}>
                  <div className="progress-fill" style={{ width: `${a.success}%`, background: COLORS[i % COLORS.length] }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
