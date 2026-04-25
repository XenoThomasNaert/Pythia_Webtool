#!/usr/bin/env python3
"""
Connection pool for SQLite with optimized settings.

Use this for production web hosting with many concurrent users.
Instead of creating a new connection per request, reuse connections from a pool.

Usage:
    from connection_pool import ConnectionPool

    # Create pool once at app startup
    pool = ConnectionPool('db/database.db', pool_size=5, profile='medium')

    # In your request handler
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM table")
        results = cursor.fetchall()
    # Connection automatically returned to pool
"""

import sqlite3
import threading
from queue import Queue, Empty
from contextlib import contextmanager
from connection_helper import get_optimized_connection


class ConnectionPool:
    """
    Thread-safe connection pool for SQLite databases.

    Manages a pool of optimized connections that can be reused across requests.
    """

    def __init__(self, db_path, pool_size=5, profile='medium', timeout=30.0):
        """
        Create a connection pool.

        Args:
            db_path: Path to SQLite database
            pool_size: Number of connections in pool (default: 5)
            profile: Performance profile - 'high', 'medium', or 'low' (default: 'medium')
            timeout: Database lock timeout in seconds

        Recommended pool sizes:
            - Small site (10-50 users): 3-5 connections, medium profile
            - Medium site (50-200 users): 5-10 connections, medium profile
            - Large site (200+ users): 10-20 connections, low profile

        RAM Usage:
            - 5 connections × medium profile = 1.3-3.8GB
            - 10 connections × medium profile = 2.6-7.6GB
            - 5 connections × low profile = 0.6-1.9GB
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.profile = profile
        self.timeout = timeout

        # Thread-safe queue to hold available connections
        self._pool = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._closed = False

        # Create initial pool of connections
        for _ in range(pool_size):
            conn = get_optimized_connection(db_path, timeout=timeout, profile=profile)
            self._pool.put(conn)

        print(f"[ConnectionPool] Created pool with {pool_size} connections (profile={profile})")
        print(f"[ConnectionPool] Estimated RAM usage: {self._estimate_ram_usage()}")

    def _estimate_ram_usage(self):
        """Estimate RAM usage for the pool."""
        ram_per_conn = {
            'high': (512, 1536),
            'medium': (256, 768),
            'low': (128, 384)
        }
        min_ram, max_ram = ram_per_conn.get(self.profile, (256, 768))
        min_total = min_ram * self.pool_size
        max_total = max_ram * self.pool_size
        return f"{min_total}-{max_total}MB ({min_total/1024:.1f}-{max_total/1024:.1f}GB)"

    @contextmanager
    def get_connection(self, block=True, timeout=5.0):
        """
        Get a connection from the pool (context manager).

        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")

        Args:
            block: Wait for connection if pool is empty (default: True)
            timeout: Max seconds to wait for connection (default: 5.0)

        Raises:
            Empty: If no connection available and block=False or timeout exceeded
            RuntimeError: If pool is closed
        """
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        try:
            # Get connection from pool
            conn = self._pool.get(block=block, timeout=timeout)
            yield conn
        finally:
            # Return connection to pool
            if not self._closed:
                self._pool.put(conn)

    def close(self):
        """Close all connections in the pool."""
        with self._lock:
            if self._closed:
                return

            self._closed = True

            # Close all connections
            closed_count = 0
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                    closed_count += 1
                except Empty:
                    break

            print(f"[ConnectionPool] Closed {closed_count} connections")

    def __enter__(self):
        """Support 'with' statement for pool lifetime."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto-close pool when exiting 'with' block."""
        self.close()

    def __del__(self):
        """Cleanup on garbage collection."""
        if not self._closed:
            self.close()


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python connection_pool.py <database_path>")
        print("\nThis will test the connection pool.")
        sys.exit(1)

    db_path = sys.argv[1]

    print(f"Testing connection pool with {db_path}...\n")

    # Create pool with 5 connections, medium profile
    with ConnectionPool(db_path, pool_size=5, profile='medium') as pool:
        print("\nTesting connection checkout/return:")

        # Test getting multiple connections
        for i in range(3):
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master")
                count = cursor.fetchone()[0]
                print(f"  Connection {i+1}: Found {count} objects in database")

        print("\nPool test successful!")
        print("All connections returned to pool and can be reused.")
