import { FormEvent, useEffect, useState } from 'react';

type User = { id: number; username: string; role: string };
type Lookup = { id: number; name: string };
type Ticket = {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  resolution: string;
  priority: Lookup;
  status: string;
  requester?: User;
  comments: { id: number; body: string; author: User; created_at: string }[];
};

type Props = { apiBaseUrl: string; token: string; user: User };

async function responseError(response: Response) {
  const data = await response.json().catch(() => null);
  if (typeof data?.detail === 'string') return data.detail;
  if (data && typeof data === 'object') {
    return Object.entries(data).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(' ') : String(value)}`).join(' ');
  }
  return `Request failed (${response.status})`;
}

export default function TicketWorkspace({ apiBaseUrl, token, user }: Props) {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [departments, setDepartments] = useState<Lookup[]>([]);
  const [categories, setCategories] = useState<Lookup[]>([]);
  const [priorities, setPriorities] = useState<Lookup[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [department, setDepartment] = useState('');
  const [category, setCategory] = useState('');
  const [priority, setPriority] = useState('');
  const [comments, setComments] = useState<Record<number, string>>({});
  const [resolutions, setResolutions] = useState<Record<number, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const isSupport = ['it_support', 'it_admin'].includes(user.role);

  async function api(path: string, init: RequestInit = {}) {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(init.body ? { 'Content-Type': 'application/json' } : {}),
        ...init.headers,
      },
    });
    if (!response.ok) throw new Error(await responseError(response));
    return response;
  }

  async function loadTickets() {
    const response = await api('/api/tickets/');
    const data = await response.json();
    setTickets(data.results || data);
  }

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const paths = ['/api/tickets/', '/api/ticket-departments/', '/api/categories/', '/api/priorities/'];
        const responses = await Promise.all(paths.map((path) => fetch(`${apiBaseUrl}${path}`, { headers: { Authorization: `Bearer ${token}` } })));
        const failed = responses.find((response) => !response.ok);
        if (failed) throw new Error(await responseError(failed));
        const [ticketsData, departmentsData, categoriesData, prioritiesData] = await Promise.all(responses.map((response) => response.json()));
        if (!active) return;
        setTickets(ticketsData.results || ticketsData);
        setDepartments(departmentsData.results || departmentsData);
        setCategories(categoriesData.results || categoriesData);
        setPriorities(prioritiesData.results || prioritiesData);
      } catch (cause) {
        if (active) setError(cause instanceof Error ? cause.message : 'Could not load tickets.');
      }
    }
    void load();
    return () => { active = false; };
  }, [apiBaseUrl, token]);

  async function submitTicket(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      await api('/api/tickets/', {
        method: 'POST',
        body: JSON.stringify({ title, description, department: Number(department), category: Number(category), priority: Number(priority) }),
      });
      setTitle(''); setDescription(''); setDepartment(''); setCategory(''); setPriority(''); setShowForm(false);
      await loadTickets();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not submit the ticket.');
    } finally { setBusy(false); }
  }

  async function act(ticketId: number, action: string, data?: object) {
    setError('');
    try {
      await api(`/api/tickets/${ticketId}/${action}/`, { method: 'POST', body: data ? JSON.stringify(data) : undefined });
      await loadTickets();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Ticket update failed.');
    }
  }

  async function downloadReport() {
    try {
      const response = await api('/api/reports/tickets.csv');
      const fileUrl = URL.createObjectURL(await response.blob());
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = 'kawuo-ticket-report.csv';
      link.click();
      URL.revokeObjectURL(fileUrl);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not download the report.');
    }
  }

  return (
    <>
      <section className="panel ticket-workspace">
        <div className="panel-header">
          <h2>{isSupport ? 'Ticket queue' : 'My tickets'}</h2>
          <div className="panel-tools">
            {isSupport && <button className="secondary-button" onClick={() => void downloadReport()}>Download report</button>}
            {!isSupport && <button className="primary-button" onClick={() => setShowForm(!showForm)}>{showForm ? 'Cancel' : 'Create ticket'}</button>}
          </div>
        </div>
        {error && <p className="error-message" role="alert">{error}</p>}
        {showForm && <form className="ticket-form" onSubmit={submitTicket}>
          <label>Issue title<input value={title} maxLength={255} onChange={(event) => setTitle(event.target.value)} required /></label>
          <label>Description<textarea rows={4} value={description} onChange={(event) => setDescription(event.target.value)} required /></label>
          <div className="lookup-fields">
            <label>Department<select value={department} onChange={(event) => setDepartment(event.target.value)} required><option value="">Select</option>{departments.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <label>Category<select value={category} onChange={(event) => setCategory(event.target.value)} required><option value="">Select</option>{categories.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <label>Priority<select value={priority} onChange={(event) => setPriority(event.target.value)} required><option value="">Select</option>{priorities.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          </div>
          <button className="primary-button" disabled={busy}>{busy ? 'Submitting…' : 'Submit ticket'}</button>
        </form>}
        {tickets.length === 0 ? <p className="table-state">No tickets to show yet.</p> : <div className="table-scroll">
          <table>
            <thead><tr><th>Ticket</th>{isSupport && <th>Requester</th>}<th>Issue</th><th>Priority</th><th>Status</th><th>Resolution / feedback</th></tr></thead>
            <tbody>{tickets.map((ticket) => <tr key={ticket.id}>
              <td>{ticket.ticket_number}</td>
              {isSupport && <td>{(ticket as Ticket & { requester?: User }).requester?.username}</td>}
              <td>{ticket.title}</td>
              <td><span className={`pill ${ticket.priority.name.toLowerCase()}`}>{ticket.priority.name}</span></td>
              <td>{ticket.status.replace(/_/g, ' ').toLowerCase()}</td>
              <td className="ticket-workflow-cell">
                {isSupport && ticket.status === 'NEW' && <button className="small-button" onClick={() => void act(ticket.id, 'acknowledge')}>Acknowledge</button>}
                {isSupport && !['RESOLVED', 'CLOSED'].includes(ticket.status) && <button className="small-button" onClick={() => void act(ticket.id, 'assign', { assigned_to: user.id })}>Assign to me</button>}
                {isSupport && !['RESOLVED', 'CLOSED'].includes(ticket.status) && <form className="inline-action" onSubmit={(event) => { event.preventDefault(); void act(ticket.id, 'resolve', { resolution: resolutions[ticket.id] || '' }); }}><input aria-label={`Resolution for ${ticket.ticket_number}`} placeholder="Resolution summary" value={resolutions[ticket.id] || ''} onChange={(event) => setResolutions({ ...resolutions, [ticket.id]: event.target.value })} required /><button className="small-button">Resolve</button></form>}
                {isSupport && ticket.status === 'RESOLVED' && <button className="small-button" onClick={() => void act(ticket.id, 'close')}>Close</button>}
                {!isSupport && ticket.status === 'RESOLVED' && <form className="inline-action" onSubmit={(event) => { event.preventDefault(); const body = comments[ticket.id] || ''; void act(ticket.id, 'comment', { body }); setComments({ ...comments, [ticket.id]: '' }); }}><input aria-label={`Feedback for ${ticket.ticket_number}`} placeholder="Add feedback" value={comments[ticket.id] || ''} onChange={(event) => setComments({ ...comments, [ticket.id]: event.target.value })} required /><button className="small-button">Send</button></form>}
                {ticket.resolution && <small className="comment-line">Resolution: {ticket.resolution}</small>}
                {ticket.comments?.map((comment) => <small className="comment-line" key={comment.id}>{comment.author.username}: {comment.body}</small>)}
              </td>
            </tr>)}</tbody>
          </table>
        </div>}
      </section>
    </>
  );
}
