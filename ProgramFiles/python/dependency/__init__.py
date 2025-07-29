"""
This package contains the core application logic, including agents, tools,
and setup scripts for the log analyzer.
"""

import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

from . import ChatBot
from .initialSetups import run_processing

__all__ = ["ChatBot", "run_processing", "PROJECT_ROOT"]

# NOTE: The call to run_processing() has been removed. It is best practice to call
# initialization functions from a main entrypoint script, not as a side-effect
# of importing a package.
