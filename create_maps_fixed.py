import json
import os

data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

# 1. Office Layout
office_layout = {
    "width": 1000,
    "height": 600,
    "nodes": {
        "Reception": [100, 300],
        "Hallway_West": [300, 300],
        "Hallway_Center": [500, 300],
        "Hallway_East": [700, 300],
        "Meeting_Room": [300, 150],
        "Cafeteria": [500, 150],
        "Cubicles_A": [300, 450],
        "Cubicles_B": [500, 450],
        "Front_Door_Exit": [50, 300],
        "Fire_Escape_North": [500, 50],
        "Fire_Escape_East": [900, 300]
    },
    "edges": [
        ["Reception", "Front_Door_Exit", 50],
        ["Reception", "Hallway_West", 200],
        ["Hallway_West", "Hallway_Center", 200],
        ["Hallway_Center", "Hallway_East", 200],
        ["Hallway_West", "Meeting_Room", 150],
        ["Hallway_West", "Cubicles_A", 150],
        ["Hallway_Center", "Cafeteria", 150],
        ["Hallway_Center", "Cubicles_B", 150],
        ["Cafeteria", "Fire_Escape_North", 100],
        ["Hallway_East", "Fire_Escape_East", 200]
    ],
    "exit_nodes": [
        "Front_Door_Exit",
        "Fire_Escape_North",
        "Fire_Escape_East"
    ],
    "corridors": [
        {"x": 100, "y": 280, "w": 640, "h": 40},
        {"x": 280, "y": 150, "w": 40, "h": 300},
        {"x": 480, "y": 150, "w": 40, "h": 300}
    ],
    "rooms": {
        "Reception": {"x": 50, "y": 250, "w": 100, "h": 100, "label": "Reception", "icon": "🏢"},
        "Meeting_Room": {"x": 220, "y": 50, "w": 160, "h": 100, "label": "Meeting Room", "icon": "👥"},
        "Cafeteria": {"x": 420, "y": 50, "w": 160, "h": 100, "label": "Cafeteria", "icon": "☕"},
        "Cubicles_A": {"x": 220, "y": 450, "w": 160, "h": 120, "label": "Dev Team", "icon": "💻"},
        "Cubicles_B": {"x": 420, "y": 450, "w": 160, "h": 120, "label": "Sales Team", "icon": "📞"},
        "Front_Door_Exit": {"x": 10, "y": 280, "w": 40, "h": 40, "label": "Main Exit", "icon": "🚪"},
        "Fire_Escape_North": {"x": 480, "y": 10, "w": 40, "h": 40, "label": "Fire Escape", "icon": "🚨"},
        "Fire_Escape_East": {"x": 740, "y": 280, "w": 40, "h": 40, "label": "East Exit", "icon": "🚨"}
    }
}

# 2. Hospital Layout
hospital_layout = {
    "width": 1200,
    "height": 700,
    "nodes": {
        "Lobby": [150, 350],
        "Elevator_Bank": [400, 350],
        "ICU_Wing": [400, 150],
        "Maternity_Wing": [650, 500],
        "Surgery_Ward": [400, 550],
        "Pharmacy": [650, 200],
        "Main_Entrance": [50, 350],
        "Emergency_Exit_West": [400, 50],
        "Emergency_Exit_North": [850, 350]
    },
    "edges": [
        ["Main_Entrance", "Lobby", 100],
        ["Lobby", "Elevator_Bank", 250],
        ["Elevator_Bank", "ICU_Wing", 200],
        ["Elevator_Bank", "Surgery_Ward", 200],
        ["Elevator_Bank", "Emergency_Exit_North", 450],
        ["ICU_Wing", "Pharmacy", 250],
        ["ICU_Wing", "Emergency_Exit_West", 100],
        ["Surgery_Ward", "Maternity_Wing", 250]
    ],
    "exit_nodes": [
        "Main_Entrance",
        "Emergency_Exit_West",
        "Emergency_Exit_North"
    ],
    "corridors": [
        {"x": 100, "y": 330, "w": 750, "h": 40},
        {"x": 380, "y": 150, "w": 40, "h": 400},
        {"x": 400, "y": 200, "w": 250, "h": 40},
        {"x": 400, "y": 500, "w": 250, "h": 40}
    ],
    "rooms": {
        "Lobby": {"x": 100, "y": 300, "w": 100, "h": 100, "label": "Lobby", "icon": "🏥"},
        "ICU_Wing": {"x": 320, "y": 150, "w": 160, "h": 100, "label": "ICU", "icon": "❤️"},
        "Pharmacy": {"x": 600, "y": 150, "w": 140, "h": 100, "label": "Pharmacy", "icon": "💊"},
        "Maternity_Wing": {"x": 550, "y": 420, "w": 140, "h": 140, "label": "Maternity", "icon": "👶"},
        "Surgery_Ward": {"x": 320, "y": 550, "w": 160, "h": 140, "label": "Surgery", "icon": "🔪"},
        "Main_Entrance": {"x": 10, "y": 330, "w": 40, "h": 40, "label": "Entrance", "icon": "🚪"},
        "Emergency_Exit_West": {"x": 380, "y": 10, "w": 40, "h": 40, "label": "West Exit", "icon": "🚨"},
        "Emergency_Exit_North": {"x": 850, "y": 330, "w": 40, "h": 40, "label": "North Exit", "icon": "🚨"}
    }
}

with open(os.path.join(data_dir, 'map_office.json'), 'w', encoding='utf-8') as f:
    json.dump(office_layout, f, indent=2)

with open(os.path.join(data_dir, 'map_hospital.json'), 'w', encoding='utf-8') as f:
    json.dump(hospital_layout, f, indent=2)
    
# Automatically create the fixed map_layout.json if it exists so the user doesn't have to rename again
import shutil
shutil.copyfile(os.path.join(data_dir, 'map_office.json'), os.path.join(data_dir, 'map_layout.json'))

print("Generated corrected maps with edges and exit_nodes.")
