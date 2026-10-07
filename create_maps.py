import json
import os

data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

# Map 1: Office Layout
office_layout = {
    "width": 1000,
    "height": 600,
    "nodes": {
        "Reception": [100, 300],
        "Hallway_West": [300, 300],
        "Hallway_Center": [500, 300],
        "Hallway_East": [700, 300],
        "Meeting_Room": [500, 100],
        "Cafeteria": [500, 500],
        "Cubicles_A": [300, 100],
        "Cubicles_B": [700, 100],
        "Front_Door_Exit": [50, 300],
        "Fire_Escape_North": [500, 50],
        "Fire_Escape_East": [900, 300]
    },
    "edges": [
        ["Reception", "Hallway_West", 20],
        ["Hallway_West", "Hallway_Center", 20],
        ["Hallway_Center", "Hallway_East", 20],
        ["Hallway_Center", "Meeting_Room", 20],
        ["Hallway_Center", "Cafeteria", 20],
        ["Hallway_West", "Cubicles_A", 20],
        ["Hallway_East", "Cubicles_B", 20],
        ["Reception", "Front_Door_Exit", 5],
        ["Meeting_Room", "Fire_Escape_North", 5],
        ["Hallway_East", "Fire_Escape_East", 20]
    ],
    "exit_nodes": ["Front_Door_Exit", "Fire_Escape_North", "Fire_Escape_East"],
    "camera_exit": "Front_Door_Exit",
    "corridors": [
        {"x": 100, "y": 270, "w": 600, "h": 60}
    ],
    "room_rects": {
        "Reception": {"x": 50, "y": 250, "w": 100, "h": 100, "label": "Reception", "icon": "🏢"},
        "Meeting_Room": {"x": 420, "y": 50, "w": 160, "h": 100, "label": "Meeting Rm", "icon": "💼"},
        "Cafeteria": {"x": 420, "y": 450, "w": 160, "h": 120, "label": "Cafeteria", "icon": "☕"},
        "Cubicles_A": {"x": 220, "y": 50, "w": 160, "h": 120, "label": "Dev Team", "icon": "💻"},
        "Cubicles_B": {"x": 620, "y": 50, "w": 160, "h": 120, "label": "Sales Team", "icon": "📈"}
    }
}

# Map 2: Hospital Layout
hospital_layout = {
    "width": 800,
    "height": 800,
    "nodes": {
        "Lobby": [400, 700],
        "Elevator_Bank": [400, 500],
        "ICU_Wing": [200, 500],
        "Maternity_Wing": [600, 500],
        "Surgery_Ward": [400, 300],
        "Pharmacy": [200, 700],
        "Main_Entrance": [400, 780],
        "Emergency_Exit_West": [50, 500],
        "Emergency_Exit_North": [400, 100]
    },
    "edges": [
        ["Lobby", "Elevator_Bank", 20],
        ["Lobby", "Pharmacy", 20],
        ["Elevator_Bank", "ICU_Wing", 20],
        ["Elevator_Bank", "Maternity_Wing", 20],
        ["Elevator_Bank", "Surgery_Ward", 20],
        ["Lobby", "Main_Entrance", 8],
        ["ICU_Wing", "Emergency_Exit_West", 15],
        ["Surgery_Ward", "Emergency_Exit_North", 20]
    ],
    "exit_nodes": ["Main_Entrance", "Emergency_Exit_West", "Emergency_Exit_North"],
    "camera_exit": "Main_Entrance",
    "corridors": [
        {"x": 370, "y": 300, "w": 60, "h": 400},
        {"x": 200, "y": 470, "w": 400, "h": 60}
    ],
    "room_rects": {
        "Lobby": {"x": 320, "y": 650, "w": 160, "h": 100, "label": "Lobby", "icon": "🏥"},
        "Pharmacy": {"x": 100, "y": 650, "w": 140, "h": 100, "label": "Pharmacy", "icon": "💊"},
        "ICU_Wing": {"x": 100, "y": 420, "w": 140, "h": 140, "label": "ICU", "icon": "❤️"},
        "Maternity_Wing": {"x": 550, "y": 420, "w": 140, "h": 140, "label": "Maternity", "icon": "👶"},
        "Surgery_Ward": {"x": 320, "y": 150, "w": 160, "h": 140, "label": "Surgery", "icon": "⚕️"}
    }
}

with open(os.path.join(data_dir, 'map_office.json'), 'w', encoding='utf-8') as f:
    json.dump(office_layout, f, indent=2)

with open(os.path.join(data_dir, 'map_hospital.json'), 'w', encoding='utf-8') as f:
    json.dump(hospital_layout, f, indent=2)

print("Created map_office.json and map_hospital.json in data/ folder.")
