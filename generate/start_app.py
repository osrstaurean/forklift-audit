#!/usr/bin/env python3
import os
import secrets
import subprocess

# 1. Generate a URL‑safe 32‑byte token
token = secrets.token_urlsafe(32)
print(f"🚀 ForkliftAudit token: {token}\n")

# 2. Export it into the environment for app.py to pick up
env = os.environ.copy()
env['FORKLIFT_APP_TOKEN'] = token

# 3. Execute your Flask app with that env var set
#    Assumes app.py is in the same directory
subprocess.run(['python', 'app.py'], env=env)
