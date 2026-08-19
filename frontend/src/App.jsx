import { useState, useEffect } from 'react'
import './App.css'
import UploadScreen from './components/UploadScreen'
import ChatScreen from './components/ChatScreen'

export default function App() {
  const [screen, setScreen] = useState('upload') // 'upload' | 'chat'
  const [sessionId, setSessionId] = useState(null)
  const [docSource, setDocSource] = useState('')

  function handleUploadSuccess(data) {
    setSessionId(data.session_id)
    setDocSource(data.source)
    setScreen('chat')
  }

  async function handleNewDoc() {
    await cleanupSession(sessionId)
    setSessionId(null)
    setDocSource('')
    setScreen('upload')
  }

  // Delete in-memory Chroma session when tab/window closes
  useEffect(() => {
    function onUnload() {
      if (sessionId) {
        fetch(`/session/${sessionId}`, { method: 'DELETE', keepalive: true })
      }
    }
    window.addEventListener('beforeunload', onUnload)
    return () => window.removeEventListener('beforeunload', onUnload)
  }, [sessionId])

  return (
    <>
      {screen === 'upload' && <UploadScreen onSuccess={handleUploadSuccess} />}
      {screen === 'chat' && (
        <ChatScreen
          sessionId={sessionId}
          docSource={docSource}
          onNewDoc={handleNewDoc}
        />
      )}
    </>
  )
}

async function cleanupSession(sessionId) {
  if (!sessionId) return
  try { await fetch(`/session/${sessionId}`, { method: 'DELETE', keepalive: true }) } catch (_) {}
}
