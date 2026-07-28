// Tailwind config (CommonJS — project is "type": "module", so .cjs is required).
// Warm-parchment palette aligned with the v3 HTML prototype.

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
        bg: '#FAF8F3',
        paper: '#FAF8F3',
        panel: '#F3EFE6',
        ink: '#1A1A1A',
        muted: '#6B6357',
        accent: '#8B2C2C',
        border: '#E8E2D6',
      },
      fontFamily: {
        sans: ['system-ui', 'Segoe UI', 'Roboto', 'sans-serif'],
        serif: ['Charter', 'Georgia', 'serif'],
      },
    },
  },
  plugins,
};
