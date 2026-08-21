# 🚨 Emergency Exit System
### AI-Powered, Crowd-Aware Indoor Evacuation Navigation

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B35?style=flat)](https://ultralytics.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

---

## 📖 Overview

The **Emergency Exit System** is a real-time, indoor emergency evacuation platform built as a final-year major project. It combines **YOLOv8 AI crowd detection**, **Dijkstra's algorithm for dynamic pathfinding**, and **Pedestrian Dead Reckoning (PDR)** to guide occupants to the safest exit — all without GPS or any special hardware.

A user scans a QR code in their room, opens the web app on their phone, and receives a **live-updated navigation path** to the least-crowded exit. As crowd conditions change (detected by webcam), the route automatically recalculates.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **AI Crowd Detection** | YOLOv8 nano model detects and counts people at exit points via webcam in real-time |
| 🗺️ **Dynamic Pathfinding** | Dijkstra's algorithm routes users away from crowded exits using live crowd weights |
| 📍 **PDR Navigation** | Pedestrian Dead Reckoning uses phone's accelerometer + compass — no GPS or BLE beacons needed |
| 📱 **Mobile-First Web App** | Runs entirely in the browser; no app installation required |
| 🏛️ **Admin Dashboard** | Real-time crowd management panel to manually update occupancy counts |
| 📷 **QR Code Entry** | Scanning a room's QR code auto-sets the user's location |
| ♻️ **Auto-Rereouting** | Path recalculates every ~4 seconds as crowd data updates |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      PHONE (User Browser)                    │
│                                                              │
│  1. Scans QR code → Opens https://[ngrok-url]/locate/Room   │
│  2. Gets floor map + crowd data from Flask API               │
│  3. Dijkstra runs CLIENT-SIDE in JavaScript                  │
│  4. Accelerometer + Compass → PDR moves the "YOU" dot        │
│  5. Polls /api/crowd every 4s → path recalculates            │
└──────────────────────────────────────────────────────────────┘
         ▲  HTTP (REST API)  │
         │                   ▼
┌──────────────────────────────────────────────────────────────┐
│                   PC / SERVER (Flask + app.py)               │
│                                                              │
│  • Serves index.html and admin.html                          │
│  • REST endpoints: /api/graph, /api/crowd, /api/rooms        │
│  • Reads/writes crowd_state.json, room_state.json            │
└────────────────────┬─────────────────────────────────────────┘
                     │  POST /api/crowd (every 5s)
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                yolo_crowd.py (runs separately)               │
│                                                              │
│  • Webcam captures exit-area footage                         │
│  • YOLOv8 counts people per frame                            │
│  • Pushes crowd count to Flask API automatically             │
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Project_Exit/
│
├── app.py                        # Flask backend — API endpoints + page serving
├── yolo_crowd.py                 # YOLOv8 webcam-based crowd detection script
├── generate_qr.py                # Generates per-room QR codes pointing to /locate/<room>
├── generate_cert.py              # Self-signed SSL cert generator (for local HTTPS testing)
├── start_tunnel.py               # Automates ngrok tunnel setup for mobile HTTPS access
├── requirements.txt              # Python dependencies
├── .gitignore                    # Excludes SSL keys, .env, cache, QR images, etc.
│
├── data/
│   ├── floor_graph.json          # Graph definition: nodes, edges, exit list
│   ├── crowd_state.json          # Live crowd count per exit (runtime state)
│   └── room_state.json           # Live room occupancy counts (runtime state)
│
├── templates/
│   ├── index.html                # Main user-facing map + navigation page (~73 KB)
│   └── admin.html                # Admin control panel for crowd management
│
├── emergency_exit_system/        # Legacy/alternate Python implementation modules
│   ├── main.py                   # Entry point for standalone Python version
│   ├── dashboard.py              # Tkinter/web dashboard module
│   ├── dijkstra.py               # Pure Python Dijkstra + path reconstruction
│   ├── floor_map.py              # Floor plan node/edge definitions
│   ├── ui_map.py                 # Canvas-based floor map renderer
│   └── crowd_simulator.py        # Crowd simulation for offline demo/testing
│
├── web_demo/                     # Static web demo placeholder
└── qr_codes/                     # Generated QR images (git-ignored)
```

---

## 🔧 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.10+, Flask 3.0 | REST API server, page serving |
| **AI / CV** | YOLOv8 (Ultralytics), OpenCV | Real-time person detection at exits |
| **Frontend** | HTML5, Vanilla JS, CSS | Mobile map + navigation UI |
| **Rendering** | HTML5 Canvas API | Floor map drawing at 60 fps |
| **Pathfinding** | Dijkstra's Algorithm (JS) | Crowd-weighted shortest path |
| **Indoor Nav** | PDR (Dead Reckoning) | Step detection + compass heading |
| **Sensors** | DeviceMotionEvent, DeviceOrientationEvent | Browser APIs for accelerometer & compass |
| **Data** | JSON files | Lightweight runtime state storage |
| **Tunnel** | ngrok | HTTPS tunnel for mobile sensor access |
| **Location** | QR Codes (qrcode library) | Zero-friction room location initialization |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A webcam (for live YOLO detection)
- A smartphone (for PDR navigation demo)
- [ngrok](https://ngrok.com/) installed and authenticated (for mobile sensor access)

### 1. Clone the Repository

```bash
git clone https://github.com/Nischay912/Project-clg-major-project.git
cd Project-clg-major-project
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The `yolov8n.pt` model file (~6.5 MB) will auto-download on first run if not present.

### 3. Configure Environment (Optional)

Create a `.env` file for any custom configuration:

```env
FLASK_PORT=5000
CAMERA_EXIT=Main_Entrance
```

### 4. Run the Flask Server

```bash
python app.py
```

The server starts at `http://localhost:5000`. Open this on your PC browser to see the map.

### 5. Run YOLO Crowd Detection (Separate Terminal)

```bash
python yolo_crowd.py
```

This opens your webcam, detects people, and automatically pushes crowd counts to the Flask server every 5 seconds.

### 6. Enable Mobile Access (HTTPS via ngrok)

Phone browsers require HTTPS to access motion sensors.

```bash
ngrok http 5000
```

Open the generated `https://xxxx.ngrok-free.app` URL on your phone. For automatic tunnel setup:

```bash
python start_tunnel.py
```

### 7. Generate QR Codes for Rooms

```bash
python generate_qr.py
```

QR images are saved to `qr_codes/` (git-ignored). Print and place them in rooms for the demo.

---

## 📱 How It Works — User Flow

```
1. User enters a room during an emergency
         ↓
2. Scans the QR code on the wall
         ↓
3. Browser opens → auto-set to their location on the map
         ↓
4. Dijkstra calculates safest exit (avoids crowded ones)
         ↓
5. Animated yellow path shows the route
         ↓
6. User walks → PDR (accelerometer + compass) moves the dot
         ↓
7. Every 4 seconds: crowd data refreshes → path may update
         ↓
8. User reaches the exit ✅
```

---

## 🧮 Algorithm Details

### Dijkstra's Pathfinding with Dynamic Weights

The floor plan is modeled as a **weighted undirected graph**:

- **Nodes** — rooms, corridors, exits
- **Edges** — passageways with distance-based weights

Crowd density dynamically multiplies edge weights at exits:

| Crowd Level | People Count | Weight Multiplier |
|---|---|---|
| 🟢 Low | 0 – 20 | ×1.0 |
| 🟡 Medium | 21 – 55 | ×2.5 |
| 🔴 High | 56 – 100 | ×6.0 |

This makes overcrowded exits "expensive" — Dijkstra naturally avoids them and routes users to safer alternatives.

### PDR — Pedestrian Dead Reckoning

No GPS works indoors. PDR uses sensors already in every smartphone:

1. **Step Detection** — `DeviceMotionEvent` monitors the accelerometer. A spike > 1.8 m/s² above gravity (9.8 m/s²) is counted as one step (~22 map units).
2. **Heading** — `DeviceOrientationEvent` / `webkitCompassHeading` provides compass bearing.
3. **Position Update**:
   ```
   dx = stepLength × sin(mapHeading)
   dy = −stepLength × cos(mapHeading)
   ```
4. **Path Snapping** — Position snaps to the nearest corridor edge to prevent drift through walls.

---

## 🖥️ Admin Dashboard

Visit `/admin` to access the control panel:

- **Update crowd counts** at each exit (0–100 people)
- **Update room occupancy** numbers
- **Trigger emergency mode** simulation
- View **real-time system status** including total building occupancy

All changes reflect on user devices within ~4 seconds.

---

## 🔬 Research Contribution

This project addresses recognized gaps in existing indoor evacuation literature:

| Limitation in Existing Systems | Our Solution |
|---|---|
| Static exit signs — no crowd awareness | Real-time YOLO crowd detection + dynamic rerouting |
| BLE beacon positioning (₹2000+/beacon) | Zero-cost PDR using built-in phone sensors |
| Manual crowd estimation | Automated AI-based visual counting |
| Centralized routing (server bottleneck) | Client-side Dijkstra — works even under server load |

---

## 📋 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Main user navigation page |
| `/admin` | GET | Admin control panel |
| `/locate/<room_id>` | GET | Set user location via QR code |
| `/api/graph` | GET | Full floor graph (nodes, edges, exits) |
| `/api/crowd` | GET | Current crowd counts at all exits |
| `/api/crowd` | POST | Update crowd count(s) — `{"Exit_Name": 45}` |
| `/api/rooms` | GET | Current room occupancy counts |
| `/api/rooms` | POST | Update room count(s) |
| `/api/status` | GET | System overview — total occupancy + all counts |

---

## 🔒 Security Notes

- SSL certificate files (`*.pem`, `*.key`) are **git-ignored** — never commit them.
- The `.env` file is **git-ignored** — add sensitive config there.
- QR code images are **git-ignored** (generated locally).
- The `yolov8n.pt` model is included in the repo (~6.5 MB) for convenience.

---

## 👥 Team

**Major Project — B.Tech CSE (2026)**

> Built as a final-year college major project demonstrating real-world integration of AI, mobile web technologies, and classical algorithms for emergency safety applications.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

*For technical deep-dive, see [tech.md](tech.md) | For demo instructions, see [DEMO_GUIDE.md](DEMO_GUIDE.md)*
