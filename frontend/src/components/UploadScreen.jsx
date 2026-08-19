import { useState, useRef, useEffect } from 'react'

const ALLOWED = new Set(['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg'])

export default function UploadScreen({ onSuccess }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState({ msg: '', err: false })
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef()

  function pickFile(f) {
    const ext = '.' + f.name.split('.').pop().toLowerCase()
    if (!ALLOWED.has(ext)) {
      setStatus({ msg: `Unsupported file type: ${ext}`, err: true })
      return
    }
    setFile(f)
    setStatus({ msg: '', err: false })
  }

  function clearFile(e) {
    e.stopPropagation()
    setFile(null)
    inputRef.current.value = ''
  }

  async function handleUpload() {
    if (!file) return
    setLoading(true)
    setStatus({ msg: 'Parsing document…', err: false })
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch('/upload', { method: 'POST', body: fd })
      if (!res.ok) {
        let msg = 'Upload failed'
        try { const e = await res.json(); msg = e.detail || msg } catch (_) {}
        throw new Error(msg)
      }
      setStatus({ msg: 'Building knowledge index…', err: false })
      const data = await res.json()
      onSuccess(data)
    } catch (e) {
      setStatus({ msg: e.message, err: true })
      setLoading(false)
    }
  }

  return (
    <div className="upload-screen">
      <div className="brand">
        <span className="brand-icon">⚖️</span>
        <h1>LegalLens</h1>
        <p>Upload your contract — get instant AI-powered insights</p>
      </div>

      <div className="upload-card">
        {/* Drop zone — hidden when file selected */}
        {!file && (
          <div
            className={`dropzone${dragOver ? ' drag-over' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={e => { e.preventDefault(); setDragOver(false); if (e.dataTransfer.files[0]) pickFile(e.dataTransfer.files[0]) }}
            onClick={() => inputRef.current.click()}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg"
              onChange={e => { if (e.target.files[0]) pickFile(e.target.files[0]) }}
              style={{ display: 'none' }}
            />
            <span className="dz-icon">📄</span>
            <h3>Drag & drop your contract</h3>
            <p>or click to browse files</p>
            <div className="formats">
              {['PDF', 'DOCX', 'DOC', 'TXT', 'PNG', 'JPG'].map(f => (
                <span key={f} className="ftag">{f}</span>
              ))}
            </div>
          </div>
        )}

        {/* Selected file row */}
        {file && (
          <div className="file-row">
            <span>📄</span>
            <span className="file-name">{file.name}</span>
            <button className="rm-btn" onClick={clearFile} title="Remove">✕</button>
          </div>
        )}

        <button
          className="upload-btn"
          disabled={!file || loading}
          onClick={handleUpload}
        >
          {loading ? <><span className="spinner" />Processing…</> : file ? 'Analyze Contract' : 'Select a file to continue'}
        </button>

        <div className={`status-msg${status.err ? ' err' : ''}`}>{status.msg}</div>
      </div>
    </div>
  )
}
