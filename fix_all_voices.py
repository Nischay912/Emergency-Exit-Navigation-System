import re

# =================================================================
# STEP 1: app.py - Add deep-translator to api_broadcast
# =================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

old_broadcast = '''
@app.route("/api/broadcast", methods=["POST"])
def api_broadcast():
    global LATEST_BROADCAST
    data = request.json or {}
    msg = data.get("message", "").strip()
    if msg:
        import time
        LATEST_BROADCAST = {"id": int(time.time()), "message": msg}
    return jsonify({"success": True})
'''

new_broadcast = '''
@app.route("/api/broadcast", methods=["POST"])
def api_broadcast():
    global LATEST_BROADCAST
    data = request.json or {}
    msg = data.get("message", "").strip()
    if msg:
        import time
        try:
            from deep_translator import GoogleTranslator
            msg_hi = GoogleTranslator(source='auto', target='hi').translate(msg)
            msg_kn = GoogleTranslator(source='auto', target='kn').translate(msg)
        except Exception:
            msg_hi = msg
            msg_kn = msg
            
        LATEST_BROADCAST = {
            "id": int(time.time()), 
            "message": msg,
            "message_hi": msg_hi,
            "message_kn": msg_kn
        }
    return jsonify({"success": True})
'''

if 'GoogleTranslator' not in app:
    app = app.replace(old_broadcast.strip(), new_broadcast.strip())

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)

print("app.py updated with auto-translation")


# =================================================================
# STEP 2: index.html - Update voice logic and broadcast handler
# =================================================================
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 2a. Update Broadcast JS handler to use translated fields
old_bc_js = '''      // Broadcast logic
      if (st.broadcast && st.broadcast.id > lastBroadcastId) {
        lastBroadcastId = st.broadcast.id;
        if (typeof speak === 'function') speak(st.broadcast.message);
        
        // Show a prominent alert toast
        const toast = document.getElementById("toast");
        if (toast) {
          toast.innerHTML = `<strong style="color:#facc15">&#128227; ADMIN BROADCAST:</strong><br>${st.broadcast.message}`;
          toast.className = "toast show";
          setTimeout(() => { toast.className = "toast"; }, 8000);
        }
      }'''

new_bc_js = '''      // Broadcast logic
      if (st.broadcast && st.broadcast.id > lastBroadcastId) {
        lastBroadcastId = st.broadcast.id;
        
        let bMsg = st.broadcast.message;
        if (typeof VOICE !== 'undefined') {
            if (VOICE.lang === 'hi-IN' && st.broadcast.message_hi) bMsg = st.broadcast.message_hi;
            if (VOICE.lang === 'kn-IN' && st.broadcast.message_kn) bMsg = st.broadcast.message_kn;
        }
        
        if (typeof speak === 'function') speak(bMsg);
        
        // Show a prominent alert toast
        const toast = document.getElementById("toast");
        if (toast) {
          toast.innerHTML = `<strong style="color:#facc15">&#128227; ADMIN BROADCAST:</strong><br>${bMsg}`;
          toast.className = "toast show";
          setTimeout(() => { toast.className = "toast"; }, 10000);
        }
      }'''

html = html.replace(old_bc_js, new_bc_js)

# 2b. Bruteforce replacement for Smoke/SOS/Safe translations
# Because they might be in any state due to previous patch failing on whitespace
# We will use regex to find and replace them reliably.

html = re.sub(
    r"if \(typeof speak === 'function'\) speak\([\"']Warning! Smoke detected[^\)]+\);\s*",
    """if (typeof speak === 'function') {
          let smokeMsg = "Warning! Smoke detected. Follow the glowing path to the nearest exit immediately!";
          if (typeof VOICE !== 'undefined') {
            if (VOICE.lang === 'hi-IN') smokeMsg = "चेतावनी! धुआं पाया गया है। तुरंत चमकते हुए रास्ते से बाहर निकलें!";
            if (VOICE.lang === 'kn-IN') smokeMsg = "ಎಚ್ಚರಿಕೆ! ಹೊಗೆ ಪತ್ತೆಯಾಗಿದೆ. ಹೊಳೆಯುವ ದಾರಿಯನ್ನು ಅನುಸರಿಸಿ ತಕ್ಷಣ ಹೊರಬನ್ನಿ!";
          }
          speak(smokeMsg);
        }
        """,
    html
)

html = re.sub(
    r"if \(typeof speak === 'function'\) speak\([\"']S O S sent! Help is on the way[^\)]+\);\s*",
    """if (typeof speak === 'function') {
      let sosMsg = 'S O S sent! Help is on the way. Stay calm and stay put.';
      if (typeof VOICE !== 'undefined') {
        if (VOICE.lang === 'hi-IN') sosMsg = "एस ओ एस भेज दिया गया है! मदद आ रही है। शांत रहें और वहीं रहें।";
        if (VOICE.lang === 'kn-IN') sosMsg = "ಎಸ್ ಓ ಎಸ್ ಕಳುಹಿಸಲಾಗಿದೆ! ಸಹಾಯ ಬರುತ್ತಿದೆ. ಶಾಂತರಾಗಿರಿ ಮತ್ತು ಅಲ್ಲೇ ಇರಿ.";
      }
      speak(sosMsg);
    }\n    """,
    html
)

html = re.sub(
    r"if \(typeof speak === 'function'\) speak\([\"']You have been accounted for[^\)]+\);\s*",
    """if (typeof speak === 'function') {
        let safeMsg = 'You have been accounted for at the safe assembly point.';
        if (typeof VOICE !== 'undefined') {
          if (VOICE.lang === 'hi-IN') safeMsg = "सुरक्षित क्षेत्र में आपकी उपस्थिति दर्ज कर ली गई है।";
          if (VOICE.lang === 'kn-IN') safeMsg = "ಸುರಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ನಿಮ್ಮ ಹಾಜರಾತಿಯನ್ನು ದಾಖಲಿಸಲಾಗಿದೆ.";
        }
        speak(safeMsg);
      }\n      """,
    html
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html translations forcefully updated.")
