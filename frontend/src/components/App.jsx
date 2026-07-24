import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './Navbar.jsx'
import Dashboard from './Dashboard.jsx'
import Profile from './Profile.jsx'
import Login from './Login.jsx'
import Register from './Register.jsx'
import { getProfile, logout as apiLogout } from '../api.js'

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('cc_token')
    if (!token) {
      setLoading(false)
      return
    }
    getProfile()
      .then(setUser)
      .catch(() => {
        apiLogout()
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  function handleLogout() {
    apiLogout()
    setUser(null)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 text-gray-500 dark:text-gray-400">
        Loading…
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100">
      <Navbar user={user} onLogout={handleLogout} />
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login onLogin={setUser} />} />
        <Route
          path="/register"
          element={user ? <Navigate to="/" replace /> : <Register onLogin={setUser} />}
        />
        <Route path="/" element={user ? <Dashboard user={user} /> : <Navigate to="/login" replace />} />
        <Route
          path="/profile"
          element={user ? <Profile user={user} onUpdate={setUser} /> : <Navigate to="/login" replace />}
        />
      </Routes>
    </div>
  )
}
