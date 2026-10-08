import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the button names
html = html.replace('>🔥 Fire at Mid-Hall 1</button>', '>🔥 Fire near Staff Lounge (Left)</button>')
html = html.replace('>🚧 Collapse at East Corridor</button>', '>🚧 Blockade at East Hallway</button>')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
