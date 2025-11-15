import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

  // Development server configuration
  server: {
    port: 5173,
    host: '0.0.0.0', // Allow external connections
    proxy: {
      // Proxy API requests to nginx proxy
      '/api': {
        target: 'http://localhost:80',
        changeOrigin: true,
        secure: false
      },
      // Proxy ML service requests to nginx proxy
      '/ml': {
        target: 'http://localhost:80',
        changeOrigin: true,
        secure: false
      }
    }
  },

  // Build configuration
  build: {
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV === 'development'
  },

  // Environment variables prefix
  envPrefix: 'VITE_'
})
