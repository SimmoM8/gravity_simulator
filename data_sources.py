from presets import get_preset_names

DATA_SOURCES = {
    "preset_objects": get_preset_names,
    # Add future dynamic data sources here as needed
}

def get_options(source_key):
    """Return options list from the registered data source callable by key."""
    source_func = DATA_SOURCES.get(source_key)
    if callable(source_func):
        return source_func()
    return []