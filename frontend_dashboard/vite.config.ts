import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')
  
  const backendUrl = env.BACKEND_URL || 'http://127.0.0.1:8000'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        'vue': 'vue/dist/vue.esm-bundler.js'
      }
    },
    server: {
      host: '0.0.0.0',
      port: 8080,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
        },
        '/admin': {
          target: backendUrl,
          changeOrigin: true,
        },
        '/static': {
          target: backendUrl,
          changeOrigin: true,
        }
      }
    }
  }
})
