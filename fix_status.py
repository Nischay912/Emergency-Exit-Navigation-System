import re

with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# Replace api_status
new_status = """def api_status():
    from flask import make_response
    g = load_json(GRAPH_FILE)
    crowd = load_json(CROWD_FILE)
    rooms = load_json(ROOM_FILE)
    total = sum(crowd.values()) + sum(rooms.values())
    resp = make_response(jsonify({
        "status": "online",
        "camera_exit": g.get("camera_exit", "Main_Entrance"),
        "crowd": {k: {"count": v, "level": count_to_level(v)} for k, v in crowd.items()},
        "rooms": rooms,
        "total_people": total,
        "alarm_active": ALARM_ACTIVE,
        "hazards": HAZARDS,
        "sos_alerts": SOS_ALERTS,
        "smoke_level": SMOKE_LEVEL,
        "safe_list": SAFE_LIST,
        "broadcast": LATEST_BROADCAST
    }))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

# --- Voice Broadcast ---"""

app = re.sub(r'def api_status\(\):.*?(?=# --- Voice Broadcast ---)', new_status, app, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)
