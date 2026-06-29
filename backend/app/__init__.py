# All Python packages — init files
import os
import sys

# Add parent directory of 'backend/app' (the project root) to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
