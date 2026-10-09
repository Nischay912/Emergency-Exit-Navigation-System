import re

# 1. Add PWA Routes to app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

pwa_routes = '''
@app.route("/manifest.json")
def serve_manifest():
    from flask import send_file
    return send_file("manifest.json")

@app.route("/sw.js")
def serve_sw():
    from flask import send_file
    return send_file("sw.js")

'''
if 'serve_manifest' not in app:
    app = app.replace('if __name__ == "__main__":', pwa_routes + 'if __name__ == "__main__":')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)


# 2. Add PWA link to index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

pwa_head = '''  <!-- PWA Support -->
  <link rel="manifest" href="/manifest.json">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Evac AI">
'''

if 'rel="manifest"' not in html:
    html = html.replace('</head>', pwa_head + '</head>')

pwa_js = '''
  // Register Service Worker for PWA
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW registration failed:', err));
  }
'''

if 'navigator.serviceWorker.register' not in html:
    html = html.replace('</script>', pwa_js + '\n  </script>', 1)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("PWA features injected.")
