import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom'
import AdminLayout from './components/AdminLayout'
import { I18nProvider } from './i18n'
import Dashboard from './pages/Dashboard'
import AIProviderConfig from './pages/AIProviderConfig'
import Login from './pages/Login'
import OrderManagement from './pages/OrderManagement'
import PermissionPrices from './pages/PermissionPrices'
import RevenueStats from './pages/RevenueStats'
import UserManagement from './pages/UserManagement'
import './styles/index.css'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const token = localStorage.getItem('admin_token')

  if (!token) {
    return <Navigate to="/admin/login" />
  }

  return <>{children}</>
}

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/admin/login" element={<Login />} />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="orders" element={<OrderManagement />} />
          <Route path="revenue" element={<RevenueStats />} />
          <Route path="permissions" element={<PermissionPrices />} />
          <Route path="ai-config" element={<AIProviderConfig />} />
        </Route>
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
