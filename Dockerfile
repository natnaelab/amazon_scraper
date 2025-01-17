FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    build-essential \
    libffi-dev \
    x11vnc \
    fluxbox \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ensure correct permissions and directories for X11
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix \
    && mkdir -p /var/lib/fluxbox/.fluxbox/styles \
    && chown -R root:root /var/lib/fluxbox

# Expose ports (Django, Flower, VNC)
EXPOSE 8000 5555 5900

# Create entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
