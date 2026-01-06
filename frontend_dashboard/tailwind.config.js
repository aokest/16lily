/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // 颜色系统扩展 (Color System Extension)
      colors: {
        // 品牌色 (Brand Colors)
        'pomegranate': {
          DEFAULT: '#D64045',
          50: '#FDE8E9',
          100: '#FBD1D3',
          200: '#F8A3A7',
          300: '#F4757C',
          400: '#F14750',
          500: '#D64045', // 主色
          600: '#A61B29',
          700: '#7D1420',
          800: '#540E16',
          900: '#2B070B',
        },
        'gold': {
          DEFAULT: '#D4AF37',
          50: '#FBF5E0',
          100: '#F7EAC1',
          200: '#F0D583',
          300: '#E8C045',
          400: '#D4AF37', // 主色
          500: '#B8941E',
          600: '#8B7017',
          700: '#5E4B10',
          800: '#312608',
          900: '#040301',
        },
        // 中性色 (Neutral Colors)
        'graphite': '#1A1A1A',
        'dark-gray': '#4A4A4A',
        'medium-gray': '#757575',
        'light-gray': '#E5E5E5',
        'background': '#F8F9FA',
        // 功能色 (Functional Colors) - 使用Tailwind默认色，但确保一致性
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'info': '#3B82F6',
      },
      // 字体系统扩展 (Typography Extension)
      fontFamily: {
        'sans': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        'mono': ['JetBrains Mono', 'SF Mono', 'Monaco', 'Cascadia Code', 'monospace'],
      },
      // 字体大小扩展 (Font Size Extension)
      fontSize: {
        'xxs': '0.625rem',    // 10px
        'xs': '0.75rem',      // 12px
        'sm': '0.875rem',     // 14px
        'base': '1rem',       // 16px
        'lg': '1.125rem',     // 18px
        'xl': '1.25rem',      // 20px
        '2xl': '1.5rem',      // 24px
        '3xl': '2rem',        // 32px
        '4xl': '2.5rem',      // 40px
        '5xl': '3rem',        // 48px
      },
      // 字重扩展 (Font Weight Extension)
      fontWeight: {
        'thin': 100,
        'extralight': 200,
        'light': 300,
        'normal': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700,
        'extrabold': 800,
        'black': 900,
      },
      // 间距扩展 (Spacing Extension)
      spacing: {
        'xxs': '0.25rem',    // 4px
        'xs': '0.5rem',      // 8px
        'sm': '0.75rem',     // 12px
        'md': '1rem',        // 16px
        'lg': '1.5rem',      // 24px
        'xl': '2rem',        // 32px
        '2xl': '3rem',       // 48px
        '3xl': '4rem',       // 64px
        '4xl': '6rem',       // 96px
      },
      // 圆角扩展 (Border Radius Extension)
      borderRadius: {
        'none': '0',
        'sm': '0.25rem',     // 4px
        'md': '0.5rem',      // 8px
        'lg': '0.75rem',     // 12px
        'xl': '1rem',        // 16px
        '2xl': '1.5rem',     // 24px
        '3xl': '2rem',       // 32px
        'full': '9999px',
      },
      // 阴影扩展 (Shadow Extension)
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        // 自定义阴影 (Custom Shadows)
        'card': '0 4px 12px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 12px 24px rgba(0, 0, 0, 0.12), 0 3px 8px rgba(0, 0, 0, 0.08)',
        'modal': '0 30px 60px rgba(0, 0, 0, 0.15), 0 10px 30px rgba(0, 0, 0, 0.1)',
      },
      // 动画扩展 (Animation Extension)
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      // 过渡扩展 (Transition Extension)
      transitionProperty: {
        'height': 'height',
        'spacing': 'margin, padding',
        'shadow': 'box-shadow',
        'transform': 'transform',
      },
      transitionDuration: {
        '250': '250ms',
        '350': '350ms',
        '450': '450ms',
      },
    },
  },
  plugins: [],
}