import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Declare GLOBAL_HAZARDS properly
if "let GLOBAL_HAZARDS = {};" not in html:
    html = html.replace('let GRAPH=null', 'let GLOBAL_HAZARDS = {};\nlet GRAPH=null')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
