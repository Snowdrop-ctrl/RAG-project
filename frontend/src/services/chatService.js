// Chat API layer. The UI only talks to `askQuestion`.

export const MODES = [
  { id: 'llm', label: 'LLM', description: 'Answer directly from the model' },
  { id: 'llm_rag', label: 'LLM + RAG', description: 'Ground answers in your documents' },
]

// Empty in dev: Vite proxies /api to the backend. Set VITE_API_URL for deployed builds.
const API_URL = import.meta.env.VITE_API_URL ?? ''

export async function askQuestion({ question, mode, signal }) {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, mode }),
    signal,
  })
  if (!res.ok) throw new Error(`Request failed (${res.status})`)
  return res.json() // { answer: string, sources: string[] }
}
