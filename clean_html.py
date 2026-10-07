with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_idx = html.find('<!-- Floating Top Search Bar -->')
end_idx = html.find('<div class="app">')
if start_idx != -1 and end_idx != -1:
    html = html[:start_idx] + html[end_idx:]

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
