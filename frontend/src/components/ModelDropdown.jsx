import { useEffect, useRef, useState } from 'react'
import { MODES } from '../services/chatService'

export default function ModelDropdown({ value, onChange }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)
  const selected = MODES.find((m) => m.id === value)

  useEffect(() => {
    if (!open) return
    const onClick = (e) => {
      if (!ref.current?.contains(e.target)) setOpen(false)
    }
    const onKey = (e) => e.key === 'Escape' && setOpen(false)
    document.addEventListener('mousedown', onClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <div className="dropdown" ref={ref}>
      <button
        type="button"
        className={`dropdown-trigger ${open ? 'is-open' : ''}`}
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span className={`mode-dot mode-dot--${value}`} />
        {selected?.label}
        <svg className="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      {open && (
        <ul className="dropdown-menu" role="listbox">
          {MODES.map((mode, i) => (
            <li key={mode.id}>
              <button
                type="button"
                role="option"
                aria-selected={mode.id === value}
                className={`dropdown-item ${mode.id === value ? 'is-active' : ''}`}
                onClick={() => {
                  onChange(mode.id)
                  setOpen(false)
                }}
              >
                <span className="dropdown-index">{i + 1}</span>
                <span className="dropdown-text">
                  <span className="dropdown-label">{mode.label}</span>
                  <span className="dropdown-desc">{mode.description}</span>
                </span>
                {mode.id === value && (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 6 9 17l-5-5" />
                  </svg>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
