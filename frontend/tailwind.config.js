/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
        extend: {
                borderRadius: {
                        lg: 'var(--radius)',
                        md: 'calc(var(--radius) - 2px)',
                        sm: 'calc(var(--radius) - 4px)'
                },
                colors: {
                        // Modern Business Professional Theme
                        background: 'hsl(var(--background))',
                        foreground: 'hsl(var(--foreground))',
                        card: {
                                DEFAULT: 'hsl(var(--card))',
                                foreground: 'hsl(var(--card-foreground))'
                        },
                        popover: {
                                DEFAULT: 'hsl(var(--popover))',
                                foreground: 'hsl(var(--popover-foreground))'
                        },
                        primary: {
                                DEFAULT: 'hsl(var(--primary))',
                                foreground: 'hsl(var(--primary-foreground))',
                                50: '#f8fafc',
                                100: '#f1f5f9',
                                200: '#e2e8f0',
                                300: '#cbd5e1',
                                400: '#94a3b8',
                                500: '#64748b',
                                600: '#475569',
                                700: '#334155',
                                800: '#1e293b',
                                900: '#0f172a'
                        },
                        secondary: {
                                DEFAULT: 'hsl(var(--secondary))',
                                foreground: 'hsl(var(--secondary-foreground))'
                        },
                        muted: {
                                DEFAULT: 'hsl(var(--muted))',
                                foreground: 'hsl(var(--muted-foreground))'
                        },
                        accent: {
                                DEFAULT: 'hsl(var(--accent))',
                                foreground: 'hsl(var(--accent-foreground))'
                        },
                        destructive: {
                                DEFAULT: 'hsl(var(--destructive))',
                                foreground: 'hsl(var(--destructive-foreground))'
                        },
                        border: 'hsl(var(--border))',
                        input: 'hsl(var(--input))',
                        ring: 'hsl(var(--ring))',
                        chart: {
                                '1': 'hsl(var(--chart-1))',
                                '2': 'hsl(var(--chart-2))',
                                '3': 'hsl(var(--chart-3))',
                                '4': 'hsl(var(--chart-4))',
                                '5': 'hsl(var(--chart-5))'
                        },
                        // Business Professional Colors
                        blue: {
                                50: '#eff6ff',
                                100: '#dbeafe',
                                200: '#bfdbfe',
                                300: '#93c5fd',
                                400: '#60a5fa',
                                500: '#3b82f6',
                                600: '#2563eb',
                                700: '#1d4ed8',
                                800: '#1e40af',
                                900: '#1e3a8a',
                                950: '#172554'
                        },
                        slate: {
                                50: '#f8fafc',
                                100: '#f1f5f9',
                                200: '#e2e8f0',
                                300: '#cbd5e1',
                                400: '#94a3b8',
                                500: '#64748b',
                                600: '#475569',
                                700: '#334155',
                                800: '#1e293b',
                                900: '#0f172a',
                                950: '#020617'
                        },
                        gray: {
                                50: '#f9fafb',
                                100: '#f3f4f6',
                                200: '#e5e7eb',
                                300: '#d1d5db',
                                400: '#9ca3af',
                                500: '#6b7280',
                                600: '#4b5563',
                                700: '#374151',
                                800: '#1f2937',
                                900: '#111827',
                                950: '#030712'
                        }
                },
                keyframes: {
                        'accordion-down': {
                                from: {
                                        height: '0'
                                },
                                to: {
                                        height: 'var(--radix-accordion-content-height)'
                                }
                        },
                        'accordion-up': {
                                from: {
                                        height: 'var(--radix-accordion-content-height)'
                                },
                                to: {
                                        height: '0'
                                }
                        },
                        'slide-in-up': {
                                '0%': { 
                                        opacity: '0',
                                        transform: 'translateY(30px)'
                                },
                                '100%': { 
                                        opacity: '1',
                                        transform: 'translateY(0px)'
                                }
                        },
                        'fade-in': {
                                '0%': { 
                                        opacity: '0',
                                        transform: 'scale(0.95)'
                                },
                                '100%': { 
                                        opacity: '1',
                                        transform: 'scale(1)'
                                }
                        },
                        'pulse-glow': {
                                '0%, 100%': { 
                                        boxShadow: '0 0 20px rgba(59, 130, 246, 0.3)'
                                },
                                '50%': { 
                                        boxShadow: '0 0 30px rgba(59, 130, 246, 0.5)'
                                }
                        },
                        'shimmer': {
                                '0%': { backgroundPosition: '200% 0' },
                                '100%': { backgroundPosition: '-200% 0' }
                        }
                },
                animation: {
                        'accordion-down': 'accordion-down 0.2s ease-out',
                        'accordion-up': 'accordion-up 0.2s ease-out',
                        'slide-in-up': 'slide-in-up 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
                        'fade-in': 'fade-in 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
                        'pulse-glow': 'pulse-glow 3s ease-in-out infinite',
                        'shimmer': 'shimmer 2s infinite'
                },
                backgroundImage: {
                        'gradient-business': 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                        'gradient-success': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        'gradient-warning': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                        'gradient-error': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                        'gradient-hero': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                },
                boxShadow: {
                        'professional': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
                        'professional-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
                        'professional-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
                        'business': '0 10px 25px -5px rgba(37, 99, 235, 0.2)',
                        'business-lg': '0 20px 40px -10px rgba(37, 99, 235, 0.3)'
                },
                backdropBlur: {
                        '25': '25px'
                },
                fontFamily: {
                        'sans': ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'Noto Sans', 'sans-serif']
                }
        }
  },
  plugins: [require("tailwindcss-animate")],
};