import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the exact block
old_block = """:root{
  --bg:#08091a;--card:#0f1629;--panel:#111e38;--border:#1e2f55;
  --red:#e94560;--purple:#7c3aed;--green:#10b981;--amber:#f59e0b;
  --blue:#3b82f6;--text:#e2e8f0;--muted:#64748b;
  --low:#10b981;--med:#f59e0b;--high:#ef4444;
}"""

# Allow for varying whitespace/newlines
pattern = re.compile(r':root\s*\{\s*--bg:#08091a;--card:#0f1629;--panel:#111e38;--border:#1e2f55;\s*--red:#e94560;--purple:#7c3aed;--green:#10b981;--amber:#f59e0b;\s*--blue:#3b82f6;--text:#e2e8f0;--muted:#64748b;\s*--low:#10b981;--med:#f59e0b;--high:#ef4444;\s*\}', re.MULTILINE)

new_block = """:root {
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
.theme-btn { background: var(--panel); border: 1px solid var(--border); border-radius: 50%; width: 32px; height: 32px; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; color: var(--text); box-shadow: 0 1px 2px rgba(0,0,0,0.1); margin-left: 10px; }
.theme-btn:hover { background: var(--card); }"""

html = pattern.sub(new_block, html)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
