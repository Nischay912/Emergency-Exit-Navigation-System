import os

file_path = 'templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the infinite growing canvas bug by constraining its height in CSS
if '#navCanvas { width: 100%; height: 150px; flex: none; }' not in html:
    html = html.replace('</style>', '  #navCanvas { width: 100%; height: 150px; flex: none; }\n  </style>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
