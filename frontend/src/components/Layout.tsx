import { Link } from 'react-router-dom'
import { ReactNode } from 'react'

export function Layout({ children }: { children: ReactNode }) {
  const navItems = [
    ['Dashboard', '/'],
    ['公司管理', '/company'],
    ['使用統計', '/stats'],
    ['訂閱管理', '/subscription'],
    ['使用者管理', '/users'],
  ]

  return (
    <div className="min-h-screen bg-slate-100">
      <nav className="bg-slate-800 text-white p-4 flex gap-4">
        {navItems.map(([label, path]) => (
          <Link key={path} to={path} className="hover:text-cyan-300">{label}</Link>
        ))}
      </nav>
      <main className="p-6">{children}</main>
    </div>
  )
}
