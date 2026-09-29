const stats = [
  { label: 'Open tickets', value: '24', change: '+5%' },
  { label: 'Critical incidents', value: '3', change: '2 due today' },
  { label: 'SLA compliance', value: '92%', change: '+4%' },
  { label: 'Asset availability', value: '89%', change: '14 in repair' },
];

const tickets = [
  { id: 'KAWUO-IT-000145', title: 'Laptop cannot connect to Wi-Fi', priority: 'Critical', status: 'In Progress' },
  { id: 'KAWUO-IT-000136', title: 'Printer offline in finance office', priority: 'High', status: 'Assigned' },
  { id: 'KAWUO-IT-000122', title: 'New user account request', priority: 'Medium', status: 'New' },
];

export default function App() {
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

        <nav className="nav">
          <a className="active" href="#">Dashboard</a>
          <a href="#">Tickets</a>
          <a href="#">Assets</a>
          <a href="#">Maintenance</a>
          <a href="#">Service Requests</a>
          <a href="#">Knowledge Base</a>
          <a href="#">Reports</a>
          <a href="#">Administration</a>
        </nav>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations overview</p>
            <h1>IT Service Dashboard</h1>
          </div>
          <button className="primary-button">Create ticket</button>
        </header>

        <section className="stats-grid">
          {stats.map((stat) => (
            <article key={stat.label} className="stat-card">
              <span>{stat.label}</span>
              <strong>{stat.value}</strong>
              <small>{stat.change}</small>
            </article>
          ))}
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Recent tickets</h2>
            <a href="#">View all</a>
          </div>

          <table>
            <thead>
              <tr>
                <th>Ticket</th>
                <th>Issue</th>
                <th>Priority</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((ticket) => (
                <tr key={ticket.id}>
                  <td>{ticket.id}</td>
                  <td>{ticket.title}</td>
                  <td><span className={`pill ${ticket.priority.toLowerCase()}`}>{ticket.priority}</span></td>
                  <td>{ticket.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}
