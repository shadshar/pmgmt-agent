"""
APT package manager implementation.
"""

import subprocess
import logging
import distro
from typing import Dict, List, Any

from .base import PackageManager

logger = logging.getLogger(__name__)


class AptPackageManager(PackageManager):
    """
    Implementation of the APT package manager for Debian-based distributions.
    """
    
    def get_distribution_info(self) -> Dict[str, str]:
        """
        Get information about the current Debian-based distribution.
        
        Returns:
            Dict[str, str]: A dictionary containing distribution information.
        """
        return {
            "id": distro.id(),
            "version": distro.version(),
            "codename": distro.codename(),
            "name": distro.name(),
            "package_manager": "apt"
        }
    
    def get_available_updates(self) -> List[Dict[str, Any]]:
        """
        Get a list of available package updates using APT.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing information
                                 about an available package update.
        """
        logger.info("Checking for available updates with APT")
        
        try:
            # Get list of upgradable packages
            cmd = ["apt", "list", "--upgradable"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the output
            updates = []
            lines = result.stdout.strip().split('\n')
            
            # Skip the first line (header)
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                try:
                    # Format is typically: package/source,now version arch [upgradable from: old-version]
                    parts = line.split()
                    if len(parts) < 4:
                        continue
                    
                    package_info = parts[0].split('/')
                    package_name = package_info[0]
                    
                    # Extract version
                    version_info = line.split('[upgradable from: ')[1].rstrip(']')
                    new_version = parts[1]
                    
                    # Get additional package information
                    pkg_info = self._get_package_details(package_name)
                    
                    update_info = {
                        "name": package_name,
                        "version": new_version,
                        "current_version": version_info,
                        "architecture": parts[2] if len(parts) > 2 else "",
                        "is_security_update": self._is_security_update(package_name),
                    }
                    
                    # Add additional package details if available
                    if pkg_info:
                        update_info.update(pkg_info)
                    
                    updates.append(update_info)
                    
                except (IndexError, ValueError) as e:
                    logger.warning(f"Failed to parse package line: {line}. Error: {e}")
            
            return updates
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running APT command: {e}")
            return []
    
    def _get_package_details(self, package_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific package.
        
        Args:
            package_name (str): The name of the package.
            
        Returns:
            Dict[str, Any]: A dictionary containing package details.
        """
        try:
            cmd = ["apt-cache", "show", package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            details = {}
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if not line or ': ' not in line:
                    continue
                
                key, value = line.split(': ', 1)
                key = key.lower().replace('-', '_')
                
                if key == "size":
                    try:
                        details["size_bytes"] = int(value)
                    except ValueError:
                        details["size"] = value
                elif key == "homepage":
                    details["website"] = value
                elif key in ["maintainer", "section", "priority", "description"]:
                    details[key] = value
            
            return details
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Error getting details for package {package_name}: {e}")
            return {}
    
    def _is_security_update(self, package_name: str) -> bool:
        """
        Determine if a package update is a security update.
        
        Args:
            package_name (str): The name of the package.
            
        Returns:
            bool: True if the update is a security update, False otherwise.
        """
        try:
            # Check if the package is from a security repository
            cmd = ["apt-cache", "policy", package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return "security" in result.stdout.lower()
            
        except subprocess.CalledProcessError:
            return False