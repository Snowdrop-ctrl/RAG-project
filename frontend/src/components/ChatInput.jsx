import { useEffect, useRef, useState } from 'react'

export default function ChatInput({ onSubmit, disabled }) {
  const [text, setText] = useState('')
  const ref = useRef(null)

  // Auto-grow the textarea up to the max height set in CSS.
  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
    // Only allow scrolling once the text exceeds the CSS max-height.
    el.style.overflowY = el.scrollHeight > el.clientHeight + 1 ? 'auto' : 'hidden'
  }, [text])

  const submit = (e) => {
    e?.preventDefault()
    const question = text.trim()
    if (!question || disabled) return
    onSubmit(question)
    setText('')
  }

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) submit(e)
  }

  return (
    <form className="chat-input" onSubmit={submit}>
      <textarea
        ref={ref}
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Ask your question"
        aria-label="Ask your question"
        autoFocus
      />
      <button type="submit" className="send-btn" disabled={!text.trim() || disabled} aria-label="Submit question">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 19V5M5 12l7-7 7 7" />
        </svg>
      </button>
    </form>
  )
}
