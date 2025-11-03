/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: {
          deep: '#0f1419',
          mid: '#1a2332',
          light: '#252f3f',
        },
        silver: {
          warm: '#e8eef2',
          warmer: '#f0f4f7',
        },
      },
    },
  },
  plugins: [],
}
