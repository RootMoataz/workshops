import { useEffect, useState } from 'react'

// Set at build time: VITE_API_URL=https://<api-id>.execute-api.us-east-1.amazonaws.com npm run build
const API_URL = `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/notices`

export default function App() {
  const [notices, setNotices] = useState([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [error, setError] = useState('')

  async function call(url, options) {
    const res = await fetch(url, options)
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`)
    return data
  }

  async function load() {
    try {
      setNotices(await call(API_URL))
      setError('')
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => { load() }, [])

  function reset() {
    setEditingId(null)
    setTitle('')
    setContent('')
  }

  async function save(event) {
    event.preventDefault()
    const url = editingId ? `${API_URL}/${editingId}` : API_URL
    try {
      await call(url, {
        method: editingId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      })
      reset()
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  async function remove(id) {
    try {
      await call(`${API_URL}/${id}`, { method: 'DELETE' })
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  function edit(notice) {
    setEditingId(notice._id)
    setTitle(notice.title)
    setContent(notice.content)
  }

  return (
    <main className="board">
      <h1>Notice Board</h1>
      {error && <p className="error" role="alert">{error}</p>}
      <form onSubmit={save}>
        <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <textarea placeholder="Content" value={content} onChange={(e) => setContent(e.target.value)} />
        <div className="row">
          <button type="submit">{editingId ? 'Save changes' : 'Add notice'}</button>
          {editingId && (
            <button type="button" className="secondary" onClick={reset}>Cancel</button>
          )}
        </div>
      </form>
      <h2>All notices</h2>
      {notices.length === 0 && <p className="muted">No notices yet.</p>}
      {notices.map((n) => (
        <article key={n._id} className="notice">
          <h3>{n.title}</h3>
          <p>{n.content}</p>
          <div className="row">
            <button className="secondary" onClick={() => edit(n)}>Edit</button>
            <button className="danger" onClick={() => remove(n._id)}>Delete</button>
          </div>
        </article>
      ))}
    </main>
  )
}
