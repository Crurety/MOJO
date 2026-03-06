import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store'

// 页面组件
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

// 布局组件
import Layout from './components/layout/Layout'

// 样式
import './styles/index.css'

// 路由守卫
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore.getState().isAuthenticated
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }
  
  return <>{children}</>
}

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout children={<Home />} />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route path="/create/script" element={<ProtectedRoute children={<ScriptCreate />} />} />
        <Route path="/create/image" element={<ProtectedRoute children={<ImageCreate />} />} />
        <Route path="/create/video" element={<ProtectedRoute children={<VideoCreate />} />} />
        <Route path="/create/ad" element={<ProtectedRoute children={<AdCreate />} />} />
        
        <Route path="/tasks" element={<ProtectedRoute children={<Tasks />} />} />
        <Route path="/works" element={<ProtectedRoute children={<Works />} />} />
        <Route path="/gallery" element={<Layout children={<Gallery />} />} />
        <Route path="/pricing" element={<Layout children={<Pricing />} />} />
        <Route path="/account" element={<ProtectedRoute children={<Account />} />} />
      </Routes>
    </Router>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
