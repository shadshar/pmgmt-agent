"""
Basic tests for pmgmt-agent.
"""

import unittest
from pmgmt_agent import __version__


class TestBasic(unittest.TestCase):
    """Basic tests for pmgmt-agent."""

    def test_version(self):
        """Test that version is a string."""
        self.assertIsInstance(__version__, str)


if __name__ == "__main__":
    unittest.main()