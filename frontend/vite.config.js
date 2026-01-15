import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  optimizeDeps: {
    force: true
  },
  
  // Server configuration for Docker
  server: {
    host: '0.0.0.0',  // Accept connections from Docker network
    port: 5173,        // Port number
    watch: {
      usePolling: true,  // Required for Docker file watching
    },
    hmr: {
      host: 'localhost',  // Hot Module Replacement
    }
  }
})
