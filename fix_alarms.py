import re

with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# Fix get_alarm
app = app.replace(
    'def get_alarm():\n    global ALARM_ACTIVE',
    'def get_alarm():\n    global ALARM_ACTIVE\n    return jsonify({"active": ALARM_ACTIVE})'
)

# Fix post_alarm
app = app.replace(
    'ALARM_ACTIVE = not ALARM_ACTIVE # toggle',
    'ALARM_ACTIVE = not ALARM_ACTIVE # toggle\n    return jsonify({"active": ALARM_ACTIVE})'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)
