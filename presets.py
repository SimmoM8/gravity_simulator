# presets.py
PRESET_OBJECTS = {
    "Earth": {
        "name": "Earth",
        "mass": 5.972e24,
        "radius": 6371e3,
        "color": (0, 100, 255)
    },
    "Moon": {
        "name": "Moon",
        "mass": 7.342e22,
        "radius": 1737e3,
        "color": (150, 150, 150)
    },
    "Sun": {
        "name": "Sun",
        "mass": 1.989e30,
        "radius": 696340e3,
        "color": (255, 204, 0)
    }
}

def get_preset_names():
    return list(PRESET_OBJECTS.keys())