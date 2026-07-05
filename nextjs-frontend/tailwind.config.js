/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          400: '#A78BFA',
          500: '#8B5CF6',
          600: '#6D5DF6',
          700: '#5B4FD4',
        },
        dark: {
          bg: '#08061a',
          card: '#0c0a1e',
          border: 'rgba(255,255,255,0.06)',
          hover: '#12102a',
          sidebar: '#060518',
          sidebarActive: '#1a1838',
        },
        text: {
          heading: '#F0EEFF',
          main: '#8E8BA3',
          muted: '#5C5A7A',
          tableh: '#6B6890',
        },
        accent: {
          amber: '#F59E4A',
          violet: '#8B5CF6',
          blue: '#6D5DF6',
          purple: '#A855F7',
        },
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
