"""Version management for VICORE web application."""

import importlib.metadata
from typing import Final

from loguru import logger


def get_version() -> str:
    """
    Get the package version from installed metadata.

    Returns:
        str: The version string, or 'dev' if running in development mode
             where the package is not installed.
    """
    try:
        return importlib.metadata.version("eurotunnel_web")
    except importlib.metadata.PackageNotFoundError:
        # Running in development container where poetry hasn't installed the package
        # In production container, this works fine
        logger.debug("Package not installed, using 'dev' version")
        return "dev"
    except Exception as e:
        # Catch any other unexpected errors
        logger.warning(f"Could not determine version: {e}")
        return "unknown"


VERSION: Final[str] = get_version()
