import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function DashboardPage() {
  const [stats, setStats] = useState<any>()

  useEffect(() => {
    api.get('/dashboard/usage').then((res) => setStats(res.data))
  }, [])

  return <pre className="bg-white p-4 rounded shadow">{JSON.stringify(stats, null, 2)}</pre>
}
