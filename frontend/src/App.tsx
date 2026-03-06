import { Routes, Route, Outlet } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import ScriptCreate from './pages/create/ScriptCreate'
import ImageCreate from './pages/create/ImageCreate'
import VideoCreate from './pages/create/VideoCreate'
import AdCreate from './pages/create/AdCreate'
import Works from './pages/works/Works'
import Tasks from './pages/works/Tasks'
import Gallery from './pages/works/Gallery'
import Account from './pages/account/Account'
import Pricing from './pages/Pricing'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout children={<Outlet />} />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="create/script" element={<ScriptCreate />} />
        <Route path="create/image" element={<ImageCreate />} />
        <Route path="create/video" element={<VideoCreate />} />
        <Route path="create/ad" element={<AdCreate />} />
        <Route path="works" element={<Works />} />
        <Route path="tasks" element={<Tasks />} />
        <Route path="gallery" element={<Gallery />} />
        <Route path="account/*" element={<Account />} />
        <Route path="pricing" element={<Pricing />} />
      </Route>
    </Routes>
  )
}

export default App
