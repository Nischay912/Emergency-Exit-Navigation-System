import re

with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

pattern = r'"alarm_active": ALARM_ACTIVE\s*\}'
replacement = '"alarm_active": ALARM_ACTIVE,\n        "hazards": HAZARDS\n    }'

if '"hazards": HAZARDS' not in app_code:
    app_code = re.sub(pattern, replacement, app_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)
