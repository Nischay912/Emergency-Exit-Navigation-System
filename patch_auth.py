import re

with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# 1. Add secret key
if "app.secret_key" not in app:
    app = app.replace('CORS(app)', 'CORS(app)\napp.secret_key = "secure_admin_key_123"')

# 2. Replace the admin route and add login/logout routes
old_admin = """@app.route("/admin")
def admin():
    # Simple password protection for demo purposes
    # E.g. /admin?pwd=admin
    pwd = request.args.get("pwd")
    if pwd != "admin":
        return \"\"\"
        <div style="font-family:sans-serif; text-align:center; margin-top:100px;">
            <h2>Admin Panel Restricted</h2>
            <form onsubmit="window.location.href='/admin?pwd=' + document.getElementById('pwd').value; return false;">
                <input type="password" id="pwd" placeholder="Enter Password" style="padding:8px; font-size:16px;">
                <button type="submit" style="padding:8px 16px; font-size:16px;">Login</button>
            </form>
            <p style="color:#666; font-size:12px;">(Hint: password is "admin")</p>
        </div>
        \"\"\"
    return render_template("admin.html")"""

new_admin = """@app.route("/admin")
def admin():
    from flask import session
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    from flask import make_response
    resp = make_response(render_template("admin.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

@app.route("/login", methods=["GET", "POST"])
def login():
    from flask import session
    if request.method == "POST":
        pwd = request.form.get("password")
        if pwd == "admin":
            session["is_admin"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Invalid credentials. Access denied.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    from flask import session
    session.pop("is_admin", None)
    return redirect(url_for("login"))"""

app = app.replace(old_admin, new_admin)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)
