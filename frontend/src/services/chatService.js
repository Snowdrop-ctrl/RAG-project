// API layer. The UI only talks to the functions in this file.

export const MODES = [
  { id: 'llm', label: 'LLM', description: 'Answer directly from the model' },
  { id: 'llm_rag', label: 'LLM + RAG', description: 'Ground answers in your documents' },
]

// Empty in dev: Vite proxies /api to the backend. Set VITE_API_URL for deployed builds.
const API_URL = import.meta.env.VITE_API_URL ?? ''

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}/api${path}`, options)
  if (!res.ok) {
    const detail = await res
      .json()
      .then((b) => b.detail)
      .catch(() => null)
    throw new Error(typeof detail === 'string' ? detail : `Request failed (${res.status})`)
  }
  return res.status === 204 ? null : res.json()
}

export function askQuestion({ question, mode, signal }) {
  return request('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, mode }),
    signal,
  }) // { answer: string, sources: [{ label, source, page, score }] }
}

export function listDocuments() {
  return request('/documents') // { documents: [{ source, chunks }], total_chunks }
}

export function uploadDocument(file) {
  const body = new FormData()
  body.append('file', file)
  return request('/documents', { method: 'POST', body })
}

export function deleteDocument(source) {
  return request(`/documents/${encodeURIComponent(source)}`, { method: 'DELETE' })
}
