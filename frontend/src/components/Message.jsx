import { useState } from 'react'

// Format markdown-style bold, headings, and newlines to JSX-safe HTML string
function formatText(raw) {
  return raw
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^#### (.+)$/gm, '<h5>$1</h5>')
    .replace(/\n/g, '<br>')
}

export default function Message({ role, text, contractSources = [], legalSources = [] }) {
  const [srcOpen, setSrcOpen] = useState(false)
  const hasSources = role === 'ai' && !!(contractSources.length || legalSources.length)

  return (
    <div className={`msg ${role}`}>
      <div className="avatar">{role === 'user' ? '👤' : '⚖️'}</div>
      <div>
        <div
          className="bubble"
          dangerouslySetInnerHTML={{ __html: formatText(text) }}
        />
        {hasSources && (
          <>
            <button className="src-toggle" onClick={() => setSrcOpen(o => !o)}>
              <span>📎 Sources</span>
              <span>{srcOpen ? '▲' : '▼'}</span>
            </button>
            <div className={`src-body${srcOpen ? ' open' : ''}`}>
              {contractSources.length > 0 && (
                <div className="src-sect">
                  <h5>Contract Clauses</h5>
                  <ul>{contractSources.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              )}
              {legalSources.length > 0 && (
                <div className="src-sect">
                  <h5>Legal Knowledge Base</h5>
                  <ul>{legalSources.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
