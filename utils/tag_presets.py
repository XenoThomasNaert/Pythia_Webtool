import json
import os


def load_tag_presets():
    """Load tag presets from JSON file"""
    # tag_presets.json is in the project root (parent of utils/)
    preset_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tag_presets.json')
    try:
        with open(preset_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default structure if file doesn't exist
        return {"presets": [], "linkers": [], "tags": []}


# Load presets at startup
TAG_PRESETS = load_tag_presets()
