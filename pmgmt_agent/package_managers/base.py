"""
Base class for package managers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class PackageManager(ABC):
    """
    Abstract base class for package managers.
    """
    
    @abstractmethod
    def get_distribution_info(self) -> Dict[str, str]:
        """
        Get information about the current distribution.
        
        Returns:
            Dict[str, str]: A dictionary containing distribution information.
        """
        pass
    
    @abstractmethod
    def get_available_updates(self) -> List[Dict[str, Any]]:
        """
        Get a list of available package updates.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing information
                                 about an available package update.
        """
        pass