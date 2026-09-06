import { FormEvent, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { authApi } from '@/services/authApi'
import { useAuthStore } from '@/store/authStore'

export default function Login() {
  const token = useAuthStore((state) => state.accessToken)
  const setSession = useAuthStore((state) => state.setSession)
  const [email, setEmail] = useState('demo@example.com')
  const [password, setPassword] = useState('ChangeMe123!')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (token) {
    return <Navigate to="/" replace />
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')

    try {
      let data
      try {
        data = await authApi.login(email, password)
      } catch {
        data = await authApi.register(email, password, 'Parmod K')
      }
      setSession(data.access_token, data.account)
    } catch {
      setError('Sign-in failed. Check API/database and credentials.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid min-h-screen place-items-center p-5">
      <Card className="w-full max-w-md p-7">
        <div className="mb-6">
          <p className="text-sm font-semibold text-primary">RETENTIONOS</p>
          <h1 className="mt-2 text-2xl font-semibold">Product analytics workspace</h1>
          <p className="mt-2 text-sm opacity-60">
            Use the demo credentials; the first submit automatically creates the account if it does
            not exist.
          </p>
        </div>

        <form className="space-y-4" onSubmit={submit}>
          <label className="block text-sm">
            Email
            <input
              className="mt-1 w-full rounded-xl border bg-background px-3 py-2"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              required
            />
          </label>

          <label className="block text-sm">
            Password
            <input
              className="mt-1 w-full rounded-xl border bg-background px-3 py-2"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              minLength={10}
              required
            />
          </label>

          {error && <p className="text-sm text-danger">{error}</p>}

          <Button className="w-full" disabled={busy}>
            {busy ? 'Connecting…' : 'Enter workspace'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
