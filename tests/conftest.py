"""Pytest configuration helpers for the build visualization package.

This file prepares the test environment so that the `src` package is
importable without requiring the package to be installed in the current
Python environment.
"""

import os
import sys

# Ensure the project's source tree is on sys.path for tests.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
