"""
TikTok Bot Exact - Visual Studio Entry Point
==============================================
This is the startup file for the Visual Studio project.
Press F5 to run the bot.
"""

import os
import sys

# Ensure the project root is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and run the main bot
from main import main

if __name__ == "__main__":
    main()
