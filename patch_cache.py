import re

with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# Let's replace the whole api_status block
match = re.search(r'@app\.route\("/api/status", methods=\["GET"\]\)\ndef api_status\(\):.*?return jsonify\(\{.*?"broadcast": LATEST_BROADCAST\n    \}\)', app, re.DOTALL)

if match:
    new_func = """@app.route("/api/status", methods=["GET"])
def api_status():
    from flask import make_response
    resp = make_response(jsonify({
        "alarm_active": ALARM_ACTIVE,
        "camera_exit": CAMERA_EXIT,
        "total_people": get_total_people(),
        "rooms": ROOMS,
        "crowd": CROWD,
        "hazards": HAZARDS,
        "sos_alerts": SOS_ALERTS,
        "smoke_level": SMOKE_LEVEL,
        "safe_list": SAFE_LIST,
        "broadcast": LATEST_BROADCAST
    }))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp"""
    app = app[:match.start()] + new_func + app[match.end():]
else:
    # Maybe it was already partially replaced by the powershell command
    pass

# ALSO add caching headers to index.html and admin.html routes
html_routes = """@app.route("/")
def index():
    from flask import make_response
    resp = make_response(render_template("index.html", user_node="Library"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

@app.route("/admin")
def admin():
    from flask import make_response
    resp = make_response(render_template("admin.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp"""

app = re.sub(r'@app\.route\("/"\)\ndef index\(\):\s*return render_template\("index\.html", user_node="Library"\)\s*@app\.route\("/admin"\)\ndef admin\(\):\s*return render_template\("admin\.html"\)', html_routes, app)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)

# Also let's edit index.html to add a timestamp to fetch
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('fetch("/api/status")', 'fetch(`/api/status?t=${Date.now()}`)')
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
