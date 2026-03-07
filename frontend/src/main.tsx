import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from './store'

import Home from './pages/Home'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import ScriptCreate from './pages/create/ScriptCreate'
import ImageCreate from './pages/create/ImageCreate'
import VideoCreate from './pages/create/VideoCreate'
import AdCreate from './pages/create/AdCreate'
import Tasks from './pages/works/Tasks'
import Works from './pages/works/Works'
import Gallery from './pages/works/Gallery'
import Pricing from './pages/Pricing'
import Account from './pages/account/Account'

import Layout from './components/layout/Layout'
import { I18nProvider } from './i18n'
import './styles/index.css'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

const withLayout = (node: React.ReactNode) => <Layout>{node}</Layout>

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={withLayout(<Home />)} />
        <Route path="/gallery" element={withLayout(<Gallery />)} />
        <Route path="/pricing" element={withLayout(<Pricing />)} />

        <Route
          path="/create/script"
          element={<ProtectedRoute>{withLayout(<ScriptCreate />)}</ProtectedRoute>}
        />
        <Route
          path="/create/image"
          element={<ProtectedRoute>{withLayout(<ImageCreate />)}</ProtectedRoute>}
        />
        <Route
          path="/create/video"
          element={<ProtectedRoute>{withLayout(<VideoCreate />)}</ProtectedRoute>}
        />
        <Route
          path="/create/ad"
          element={<ProtectedRoute>{withLayout(<AdCreate />)}</ProtectedRoute>}
        />
        <Route
          path="/tasks"
          element={<ProtectedRoute>{withLayout(<Tasks />)}</ProtectedRoute>}
        />
        <Route
          path="/works"
          element={<ProtectedRoute>{withLayout(<Works />)}</ProtectedRoute>}
        />
        <Route
          path="/account"
          element={<ProtectedRoute>{withLayout(<Account />)}</ProtectedRoute>}
        />

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <I18nProvider>
      <App />
    </I18nProvider>
  </React.StrictMode>
)
