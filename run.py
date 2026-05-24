"""
run.py — Development server entry point
For production, use gunicorn via Render's start command.
"""

import os
from app import create_app

# Select config based on FLASK_ENV environment variable
env = os.environ.get("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = env == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
