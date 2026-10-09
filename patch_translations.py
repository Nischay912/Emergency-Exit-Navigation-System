import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. SMOKE VOICE PATCH
smoke_old = '''      if (SMOKE_LEVEL !== "none" && !window.smokeVoiceTriggered) {
        window.smokeVoiceTriggered = true;
        if (typeof speak === 'function') speak("Warning! Smoke detected. Follow the glowing path to the nearest exit immediately!");'''

smoke_new = '''      if (SMOKE_LEVEL !== "none" && !window.smokeVoiceTriggered) {
        window.smokeVoiceTriggered = true;
        if (typeof speak === 'function') {
          let smokeMsg = "Warning! Smoke detected. Follow the glowing path to the nearest exit immediately!";
          if (typeof VOICE !== 'undefined') {
            if (VOICE.lang === 'hi-IN') smokeMsg = "चेतावनी! धुआं पाया गया है। तुरंत चमकते हुए रास्ते से बाहर निकलें!";
            if (VOICE.lang === 'kn-IN') smokeMsg = "ಎಚ್ಚರಿಕೆ! ಹೊಗೆ ಪತ್ತೆಯಾಗಿದೆ. ಹೊಳೆಯುವ ದಾರಿಯನ್ನು ಅನುಸರಿಸಿ ತಕ್ಷಣ ಹೊರಬನ್ನಿ!";
          }
          speak(smokeMsg);
        }'''

html = html.replace(smoke_old, smoke_new)

# 2. SOS VOICE PATCH
sos_old = '''    if (typeof speak === 'function') speak('S O S sent! Help is on the way. Stay calm and stay put.');'''
sos_new = '''    if (typeof speak === 'function') {
      let sosMsg = 'S O S sent! Help is on the way. Stay calm and stay put.';
      if (typeof VOICE !== 'undefined') {
        if (VOICE.lang === 'hi-IN') sosMsg = "एस ओ एस भेज दिया गया है! मदद आ रही है। शांत रहें और वहीं रहें।";
        if (VOICE.lang === 'kn-IN') sosMsg = "ಎಸ್ ಓ ಎಸ್ ಕಳುಹಿಸಲಾಗಿದೆ! ಸಹಾಯ ಬರುತ್ತಿದೆ. ಶಾಂತರಾಗಿರಿ ಮತ್ತು ಅಲ್ಲೇ ಇರಿ.";
      }
      speak(sosMsg);
    }'''

html = html.replace(sos_old, sos_new)

# 3. SAFE VOICE PATCH
safe_old = '''      if (typeof speak === 'function') speak('You have been accounted for at the safe assembly point.');'''
safe_new = '''      if (typeof speak === 'function') {
        let safeMsg = 'You have been accounted for at the safe assembly point.';
        if (typeof VOICE !== 'undefined') {
          if (VOICE.lang === 'hi-IN') safeMsg = "सुरक्षित क्षेत्र में आपकी उपस्थिति दर्ज कर ली गई है।";
          if (VOICE.lang === 'kn-IN') safeMsg = "ಸುರಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ನಿಮ್ಮ ಹಾಜರಾತಿಯನ್ನು ದಾಖಲಿಸಲಾಗಿದೆ.";
        }
        speak(safeMsg);
      }'''

html = html.replace(safe_old, safe_new)


with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Translations applied successfully.")
