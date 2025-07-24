from presets import get_preset_names

DATA_SOURCES = {
    "preset_objects": get_preset_names,
    # Add future dynamic data sources here as needed
}

def get_options(source_key):
    func = DATA_SOURCES.get(source_key)
    if callable(func):
        result = func()
        return result
    return []