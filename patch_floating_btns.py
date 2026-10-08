import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Change floating button CSS to start lower down so it doesn't overlap header badges
old_btn = """.floating-btn { position: fixed; top: 20px; right: 20px;"""
new_btn = """.floating-btn { position: fixed; top: 75px; right: 20px;"""

if old_btn in html:
    html = html.replace(old_btn, new_btn)

# 2. Adjust the inline style of the second button
old_audio = """<button id="audioToggle" class="floating-btn" onclick="openAudioSettings()" style="top: 80px;">"""
new_audio = """<button id="audioToggle" class="floating-btn" onclick="openAudioSettings()" style="top: 135px;">"""

if old_audio in html:
    html = html.replace(old_audio, new_audio)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
