import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.post('/auth/login', { email, password })
    navigate('/dashboard')
  }

  return (
    <form onSubmit={submit} className="max-w-md mx-auto mt-20 bg-white p-6 rounded shadow space-y-3">
      <h1 className="text-xl font-bold">登入</h1>
      <input className="w-full border p-2" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input className="w-full border p-2" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button className="bg-blue-600 text-white px-4 py-2 rounded" type="submit">登入</button>
    </form>
  )
}
