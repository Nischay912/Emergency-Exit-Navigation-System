const fs = require('fs');
let html = fs.readFileSync('templates/index.html', 'utf8');

const oldMiniMap = `function renderNavMiniMap(path) {
  const nc = document.getElementById("navCanvas");
  const nwrap = nc.parentElement;
  nc.width = nwrap.clientWidth;
  nc.height = nwrap.clientHeight;
  const nctx = nc.getContext("2d");

  const nDW = 880, nDH = 580;
  const nsx = nc.width/nDW, nsy = nc.height/nDH;
  const NX = x => x*nsx, NY = y => y*nsy, NR = r => r*Math.min(nsx,nsy);`;

const newMiniMap = `function renderNavMiniMap(path) {
  const nc = document.getElementById("navCanvas");
  const nwrap = nc.parentElement;
  nc.width = nwrap.clientWidth;
  nc.height = nwrap.clientHeight;
  const nctx = nc.getContext("2d");

  const DW = 880, DH = 580;
  // Use Math.min to maintain perfect aspect ratio so the map is never distorted
  const scale = Math.min(nc.width / DW, nc.height / DH) * 0.9;
  const cx = (nc.width - DW * scale) / 2;
  const cy = (nc.height - DH * scale) / 2;
  
  const NX = x => cx + (x * scale);
  const NY = y => cy + (y * scale);
  const NR = r => Math.max(r * scale, 3);`;

// We also need to fix the drawing calls inside renderNavMiniMap
let blockStart = html.indexOf('function renderNavMiniMap(path)');
let blockEnd = html.indexOf('function updateNavUI()');
if (blockStart !== -1 && blockEnd !== -1) {
    let block = html.substring(blockStart, blockEnd);
    
    // Replace the top variables
    block = block.replace(/const nDW[\s\S]*?Math\.min\(nsx,nsy\);/, `const DW = 880, DH = 580;
  const scale = Math.min(nc.width / DW, nc.height / DH) * 0.9;
  const cx = (nc.width - DW * scale) / 2;
  const cy = (nc.height - DH * scale) / 2;
  
  const NX = x => cx + (x * scale);
  const NY = y => cy + (y * scale);
  const NR = r => Math.max(r * scale, 3);`);
    
    // Replace corridor rect
    block = block.replace(/nctx\.fillRect\(NX\(c\.x\), NY\(c\.y\), c\.w\*nsx, c\.h\*nsy\);/g, 'nctx.fillRect(NX(c.x), NY(c.y), c.w * scale, c.h * scale);');
    
    // Replace room rect
    block = block.replace(/nctx\.rect\(NX\(r\.x\), NY\(r\.y\), r\.w\*nsx, r\.h\*nsy\);/g, 'nctx.rect(NX(r.x), NY(r.y), r.w * scale, r.h * scale);');
    
    html = html.substring(0, blockStart) + block + html.substring(blockEnd);
}

fs.writeFileSync('templates/index.html', html, 'utf8');
