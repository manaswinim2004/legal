import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy API calls to FastAPI in dev mode
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/upload': 'http://localhost:8000',
      '/chat': 'http://localhost:8000',
      '/session': 'http://localhost:8000',
    },
  },
})
