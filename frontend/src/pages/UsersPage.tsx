import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([])

  useEffect(() => {
    api.get('/users').then((res) => setUsers(res.data))
  }, [])

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-bold mb-3">使用者管理頁</h2>
      <ul className="space-y-2">{users.map((u) => <li key={u.id}>{u.email} - {u.role}</li>)}</ul>
    </div>
  )
}
