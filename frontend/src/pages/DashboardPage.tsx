import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Dashboard = { usage: number; members: number; conversations: number; plan: string; subscription_status: string }

export function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null)

  useEffect(() => {
    api.get('/company/dashboard').then((res) => setData(res.data))
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      {data && (
        <div className="grid grid-cols-2 gap-4">
          <Card title="用量" value={String(data.usage)} />
          <Card title="成員" value={String(data.members)} />
          <Card title="對話" value={String(data.conversations)} />
          <Card title="方案" value={`${data.plan} (${data.subscription_status})`} />
        </div>
      )}
    </div>
  )
}

function Card({ title, value }: { title: string; value: string }) {
  return <div className="bg-white p-4 shadow rounded"><div className="text-gray-500">{title}</div><div className="text-xl">{value}</div></div>
}
