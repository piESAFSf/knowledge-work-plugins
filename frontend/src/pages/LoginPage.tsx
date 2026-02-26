import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('owner@example.com')
  const [password, setPassword] = useState('password123')

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    await api.post('/auth/login', { email, password })
    navigate('/')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <form onSubmit={onSubmit} className="bg-white p-8 rounded shadow w-[360px] space-y-4">
        <h1 className="text-2xl font-bold">企業登入</h1>
        <input className="w-full border rounded p-2" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="w-full border rounded p-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button className="w-full bg-slate-800 text-white p-2 rounded">登入</button>
      </form>
    </div>
  )
}
