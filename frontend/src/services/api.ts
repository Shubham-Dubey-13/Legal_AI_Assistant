import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 90000, // 90 second timeout
})

// Attach JWT token automatically
api.interceptors.request.use((config) => {
  const stored = localStorage.getItem('legal-ai-auth')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      const token = parsed?.state?.token
      if (token) config.headers.Authorization = `Bearer ${token}`
    } catch {}
  }
  return config
})

// Response interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const isAuthRoute = error?.config?.url?.includes('/auth/')

    if (!error.response) {
      // Network error — backend not running
      error.userMessage = '🔌 Cannot connect to server. Make sure the backend is running: cd backend && uvicorn app.main:app --reload --port 8000'
    } else if (status === 401 && !isAuthRoute) {
      // Token expired — clear and redirect
      try {
        const stored = localStorage.getItem('legal-ai-auth')
        if (stored) { localStorage.removeItem('legal-ai-auth'); window.location.href = '/auth' }
      } catch {}
      error.userMessage = '🔑 Session expired. Please log in again.'
    } else if (status === 500) {
      error.userMessage = '⚠️ Server error. Please try again in a moment.'
    } else if (status === 504) {
      error.userMessage = '⏳ Request timed out. The AI is taking longer than usual — please try again.'
    } else if (status === 429) {
      error.userMessage = '🚦 Too many requests. Please wait a moment before trying again.'
    }
    return Promise.reject(error)
  }
)

// Auth
export const authAPI = {
  register: (data: any) => api.post('/auth/register', data),
  login: (data: any) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
}

// Chat
export const chatAPI = {
  query: (data: any) => api.post('/chat/query', data, { timeout: 90000 }),
  history: (id: string) => api.get(`/chat/conversations/${id}/history`),
  delete: (id: string) => api.delete(`/chat/conversations/${id}`),
  conversations: () => api.get('/chat/conversations'),
  exportPdf: (conversationId: string) =>
    api.get(`/chat/conversations/${conversationId}/export-pdf`, { responseType: 'blob' }),
  shareChatLink: (conversationId: string) => api.post(`/chat/conversations/${conversationId}/share`),
}

// Documents
export const documentsAPI = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  get: (id: string) => api.get(`/documents/${id}`),
  list: () => api.get('/documents/'),
  delete: (id: string) => api.delete(`/documents/${id}`),
}

// Search
export const searchAPI = {
  caseLaw: (data: any) => api.post('/search/caselaw', data),
  ipcSections: (query: string) => api.get(`/search/ipc-sections?query=${encodeURIComponent(query)}`),
  bnsSections: (query: string) => api.get(`/search/bns-sections?query=${encodeURIComponent(query)}`),
  similarCases: (desc: string, topK = 5) => api.get(`/search/similar-cases?case_description=${encodeURIComponent(desc)}&top_k=${topK}`),
  acts: () => api.get('/search/acts'),
}

// Drafts
export const draftsAPI = {
  generate: (data: any) => api.post('/drafts/generate', data),
  templates: () => api.get('/drafts/templates'),
  list: () => api.get('/drafts/'),
}

// Agents
export const agentsAPI = {
  status: () => api.get('/agents/status'),
  predictJudgment: (data: any) => api.post('/agents/predict-judgment', data),
  research: (query: string) => api.post('/agents/research', null, { params: { query } }),
  pipelineTrace: (id: string) => api.get(`/agents/pipeline-trace/${id}`),
}

// Analytics
export const analyticsAPI = {
  dashboard: () => api.get('/analytics/dashboard'),
}

export default api
