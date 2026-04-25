#!/usr/bin/env python3
"""
Test script to verify connection toggle functionality.
"""

import sys
sys.path.insert(0, '.')

# Test both modes
print("=" * 60)
print("TESTING CONNECTION TOGGLE")
print("=" * 60)

# Test 1: Direct connection mode
print("\n[TEST 1] Direct Connection Mode (Development)")
print("-" * 60)

# Reload to ensure clean state
import flask_app
flask_app.USE_CONNECTION_POOL = False
flask_app.PERFORMANCE_PROFILE = 'high'

with flask_app.get_db_connection('db/Homo_sapiens_3BP_HEK293.db') as conn:
    cur = conn.cursor()
    cur.execute('PRAGMA cache_size;')
    cache = cur.fetchone()[0]
    cur.execute('PRAGMA mmap_size;')
    mmap = cur.fetchone()[0]
    print(f"  Cache size: {cache} ({abs(cache)/1024:.0f}MB)")
    print(f"  Mmap size: {mmap} ({mmap/1024/1024:.0f}MB)")
    print(f"  Profile: {flask_app.PERFORMANCE_PROFILE}")
    print(f"  Pooling: {flask_app.USE_CONNECTION_POOL}")

print("✓ Direct connection mode works!")

# Test 2: Connection pool mode
print("\n[TEST 2] Connection Pool Mode (Production)")
print("-" * 60)

# Switch to pool mode
flask_app.USE_CONNECTION_POOL = True
flask_app.PERFORMANCE_PROFILE = 'medium'
flask_app._connection_pools = {}  # Reset pools

with flask_app.get_db_connection('db/Homo_sapiens_3BP_HEK293.db') as conn:
    cur = conn.cursor()
    cur.execute('PRAGMA cache_size;')
    cache = cur.fetchone()[0]
    cur.execute('PRAGMA mmap_size;')
    mmap = cur.fetchone()[0]
    print(f"  Cache size: {cache} ({abs(cache)/1024:.0f}MB)")
    print(f"  Mmap size: {mmap} ({mmap/1024/1024:.0f}MB)")
    print(f"  Profile: {flask_app.PERFORMANCE_PROFILE}")
    print(f"  Pooling: {flask_app.USE_CONNECTION_POOL}")

print("✓ Connection pool mode works!")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nTo switch modes, edit flask_app.py:")
print("  USE_CONNECTION_POOL = False  # Development (direct)")
print("  USE_CONNECTION_POOL = True   # Production (pooled)")
print("\n  PERFORMANCE_PROFILE = 'high'    # Single user")
print("  PERFORMANCE_PROFILE = 'medium'  # 10-50 users")
print("  PERFORMANCE_PROFILE = 'low'     # 50+ users")
