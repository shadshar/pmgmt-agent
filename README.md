# Patch Management Agent (pmgmt-agent)

A command-line tool to determine available package updates for the host operating system.

## Features

- Automatically detects the Linux distribution and uses the appropriate package manager
- Supports APT (Ubuntu, Debian) and DNF (Fedora) package managers
- Extensible architecture for adding more package managers
- Outputs available updates in a standardized JSON format
- Can send data to a central API or output to stdout
- Configurable via config file or command-line options

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/pmgmt-agent.git
cd pmgmt-agent

# Set up Python environment with pyenv
pyenv install 3.10.0  # or your preferred version
pyenv local 3.10.0

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

## Usage

```bash
# Run with default settings (output to stdout)
pmgmt-agent

# Specify a custom config file
pmgmt-agent --config /path/to/config.conf

# Send output to API instead of stdout
pmgmt-agent --send-to-api

# Override API URL and key
pmgmt-agent --send-to-api --api-url https://example.com/api --api-key YOUR_KEY

# Override hostname
pmgmt-agent --hostname custom-hostname
```

## Configuration

Default configuration file location: `/etc/pmgmt-agent/pmgmt-agent.conf`

Example configuration:
```ini
[api]
url = https://pmgmt-service.example.com/api/updates
key = your-api-key-here

[general]
hostname = auto
```