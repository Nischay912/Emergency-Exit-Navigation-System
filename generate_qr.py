"""
generate_qr.py  —  Generate QR codes for every floor node
Each QR encodes a URL: http://<YOUR_IP>:5000/locate/<NodeName>
Scan the QR at that location → opens the map with you placed there.

Run once:  python generate_qr.py
Output:    qr_codes/ folder with one PNG per node
"""

import qrcode
import socket
import json
from pathlib import Path

# ── detect your LAN IP automatically ──
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

BASE = Path(__file__).parent
OUT  = BASE / "qr_codes"
OUT.mkdir(exist_ok=True)

IP   = get_local_ip()
PORT = 5000

with open(BASE / "data" / "floor_graph.json") as f:
    graph = json.load(f)

nodes = graph["nodes"]
exits = set(graph["exit_nodes"])

print(f"\n[QR Generator] Your LAN IP: {IP}")
print(f"[QR Generator] Generating {len(nodes)} QR codes...\n")

for name in nodes:
    url = f"http://{IP}:{PORT}/locate/{name}"
    qr  = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # colour: red border for exits, blue for rooms/corridors
    fill_color  = "black"
    back_color  = "white"

    img  = qr.make_image(fill_color=fill_color, back_color=back_color)
    file = OUT / f"{name}.png"
    img.save(file)

    tag = " [EXIT]" if name in exits else ""
    print(f"  [OK]  {name}{tag}")
    print(f"       -> {url}")
    print(f"       -> saved: {file.name}\n")

print(f"\n[QR Generator] Done! Print the PNGs from: {OUT}")
print("[QR Generator] Place each QR code at the matching location on the floor.\n")
