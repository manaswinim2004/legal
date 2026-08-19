import { useState, useRef, useEffect } from 'react'
import Message from './Message'

const SUGGESTIONS = [
  'What are the risky clauses?',
  'Summarize the key obligations',
  'Are there any red flags?',
  'What are my termination rights?',
  'Explain the indemnification clause',
]

export default function ChatScreen({ sessionId, docSource, onNewDoc }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [typing, setTyping] = useState(false)
  const msgsRef = useRef()

  // Scroll to bottom whenever messages or typing state changes
  useEffect(() => {
    if (msgsRef.current) msgsRef.current.scrollTop = msgsRef.current.scrollHeight
  }, [messages, typing])

  async function sendMessage(text) {
    const msg = (text || input).trim()
    if (!msg || busy) return
    setInput('')
    setBusy(true)
    setMessages(prev => [...prev, { role: 'user', text: msg }])
    setTyping(true)
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: msg }),
      })
      if (!res.ok) {
        let msg = 'Error'
        try { const e = await res.json(); msg = e.detail || msg } catch (_) {}
        throw new Error(msg)
      }
      const data = await res.json()
      setMessages(prev => [...prev, {
        role: 'ai',
        text: data.answer,
        contractSources: data.contract_sources || [],
        legalSources: data.legal_sources || [],
      }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'ai', text: `⚠️ ${e.message}` }])
    } finally {
      setTyping(false)
      setBusy(false)
    }
  }

  return (
    <div className="chat-screen">
      <div className="chat-header">
        <span className="header-brand">⚖️ LegalLens</span>
        <div className="header-div" />
        <div className="doc-info">
          <span className="doc-name">{docSource}</span>
        </div>
        <button className="new-btn" onClick={onNewDoc}>↩ New Document</button>
      </div>

      <div className="msgs" ref={msgsRef}>
        {/* Welcome prompt shown until first message */}
        {messages.length === 0 && (
          <div className="welcome">
            <span className="welcome-icon">🔍</span>
            <h3>Ready to analyze your contract</h3>
            <p>Ask me anything — risky clauses, obligations, red flags, termination rights, or legal implications.</p>
            <div className="chips">
              {SUGGESTIONS.map(s => (
                <button key={s} className="chip" onClick={() => sendMessage(s)}>{s}</button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <Message key={i} {...m} />
        ))}

        {typing && (
          <div className="typing">
            <div className="avatar" style={{ background: 'var(--surface-2)', border: '1px solid var(--border)' }}>⚖️</div>
            <div className="dots"><span /><span /><span /></div>
          </div>
        )}
      </div>

      <div className="input-area">
        <input
          className="msg-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() } }}
          placeholder="Ask anything about this contract…"
          maxLength={1000}
          autoComplete="off"
          disabled={busy}
        />
        <button className="send-btn" onClick={() => sendMessage()} disabled={busy || !input.trim()}>
          Send →
        </button>
      </div>
    </div>
  )
}
