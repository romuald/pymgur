"""
This module can be used to run the server without installing the package

Simply run python3 /path/to/pymgur
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pymgur import main

main()