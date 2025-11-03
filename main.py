#!/usr/bin/env python3
"""
Token Impact Estimation System

Calculate environmental impact (kWh, CO₂, Water) of AI token usage
using peer-reviewed research methodologies (MIT and Google studies)
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli import cli

if __name__ == '__main__':
    cli()
