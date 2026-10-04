const fs = require('fs');
const path = require('path');

function verifySafeguards() {
  console.log('=== RUNNING FRONTEND STYLING SAFEGUARD CHECK ===');
  
  // 1. globals.css
  const globalsCssPath = path.join(__dirname, '../app/globals.css');
  if (!fs.existsSync(globalsCssPath)) {
    throw new Error('CRITICAL REGRESSION: app/globals.css is missing!');
  }
  const cssContent = fs.readFileSync(globalsCssPath, 'utf8');
  if (!cssContent.includes('@tailwind base') || !cssContent.includes('@tailwind components')) {
    throw new Error('CRITICAL REGRESSION: app/globals.css is missing Tailwind directives!');
  }
  console.log('  [x] app/globals.css directives verified.');

  // 2. layout.tsx
  const layoutPath = path.join(__dirname, '../app/layout.tsx');
  if (!fs.existsSync(layoutPath)) {
    throw new Error('CRITICAL REGRESSION: app/layout.tsx is missing!');
  }
  const layoutContent = fs.readFileSync(layoutPath, 'utf8');
  if (!layoutContent.includes("import './globals.css'") && !layoutContent.includes('import "./globals.css"')) {
    throw new Error('CRITICAL REGRESSION: app/layout.tsx does not import globals.css!');
  }
  console.log('  [x] app/layout.tsx globals.css import verified.');

  // 3. tailwind.config.js
  const tailwindConfigPath = path.join(__dirname, '../tailwind.config.js');
  if (!fs.existsSync(tailwindConfigPath)) {
    throw new Error('CRITICAL REGRESSION: tailwind.config.js is missing!');
  }
  const tailwindContent = fs.readFileSync(tailwindConfigPath, 'utf8');
  if (!tailwindContent.includes('./app/**/*.{js,ts,jsx,tsx,mdx}')) {
    throw new Error('CRITICAL REGRESSION: tailwind.config.js missing app content glob!');
  }
  console.log('  [x] tailwind.config.js content paths verified.');

  // 4. postcss.config.js
  const postcssPath = path.join(__dirname, '../postcss.config.js');
  if (!fs.existsSync(postcssPath)) {
    throw new Error('CRITICAL REGRESSION: postcss.config.js is missing!');
  }
  console.log('  [x] postcss.config.js verified.');

  console.log('SUCCESS: All frontend styling safeguards passed cleanly!\n');
}

verifySafeguards();
