"""limblab-cli package (thin wrapper)

This package is intentionally small; the actual CLI implementation lives in
the limblab (core) package. The console script entry point is configured
in pyproject.toml to point at limblab.main:app, which is provided by
limblab-core.
"""

__all__ = []
