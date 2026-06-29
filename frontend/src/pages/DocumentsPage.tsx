import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { documentsAPI } from '../services/api'
import toast from 'react-hot-toast'

interface UploadedDoc {
  id: string; filename: string; status: string; analysis?: any
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState<UploadedDoc[]>([])
  const [uploading, setUploading] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState<UploadedDoc | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      setUploading(true)
      try {
        const { data } = await documentsAPI.upload(file)
        const doc = { id: data.document_id, filename: file.name, status: 'processing' }
        setDocs(prev => [doc, ...prev])
        toast.success(`📄 "${file.name}" uploaded! AI analysis in progress...`)

        // Poll for completion
        setTimeout(async () => {
          try {
            const { data: analysis } = await documentsAPI.get(data.document_id)
            setDocs(prev => prev.map(d => d.id === data.document_id ? { ...d, status: 'completed', analysis } : d))
            toast.success(`✅ Analysis complete for "${file.name}"`)
          } catch { }
        }, 3000)
      } catch {
        toast.error(`Failed to upload ${file.name}`)
      } finally { setUploading(false) }
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'], 'application/msword': ['.doc', '.docx'] }, maxSize: 50 * 1024 * 1024
  })

  return (
    <div className="page-container">
      <div style={{ display: 'grid', gridTemplateColumns: selectedDoc ? '1fr 420px' : '1fr', gap: '1.5rem' }}>
        <div>
          {/* Upload Zone */}
          <div {...getRootProps()} className={`drop-zone ${isDragActive ? 'active' : ''}`} style={{ marginBottom: '1.5rem' }}>
            <input {...getInputProps()} />
            <span className="drop-icon">{uploading ? '⏳' : '📄'}</span>
            <div className="drop-title">{isDragActive ? 'Drop legal documents here...' : uploading ? 'Uploading and analyzing...' : 'Upload Legal Documents'}</div>
            <div className="drop-subtitle">Drag & drop PDF/DOCX files, or click to browse</div>
            <div style={{ marginTop: '1rem', display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
              {['📋 FIR', '📜 Judgment', '📑 Contract', '🏛️ Petition', '📝 Notice'].map(t => (
                <span key={t} className="badge badge-primary">{t}</span>
              ))}
            </div>
            {uploading && <div className="progress-bar" style={{ marginTop: '1.5rem', maxWidth: 300, margin: '1.5rem auto 0' }}><div className="progress-fill" style={{ width: '60%' }} /></div>}
          </div>

          {/* Processing Pipeline Info */}
          <div className="card" style={{ marginBottom: '1.5rem', padding: '1.25rem' }}>
            <h4 style={{ marginBottom: '0.875rem', color: 'var(--text-muted)', fontSize: '0.75rem', letterSpacing: '0.08em', textTransform: 'uppercase' }}>AI Processing Pipeline</h4>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {['1. PDF Parse (PyMuPDF)', '2. OCR Fallback', '3. Section Chunking', '4. OpenAI Embeddings', '5. ChromaDB Index', '6. IPC/BNS Detection', '7. NER Extraction', '8. AI Summary'].map((s, i) => (
                <span key={i} className="badge badge-info" style={{ fontSize: '0.65rem' }}>{s}</span>
              ))}
            </div>
          </div>

          {/* Document List */}
          {docs.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📂</div>
              <div className="empty-title">No Documents Yet</div>
              <div className="empty-desc">Upload a legal PDF to get AI-powered analysis, section identification, and summary.</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
              {docs.map(doc => (
                <motion.div key={doc.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  className="case-card" onClick={() => setSelectedDoc(doc === selectedDoc ? null : doc)}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ fontSize: '1.75rem' }}>📄</span>
                    <div style={{ flex: 1 }}>
                      <div className="case-name">{doc.filename}</div>
                      <div style={{ display: 'flex', gap: 8, marginTop: 6, flexWrap: 'wrap' }}>
                        <span className={`badge ${doc.status === 'completed' ? 'badge-success' : 'badge-gold'}`}>
                          {doc.status === 'completed' ? '✅ Analyzed' : '⏳ Processing...'}
                        </span>
                        {doc.analysis?.case_type && <span className="badge badge-primary">{doc.analysis.case_type}</span>}
                        {doc.analysis?.page_count && <span className="badge badge-info">📑 {doc.analysis.page_count} pages</span>}
                      </div>
                    </div>
                    {doc.status === 'processing' && (
                      <div style={{ width: 20, height: 20, border: '2px solid var(--primary)', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Analysis Panel */}
        <AnimatePresence>
          {selectedDoc?.analysis && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}
              className="card" style={{ height: 'fit-content', position: 'sticky', top: '80px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '0.95rem' }}>📊 AI Analysis</h3>
                <button className="btn btn-ghost btn-sm" onClick={() => setSelectedDoc(null)}>✕</button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <div className="form-label" style={{ marginBottom: 6 }}>📝 Summary</div>
                  <p style={{ fontSize: '0.8rem', lineHeight: 1.6 }}>{selectedDoc.analysis.summary}</p>
                </div>
                {selectedDoc.analysis.bns_sections?.length > 0 && (
                  <div>
                    <div className="form-label" style={{ marginBottom: 6 }}>📜 BNS Sections</div>
                    <div className="sections-row">{selectedDoc.analysis.bns_sections?.map((s: string, i: number) => <span key={i} className="badge badge-primary">{s}</span>)}</div>
                  </div>
                )}
                {selectedDoc.analysis.key_points?.length > 0 && (
                  <div>
                    <div className="form-label" style={{ marginBottom: 6 }}>🔑 Key Points</div>
                    <ul style={{ paddingLeft: '1rem' }}>
                      {selectedDoc.analysis.key_points?.map((p: string, i: number) => (
                        <li key={i} style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: 4 }}>{p}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div>
                  <div className="form-label" style={{ marginBottom: 6 }}>👥 Parties</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                    <div>Petitioner: {selectedDoc.analysis.parties?.petitioner || 'N/A'}</div>
                    <div>Respondent: {selectedDoc.analysis.parties?.respondent || 'N/A'}</div>
                  </div>
                </div>
                <button className="btn btn-primary btn-sm" style={{ width: '100%' }} onClick={() => toast.success('Opening in chat...')}>
                  💬 Ask Questions About This Document
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
