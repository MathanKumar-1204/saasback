import os
import sys

# Ensure directory is on sys.path for serverless execution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from scraper_server import app

# Vercel serverless entrypoint
# The Flask instance 'app' is automatically detected as the WSGI callable.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
