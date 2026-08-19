# 🚨 Emergency Exit System — Demo Guide
> **For beginners. Read top to bottom. Step by step.**

---

## 📋 What You Have

Your project has two parts running together:
| Part | What it does |
|---|---|
| **Flask server** (`app.py`) | Runs on your PC. Powers the map, pathfinding, crowd data |
| **ngrok tunnel** | Gives your phone a real HTTPS link so motion sensors work |

---

## 🗂️ Files That Matter
```
Project_Exit/
├── app.py              ← Main server (run this first)
├── ngrok.exe           ← HTTPS tunnel (run this second)
├── templates/
│   ├── index.html      ← Mobile user map page
│   └── admin.html      ← Admin control panel
└── data/
    ├── floor_graph.json   ← Building layout
    └── crowd_state.json   ← Current crowd numbers
```

---

## 🚀 EVERY TIME YOU WANT TO DEMO — Do These Steps

### STEP 1 — Open TWO PowerShell windows

Right-click Start → "Terminal" or "PowerShell"  
Do this twice. You need two separate windows.

---

### STEP 2 — Window 1: Start the server

```powershell
cd "C:\Users\ben09\OneDrive\Desktop\Project_Exit"
python app.py
```

✅ You should see:
```
Emergency Exit System — Running
Local PC    -> http://localhost:5000/
```

**Leave this window open. Do NOT close it.**

---

### STEP 3 — Window 2: Start the tunnel

```powershell
cd "C:\Users\ben09\OneDrive\Desktop\Project_Exit"
taskkill /F /IM ngrok.exe 2>$null; python start_tunnel.py
```

> The `taskkill` part clears any old tunnel automatically. Safe to run every time.

✅ You will see:
```
============================================================
  >> TUNNEL IS LIVE! <<

  OPEN THIS ON YOUR PHONE:
  >>> https://something-random.ngrok-free.dev <<<
============================================================
```

**Copy that `https://...ngrok-free.dev` URL — this is your phone URL!**

> Note: The URL changes every time you restart the tunnel. That's normal on the free plan.

---

### STEP 4 — Open on your phone

1. Open **Chrome** on your phone
2. Type the `https://abc123xyz.ngrok-free.app` URL
3. ✅ Page loads with NO security warning
4. Motion sensors work automatically!

---

### STEP 5 — Open Admin Panel (on PC)

Open your PC browser and go to:
```
http://localhost:5000/admin
```

This is where you control crowd numbers during the demo.

---

## 🎓 HOW TO GIVE THE FULL DEMO

### Roles (if you have a friend helping)
| Person | Device | Task |
|---|---|---|
| You (presenter) | Phone | Walk the floor map, show navigation |
| Friend (optional) | PC browser | Control admin panel, change crowd |

---

### Demo Script (say these things)

#### 🎬 Scene 1 — Show the system

> *"This is our Emergency Exit System. It works on any smartphone — no app install needed, just a browser."*

- Open the ngrok URL on your phone
- Show the floor map with rooms
- Point out: "Each room shows crowd level — Low, Medium, or High"

---

#### 🎬 Scene 2 — Show pathfinding

> *"When a user opens the app, they select their current room from the dropdown."*

1. On phone → tap the **room dropdown** → select your room (e.g. "Room 101")
2. Tap **"Find Exit"** or **"Navigate"**
3. The green path appears on the map

> *"The algorithm calculates the safest path — it avoids high-crowd exits automatically."*

---

#### 🎬 Scene 3 — Show crowd detection

> *"Here's what makes this different — crowd levels are updated in real-time."*

1. On PC → open `http://localhost:5000/admin`
2. Change an exit from 10 → 80 people (click the slider or number)
3. Click **Update**
4. Go back to phone — show the path **changed** to avoid the crowded exit

> *"As crowd levels change, the system re-routes automatically to the safest exit."*

---

#### 🎬 Scene 4 — Show PDR navigation (motion sensors)

> *"For the research contribution — we implemented PDR: Pedestrian Dead Reckoning. This means the phone uses its own accelerometer and compass to track your real-world movement on the virtual map. No GPS, no extra hardware."*

1. On phone → scroll to **"Walking Navigation"** section
2. Tap **"Enable Phone Sensors"** → tap Allow on the popup
3. Tap **"Calibrate North"** → face the north wall of your room → tap
4. Tap **"Start Walking"** → walk forward
5. Your red dot moves on the map!

> *"This fills a key research gap — existing systems require expensive BLE beacons or GPS. Ours works entirely from the phone's built-in sensors."*

---

#### 🎬 Scene 5 — QR Code (bonus)

> *"For real deployment, each room has a QR code. Scanning it automatically sets your location."*

1. Show one of the QR codes from the `qr_codes/` folder
2. Scan with phone camera
3. Location auto-sets in the app

---

## 🔧 ONE-TIME SETUP — Fix Windows Defender Blocking ngrok

> Windows Defender wrongly flags ngrok as a virus. It is NOT a virus — it is a popular developer tool used by millions. You need to whitelist it manually.

### Method: Manual Exclusion in Windows Security

> ✅ ALREADY DONE — You completed this step. No need to do it again.

1. Press **Windows key** → type **"Windows Security"** → open it
2. Click **"Virus & threat protection"**
3. → **"Manage settings"** → scroll to **"Exclusions"** → **"Add or remove exclusions"**
4. Add these two folders:
   ```
   C:\Users\ben09\AppData\Local\Python\pythoncore-3.14-64\Scripts
   C:\Users\ben09\AppData\Local\ngrok
   ```
5. ✅ Done — ngrok runs via `python start_tunnel.py` without being blocked

After doing this, go back to **STEP 3** above and run ngrok again.

---

## ❌ Common Problems & Fixes

| Problem | Fix |
|---|---|
| `python: command not found` | Open a new terminal window — Python path not loaded |
| `ngrok: virus detected` | Do the ONE-TIME SETUP above to whitelist |
| ngrok shows no URL | Check Flask is running in Window 1 first |
| Phone says "connection refused" | Make sure Flask server is running |
| Sensors say "no motion sensors" | You're on HTTP — use the ngrok `https://` URL |
| Path not changing after crowd update | Refresh the phone page |
| ngrok URL changes every time | This is normal on free plan — just copy the new URL |

---

## 📱 Quick Reference Card (for demo day)

```
BEFORE DEMO:
1. Window 1: python app.py
2. Window 2: [run ngrok command]
3. Copy the https://xxx.ngrok-free.app URL
4. Open that URL on your phone
5. Open http://localhost:5000/admin on PC

DEMO ORDER:
1. Show map + room selection
2. Click Find Exit → show green path
3. Admin panel → change crowd → path changes
4. Enable sensors → calibrate → walk → dot moves
5. Show QR code scanning (optional)
```

---

## 🔑 Your ngrok Auth Token (saved — do not share publicly)
```
Token already saved to: C:\Users\ben09\AppData\Local\ngrok\ngrok.yml
```
*Token is configured. You do NOT need to re-enter it.*

---

*Guide created for Emergency Exit System — Major Project Demo*
