import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'

// 页面组件
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import UserManagement from './pages/UserManagement'
import OrderManagement from './pages/OrderManagement'
import RevenueStats from './pages/RevenueStats'
import PermissionPrices from './pages/PermissionPrices'

// 布局组件
import AdminLayout from './components/AdminLayout'

// 样式
import './styles/index.css'

// 路由守卫
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
        </Route>
      </Routes>
    </Router>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
