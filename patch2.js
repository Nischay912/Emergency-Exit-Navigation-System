const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

// 1. Remove currentUser overwrite in walkDemoStep
const badCodeStart = html.indexOf('// Update main map user position (currentUser = from node of this step)');
if (badCodeStart !== -1) {
    const badCodeEnd = html.indexOf('// Smooth interpolation: move dot from fromPos to toPos', badCodeStart);
    if (badCodeEnd !== -1) {
        html = html.substring(0, badCodeStart) + html.substring(badCodeEnd);
    }
}

// 2. Adjust animation duration
html = html.replace('const duration = Math.max(6000, step.dist * 450);', 'const duration = Math.max(4500, step.dist * 300);');
html = html.replace('setTimeout(() => walkDemoStep(stepIdx+1), 600);', 'setTimeout(() => walkDemoStep(stepIdx+1), 1000);');

// 3. Improve Mobile UI (Bottom Sheet Handle + Rounded Corners)
const mobileCssStart = html.indexOf('@media(max-width: 768px) {');
if (mobileCssStart !== -1) {
    const oldMobile = `.sidebar { width: 100%; height: 45vh; border-right: none; border-top: 1px solid var(--border); box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }`;
    const newMobile = `.sidebar { 
    width: 100%; height: 50vh; border-right: none; border-top: 1px solid var(--border); 
    box-shadow: 0 -4px 16px rgba(0,0,0,0.15); 
    border-top-left-radius: 24px; border-top-right-radius: 24px; 
    padding-top: 24px; position: relative;
  }
  .sidebar::before {
    content: ''; position: absolute; top: 8px; left: 50%; transform: translateX(-50%);
    width: 40px; height: 5px; background: var(--muted); border-radius: 3px; opacity: 0.5;
  }`;
    html = html.replace(oldMobile, newMobile);
}

fs.writeFileSync('templates/index.html', html, 'utf8');
