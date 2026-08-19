# Emergency Exit System — Presentation Cheat Sheet
> Read this 5 mins before demo. Top to bottom. Don't skip.

---

## BEFORE YOU START (Do this first, silently)

Open **2 terminal windows**:

**Terminal 1:**
```
cd "C:\Users\ben09\OneDrive\Desktop\Project_Exit"
python app.py
```

**Terminal 2:**
```
cd "C:\Users\ben09\OneDrive\Desktop\Project_Exit"
taskkill /F /IM ngrok.exe 2>$null; python start_tunnel.py
```

Copy the `https://xxx.ngrok-free.dev` URL from Terminal 2.

Open on **PC browser:** `http://localhost:5000`
Open on **Phone:** the ngrok `https://` URL
Open on **PC (second tab):** `http://localhost:5000/admin`

---

## DEMO ORDER — Do exactly this

---

### SCENE 1 — Introduce (30 sec)

> *"This is our Emergency Exit System. It runs on any smartphone — no app install, just a browser link. In an emergency, users scan a QR code or select their room, and the system guides them to the safest exit in real time."*

**Show:** The floor map on PC. Point to rooms, corridors, exits.

---

### SCENE 2 — Pathfinding (45 sec)

> *"The system uses Dijkstra's algorithm to calculate the optimal path. It doesn't just find the shortest path — it avoids crowded exits."*

**Click:**
1. Dropdown → select **"Lobby"**
2. Red dot appears → green path shows → purple ★ SAFEST exit highlighted
3. Point to bottom bar: *"Safest exit, crowd level, and route score — all live."*

---

### SCENE 3 — Dynamic Rerouting (45 sec)

> *"Here's what makes it different. If a camera detects high crowd at one exit, the route updates automatically."*

**Click:**
1. Switch to **admin tab**
2. Change any exit slider/number to **80** → click Update
3. Switch back to map tab
4. Show path **changed** to a different exit

> *"The path just re-routed away from the crowded exit. This is real-time dynamic rerouting — no manual intervention needed."*

---

### SCENE 4 — Mobile + PDR Sensors (60 sec)

> *"Now on mobile. This is the research contribution — PDR: Pedestrian Dead Reckoning."*

**On phone:**
1. Select **"Lobby"** from dropdown
2. Tap **"Step 1: Enable Phone Sensors"** → tap Allow
3. Tap **"Step 2: Calibrate North"** → face any direction → tap
4. Tap **"Step 3: Start Walking"**
5. Walk 10–15 steps → show screen

> *"The red dot moves with my steps. The blue arrow shows my direction from the phone's compass. No GPS, no Bluetooth beacons — just the phone's built-in accelerometer and compass. This is the key research gap we fill — existing systems need expensive hardware. Ours needs nothing extra."*

Show the **purple trail** on the map. Show the **live step count** and **compass heading** updating.

---

### SCENE 5 — QR Code (20 sec, optional)

> *"For real deployment, each room has a printed QR code. Scanning it sets your location automatically."*

Show any QR code image from the `qr_codes/` folder on PC.

---

## KEY LINES TO REMEMBER

| If asked... | Say... |
|---|---|
| "Why not GPS?" | "GPS doesn't work indoors. PDR uses onboard sensors — zero extra hardware." |
| "Is this map your real college?" | "This is a prototype layout. Real deployment uses the actual building blueprint." |
| "How does rerouting work?" | "Crowd data updates every 4 seconds. Dijkstra recalculates on each update." |
| "What's the camera doing?" | "YOLO v8 detects and counts people at exit points. Count feeds into the routing weight." |
| "How accurate is PDR?" | "PDR drifts ~5% per 10 steps without correction. QR codes at checkpoints reset the position." |

---

## IF SOMETHING BREAKS

| Problem | Fix |
|---|---|
| Map not loading | Check Terminal 1 — Flask must be running |
| Phone not opening | Check Terminal 2 — ngrok URL must be active |
| Sensors say "no motion" | You're on HTTP not HTTPS — use the ngrok `https://` link |
| Dot not moving | Tap "Stop Walking" → re-select location → tap "Start Walking" again |
| Path not changing | Refresh the map page after updating admin |

---

## ONE-LINER SUMMARY (if they ask "what's the point?")

> *"Most evacuation systems are static signs or expensive IoT sensor networks. Ours is a real-time, AI-powered system that runs on any smartphone, uses the phone's own sensors for navigation, and dynamically avoids crowded exits — all with zero hardware cost beyond a QR code printout."*

---

*Good luck. You built this. Own it.*
