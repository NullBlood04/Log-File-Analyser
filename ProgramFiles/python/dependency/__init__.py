"""
This package contains the core application logic, including agents, tools,
and setup scripts for the log analyzer.
"""

from Agents import ChatBot
from initialSetups import run_processing

# The __all__ list defines the public API of the package.
# When a user does 'from dependency import *', only ChatBot will be imported.
__all__ = ["ChatBot"]


run_processing()
