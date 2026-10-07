import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix 1: Mobile UI Squishing (give sidebar max 45vh on mobile)
old_media = "@media(max-width: 768px) { .sidebar { width: 100%; border-right: none; border-top: 1px solid var(--border); box-shadow: 0 -2px 10px rgba(0,0,0,0.1); } .app { flex-direction: column-reverse; } }"
new_media = "@media(max-width: 768px) { .sidebar { width: 100%; height: 45vh; border-right: none; border-top: 1px solid var(--border); box-shadow: 0 -2px 10px rgba(0,0,0,0.1); } .app { flex-direction: column-reverse; } }"
if old_media in html:
    html = html.replace(old_media, new_media)

# Fix 2: Full Dark Theme Support
old_root = """:root {
  --bg: #F8F9FA; --panel: #FFFFFF; --border: #DADCE0; --text: #202124; --muted: #5F6368;
  --red: #EA4335; --green: #34A853; --amber: #FBBC04; --blue: #1A73E8; --route-bg: #E8F0FE;
}"""
new_root = """:root {
  --bg: #F8F9FA; --panel: #FFFFFF; --border: #DADCE0; --text: #202124; --muted: #5F6368;
  --red: #EA4335; --green: #34A853; --amber: #FBBC04; --blue: #1A73E8; --route-bg: #E8F0FE; --map-bg: #E8EAED;
}
:root[data-theme="dark"] {
  --bg: #121212; --panel: #1E1E1E; --border: #333333; --text: #E8EAED; --muted: #9AA0A6;
  --route-bg: #174EA6; --blue: #8AB4F8; --map-bg: #1A1A1A;
}"""
if old_root in html:
    html = html.replace(old_root, new_root)

# Fix .map-col background to use --map-bg
html = html.replace('background: #E8EAED;', 'background: var(--map-bg);')

# Fix 3: Minimap Zoom issue
html = html.replace('const nDW = 880, nDH = 580;', 'const nDW = DW, nDH = DH;')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
