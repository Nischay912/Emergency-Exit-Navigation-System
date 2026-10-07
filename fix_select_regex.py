import re
import os

file_path = 'templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the entire <select> block robustly using regex
select_pattern = re.compile(r'<select onchange="changeLanguage\(this\.value\)".*?</select>', re.DOTALL)

new_select = """<select onchange="changeLanguage(this.value)" style="
          background: var(--panel); color: var(--text); border: 2px solid var(--border);
          border-radius: 10px; padding: 0 12px; font-size: 0.9rem; font-weight: 600; cursor: pointer;
        ">
          <option value="en-IN">🇬🇧 EN</option>
          <option value="hi-IN">🇮🇳 HI</option>
          <option value="kn-IN">🇮🇳 KN</option>
        </select>"""

html = select_pattern.sub(new_select, html)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
