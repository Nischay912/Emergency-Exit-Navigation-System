import sys

with open('templates/index.html', 'r', encoding='utf8') as f:
    text = f.read()

# 1. Insert Kannada phrases
kn_phrases = '''const KANNADA_PHRASES = {
  "↑": "ನೇರವಾಗಿ ಹೋಗಿ",
  "→": "ಬಲಕ್ಕೆ ತಿರುಗಿ",
  "←": "ಎಡಕ್ಕೆ ತಿರುಗಿ",
  "↗": "ಸ್ವಲ್ಪ ಬಲಕ್ಕೆ ಹೋಗಿ",
  "↖": "ಸ್ವಲ್ಪ ಎಡಕ್ಕೆ ಹೋಗಿ",
  "↓": "ಹಿಂದೆ ತಿರುಗಿ",
  "🚨": "ನೀವು ತುರ್ತು ನಿರ್ಗಮನವನ್ನು ತಲುಪಿದ್ದೀರಿ. ಸುರಕ್ಷಿತವಾಗಿ ಹೊರಬನ್ನಿ!"
};

// Must be called'''

text = text.replace('// Must be called', kn_phrases)

# 2. Update speak function for kn-IN rate
text = text.replace("utter.rate = VOICE.lang === 'hi-IN' ? 0.85 : 0.95;", "utter.rate = (VOICE.lang === 'hi-IN' || VOICE.lang === 'kn-IN') ? 0.85 : 0.95;")

# 3. Update speakStep for exitMsg
old_exit = "speak(VOICE.lang === 'hi-IN' ? HINDI_PHRASES[\"🚨\"] : \"You have reached the emergency exit. Please evacuate safely.\");"
new_exit = "const exitMsg = VOICE.lang === 'hi-IN' ? HINDI_PHRASES[\"🚨\"] : VOICE.lang === 'kn-IN' ? KANNADA_PHRASES[\"🚨\"] : \"You have reached the emergency exit. Please evacuate safely.\";\n    speak(exitMsg);"
text = text.replace(old_exit, new_exit)

# 4. Replace speakStep big if/else
old_if_else = """  if (VOICE.lang === 'hi-IN') {
    if (arrow === "🚨") phrase = HINDI_PHRASES["🚨"];
    else if (HINDI_PHRASES[arrow]) phrase = `${target} ${HINDI_PHRASES[arrow]}`;
    else phrase = `${target} की ओर जाएं`;
    if (step.dist && arrow !== "🚨") phrase += `, लगभग ${step.dist} मीटर।`;
  } else {"""

new_if_else = """  if (VOICE.lang === 'hi-IN') {
    if (arrow === "🚨") phrase = HINDI_PHRASES["🚨"];
    else if (HINDI_PHRASES[arrow]) phrase = `${target} ${HINDI_PHRASES[arrow]}`;
    else phrase = `${target} की ओर जाएं`;
    if (step.dist && arrow !== "🚨") phrase += `, लगभग ${step.dist} मीटर।`;
  } else if (VOICE.lang === 'kn-IN') {
    if (arrow === "🚨") phrase = KANNADA_PHRASES["🚨"];
    else if (KANNADA_PHRASES[arrow]) phrase = `${target} ಕಡೆಗೆ ${KANNADA_PHRASES[arrow]}`;
    else phrase = `${target} ಕಡೆಗೆ ಹೋಗಿ`;
    if (step.dist && arrow !== "🚨") phrase += `, ಸುಮಾರು ${step.dist} ಮೀಟರ್.`;
  } else {"""

text = text.replace(old_if_else, new_if_else)

with open('templates/index.html', 'w', encoding='utf8') as f:
    f.write(text)
print('Done!')
