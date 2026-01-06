import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // allowedHosts: [
    //   'jola197.mikrus.xyz'
    // ],
    // host: true,

    host: '0.0.0.0', // to już pewnie masz, żeby Docker działał
    allowedHosts: [
      'domatormyszyniec.pl',
      'www.domatormyszyniec.pl',
      'jola197.mikrus.xyz',
      'localhost',
      // 'localhost:20197',
      // 'localhost:30197'
    ],
    strictPort: true
  }
})
