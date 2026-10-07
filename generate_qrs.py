import json
import os
import urllib.parse
import subprocess
import sys

# Ensure qrcode is installed
try:
    import qrcode
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode[pil]"])
    import qrcode

def generate_qr_codes(map_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(map_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    nodes = list(data.get("nodes", {}).keys())
    
    # Base URL for the app (using localhost for local dev, or ngrok URL for production)
    # The app can read a URL parameter like ?loc=Library
    base_url = "http://localhost:5000/?loc="
    
    print(f"Generating QR Codes for {map_file}...")
    for node in nodes:
        url = base_url + urllib.parse.quote(node)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        filename = f"{node}_QR.png"
        filepath = os.path.join(output_dir, filename)
        img.save(filepath)
        print(f" - Created {filename}")

if __name__ == "__main__":
    generate_qr_codes('data/map_office.json', 'qr_codes/office_qrs')
    generate_qr_codes('data/map_hospital.json', 'qr_codes/hospital_qrs')
    # If the original map exists
    if os.path.exists('data/map_college.json'):
        generate_qr_codes('data/map_college.json', 'qr_codes/college_qrs')
    elif os.path.exists('map_layout.json'):
        generate_qr_codes('map_layout.json', 'qr_codes/current_map_qrs')
        
    print("\nAll QR codes generated successfully!")
