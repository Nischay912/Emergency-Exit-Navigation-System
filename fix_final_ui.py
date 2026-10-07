import os

file_path = 'templates/index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix the Minimap Aspect Ratio
old_minimap = """function renderNavMiniMap(path) {
  const nc = document.getElementById("navCanvas");
  const nwrap = nc.parentElement;
  nc.width = nwrap.clientWidth;
  nc.height = nwrap.clientHeight;
  const nctx = nc.getContext("2d");

  const nDW = 880, nDH = 580;
  const nsx = nc.width/nDW, nsy = nc.height/nDH;
  const NX = x => x*nsx, NY = y => y*nsy, NR = r => r*Math.min(nsx,nsy);"""

new_minimap = """function renderNavMiniMap(path) {
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
  const NR = r => Math.max(r * scale, 3);"""

html = html.replace(old_minimap, new_minimap)

# Also fix the drawing calls inside renderNavMiniMap to use scale instead of nsx/nsy
html = html.replace('nctx.fillRect(NX(c.x), NY(c.y), c.w*nsx, c.h*nsy);', 'nctx.fillRect(NX(c.x), NY(c.y), c.w * scale, c.h * scale);')
html = html.replace('nctx.rect(NX(r.x), NY(r.y), r.w*nsx, r.h*nsy);', 'nctx.rect(NX(r.x), NY(r.y), r.w * scale, r.h * scale);')


# 2. Fix the Language Dropdown styling and emojis
old_select = """        <select onchange="changeLanguage(this.value)" style="
          background:#0c1e3c;color:var(--text);border:1px solid var(--border);
          border-radius:10px;padding:0 8px;font-size:.8rem;cursor:pointer;
        ">
          <option value="en-IN">dYتdY  EN</option>
          <option value="hi-IN">dYrdY3 HI</option>
          <option value="kn-IN">dYrdY3 KN</option>
        </select>"""

new_select = """        <select class="nav-lang-select" onchange="changeLanguage(this.value)" style="
          background: var(--panel); color: var(--text); border: 2px solid var(--border);
          border-radius: 10px; padding: 0 12px; font-size: 0.9rem; font-weight: 600; cursor: pointer;
        ">
          <option value="en-IN">🇬🇧 EN</option>
          <option value="hi-IN">🇮🇳 HI</option>
          <option value="kn-IN">🇮🇳 KN</option>
        </select>"""

html = html.replace(old_select, new_select)


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
