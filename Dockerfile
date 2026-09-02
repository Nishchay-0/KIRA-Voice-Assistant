# Multi-Platform Production Dockerfile for KIRA Voice Assistant
FROM python:3.11-slim

# Set environment variables for non-interactive installs, Python output, and audio UTF-8 encoding
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Linux system dependencies: audio (ALSA, PortAudio, PulseAudio), speech synthesis (espeak-ng), ffmpeg, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    curl \
    git \
    ffmpeg \
    portaudio19-dev \
    python3-pyaudio \
    libasound2-dev \
    alsa-utils \
    pulseaudio \
    pulseaudio-utils \
    libespeak-ng1 \
    espeak-ng \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Upgrade pip and install wheel & setuptools
RUN pip install --upgrade pip setuptools wheel

# Install PyTorch CPU build first for optimized container size & faster layer caching
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements file and install Python packages
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy application code into container
COPY . /app/

# Ensure entrypoint script is executable
RUN chmod +x /app/docker-entrypoint.sh 2>/dev/null || true

# Set up ALSA / PulseAudio default sound configuration
RUN mkdir -p /root/.config/pulse /etc/alsa/conf.d

# Set entrypoint and default command
ENTRYPOINT ["/bin/bash", "/app/docker-entrypoint.sh"]
CMD ["python", "main.py"]
