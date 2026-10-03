import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Sidebar from './components/common/Sidebar'
import Header from './components/common/Header'
import LandingPage from './pages/LandingPage'
import ChatPage from './pages/ChatPage'
import DocumentsPage from './pages/DocumentsPage'
import SearchPage from './pages/SearchPage'
import DraftsPage from './pages/DraftsPage'
import AnalyticsPage from './pages/AnalyticsPage'
import AgentsPage from './pages/AgentsPage'
import PredictionPage from './pages/PredictionPage'
import AuthPage from './pages/AuthPage'
import LawyerFinderPage from './pages/LawyerFinderPage'
import SettingsPage from './pages/SettingsPage'
import SharedChatPage from './pages/SharedChatPage'

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <Header />
        {children}
      </div>
    </div>
  )
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/auth" replace />
  return <ProtectedLayout>{children}</ProtectedLayout>
}

export default function App() {
  const { isAuthenticated, theme } = useAuthStore()

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  return (
    <Routes>
      <Route path="/" element={isAuthenticated ? <Navigate to="/chat" /> : <LandingPage />} />
      <Route path="/auth" element={isAuthenticated ? <Navigate to="/chat" /> : <AuthPage />} />
      <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
      <Route path="/documents" element={<ProtectedRoute><DocumentsPage /></ProtectedRoute>} />
      <Route path="/search" element={<ProtectedRoute><SearchPage /></ProtectedRoute>} />
      <Route path="/drafts" element={<ProtectedRoute><DraftsPage /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
      <Route path="/agents" element={<ProtectedRoute><AgentsPage /></ProtectedRoute>} />
      <Route path="/prediction" element={<ProtectedRoute><PredictionPage /></ProtectedRoute>} />
      <Route path="/lawyer-finder" element={<ProtectedRoute><LawyerFinderPage /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
      <Route path="/shared/:conversationId" element={<SharedChatPage />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
