from setuptools import setup, find_packages

setup(
    name="pmgmt-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "distro",  # For detecting Linux distribution
        "requests",  # For API communication
        "configparser",  # For configuration file handling
    ],
    entry_points={
        "console_scripts": [
            "pmgmt-agent=pmgmt_agent.cli:main",
        ],
    },
    author="Your Organization",
    author_email="your.email@example.com",
    description="Patch Management Agent for detecting available package updates",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/pmgmt-agent",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
)