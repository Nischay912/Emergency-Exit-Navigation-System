"""
start_tunnel.py
Run this in a SECOND terminal while app.py is running in the first.
It creates an HTTPS tunnel so your phone can access the server with sensors.

Usage:
    python start_tunnel.py
"""

from pyngrok import ngrok, conf

# Your ngrok auth token
AUTH_TOKEN = "3I9WmfJZn9IlA8C2Z4Ig3xixk06_46Chof1JwynYB4i4H26M6"

conf.get_default().auth_token = AUTH_TOKEN

print("=" * 60)
print("  Starting ngrok HTTPS tunnel...")
print("=" * 60)

# Kill any leftover ngrok processes from previous runs
try:
    ngrok.kill()
except Exception:
    pass

# Open a tunnel on port 5000 (where Flask is running)
tunnel = ngrok.connect(5000, "http")

url = tunnel.public_url
# ngrok gives http:// by default — we want https://
https_url = url.replace("http://", "https://")

print()
print("  >> TUNNEL IS LIVE! <<")
print()
print(f"  OPEN THIS ON YOUR PHONE:")
print(f"  >>> {https_url} <<<")
print()
print(f"  Admin panel (PC only):")
print(f"  >>> http://localhost:5000/admin <<<")
print()
print("  Sensors (accelerometer, compass) will work on your phone!")
print("  Keep this window open during your entire demo.")
print("=" * 60)
print()
print("  Press CTRL+C to stop the tunnel.")
print()

# Keep the tunnel alive — just wait here until Ctrl+C
try:
    input()
except KeyboardInterrupt:
    pass
finally:
    ngrok.kill()
    print("Tunnel stopped.")
