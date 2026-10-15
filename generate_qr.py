import os
import sys
import json
from pathlib import Path
import qrcode
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).parent
OUT = BASE / "qr_codes"
OUT.mkdir(exist_ok=True)

# Default to the persistent ngrok domain provided by the user
DEFAULT_DOMAIN = "https://fanciness-celibate-send.ngrok-free.dev"

if len(sys.argv) > 1:
    base_url = sys.argv[1].rstrip("/")
else:
    base_url = DEFAULT_DOMAIN

try:
    with open(BASE / "data" / "floor_graph.json", "r", encoding="utf-8") as f:
        graph = json.load(f)
except FileNotFoundError:
    print("[ERROR] floor_graph.json not found in data/ folder!")
    sys.exit(1)

nodes = graph.get("nodes", {})
exits = set(graph.get("exit_nodes", []))

print("=" * 65)
print("  EDGE-DRIVEN EVACUATION SYSTEM - QR CODE GENERATOR")
print(f"  Target HTTPS Domain: {base_url}")
print(f"  Total Graph Locations: {len(nodes)}")
print("=" * 65)

# Try loading standard font or fallback to default
try:
    font_title = ImageFont.truetype("arialbd.ttf", 20)
    font_node = ImageFont.truetype("arialbd.ttf", 26)
    font_url = ImageFont.truetype("arial.ttf", 13)
    font_inst = ImageFont.truetype("ariali.ttf", 14)
except Exception:
    font_title = font_node = font_url = font_inst = ImageFont.load_default()

for name in nodes:
    # Use clean query parameter format & locate route support
    url = f"{base_url}/locate/{name}"
    
    # 1. Generate Raw QR Code
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    # 2. Generate Professional Wall-Mount Emergency Marker Card
    card_w = 460
    card_h = 560
    card = Image.new("RGB", (card_w, card_h), "white")
    draw = ImageDraw.Draw(card)
    
    # Red Emergency Header Bar
    is_exit = name in exits
    hdr_color = (190, 20, 20) if not is_exit else (20, 140, 40)
    draw.rectangle([(0, 0), (card_w, 65)], fill=hdr_color)
    
    hdr_text = "EMERGENCY EVACUATION MAP" if not is_exit else "DESIGNATED EMERGENCY EXIT"
    draw.text((card_w / 2, 32), hdr_text, fill="white", font=font_title, anchor="mm")
    
    # Outer Border
    draw.rectangle([(2, 2), (card_w - 3, card_h - 3)], outline=hdr_color, width=4)
    
    # Room Display Name
    display_name = name.replace("_", " ").upper()
    draw.text((card_w / 2, 100), display_name, fill="black", font=font_node, anchor="mm")
    
    # Instructions
    draw.text((card_w / 2, 132), "Scan with Smartphone Camera to Auto-Localize", fill=(80, 80, 80), font=font_inst, anchor="mm")
    
    # Paste QR Code in center
    qw, qh = qr_img.size
    # Resize QR to fit nicely inside card
    target_qr_size = 320
    qr_resized = qr_img.resize((target_qr_size, target_qr_size), Image.Resampling.LANCZOS)
    card.paste(qr_resized, ((card_w - target_qr_size) // 2, 155))
    
    # Print Destination URL below QR
    draw.text((card_w / 2, 495), url, fill=(30, 70, 180), font=font_url, anchor="mm")
    draw.text((card_w / 2, 525), "Zero-Install Offline PWA Guided Turn-by-Turn Egress", fill=(100, 100, 100), font=font_url, anchor="mm")
    
    card_path = OUT / f"{name}_card.png"
    card.save(card_path)

    tag = " [EXIT]" if is_exit else ""
    print(f"  [OK] {name:<26} -> {url}")

print("=" * 65)
print(f"[SUCCESS] Generated {len(nodes)} QR codes & wall markers in: {OUT.resolve()}")
print("Scan from any smartphone to test deep-linking into your ngrok server!")
print("=" * 65)
