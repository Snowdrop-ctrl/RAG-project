import { useEffect, useRef, useState } from 'react'
import { deleteDocument, uploadDocument } from '../services/chatService'

const ACCEPT = '.pdf,.docx,.txt,.md'

export default function DocumentsPanel({ open, onClose, documents, onRefresh }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [dragging, setDragging] = useState(false)
  const fileRef = useRef(null)
  const panelRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  const handleFiles = async (files) => {
    if (!files?.length) return
    setBusy(true)
    setError(null)
    try {
      for (const file of files) {
        await uploadDocument(file)
      }
      await onRefresh()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  const handleDelete = async (source) => {
    setBusy(true)
    setError(null)
    try {
      await deleteDocument(source)
      await onRefresh()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="panel" ref={panelRef} role="dialog" aria-label="Documents">
        <header className="panel-header">
          <h2>Your documents</h2>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </header>

        <div
          className={`dropzone ${dragging ? 'is-dragging' : ''}`}
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            handleFiles([...e.dataTransfer.files])
          }}
        >
          <input
            ref={fileRef}
            type="file"
            accept={ACCEPT}
            multiple
            hidden
            onChange={(e) => handleFiles([...e.target.files])}
          />
          <p className="dropzone-title">Drop files here</p>
          <p className="dropzone-sub">PDF, DOCX, TXT or MD — up to 20 MB each</p>
          <button type="button" className="primary-btn" disabled={busy} onClick={() => fileRef.current?.click()}>
            {busy ? 'Working…' : 'Choose files'}
          </button>
        </div>

        {error && <p className="panel-error">{error}</p>}

        <ul className="doc-list">
          {documents.length === 0 && !busy && (
            <li className="doc-empty">No documents yet. Upload one to use LLM + RAG mode.</li>
          )}
          {documents.map((doc) => (
            <li key={doc.source} className="doc-item">
              <span className="doc-name" title={doc.source}>{doc.source}</span>
              <span className="doc-chunks">{doc.chunks} chunks</span>
              <button
                type="button"
                className="icon-btn"
                disabled={busy}
                onClick={() => handleDelete(doc.source)}
                aria-label={`Delete ${doc.source}`}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" />
                </svg>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
