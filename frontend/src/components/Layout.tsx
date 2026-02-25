import { Link, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow p-4 flex gap-4">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/companies">公司管理</Link>
        <Link to="/users">使用者管理</Link>
        <Link to="/stats">使用統計</Link>
        <Link to="/subscriptions">訂閱管理</Link>
      </nav>
      <main className="p-6"><Outlet /></main>
    </div>
  )
}
