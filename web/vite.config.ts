import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.API_TARGET || 'http://127.0.0.1:8000'

  return {
    plugins: [vue()],
    base: '/accounting/',
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    server: {
      port: 3000,
      proxy: {
        '/accounting/api': {
          target: apiTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/accounting/, ''),
          secure: false,
          ws: true,
        },
      },
      historyApiFallback: {
        rewrites: [
          { from: /^\/accounting$/, to: '/accounting/' },
        ],
      },
    },
    appType: 'spa',
  }
})
