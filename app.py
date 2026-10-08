"""
app.py — Emergency Exit System Backend (v2)
Numeric crowd values (0-100 people). Thresholds: <=20 Low, <=55 Medium, >55 High
"""
import json, threading
from pathlib import Path
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS

BASE  = Path(__file__).parent
DATA  = BASE / "data"
GRAPH_FILE = DATA / "floor_graph.json"
CROWD_FILE = DATA / "crowd_state.json"
ROOM_FILE  = DATA / "room_state.json"

app  = Flask(__name__)
CORS(app)
_lock = threading.Lock()

def load_json(path):
    with _lock:
        with open(path) as f:
            return json.load(f)

def save_json(path, data):
    with _lock:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

def count_to_level(n):
    n = int(n)
    if n <= 20:  return "Low"
    if n <= 55:  return "Medium"
    return "High"

# Global alarm state in-memory
ALARM_ACTIVE = False

# ── PAGES ──
from flask import make_response

@app.route("/")
def index():
    resp = make_response(render_template("index.html", user_node="Library"))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@app.route("/locate/<node_id>")
def locate(node_id):
    g = load_json(GRAPH_FILE)
    if node_id not in g["nodes"]:
        return redirect(url_for("index"))
    return render_template("index.html", user_node=node_id)

@app.route("/admin")
def admin():
    # Simple password protection for demo purposes
    # E.g. /admin?pwd=admin
    pwd = request.args.get("pwd")
    if pwd != "admin":
        return """
        <div style="font-family:sans-serif; text-align:center; margin-top:100px;">
            <h2>Admin Panel Restricted</h2>
            <form onsubmit="window.location.href='/admin?pwd=' + document.getElementById('pwd').value; return false;">
                <input type="password" id="pwd" placeholder="Enter Password" style="padding:8px; font-size:16px;">
                <button type="submit" style="padding:8px 16px; font-size:16px;">Login</button>
            </form>
            <p style="color:#666; font-size:12px;">(Hint: password is "admin")</p>
        </div>
        """
    return render_template("admin.html")

# ── API ──
@app.route("/api/alarm", methods=["GET"])
def get_alarm():
    global ALARM_ACTIVE
    return jsonify({"active": ALARM_ACTIVE})

@app.route("/api/alarm", methods=["POST"])
def post_alarm():
    global ALARM_ACTIVE
    data = request.get_json(force=True) or {}
    if "active" in data:
        ALARM_ACTIVE = bool(data["active"])
    else:
        ALARM_ACTIVE = not ALARM_ACTIVE # toggle
    return jsonify({"active": ALARM_ACTIVE})

@app.route("/api/graph")
def api_graph():
    return jsonify(load_json(GRAPH_FILE))

@app.route("/api/crowd", methods=["GET"])
def api_crowd_get():
    raw = load_json(CROWD_FILE)
    result = {k: {"count": v, "level": count_to_level(v)} for k, v in raw.items()}
    return jsonify(result)

@app.route("/api/crowd", methods=["POST"])
def api_crowd_post():
    data = request.get_json(force=True) or {}
    g    = load_json(GRAPH_FILE)
    exits = set(g["exit_nodes"])
    crowd = load_json(CROWD_FILE)
    updated = {}
    for name, val in data.items():
        if name in exits:
            crowd[name] = max(0, min(100, int(val)))
            updated[name] = crowd[name]
    if not updated:
        return jsonify({"error": "No valid exits"}), 400
    save_json(CROWD_FILE, crowd)
    return jsonify({"updated": updated})

@app.route("/api/rooms", methods=["GET"])
def api_rooms_get():
    return jsonify(load_json(ROOM_FILE))

@app.route("/api/rooms", methods=["POST"])
def api_rooms_post():
    data  = request.get_json(force=True) or {}
    rooms = load_json(ROOM_FILE)
    for name, val in data.items():
        if name in rooms:
            rooms[name] = max(0, int(val))
    save_json(ROOM_FILE, rooms)
    return jsonify({"updated": rooms})

@app.route("/api/status")
def api_status():
    g = load_json(GRAPH_FILE)
    crowd = load_json(CROWD_FILE)
    rooms = load_json(ROOM_FILE)
    total = sum(crowd.values()) + sum(rooms.values())
    return jsonify({
        "status": "online",
        "camera_exit": g.get("camera_exit", "Main_Entrance"),
        "crowd": {k: {"count": v, "level": count_to_level(v)} for k, v in crowd.items()},
        "rooms": rooms,
        "total_people": total,
        "alarm_active": ALARM_ACTIVE,
        "hazards": HAZARDS
    })


# --- HAZARDS (Fire / Debris) ---
HAZARDS = {}

@app.route("/api/hazards", methods=["GET", "POST"])
def api_hazards():
    global HAZARDS
    if request.method == "POST":
        data = request.json
        if data.get("clear_all"):
            HAZARDS.clear()
        elif "node" in data and "type" in data:
            if data["type"] == "clear":
                HAZARDS.pop(data["node"], None)
            else:
                HAZARDS[data["node"]] = data["type"]
        return jsonify({"success": True})
    return jsonify(HAZARDS)

if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "YOUR_PC_IP"

    print("=" * 60)
    print("  Emergency Exit System — Running")
    print("=" * 60)
    print(f"  Local PC    -> http://localhost:5000/")
    print(f"  Local Phone -> http://{local_ip}:5000/")
    print()
    print("  For PHONE SENSORS (PDR), use ngrok:")
    print("    ngrok http 5000")
    print("  Then open the ngrok https:// URL on your phone.")
    print("=" * 60)

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
