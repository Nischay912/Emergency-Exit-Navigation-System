import qrcode
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent
OUT  = BASE / "qr_codes"
OUT.mkdir(exist_ok=True)

# Require the user to pass the ngrok URL so the QR codes actually work with sensors!
if len(sys.argv) < 2:
    print("\n[ERROR] You must provide your secure HTTPS URL from start_tunnel.py!")
    print("Usage: python generate_qr.py <https_url>")
    print("Example: python generate_qr.py https://1a2b-3c4d.ngrok-free.app\n")
    sys.exit(1)

base_url = sys.argv[1].rstrip('/')

try:
    with open(BASE / "data" / "floor_graph.json") as f:
        graph = json.load(f)
except FileNotFoundError:
    print("[ERROR] floor_graph.json not found in data/ folder!")
    sys.exit(1)

nodes = graph.get("nodes", {})
exits = set(graph.get("exit_nodes", []))

print(f"\n[QR Generator] Base URL: {base_url}")
print(f"[QR Generator] Generating {len(nodes)} QR codes...\n")

for name in nodes:
    # URL that automatically places the user in the scanned room!
    url = f"{base_url}/locate/{name}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    file_path = OUT / f"{name}.png"
    img.save(file_path)

    tag = " [EXIT]" if name in exits else ""
    print(f"  [OK]  {name}{tag}")
    print(f"       -> saved: {file_path.name}")

print(f"\n[SUCCESS] Generated {len(nodes)} QR codes in the 'qr_codes' folder.")
print("Print these out and stick them to the walls. When a user scans one,")
print("the app will open and automatically set their starting location!")
