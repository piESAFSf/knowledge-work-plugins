import { useEffect, useState } from 'react'
import { api } from '../api/client'

export function CompanyPage() {
  const [company, setCompany] = useState<{ name: string; quota_limit: number } | null>(null)
  useEffect(() => {
    api.get('/company/current').then((res) => setCompany(res.data))
  }, [])
  return <div className="bg-white p-4 rounded shadow">{company ? `${company.name} / Quota: ${company.quota_limit}` : 'Loading...'}</div>
}
