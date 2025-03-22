import path from "path"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteStaticCopy } from 'vite-plugin-static-copy';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    viteStaticCopy({
      targets: [
        {
          src: 'public/manifest.json',
          dest: '.',
          
        },
        {
          src: 'src/extension/content.js', 
          dest: '.', 
        },
        {
          src: 'src/extension/background.js',
          dest: '.',
        }      ],
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: 'build',
    rollupOptions: {
      input: {
        main: './index.html',
      },
    },
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
    },
  },
});
