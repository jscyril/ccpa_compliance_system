/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#07090f",
                accent: {
                    indigo: "#6366F1",
                    cyan: "#06B6D4",
                },
                success: "#34D399",
                error: "#F87171",
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            backdropBlur: {
                'glass': '16px',
            },
        },
    },
    plugins: [],
}
