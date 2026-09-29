import { FormEvent, useEffect, useState } from 'react';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'https://kawuo-itsm-api.onrender.com').replace(/\/$/, '');
const ACCESS_TOKEN_KEY = 'kawuo_access_token';

type User = {
  username: string;
  first_name: string;
  last_name: string;
  role: string;
};

type Ticket = {
  id: number;
  ticket_number: string;
  title: string;
  priority: { name: string };
  status: string;
};

type DashboardSummary = {
  total_tickets: number;
  open_tickets: number;
  resolved_tickets: number;
  closed_tickets: number;
  critical_tickets: number;
  recent_tickets: Ticket[];
};

async function getApiError(response: Response) {
  const body = await response.json().catch(() => null);
  if (typeof body?.detail === 'string') return body.detail;
  if (typeof body === 'object' && body) {
    return Object.entries(body)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(' ') : String(value)}`)
      .join(' ');
  }
  return `Request failed (${response.status})`;
}

export default function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem(ACCESS_TOKEN_KEY));
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState<User | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    setLoading(true);
    setError('');

    Promise.all([
      fetch(`${API_BASE_URL}/api/auth/me/`, {
        headers: { Authorization: `Bearer ${token}` },
        signal: controller.signal,
      }),
      fetch(`${API_BASE_URL}/api/dashboard/summary/`, {
        headers: { Authorization: `Bearer ${token}` },
        signal: controller.signal,
      }),
    ])
      .then(async ([userResponse, summaryResponse]) => {
        if (!userResponse.ok || !summaryResponse.ok) {
          const failedResponse = !userResponse.ok ? userResponse : summaryResponse;
          throw new Error(await getApiError(failedResponse));
        }
        const [currentUser, dashboardSummary] = await Promise.all([
          userResponse.json(),
          summaryResponse.json(),
        ]);
        setUser(currentUser);
        setSummary(dashboardSummary);
      })
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === 'AbortError') return;
        sessionStorage.removeItem(ACCESS_TOKEN_KEY);
        setToken(null);
        setUser(null);
        setSummary(null);
        setError(cause instanceof Error ? cause.message : 'Could not load your dashboard.');
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [token]);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!response.ok) throw new Error(await getApiError(response));
      const result = await response.json();
      sessionStorage.setItem(ACCESS_TOKEN_KEY, result.access);
      setUser(result.user);
      setPassword('');
      setToken(result.access);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Login failed. Check your connection and try again.');
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    setToken(null);
    setUser(null);
    setSummary(null);
    setError('');
  }

  if (!token || !user || !summary) {
    return (
      <main className="login-page">
        <section className="login-panel" aria-labelledby="login-title">
          <div className="brand login-brand">
            <div className="brand-mark">K</div>
            <div><strong>KAWUO</strong><small>IT Service Management</small></div>
          </div>
          <p className="eyebrow">Secure staff access</p>
          <h1 id="login-title">Sign in to your workspace</h1>
          <p className="login-copy">Use your KAWUO ITSM account to access your service dashboard.</p>
          <form className="login-form" onSubmit={handleLogin}>
            <label htmlFor="username">Username</label>
            <input id="username" autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} required />
            <label htmlFor="password">Password</label>
            <input id="password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
            {error && <p className="error-message" role="alert">{error}</p>}
            <button className="primary-button login-button" type="submit" disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
          <p className="login-footnote">Account access is managed by your IT administrator.</p>
        </section>
      </main>
    );
  }

  const stats = [
    { label: 'Open tickets', value: summary.open_tickets, detail: `${summary.total_tickets} total` },
    { label: 'Critical tickets', value: summary.critical_tickets, detail: 'Requires attention' },
    { label: 'Resolved', value: summary.resolved_tickets, detail: 'Awaiting closure or complete' },
    { label: 'Closed', value: summary.closed_tickets, detail: 'Completed tickets' },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">K</div>
          <div>
            <strong>KAWUO</strong>
            <small>ITSM</small>
          </div>
        </div>

        <nav className="nav" aria-label="Main navigation">
          <span className="active">Dashboard</span>
          <a href={`${API_BASE_URL}/api/tickets/`} target="_blank" rel="noreferrer">Tickets API</a>
        </nav>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations overview</p>
            <h1>IT Service Dashboard</h1>
            <p className="welcome-copy">Welcome, {user.first_name || user.username}</p>
          </div>
          <button className="secondary-button" onClick={handleLogout}>Sign out</button>
        </header>

        <section className="stats-grid">
          {stats.map((stat) => (
            <article key={stat.label} className="stat-card">
              <span>{stat.label}</span>
              <strong>{stat.value}</strong>
              <small>{stat.detail}</small>
            </article>
          ))}
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Recent tickets</h2>
            <span className="role-label">{user.role.replace(/_/g, ' ')}</span>
          </div>

          {loading ? <p className="table-state">Loading tickets…</p> : summary.recent_tickets.length === 0 ? (
            <p className="table-state">No tickets to show yet.</p>
          ) : (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr><th>Ticket</th><th>Issue</th><th>Priority</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {summary.recent_tickets.map((ticket) => (
                    <tr key={ticket.id}>
                      <td>{ticket.ticket_number}</td>
                      <td>{ticket.title}</td>
                      <td><span className={`pill ${ticket.priority.name.toLowerCase()}`}>{ticket.priority.name}</span></td>
                      <td>{ticket.status.replace(/_/g, ' ').toLowerCase()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
