import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. We must replace the hardcoded ROOM_RECTS, CORRIDORS, NODE_POS with dynamic layout fetching
# Remove the old hardcoded vars
html = re.sub(r'const ROOM_RECTS=\{.*?\};\s*const CORRIDORS=\[.*?\];\s*const NODE_POS=\{.*?\};\s*', '', html, flags=re.DOTALL)

# Add layout variables
if 'let LAYOUT = null;' not in html:
    html = html.replace('let GRAPH=null,', 'let GRAPH=null,LAYOUT=null,ROOM_RECTS={},CORRIDORS=[],NODE_POS={},')

# Update init() to fetch /api/layout first
old_init = '''async function init() {
  await fetchGraph();'''
new_init = '''async function init() {
  await fetchLayout();
  await fetchGraph();'''
html = html.replace(old_init, new_init)

fetch_layout_fn = '''
async function fetchLayout() {
  try {
    const res = await fetch("/api/layout");
    LAYOUT = await res.json();
    ROOM_RECTS = LAYOUT.rooms || {};
    CORRIDORS = LAYOUT.corridors || [];
    NODE_POS = LAYOUT.nodes || {};
    // override canvas virtual dimensions if provided
    if (LAYOUT.width) DW = LAYOUT.width;
    if (LAYOUT.height) DH = LAYOUT.height;
  } catch (e) {
    console.error("Failed to fetch map layout JSON", e);
  }
}
'''
if 'async function fetchLayout' not in html:
    html = html.replace('async function fetchGraph()', fetch_layout_fn + '\nasync function fetchGraph()')

# 2. Modernize the aesthetics!
# Let's overhaul the HTML Structure to a Floating UI
html = re.sub(r'<body>.*?<div class="app">', '''<body>
<div id="emergencyFlash" class="alarm-overlay"></div>

<!-- Floating Top Search Bar -->
<div class="floating-header">
  <div class="header-content">
    <div class="menu-icon">☰</div>
    <select id="locSelect" onchange="changeLocation(this.value)">
      <option value="">Search Location...</option>
    </select>
    <div class="user-avatar">👤</div>
  </div>
</div>

<div class="app">
''', html, flags=re.DOTALL)

# Now, we use Python to completely replace the CSS style block
css_new = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
:root {
  --bg: #e8eaed; /* Map background */
  --surface: #ffffff;
  --border: #dadce0;
  --text: #202124;
  --muted: #5f6368;
  --primary: #1a73e8; /* Google Blue */
  --red: #ea4335;
  --green: #34a853;
  --amber: #fbbc04;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Roboto', sans-serif; background: var(--bg); color: var(--text); height: 100vh; overflow: hidden; display: flex; flex-direction: column; }

/* Floating Header (Google Maps Style) */
.floating-header {
  position: absolute; top: 16px; left: 16px; right: 16px; z-index: 100;
  pointer-events: none; display: flex; justify-content: flex-start;
}
.header-content {
  pointer-events: auto; background: var(--surface); height: 48px; border-radius: 24px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3); display: flex; align-items: center; padding: 0 16px; gap: 12px; width: 100%; max-width: 400px;
}
.menu-icon, .user-avatar { font-size: 18px; color: var(--muted); cursor: pointer; }
.header-content select {
  flex: 1; border: none; outline: none; font-size: 16px; background: transparent; font-family: inherit; color: var(--text); appearance: none;
}

/* App Container */
.app { display: flex; flex: 1; height: 100%; position: relative; }

/* Map Area (Full Screen!) */
.map-panel { flex: 1; position: absolute; inset: 0; z-index: 1; }
#mapCanvas { width: 100%; height: 100%; display: block; }

/* Floating Bottom/Side Navigation Panel */
.sidebar {
  position: absolute; bottom: 0; left: 0; right: 0; background: var(--surface); z-index: 50;
  border-top-left-radius: 16px; border-top-right-radius: 16px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  display: flex; flex-direction: column; max-height: 50vh; overflow-y: auto; padding: 16px;
}
@media(min-width: 768px) {
  .sidebar { top: 80px; bottom: 16px; left: 16px; right: auto; width: 360px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); max-height: calc(100vh - 100px); }
  .header-content { max-width: 360px; }
}

/* Cards and Controls */
.sec { margin-bottom: 16px; }
.sec-lbl { font-size: 13px; font-weight: 700; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }
.rec-card { background: #e8f0fe; border-radius: 12px; padding: 16px; border: 1px solid #c2e7ff; }
.rl { color: var(--primary); font-size: 12px; font-weight: 700; margin-bottom: 4px; }
.re { color: #001d35; font-size: 20px; font-weight: 700; margin-bottom: 4px; }
.rp { color: #174ea6; font-size: 12px; }

button {
  background: var(--primary); color: #fff; border: none; padding: 12px; border-radius: 20px; font-weight: 500; font-family: inherit; cursor: pointer; transition: 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
button:hover { background: #174ea6; box-shadow: 0 2px 6px rgba(0,0,0,0.3); }

/* Walk Controls */
.walk-card { display: flex; flex-direction: column; gap: 8px; }
.walk-btn { background: #ffffff; color: var(--primary); border: 1px solid var(--border); box-shadow: none; border-radius: 8px; }
.walk-btn:hover { background: #f1f3f4; }
.walk-btn.start { background: var(--green); color: white; border: none; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
.walk-btn.start:hover { background: #0d652d; }

/* Exit List Item */
.exit-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid var(--border); cursor: pointer; }
.exit-item:last-child { border: none; }
.exit-name { font-weight: 500; font-size: 15px; color: var(--text); }
.exit-dist { font-size: 12px; color: var(--muted); margin-top: 2px; }
.badge { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.badge.Low { background: #e6f4ea; color: #137333; }
.badge.Medium { background: #fef7e0; color: #b06000; }
.badge.High { background: #fce8e6; color: #c5221f; }

/* Navigation Overlay */
.nav-overlay {
  position: fixed; inset: 0; background: var(--surface); z-index: 200; display: flex; flex-direction: column;
  transform: translateY(100%); transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.nav-overlay.active { transform: translateY(0); }
.nav-top { background: var(--primary); color: white; padding: 16px; padding-top: max(16px, env(safe-area-inset-top)); display: flex; gap: 16px; align-items: center; }
.nav-arrow { font-size: 40px; line-height: 1; font-weight: bold; width: 50px; text-align: center; }
.nav-action { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.nav-target { font-size: 15px; opacity: 0.9; }
.nav-dist { font-size: 14px; font-weight: 500; opacity: 0.8; margin-top: 4px; }
.nav-steps-wrap { flex: 1; overflow-y: auto; padding: 16px; background: #f8f9fa; }
.nav-step-item { background: white; padding: 16px; border-radius: 12px; margin-bottom: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); display: flex; gap: 16px; align-items: center; }
.nav-step-arrow { font-size: 24px; color: var(--primary); }
.nav-step-info { flex: 1; }
.nav-step-action { font-size: 16px; font-weight: 500; color: var(--text); }
.nav-step-sub { font-size: 13px; color: var(--muted); margin-top: 4px; }

.nav-bottom { padding: 16px; background: white; border-top: 1px solid var(--border); display: flex; gap: 12px; padding-bottom: max(16px, env(safe-area-inset-bottom)); }
.nav-close-btn { flex: 1; background: #f1f3f4; color: var(--text); box-shadow: none; }
.nav-demo-btn { flex: 2; background: var(--primary); color: white; }
.nav-demo-btn.stop { background: var(--red); }

/* Alarm Overlay */
@keyframes flash { 0%, 100% { background: rgba(234,67,53,0); } 50% { background: rgba(234,67,53,0.3); } }
.alarm-overlay { position: fixed; inset: 0; pointer-events: none; z-index: 9999; display: none; animation: flash 0.6s infinite; }

/* Custom Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #dadce0; border-radius: 3px; }
</style>
'''
html = re.sub(r'<style>.*?</style>', css_new, html, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
