"""Docvert module initialization."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("docvert")
except PackageNotFoundError:
    __version__ = "unknown"
