import dash
import dash_bootstrap_components as dbc
import os

# ============================================================================
# DATABASE CONNECTION CONFIGURATION
# ============================================================================
# Toggle between development (direct connections) and production (pooling)
USE_CONNECTION_POOL = False  # Set to True for production/hosting

# Performance profile: 'high', 'medium', or 'low'
# - high: 512MB cache, best for single user (dev mode)
# - medium: 256MB cache, good for 10-50 users (production)
# - low: 128MB cache, for 50+ users or limited RAM
PERFORMANCE_PROFILE = 'high'  # Change to 'medium' for production

# Connection pool settings (only used if USE_CONNECTION_POOL = True)
POOL_SIZE = 5  # Number of connections in pool
# ============================================================================

# ============================================================================
# TRANSCRIPT SEQUENCES DATABASE CONFIGURATION
# ============================================================================
# Base directory for transcript sequence databases
TRANSCRIPT_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcript_sequences")

# ============================================================================
# DASH APP INSTANCE
# ============================================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
                update_title="Calculating...")

from flask_compress import Compress
Compress(app.server)

app.title = "Pythia"
