"""
Path fix — imported at the top of every UI page.
Ensures project root is on sys.path regardless of how Streamlit was launched.
"""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Also fix working directory so relative file paths work (config.yaml etc.)
if os.getcwd() != ROOT:
    os.chdir(ROOT)
