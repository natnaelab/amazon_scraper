#!/bin/bash

# Start X11 virtual framebuffer
Xvfb :99 -screen 0 1920x1080x24 &

# Start window manager
fluxbox -display :99 &

# Start VNC server
x11vnc -display :99 -forever -nopw &

# Apply database migrations
python manage.py migrate

# Start Celery worker in the background
celery -A amazon_scraper worker --loglevel=info &

# Start Flower in the background
celery -A amazon_scraper flower --port=5555 &

# Start Django development server
python manage.py runserver 0.0.0.0:8000
