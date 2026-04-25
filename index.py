import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import logging
import sys

logging.basicConfig(
    format='[%(asctime)s] [%(name)-18s] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO,
)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

class _IndelphiSilencer:
    """Swallow inDelphi's 'Initializing model...' / 'Done' stdout noise."""
    def __init__(self, real): self._real = real
    def write(self, s):
        if not (s.startswith('Initializing model ') or s.strip() == 'Done'):
            self._real.write(s)
    def flush(self): self._real.flush()
    def __getattr__(self, name): return getattr(self._real, name)

sys.stdout = _IndelphiSilencer(sys.stdout)

import altair as alt
alt.data_transformers.disable_max_rows()

from app import app
from layouts.common import setup_layout

import callbacks.navigation
import callbacks.integration
import callbacks.editing
import callbacks.tagging_custom
import callbacks.tagging_intron
import callbacks.xenopus_browser
import callbacks.precalculated

# Register all callbacks
callbacks.navigation.register_callbacks(app)
callbacks.integration.register_callbacks(app)
callbacks.editing.register_callbacks(app)
callbacks.tagging_custom.register_callbacks(app)
callbacks.tagging_intron.register_callbacks(app)
callbacks.xenopus_browser.register_callbacks(app)
callbacks.precalculated.register_callbacks(app)

# Set up main layout (must happen after imports so page layouts are available)
setup_layout(app)

if __name__ == "__main__":
    import os
    print("\n" + "=" * 80)
    print("FLASK APP STARTING")
    print(f"Current working directory: {os.getcwd()}")
    print(f"DB folder exists: {os.path.exists('db')}")
    if os.path.exists('db'):
        db_files = [f for f in os.listdir('db') if f.endswith('.db')]
        print(f"DB files found: {len(db_files)}")
        print("Database files in db/ folder:")
        for f in db_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(db_files) > 10:
            print(f"  ... and {len(db_files) - 10} more")
    print("=" * 80 + "\n")
    app.run(host='0.0.0.0', debug=False)
