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
                        // Modern Purple Theme Colors
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
                                foreground: 'hsl(var(--primary-foreground))'
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
                        // Extended Purple Palette
                        purple: {
                                50: '#faf5ff',
                                100: '#f3e8ff',
                                200: '#e9d5ff',
                                300: '#d8b4fe',
                                400: '#c084fc',
                                500: '#a855f7',
                                600: '#9333ea',
                                700: '#7c3aed',
                                800: '#6b46c1',
                                900: '#581c87',
                                950: '#3b0764'
                        },
                        indigo: {
                                50: '#eef2ff',
                                100: '#e0e7ff',
                                200: '#c7d2fe',
                                300: '#a5b4fc',
                                400: '#818cf8',
                                500: '#6366f1',
                                600: '#4f46e5',
                                700: '#4338ca',
                                800: '#3730a3',
                                900: '#312e81',
                                950: '#1e1b4b'
                        },
                        violet: {
                                50: '#f5f3ff',
                                100: '#ede9fe',
                                200: '#ddd6fe',
                                300: '#c4b5fd',
                                400: '#a78bfa',
                                500: '#8b5cf6',
                                600: '#7c3aed',
                                700: '#6d28d9',
                                800: '#5b21b6',
                                900: '#4c1d95',
                                950: '#2e1065'
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
                        'pulse-purple': {
                                '0%, 100%': { 
                                        opacity: '1',
                                        transform: 'scale(1)',
                                        boxShadow: '0 0 0 0 rgba(139, 92, 246, 0.4)'
                                },
                                '50%': { 
                                        opacity: '0.9',
                                        transform: 'scale(1.02)',
                                        boxShadow: '0 0 0 10px rgba(139, 92, 246, 0)'
                                }
                        },
                        'gradient-shift': {
                                '0%': { backgroundPosition: '0% 50%' },
                                '50%': { backgroundPosition: '100% 50%' },
                                '100%': { backgroundPosition: '0% 50%' }
                        },
                        'float': {
                                '0%, 100%': { transform: 'translateY(0px)' },
                                '50%': { transform: 'translateY(-10px)' }
                        },
                        'glow': {
                                '0%, 100%': { 
                                        boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)'
                                },
                                '50%': { 
                                        boxShadow: '0 0 30px rgba(139, 92, 246, 0.5)'
                                }
                        }
                },
                animation: {
                        'accordion-down': 'accordion-down 0.2s ease-out',
                        'accordion-up': 'accordion-up 0.2s ease-out',
                        'pulse-purple': 'pulse-purple 2s ease-in-out infinite',
                        'gradient-shift': 'gradient-shift 6s ease infinite',
                        'float': 'float 3s ease-in-out infinite',
                        'glow': 'glow 2s ease-in-out infinite'
                },
                backgroundImage: {
                        'purple-gradient': 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
                        'purple-gradient-light': 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)',
                        'indigo-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        'hero-pattern': `radial-gradient(circle at 25px 25px, rgba(255, 255, 255, 0.1) 2px, transparent 0),
                                        radial-gradient(circle at 75px 75px, rgba(255, 255, 255, 0.1) 2px, transparent 0)`
                },
                boxShadow: {
                        'purple': '0 10px 25px -5px rgba(139, 92, 246, 0.2)',
                        'purple-lg': '0 20px 40px -10px rgba(139, 92, 246, 0.3)',
                        'purple-xl': '0 25px 50px -12px rgba(139, 92, 246, 0.4)',
                        'glow': '0 0 30px rgba(139, 92, 246, 0.3)',
                        'glow-lg': '0 0 40px rgba(139, 92, 246, 0.4)'
                },
                backdropBlur: {
                        '25': '25px'
                }
        }
  },
  plugins: [require("tailwindcss-animate")],
};