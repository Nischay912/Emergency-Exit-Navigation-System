with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

if '/log_error' not in app:
    app = app.replace('if __name__ == ', '@app.route("/log_error")\ndef log_error():\n    print("FRONTEND ERROR:", request.args.get("msg"))\n    return "ok"\n\nif __name__ == ')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)
