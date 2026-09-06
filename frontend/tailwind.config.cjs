// Tailwind config (CommonJS — project is "type": "module", so .cjs is required).
// Paper / ink / shelf green. Crayon red and the dark room are retired.

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
        // Workbench v2 (contract R5): near-white neutrals + semantic signals.
        'wb-canvas': 'var(--wb-canvas)',
        'wb-surface': 'var(--wb-surface)',
        'wb-subtle': 'var(--wb-subtle)',
        'wb-line': 'var(--wb-line)',
        'wb-line-strong': 'var(--wb-line-strong)',
        'wb-ink': 'var(--wb-ink)',
        'wb-muted': 'var(--wb-muted)',
        'wb-faint': 'var(--wb-faint)',
        'wb-primary': 'var(--wb-primary)',
        'wb-primary-strong': 'var(--wb-primary-strong)',
        'wb-primary-soft': 'var(--wb-primary-soft)',
        'wb-success': 'var(--wb-success)',
        'wb-success-soft': 'var(--wb-success-soft)',
        'wb-warning': 'var(--wb-warning)',
        'wb-warning-soft': 'var(--wb-warning-soft)',
        'wb-danger': 'var(--wb-danger)',
        'wb-danger-soft': 'var(--wb-danger-soft)',
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
