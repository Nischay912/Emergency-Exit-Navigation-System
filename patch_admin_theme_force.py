import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update CSS variables
css_pattern = r':root\s*\{[^\}]*\b--bg\b[^\}]*\}'

new_css = """:root {
    --bg: #F8F9FA; --card: #FFFFFF; --panel: #F1F3F4; --border: #DADCE0;
    --red: #D93025; --purple: #A142F4; --green: #1E8E3E; --amber: #F29900;
    --blue: #1A73E8; --text: #202124; --muted: #5F6368;
    --low: #1E8E3E; --med: #F29900; --high: #D93025;
  }
  :root[data-theme="dark"] {
    --bg:#08091a;--card:#0f1629;--panel:#111e38;--border:#1e2f55;
    --red:#e94560;--purple:#7c3aed;--green:#10b981;--amber:#f59e0b;
    --blue:#3b82f6;--text:#e2e8f0;--muted:#64748b;
    --low:#10b981;--med:#f59e0b;--high:#ef4444;
  }
  .theme-btn { background: var(--panel); border: 1px solid var(--border); border-radius: 50%; width: 32px; height: 32px; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; color: var(--text); box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
  .theme-btn:hover { background: var(--card); }"""

if '--bg: #F8F9FA' not in html:
    html = re.sub(css_pattern, new_css, html, count=1)

# 2. Add Theme Toggle Button
header_end_pattern = r'<div class="badge-live"><span class="dot"></span>CONNECTED</div>\s*</header>'
new_header_end = """<div style="display:flex; align-items:center; gap: 12px;">
      <div class="badge-live"><span class="dot"></span>CONNECTED</div>
      <button class="theme-btn" onclick="toggleTheme()" id="themeIcon">☀️</button>
    </div>
  </header>"""

if 'id="themeIcon"' not in html:
    html = re.sub(header_end_pattern, new_header_end, html, count=1)

# 3. Add JS toggle function
script_start_pattern = r'<script>\s*let ALARM_ACTIVE=false;'
new_script_start = """<script>
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    document.getElementById('themeIcon').innerHTML = next === 'dark' ? '🌙' : '☀️';
    localStorage.setItem('admin-theme', next);
  }
  // Load saved theme
  const savedTheme = localStorage.getItem('admin-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('themeIcon').innerHTML = savedTheme === 'dark' ? '🌙' : '☀️';
  });

  let ALARM_ACTIVE=false;"""

if 'function toggleTheme' not in html:
    html = re.sub(script_start_pattern, new_script_start, html, count=1)

# Ensure dark mode colors work on borders and text
style_end_pattern = r'</style>'
additional_css = """
  :root[data-theme="light"] .alert { background: #FCE8E6; }
  :root[data-theme="light"] input[type=range]::-webkit-slider-runnable-track { background: var(--border); }
</style>
"""
if 'FCE8E6' not in html:
    html = re.sub(style_end_pattern, additional_css, html, count=1)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
