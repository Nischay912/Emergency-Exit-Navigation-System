import os

file_path = 'templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the hardcoded .re and .rp colors in dark mode
css_fix = """
:root[data-theme="dark"] .re { color: #FFFFFF; }
:root[data-theme="dark"] .rp { color: #E8EAED; }
:root[data-theme="dark"] .rl { color: #8AB4F8; }
:root[data-theme="dark"] .nav-trigger { background: #174EA6; color: #FFFFFF; font-weight: 600; box-shadow: 0 2px 6px rgba(0,0,0,0.4); }
:root[data-theme="dark"] .nav-trigger:hover { background: #1967D2; }
"""

if '.re { color: #FFFFFF; }' not in html:
    html = html.replace('</style>', css_fix + '\n</style>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
