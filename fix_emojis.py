import os

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix Theme Toggle text
html = html.replace('id="themeIcon">dYOT</span>', 'id="themeIcon">&#127769;</span>')
html = html.replace("'~?,?' : 'dYOT'", "'&#9728;' : '&#127769;'")
html = html.replace("'s,?'", "'&#9888;'") # Warning icon
html = html.replace("'dYs  ", "'&#128099; ") # Footprints
html = html.replace("dYOT", "&#127769;")
html = html.replace("~?,?", "&#9728;")
html = html.replace("dYs\"", "&#128680;") # Siren
html = html.replace("o. ", "&#9989; ") # Checkmark
html = html.replace("?1 ", "&#9209; ") # Stop

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
