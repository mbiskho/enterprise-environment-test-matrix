import os

import psycopg

from conftest import need

SUPPORTED_MAJORS = {14, 15, 16, 17}


def connect():
    return psycopg.connect(need("DATABASE_URL"), connect_timeout=5)


def test_database_reachable_and_supported_version():
    with connect() as conn:
        major = conn.info.server_version // 10000
    assert major in SUPPORTED_MAJORS, f"Postgres {major} is not supported ({sorted(SUPPORTED_MAJORS)})"
    if expected := os.environ.get("EXPECTED_PG_MAJOR"):
        assert major == int(expected), "matrix and environment disagree about the Postgres version"


def test_required_extensions_installable():
    with connect() as conn:
        available = {r[0] for r in conn.execute("SELECT name FROM pg_available_extensions")}
    missing = {"pgcrypto", "pg_trgm"} - available
    assert not missing, f"customer DB lacks extensions {missing}; ask their DBA to install the contrib package"


def test_can_create_and_drop_schema():
    # Customers often give a role without CREATE; find out before the migration does.
    with connect() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS compat_probe")
        conn.execute("DROP SCHEMA compat_probe")
