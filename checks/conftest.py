import os

import pytest


def need(var: str) -> str:
    """Skip (not fail) when the environment doesn't have this component."""
    value = os.environ.get(var)
    if not value:
        pytest.skip(f"{var} not set: not part of this environment")
    return value
