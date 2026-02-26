import { useEffect, useState } from 'react'
import { api } from '../api/client'

export function UsersPage() {
  const [users, setUsers] = useState<Array<{ id: number; email: string; full_name: string; role: string }>>([])
  useEffect(() => {
    api.get('/company/users').then((res) => setUsers(res.data))
  }, [])
  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-bold mb-3">使用者管理</h2>
      <ul className="space-y-2">{users.map((u) => <li key={u.id}>{u.full_name} ({u.email}) - {u.role}</li>)}</ul>
    </div>
  )
}
