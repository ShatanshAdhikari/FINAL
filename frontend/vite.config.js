import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// Origin of the backend API, used to scope the PWA runtime cache.
// Falls back to the local dev backend when VITE_API_BASE is unset.
const apiOrigin = (() => {
  try {
    return new URL(process.env.VITE_API_BASE || 'http://localhost:8000').origin
  } catch {
    return 'http://localhost:8000'
  }
})()

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'],
      manifest: {
        name: 'GetFit — Personal Fitness Companion',
        short_name: 'GetFit',
        description: 'Track workouts, calories, and steps — all in one place.',
        theme_color: '#111118',
        background_color: '#0f0f0f',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: 'favicon.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,ico}'],
        runtimeCaching: [
          {
            // Cache API responses for 10 minutes (backend origin only)
            urlPattern: ({ url }) => url.origin === apiOrigin,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: { maxEntries: 50, maxAgeSeconds: 60 * 10 },
            },
          },
        ],
      },
    }),
  ],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
