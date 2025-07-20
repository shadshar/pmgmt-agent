"""
Package manager detection and implementation.
"""

import distro
import logging
from typing import Optional

from .base import PackageManager
from .apt import AptPackageManager
from .dnf import DnfPackageManager

logger = logging.getLogger(__name__)

def get_package_manager() -> Optional[PackageManager]:
    """
    Detect the current Linux distribution and return the appropriate package manager.
    
    Returns:
        PackageManager: An instance of the appropriate package manager class.
        None: If no supported package manager is found.
    """
    distribution = distro.id().lower()
    logger.info(f"Detected Linux distribution: {distribution}")
    
    if distribution in ["ubuntu", "debian"]:
        logger.info("Using APT package manager")
        return AptPackageManager()
    elif distribution in ["fedora"]:
        logger.info("Using DNF package manager")
        return DnfPackageManager()
    else:
        logger.error(f"Unsupported Linux distribution: {distribution}")
        return None