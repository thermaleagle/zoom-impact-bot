#!/usr/bin/env python3
"""
Railway deployment entry point for Zoom Impact Bot
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the bot
from zoom_impact_bot.run import main

if __name__ == "__main__":
    main()
