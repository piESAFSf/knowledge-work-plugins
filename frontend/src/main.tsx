import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { Layout } from './components/Layout'
import { CompanyPage } from './pages/CompanyPage'
import { DashboardPage } from './pages/DashboardPage'
import { LoginPage } from './pages/LoginPage'
import { StatsPage } from './pages/StatsPage'
import { SubscriptionPage } from './pages/SubscriptionPage'
import { UsersPage } from './pages/UsersPage'
import './index.css'

function AppRouter() {
  const location = useLocation()
  if (location.pathname === '/login') return <LoginPage />
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/company" element={<CompanyPage />} />
        <Route path="/stats" element={<StatsPage />} />
        <Route path="/subscription" element={<SubscriptionPage />} />
        <Route path="/users" element={<UsersPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  </React.StrictMode>,
)
