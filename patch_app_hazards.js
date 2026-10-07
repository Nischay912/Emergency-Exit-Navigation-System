const fs = require('fs');

let py = fs.readFileSync('app.py', 'utf8');

const hazardLogic = `
# === IICCM HAZARD DETECTION ===
active_hazards = []

@app.route("/api/hazards", methods=["GET"])
def get_hazards():
    return jsonify({"hazards": active_hazards})

@app.route("/api/hazards/add", methods=["POST"])
def add_hazard():
    data = request.get_json(force=True) or {}
    node = data.get('node')
    if node and node not in active_hazards:
        active_hazards.append(node)
    return jsonify({"status": "success", "hazards": active_hazards})

@app.route("/api/hazards/remove", methods=["POST"])
def remove_hazard():
    data = request.get_json(force=True) or {}
    node = data.get('node')
    if node in active_hazards:
        active_hazards.remove(node)
    return jsonify({"status": "success", "hazards": active_hazards})

@app.route("/api/hazards/clear", methods=["POST"])
def clear_hazards():
    active_hazards.clear()
    return jsonify({"status": "success", "hazards": active_hazards})
`;

// Insert the hazard logic before the main block
const mainBlock = 'if __name__ == "__main__":';
py = py.replace(mainBlock, hazardLogic + '\n' + mainBlock);

// Also we need to make sure the app can serve the alternative maps if needed.
// By default it serves floor_graph.json
// Let's modify api_graph to read from a symlink or let the user swap it.
// The user already swaps the files manually, so we don't need to change api_graph.

fs.writeFileSync('app.py', py, 'utf8');
