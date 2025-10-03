import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: './public',
  build: {
    outDir: '../build',
    sourcemap: false,
    emptyOutDir: true
  },
  server: {
    port: 3000,
    open: true
  }
})