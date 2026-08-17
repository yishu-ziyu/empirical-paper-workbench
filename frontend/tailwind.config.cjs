// Tailwind config (CommonJS — project is "type": "module", so .cjs is required).
// Living-notes cream/paper/green. Crayon red is retired.

// Tremor plugin: newer @tremor/react (v3.18+) no longer ships a tailwind plugin
// export; load defensively so the build stays green across versions.
let tremorPlugin = null;
try {
  const tremor = require('@tremor/react');
  tremorPlugin =
    tremor.tremorTwPlugin ||
    tremor.tailwindPlugin ||
    tremor.tremorPlugin ||
    null;
} catch {
  tremorPlugin = null;
}

const plugins = [];
if (tremorPlugin) plugins.push(tremorPlugin);

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#f4efe4',
        paper: '#f4efe4',
        cream: '#f1f0ed',
        panel: '#fffdf7',
        ink: '#181515',
        muted: '#515151',
        accent: '#2f6b4f',
        border: '#d8d2c6',
        warning: '#8a6a12',
        danger: '#9b3d30',
      },
      fontFamily: {
        serif: ['"Instrument Serif"', '"Noto Serif SC"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'Menlo', 'monospace'],
        sans: ['"Instrument Sans"', 'system-ui', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins,
};
