import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: '../dist/frontend',
  },
  server: {
    fs: {
      allow: ['..']
    },
    host: 'localhost',
    hmr: {
      // Use a more reliable WebSocket setup
      protocol: 'ws',
      host: 'localhost',
      port: 5173,
      clientPort: 5173, // Explicitly set client port
      timeout: 60000,   // Increase timeout
    }
  },
  // Load env file from the root directory
  envDir: path.resolve(__dirname, '..')
})
