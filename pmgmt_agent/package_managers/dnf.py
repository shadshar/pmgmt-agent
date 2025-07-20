"""
DNF package manager implementation.
"""

import subprocess
import logging
import distro
import json
from typing import Dict, List, Any

from .base import PackageManager

logger = logging.getLogger(__name__)


class DnfPackageManager(PackageManager):
    """
    Implementation of the DNF package manager for Fedora-based distributions.
    """
    
    def get_distribution_info(self) -> Dict[str, str]:
        """
        Get information about the current Fedora-based distribution.
        
        Returns:
            Dict[str, str]: A dictionary containing distribution information.
        """
        return {
            "id": distro.id(),
            "version": distro.version(),
            "codename": distro.codename(),
            "name": distro.name(),
            "package_manager": "dnf"
        }
    
    def get_available_updates(self) -> List[Dict[str, Any]]:
        """
        Get a list of available package updates using DNF.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing information
                                 about an available package update.
        """
        logger.info("Checking for available updates with DNF")
        
        try:
            # Use DNF's JSON output for easier parsing
            cmd = ["dnf", "check-update", "--refresh", "--assumeno", "--quiet", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # DNF returns exit code 100 when updates are available
            if result.returncode not in [0, 100]:
                logger.error(f"DNF command failed with exit code {result.returncode}")
                return []
            
            try:
                # Parse JSON output
                data = json.loads(result.stdout)
                updates = []
                
                for pkg in data.get("updates", []):
                    update_info = {
                        "name": pkg.get("name", ""),
                        "version": pkg.get("version", ""),
                        "release": pkg.get("release", ""),
                        "architecture": pkg.get("arch", ""),
                        "repository": pkg.get("repo", ""),
                        "current_version": pkg.get("installed_version", ""),
                    }
                    
                    # Get additional package details
                    pkg_info = self._get_package_details(pkg.get("name", ""))
                    if pkg_info:
                        update_info.update(pkg_info)
                    
                    # Check if it's a security update
                    update_info["is_security_update"] = self._is_security_update(pkg.get("name", ""))
                    
                    updates.append(update_info)
                
                return updates
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse DNF JSON output: {e}")
                return []
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running DNF command: {e}")
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
            cmd = ["dnf", "info", package_name, "--quiet"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            details = {}
            lines = result.stdout.strip().split('\n')
            current_key = None
            
            for line in lines:
                if not line.strip():
                    continue
                
                if ":" in line:
                    parts = line.split(":", 1)
                    key = parts[0].strip().lower().replace(" ", "_")
                    value = parts[1].strip()
                    
                    if key == "size":
                        details["size"] = value
                    elif key == "url":
                        details["website"] = value
                    elif key in ["license", "summary", "description"]:
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
            # Check if the package is from a security repository or has security advisories
            cmd = ["dnf", "updateinfo", "list", "security", package_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # If the package is listed in security updates, the output will contain the package name
            return package_name in result.stdout
            
        except subprocess.CalledProcessError:
            return False