# Dockerfile for forklift-audit with embedded ngrok and entrypoint script
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       wget unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download and install ngrok binary
RUN wget -qO /tmp/ngrok.zip https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip \
    && unzip -o -q /tmp/ngrok.zip -d /usr/local/bin \
    && rm /tmp/ngrok.zip \
    && chmod +x /usr/local/bin/ngrok

# Create entrypoint script for ngrok auth & launch
RUN cat << 'EOF' > /usr/local/bin/entrypoint.sh
#!/bin/sh

# Configure ngrok auth token if provided
if [ -n "$NGROK_AUTH_TOKEN" ]; then
  ngrok config add-authtoken "$NGROK_AUTH_TOKEN"
fi

# Start ngrok in background, forwarding port 5000
ngrok http 5000 --log=stdout &

# Launch the Flask application
exec python app.py
EOF

RUN chmod +x /usr/local/bin/entrypoint.sh

# Copy application code
COPY . .

EXPOSE 5000

# Use the entrypoint script to configure ngrok and start the app
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
