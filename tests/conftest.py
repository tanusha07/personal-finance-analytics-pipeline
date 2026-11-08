import os
import sys

# Let tests import the project's scripts (clean_data, api, ...) from the repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
