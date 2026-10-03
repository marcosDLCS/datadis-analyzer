"""DATADIS Analyzer package.

A modular CLI tool to parse, validate, and analyze residential building energy
consumption data exported from Spain's DATADIS platform.
"""


def __getattr__(name: str) -> str:
    if name == "__version__":
        from src.version import get_version

        return get_version()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["__version__"]
