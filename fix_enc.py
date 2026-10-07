with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('Hindi (~~~<~~)', 'Hindi (हिंदी)')
html = html.replace('Kannada ("3؅_-)', 'Kannada (ಕನ್ನಡ)')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
