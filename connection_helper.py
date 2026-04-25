#!/usr/bin/env python3
"""
Helper module for optimized SQLite connections.

Add this to your Flask app to ensure optimal performance settings
are applied to every database connection.

Usage:
    from connection_helper import get_optimized_connection

    conn = get_optimized_connection('path/to/database.db')
    # Use conn as normal

Performance Profiles:
    - 'high': 512MB cache, 1GB mmap (default, best for systems with 16GB+ RAM)
    - 'medium': 256MB cache, 512MB mmap (good for 8-16GB RAM)
    - 'low': 128MB cache, 256MB mmap (for systems with limited RAM or many users)

Trade-offs:
    - Higher settings = faster queries but more RAM usage per connection
    - For single user/few users: use 'high' profile
    - For many concurrent users (10+): use 'medium' or 'low' profile
"""

import sqlite3

# Performance profiles (cache_mb, mmap_mb)
PROFILES = {
    'high': (512, 1024),    # 512MB cache, 1GB mmap
    'medium': (256, 512),   # 256MB cache, 512MB mmap
    'low': (128, 256),      # 128MB cache, 256MB mmap
}


def get_optimized_connection(db_path, timeout=30.0, profile='high'):
    """
    Create an optimized SQLite connection with performance settings.

    Args:
        db_path: Path to the SQLite database file
        timeout: Database lock timeout in seconds (default: 30.0)
        profile: Performance profile - 'high', 'medium', or 'low' (default: 'high')

    Returns:
        sqlite3.Connection object with optimized settings

    RAM Usage per connection:
        - high: ~512-1536MB per connection
        - medium: ~256-768MB per connection
        - low: ~128-384MB per connection
    """
    conn = sqlite3.connect(db_path, timeout=timeout)

    # Get profile settings
    if profile not in PROFILES:
        profile = 'high'  # fallback to high if invalid
    cache_mb, mmap_mb = PROFILES[profile]

    # Apply performance optimizations
    # These settings are session-specific and must be set for each connection

    # Set cache size (negative value means KB)
    conn.execute(f"PRAGMA cache_size = -{cache_mb * 1024};")

    # Enable memory-mapped I/O
    # Allows SQLite to map the database file into memory for faster access
    conn.execute(f"PRAGMA mmap_size = {mmap_mb * 1024 * 1024};")

    # Use memory for temporary tables and indices
    conn.execute("PRAGMA temp_store = MEMORY;")

    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode = WAL;")

    # Set synchronous to NORMAL (good balance of safety and speed)
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn


def optimize_connection(conn, profile='high'):
    """
    Apply performance optimizations to an existing connection.

    Args:
        conn: An existing sqlite3.Connection object
        profile: Performance profile - 'high', 'medium', or 'low' (default: 'high')

    Returns:
        The same connection with optimizations applied
    """
    # Get profile settings
    if profile not in PROFILES:
        profile = 'high'
    cache_mb, mmap_mb = PROFILES[profile]

    conn.execute(f"PRAGMA cache_size = -{cache_mb * 1024};")
    conn.execute(f"PRAGMA mmap_size = {mmap_mb * 1024 * 1024};")
    conn.execute("PRAGMA temp_store = MEMORY;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python connection_helper.py <database_path>")
        print("\nThis will test the optimized connection.")
        sys.exit(1)

    db_path = sys.argv[1]

    print(f"Testing optimized connection to {db_path}...")
    conn = get_optimized_connection(db_path)

    cur = conn.cursor()

    # Show applied settings
    print("\nApplied settings:")
    cur.execute("PRAGMA cache_size;")
    cache = cur.fetchone()[0]
    print(f"  cache_size: {cache} ({abs(cache)/1024:.0f}MB)" if cache < 0 else f"  cache_size: {cache}")

    cur.execute("PRAGMA mmap_size;")
    mmap = cur.fetchone()[0]
    print(f"  mmap_size: {mmap} ({mmap/1024/1024:.0f}MB)")

    cur.execute("PRAGMA temp_store;")
    temp = cur.fetchone()[0]
    temp_names = {0: "DEFAULT", 1: "FILE", 2: "MEMORY"}
    print(f"  temp_store: {temp} ({temp_names.get(temp, 'UNKNOWN')})")

    cur.execute("PRAGMA journal_mode;")
    print(f"  journal_mode: {cur.fetchone()[0]}")

    cur.execute("PRAGMA synchronous;")
    sync = cur.fetchone()[0]
    sync_names = {0: "OFF", 1: "NORMAL", 2: "FULL", 3: "EXTRA"}
    print(f"  synchronous: {sync} ({sync_names.get(sync, 'UNKNOWN')})")

    conn.close()
    print("\nConnection test successful!")
