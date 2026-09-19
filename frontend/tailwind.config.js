/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: 'hsl(var(--ink))',
        canvas: 'hsl(var(--canvas))',
        surface: 'hsl(var(--surface))',
        line: 'hsl(var(--line))',
        coral: 'hsl(var(--coral))',
        mint: 'hsl(var(--mint))',
        sun: 'hsl(var(--sun))',
        sky: 'hsl(var(--sky))',
      },
      fontFamily: {
        sans: ['Manrope', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 12px 32px rgba(21, 35, 42, 0.08)',
        float: '0 20px 50px rgba(21, 35, 42, 0.13)',
      },
      borderRadius: { xl: '1rem', '2xl': '1.5rem' },
    },
  },
  plugins: [],
}
