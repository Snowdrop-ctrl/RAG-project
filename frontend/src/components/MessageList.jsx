import { useEffect, useRef } from 'react'

export default function MessageList({ messages, loading }) {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <div className="messages">
      {messages.map((msg) => (
        <div key={msg.id} className={`message message--${msg.role} ${msg.error ? 'message--error' : ''}`}>
          {msg.role === 'assistant' && <div className="avatar">AI</div>}
          <div className="bubble">
            {msg.modeLabel && <span className="bubble-tag">{msg.modeLabel}</span>}
            <p>{msg.content}</p>
            {msg.sources?.length > 0 && (
              <div className="sources">
                {msg.sources.map((s) => (
                  <span key={s} className="source-chip">{s}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}

      {loading && (
        <div className="message message--assistant">
          <div className="avatar">AI</div>
          <div className="bubble typing">
            <span /><span /><span />
          </div>
        </div>
      )}
      <div ref={endRef} />
    </div>
  )
}
