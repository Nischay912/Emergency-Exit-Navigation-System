const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

// Fix nav-top layout
const oldNavTop = `.nav-top { background: var(--green); color: white; padding: 24px; padding-top: max(24px, env(safe-area-inset-top)); display: flex; gap: 16px; align-items: center; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }`;
const newNavTop = `.nav-top { background: var(--green); color: white; padding: 20px; padding-top: max(20px, env(safe-area-inset-top)); display: flex; flex-direction: column; gap: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 10; }
.nav-arrow-row { display: flex; align-items: center; gap: 16px; width: 100%; }
.nav-street { font-size: 13px; font-weight: 500; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }
.nav-compass-badge { font-size: 12px; background: rgba(0,0,0,0.2); padding: 4px 10px; border-radius: 12px; align-self: flex-start; display: flex; align-items: center; gap: 6px; }
.nav-next { background: rgba(255,255,255,0.15); padding: 10px 16px; border-radius: 8px; width: 100%; display: flex; align-items: center; gap: 10px; font-size: 14px; margin-top: 4px; }
.nav-next-icon { font-weight: bold; font-size: 18px; opacity: 0.9; }`;

html = html.replace(oldNavTop, newNavTop);

fs.writeFileSync('templates/index.html', html, 'utf8');
