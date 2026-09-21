import { useState } from 'react'
import ModelDropdown from './components/ModelDropdown'
import ChatInput from './components/ChatInput'
import MessageList from './components/MessageList'
import { askQuestion, MODES } from './services/chatService'

export default function App() {
  const [mode, setMode] = useState('llm_rag')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (question) => {
    const modeLabel = MODES.find((m) => m.id === mode)?.label
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', content: question }])
    setLoading(true)
    try {
      const { answer, sources } = await askQuestion({ question, mode })
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'assistant', content: answer, sources, modeLabel },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'assistant', content: err.message, error: true },
      ])
    } finally {
      setLoading(false)
    }
  }

  const hasMessages = messages.length > 0

  return (
    <div className="app">
      <div className="bg-glow bg-glow--1" />
      <div className="bg-glow bg-glow--2" />

      <main className="chat-card">
        <header className="chat-header">
          <div className="brand">
            <div className="brand-logo">R</div>
            <span>RAG Chat</span>
          </div>
          <div className="header-actions">
            {hasMessages && (
              <button type="button" className="ghost-btn" onClick={() => setMessages([])}>
                New chat
              </button>
            )}
            <ModelDropdown value={mode} onChange={setMode} />
          </div>
        </header>

        {hasMessages ? (
          <>
            <MessageList messages={messages} loading={loading} />
            <div className="composer composer--bottom">
              <ChatInput onSubmit={handleSubmit} disabled={loading} />
            </div>
          </>
        ) : (
          <section className="welcome">
            <div className="welcome-badge">✦ Retrieval-Augmented Generation</div>
            <h1>
              Welcome to <span className="gradient-text">RAG project</span>
            </h1>
            <p className="welcome-sub">Ask anything — choose plain LLM or ground answers in your knowledge base.</p>
            <div className="composer">
              <ChatInput onSubmit={handleSubmit} disabled={loading} />
            </div>
          </section>
        )}
      </main>
    </div>
  )
}
