# Emergency Exit System — Technical Reference
> Everything tech used in this project. Read this before talking to your teacher.
> **This file gets updated whenever new tech is added.**

---

## BIG PICTURE — How the Whole System Works

```
PHONE (user)                    PC (server)
   |                                |
   | 1. Opens browser URL           |
   |------------------------------> |
   |                          Flask runs app.py
   |                          Reads floor_graph.json
   | 2. Gets map + crowd data       |
   |<------------------------------ |
   |                                |
   | 3. Dijkstra runs in browser    |
   |    Finds safest path           |
   |                                |
   | 4. Phone sensors (steps+compass)|
   |    PDR moves red dot           |
   |                                |
   | 5. Every 4 sec: polls /api/crowd|
   |------------------------------> |
   |<------------------------------ |
   |    Gets updated crowd numbers  |
   |    Path recalculates           |
```

---

## TECH STACK — What Technologies Are Used

### 1. Python + Flask (Backend)
**File:** `app.py`
**What it is:** Python is the programming language. Flask is a web framework — it runs a small web server on your PC.

**What it does in this project:**
- Listens on port 5000 for browser requests
- Serves the HTML pages (`index.html`, `admin.html`)
- Provides API endpoints (URLs that return data):
  - `/api/graph` → returns the floor map as JSON
  - `/api/crowd` → returns current crowd counts at exits
  - `/api/rooms` → returns room occupancy numbers
- Saves/loads crowd data to JSON files

**Why Flask?** Lightweight, simple, runs locally — perfect for a live demo without needing a cloud server.

---

### 2. HTML + CSS + JavaScript (Frontend)
**File:** `templates/index.html`, `templates/admin.html`
**What it is:** The actual app that runs in the browser on the phone.

**What it does:**
- Draws the floor map using HTML5 Canvas (a drawing surface in browser)
- Runs Dijkstra's algorithm entirely in JavaScript (no server needed for routing)
- Shows real-time updates by polling the server every 4 seconds
- Handles phone sensor events (motion, compass)

**Why no React/Angular?** Plain HTML+JS is simpler, loads faster on mobile, no build step needed.

---

### 3. HTML5 Canvas (Map Drawing)
**What it is:** A browser API that lets you draw shapes, lines, text programmatically.

**What it does in this project:**
- Draws rooms as rectangles with labels
- Draws corridors as grey strips
- Draws yellow animated path lines (the route)
- Draws the red pulsing "YOU" dot
- Draws blue compass arrow (direction you're facing)
- Draws purple trail (where you've walked)
- Redraws 60 times per second (`requestAnimationFrame`) — this is why animations are smooth

**Key code pattern:**
```javascript
requestAnimationFrame(render);  // calls render() every ~16ms = 60fps
```

---

### 4. Dijkstra's Algorithm (Pathfinding)
**File:** Inside `index.html` (JavaScript)
**What it is:** A famous graph algorithm invented by Edsger Dijkstra in 1956. Finds shortest path in a weighted graph.

**How it works in this project:**
1. Floor plan is stored as a **graph**: nodes (rooms, corridors, exits) + edges (connections with distances)
2. Each edge has a **weight** — normally the physical distance
3. When crowd is HIGH at an exit, its edges get **multiplied** (High = ×6, Medium = ×2.5, Low = ×1)
4. Dijkstra finds the path with **lowest total weight** = physically short AND crowd-safe

**Example:**
```
Main Entrance: 80 people (High) → edge weight ×6 → algorithm avoids it
Exit East: 5 people (Low) → edge weight ×1 → algorithm prefers it
```

**Why Dijkstra and not BFS/DFS?** BFS doesn't handle weighted edges. Dijkstra is the standard for weighted shortest path — it's taught in every algorithms course.

**Runs every frame** — so as crowd data updates, the path instantly recalculates.

---

### 5. JSON (Data Storage)
**Files:** `data/floor_graph.json`, `data/crowd_state.json`, `data/room_state.json`
**What it is:** JavaScript Object Notation — a simple text format for storing structured data.

**What each file stores:**
- `floor_graph.json` → all nodes (rooms), edges (connections), exit list, camera exit location
- `crowd_state.json` → current count at each exit (`{"Main_Entrance": 45, "Exit_East": 8}`)
- `room_state.json` → current count in each room

**Why JSON?** Human-readable, works natively in JavaScript, no database needed for a demo.

---

### 6. REST API (Client-Server Communication)
**What it is:** A standard way for browser and server to talk via HTTP requests.

**Endpoints in this project:**
| URL | Method | What it does |
|---|---|---|
| `/` | GET | Returns main user page |
| `/admin` | GET | Returns admin control page |
| `/api/graph` | GET | Returns floor map JSON |
| `/api/crowd` | GET | Returns current crowd data |
| `/api/crowd` | POST | Admin updates crowd numbers |
| `/api/rooms` | GET | Returns room occupancy |
| `/api/rooms` | POST | Admin updates room numbers |
| `/locate/<room>` | GET | QR code redirect — sets user location |

**How real-time updates work:**
```
Browser polls /api/crowd every 4000ms (4 seconds)
          ↓
Gets new crowd numbers
          ↓
Dijkstra re-runs with new weights
          ↓
Map redraws with new path
```
This is called **polling** — not true real-time, but sufficient for evacuation speed.

---

### 7. PDR — Pedestrian Dead Reckoning (Mobile Navigation)
**File:** `templates/index.html` (JavaScript, PDR object)
**What it is:** A navigation technique that estimates position by counting steps and tracking direction — no GPS needed.

**How it works step by step:**

#### Step 1 — Step Detection (Accelerometer)
```
Phone's accelerometer measures force in x, y, z axes
When you walk: acceleration spikes above gravity (9.8 m/s²) at each footstep
Code detects this spike → counts as 1 step → moves dot 22 units on map
```

**The math:**
```javascript
delta = rawMagnitude - 9.8  // gravity baseline
if (delta > 1.8) → step detected!  // 1.8 m/s² threshold
```

#### Step 2 — Direction (Compass / Gyroscope)
```
DeviceOrientationEvent gives compass heading in degrees
0° = North, 90° = East, 180° = South, 270° = West
After calibration: phone heading → map direction
```

**The math:**
```javascript
mapHeading = (phoneHeading - northOffset + 360) % 360
dx = stepLength × sin(mapHeading)   // east-west movement
dy = -stepLength × cos(mapHeading)  // north-south movement
```

#### Step 3 — Calibration
```
User faces "North" on the map → taps Calibrate
Code records that compass reading as northOffset
From now on: all directions relative to that reference
```

#### Step 4 — Path Snapping
```
After each step: dot's new position is snapped to nearest corridor/edge
This prevents the dot from drifting through walls
Max snap distance: 80 design units
```

**Why PDR over GPS?** GPS doesn't work indoors — buildings block satellite signal. PDR uses sensors already in every smartphone. Research gap: existing systems use BLE beacons (~₹2000/beacon) for indoor positioning. PDR = ₹0 hardware cost.

---

### 8. DeviceMotionEvent + DeviceOrientationEvent (Browser Sensor APIs)
**What they are:** Browser APIs that expose phone hardware sensors to JavaScript.

**DeviceMotionEvent gives:**
- `acceleration.x/y/z` — acceleration in 3 axes (m/s²)
- `accelerationIncludingGravity` — same but includes 9.8 m/s² gravity

**DeviceOrientationEvent gives:**
- `alpha` — compass heading (0-360°)
- `webkitCompassHeading` — iOS-specific compass (more accurate)

**Why HTTPS is required:** Browsers block sensor access on plain `http://` for security. Only `https://` pages can read phone sensors. That's why ngrok is used — it provides a real HTTPS URL.

**iOS permission:** On iPhone, sensors require explicit user permission (a popup). Android grants automatically.

---

### 9. YOLO v8 (AI Crowd Detection)
**File:** `yolo_crowd.py`
**What it is:** You Only Look Once — a real-time object detection neural network.

**What it does:**
- Takes video frame from camera at exit
- Detects and counts number of people in frame
- Returns count → stored in `crowd_state.json`
- Flask API serves this to the browser

**Why YOLO?** Fastest object detection model available — can process 30+ frames/second on a GPU. v8 is the latest version, most accurate for person detection.

**Why this matters for research:** Previous systems used manual crowd counters or pressure sensors. YOLO gives automated, real-time visual crowd estimation.

**Model file:** `yolov8n.pt` — the "nano" version (6.5MB), runs even without GPU.

---

### 10. ngrok (HTTPS Tunnel)
**File:** `start_tunnel.py`
**What it is:** A tool that creates a secure tunnel from the internet to your local PC.

**How it works:**
```
Your PC (port 5000) ←→ ngrok servers ←→ https://xxx.ngrok-free.dev ←→ Phone
```

**Why needed:** Your PC's IP (`192.168.1.8`) is only accessible on the same WiFi network. ngrok makes it accessible from anywhere, with a proper HTTPS certificate.

**Why HTTPS matters:** Browser security policy called "Secure Context" — sensors, camera, and certain APIs only work on HTTPS pages.

---

### 11. QR Codes (Location Initialization)
**File:** `generate_qr.py`
**What it is:** Quick Response code — a 2D barcode that encodes a URL.

**What it does:**
- Each room gets a QR code encoding its URL: `https://your-ngrok-url/locate/Room_Name`
- User scans with phone camera → browser opens → location auto-set
- Eliminates need for user to manually select room in emergency

**Why QR?** No app install, no Bluetooth pairing — works with any camera app.

---

## HOW REAL-TIME UPDATES WORK — Full Flow

```
Admin changes crowd number in browser
        ↓
Browser sends POST to /api/crowd (Flask)
        ↓
Flask saves new number to crowd_state.json
        ↓ (within 4 seconds)
User's browser polls GET /api/crowd
        ↓
Gets new crowd number
        ↓
crowdData object updated in JavaScript
        ↓
Next render() call → buildAdj() uses new crowd weights
        ↓
dijkstra() recalculates → new bestExit + path
        ↓
Canvas redraws → user sees new yellow path
```

Total time from admin change to user seeing update: **< 4 seconds**

---

## HOW THE DOT MOVES — Full Flow

```
User walks one step in real life
        ↓
Phone accelerometer detects spike above 1.8 m/s²
        ↓
onDeviceMotion() fires in JavaScript
        ↓
peakDetected = true → applyStep() called
        ↓
Current compass heading read from PDR.heading
        ↓
northOffset subtracted → mapHeading in map coordinates
        ↓
dx = 22 × sin(mapHeading)
dy = -22 × cos(mapHeading)
        ↓
new position = old position + (dx, dy)
        ↓
snapToPath() → snaps to nearest corridor
        ↓
PDR.pos updated
        ↓
render() runs next frame → draws red dot at new PDR.pos
        ↓ (side effect)
If near a room node → currentUser updates → Dijkstra recalculates
```

---

## TECHNOLOGIES SUMMARY TABLE

| Technology | Used For | Why Chosen |
|---|---|---|
| Python | Backend language | Simple, fast to write |
| Flask | Web server | Lightweight, easy API creation |
| HTML5 Canvas | Floor map drawing | No library needed, full control |
| JavaScript | Frontend logic, Dijkstra | Runs in browser, no install |
| Dijkstra's Algorithm | Shortest safe path | Standard weighted-graph algorithm |
| JSON | Data storage | Simple, no database needed |
| REST API | Browser-server communication | Standard web pattern |
| DeviceMotionEvent | Step detection | Built into every smartphone |
| DeviceOrientationEvent | Compass heading | Built into every smartphone |
| PDR (Dead Reckoning) | Indoor navigation | No GPS/BLE hardware needed |
| YOLO v8 | Person detection at exits | Fastest real-time object detection |
| ngrok | HTTPS tunnel for mobile | Required for sensor API access |
| QR Codes | Auto location-setting | No app install, universal |

---

## WHAT TO TELL YOUR TEACHER

**"What algorithms did you use?"**
> Dijkstra's algorithm for pathfinding with dynamic edge weights based on crowd density.

**"How does the real-time part work?"**
> The browser polls the Flask server every 4 seconds for updated crowd counts. When counts change, Dijkstra recalculates and the map redraws instantly.

**"How does the phone tracking work?"**
> PDR — Pedestrian Dead Reckoning. The phone's accelerometer detects each footstep as an acceleration spike. The compass gives direction. Together they update position on the map without GPS.

**"Why does it need HTTPS?"**
> Browser security policy (Secure Context) blocks access to device sensors on plain HTTP. HTTPS is required to read accelerometer and compass data.

**"What is the AI component?"**
> YOLO v8 (You Only Look Once) processes camera frames at exit points and counts people. This count feeds into the routing algorithm's edge weights.

**"What's the research gap you're filling?"**
> Existing indoor evacuation systems either use static exit signs (no intelligence) or require expensive BLE beacon hardware for positioning (~₹2000+ per beacon). Our system uses YOLO for crowd-aware routing and PDR for zero-hardware indoor navigation.

---

*Last updated: August 2026 | Add new tech sections above this line*
