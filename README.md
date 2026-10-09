<div align="center">
  <img src="https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/AI-YOLOv8-blue?style=for-the-badge" alt="AI Model">
  <img src="https://img.shields.io/badge/Algorithm-Dijkstra-orange?style=for-the-badge" alt="Algorithm">
</div>

<br>

# 🚨 AI-Powered Emergency Exit & Crowd Routing System

A real-time, edge-computing powered emergency evacuation system designed for large indoor spaces (malls, colleges, offices). It utilizes **Computer Vision (YOLOv8)** to monitor crowd density at exits and **Dynamic Graph Algorithms (Dijkstra)** to instantly reroute trapped users to the safest exits via their smartphones—all without requiring an app download or active GPS.

---

## 🌟 Key Features (v2.0)

- **🧠 Edge-AI Crowd Counting:** Live webcam integration running YOLOv8 to continuously monitor exits. If an exit becomes overcrowded (e.g., >50 people), the system automatically increases the mathematical "cost" of that path.
- **🗺️ Dynamic Dijkstra Pathfinding:** Re-calculates the absolute shortest and safest path to an exit dynamically in the user's browser, completely avoiding fires, blockades, and stampedes.
- **📱 PDR (Pedestrian Dead Reckoning) Indoor Navigation:** GPS doesn't work indoors. Our Web App taps into the phone's native **Accelerometer and Compass** to track physical footsteps and turns, updating the user's location on the floor map in real-time.
- **🗣️ Multi-Language Voice Megaphone & Navigation:** Uses the Web Speech API to provide turn-by-turn voice directions, and allows the Admin to broadcast custom audio messages to all connected phones simultaneously (in English, Hindi, and Kannada).
- **🎛️ Live Admin Command Center:** A secure, authenticated dashboard for emergency responders to trigger global alarms, simulate smoke propagation, block hallways, and monitor SOS signals.
- **🛡️ Extreme Resilience (State Recovery):** In emergencies, networks drop and pages accidentally reload. We use strict `localStorage` and `sessionStorage` architecture so if a user or admin refreshes the page, their location, path, and event logs are restored in milliseconds.
- **📄 Instant Incident Reporting:** One-click generation of post-evacuation `.txt` logs for enterprise and fire-department compliance.

---

## 🛠️ Tech Stack & Architecture

| Category | Technology | How it's Used |
|---|---|---|
| **Core Backend** | Python 3.10, Flask | The main web server, managing API routes and Admin sessions. |
| **Artificial Intelligence** | YOLOv8 (Ultralytics), OpenCV | Processes camera frames locally to detect and count people. |
| **Pathfinding Engine** | Dijkstra's Algorithm (JS) | Client-side dynamic graph routing for zero server latency. |
| **Frontend UI/UX** | HTML5 Canvas, Vanilla JS, CSS3 | Rendering the 60fps floor plan, dark-mode Admin dashboard. |
| **Sensor Integration** | Web API (`DeviceOrientation`) | Reading magnetometer/gyroscope data for step-tracking. |
| **Accessibility** | Web Speech API | Text-to-Speech engine for visually impaired navigation. |
| **Networking** | Ngrok | Secure HTTPS tunneling for mobile sensor access. |
| **Data Persistence** | `localStorage`, `sessionStorage` | Saving navigation state across accidental browser refreshes. |

*For a full, beginner-friendly breakdown of our technology, read the [TECH_STACK_EXPLAINED.md](TECH_STACK_EXPLAINED.md).*

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A smartphone (for scanning QR codes & motion sensors)
- Ngrok installed (for the live mobile tunnel)

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Nischay912/Project-clg-major-project.git
   cd Project-clg-major-project
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Central Server**
   ```bash
   python app.py
   ```
   *The server starts locally at `http://localhost:5000`.*

4. **Launch the Public Tunnel (For Phones)**
   Open a second terminal window and run:
   ```bash
   ngrok http 5000
   ```
   *Scan the generated HTTPS link on your smartphone to access the user interface!*

---

## 🕹️ System Walkthrough

### 1. The User Experience (Evacuation)
* **Zero-Friction Entry:** The user scans a QR code on a wall (e.g. "Library"). The web app instantly opens and locks their starting location. No login required.
* **Smart Routing:** The app queries the server for hazards. If the Main Staircase is crowded or on fire, the blue navigation line instantly diverts them to the East Fire Exit.
* **Walking:** The user taps "Enable Sensors". As they walk, the phone's accelerometer detects the bounce of their steps and moves the dot on the screen natively.

### 2. The Admin Experience (Command Center)
* **Secure Login:** Go to `/admin` (Default password provided to administrators).
* **Hazard Simulation:** Click "Fire near Staff Lounge". The server instantly broadcasts this to all connected phones, which instantly recalculate their routes away from the lounge.
* **Crowd Overrides:** Manually drag sliders to simulate massive crowds at specific exits.
* **SOS Tracking:** Monitor inbound SOS signals from trapped users, mark them as rescued, and download the final Incident Report when the building is clear.

---

## 🔒 Security & Scaling Notes

* **Edge Computing:** By processing Dijkstra's algorithm directly on the user's smartphone processor (Client-Side), the central server handles 99% less load, preventing server crashes when 10,000 panicking students ping the server at once.
* **Admin Authentication:** The dashboard is protected via Flask Encrypted Session Cookies (`app.secret_key`).
* **Privacy:** YOLOv8 runs entirely locally. Video frames are analyzed and immediately discarded. No video is ever saved or uploaded to the cloud, ensuring strict privacy compliance.

---

## 🎓 Academic Contribution

This system was built as a B.Tech Major Project to solve critical flaws in modern indoor evacuation:
* **Flaw:** Static EXIT signs route people directly into fires.
* **Solution:** AI-driven dynamic routing.
* **Flaw:** Standard indoor positioning requires expensive $10,000 Bluetooth Beacon installations.
* **Solution:** Zero-cost PDR leveraging the user's own smartphone hardware.

---

<div align="center">
  <b>Built with Python, JavaScript, and YOLOv8</b>
</div>
