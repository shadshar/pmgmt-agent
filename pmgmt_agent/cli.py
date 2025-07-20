"""
Command-line interface for the Patch Management Agent.
"""

import argparse
import configparser
import json
import logging
import os
import socket
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

import requests

from pmgmt_agent.package_managers import get_package_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.handlers.SysLogHandler(address='/dev/log')
    ]
)

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "/etc/pmgmt-agent/pmgmt-agent.conf"


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Patch Management Agent")
    
    parser.add_argument(
        "--config",
        help=f"Path to configuration file (default: {DEFAULT_CONFIG_PATH})",
        default=DEFAULT_CONFIG_PATH
    )
    
    parser.add_argument(
        "--send-to-api",
        action="store_true",
        help="Send output to API instead of stdout"
    )
    
    parser.add_argument(
        "--api-url",
        help="Override API URL from config file"
    )
    
    parser.add_argument(
        "--api-key",
        help="Override API key from config file"
    )
    
    parser.add_argument(
        "--hostname",
        help="Override hostname from config file"
    )
    
    return parser.parse_args()


def load_config(config_path: str) -> configparser.ConfigParser:
    """
    Load configuration from file.
    
    Args:
        config_path (str): Path to the configuration file.
        
    Returns:
        configparser.ConfigParser: Loaded configuration.
    """
    config = configparser.ConfigParser()
    
    # Set default values
    config["api"] = {
        "url": "",
        "key": ""
    }
    config["general"] = {
        "hostname": "auto"
    }
    
    # Try to read the config file
    if os.path.exists(config_path):
        try:
            config.read(config_path)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
    else:
        logger.warning(f"Configuration file {config_path} not found, using defaults")
    
    return config


def get_hostname(config: configparser.ConfigParser, args_hostname: Optional[str]) -> str:
    """
    Get the hostname to use.
    
    Args:
        config (configparser.ConfigParser): Loaded configuration.
        args_hostname (Optional[str]): Hostname from command-line arguments.
        
    Returns:
        str: Hostname to use.
    """
    if args_hostname:
        return args_hostname
    
    config_hostname = config.get("general", "hostname", fallback="auto")
    
    if config_hostname.lower() == "auto":
        return socket.gethostname()
    
    return config_hostname


def send_to_api(data: Dict[str, Any], api_url: str, api_key: str) -> bool:
    """
    Send data to the API.
    
    Args:
        data (Dict[str, Any]): Data to send.
        api_url (str): API URL.
        api_key (str): API key.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        logger.info(f"Sending data to API: {api_url}")
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info("Data successfully sent to API")
            return True
        else:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to API: {e}")
        return False


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    config = load_config(args.config)
    
    # Get package manager
    package_manager = get_package_manager()
    if not package_manager:
        logger.error("No supported package manager found")
        sys.exit(1)
    
    # Get distribution info
    distribution_info = package_manager.get_distribution_info()
    
    # Get available updates
    updates = package_manager.get_available_updates()
    
    # Get hostname
    hostname = get_hostname(config, args.hostname)
    
    # Prepare output data
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "hostname": hostname,
        "distribution": distribution_info,
        "updates": updates,
        "total_updates": len(updates),
        "security_updates": sum(1 for update in updates if update.get("is_security_update", False))
    }
    
    # Determine if we should send to API
    send_to_api_flag = args.send_to_api
    
    if send_to_api_flag:
        # Get API URL and key
        api_url = args.api_url or config.get("api", "url", fallback="")
        api_key = args.api_key or config.get("api", "key", fallback="")
        
        if not api_url:
            logger.error("API URL not provided")
            sys.exit(1)
        
        if not api_key:
            logger.error("API key not provided")
            sys.exit(1)
        
        # Send data to API
        success = send_to_api(output_data, api_url, api_key)
        if not success:
            sys.exit(1)
    else:
        # Output to stdout
        print(json.dumps(output_data, indent=2))
    
    sys.exit(0)


if __name__ == "__main__":
    main()