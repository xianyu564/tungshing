"""Version information for TungShing."""

__version__ = "0.1.1"
__version_info__ = tuple(map(int, __version__.split(".")))

# For compatibility with importlib.metadata
def get_version() -> str:
    """Get the version string."""
    return __version__