#!/bin/bash
set -e

# =========================================================================
# KIRA AI - Docker Container Runtime Entrypoint
# =========================================================================

echo "========================================================================="
echo "   KIRA AI VOICE ASSISTANT - DOCKER CONTAINER RUNTIME                   "
echo "   Python Version: $(python --version 2>&1)"
echo "   OS Environment: $(uname -s -r -m)"
echo "========================================================================="

# Audio Device Diagnostics & Setup
if [ -d "/dev/snd" ]; then
    echo "[Docker Init] Host ALSA audio devices detected at /dev/snd."
elif [ -n "$PULSE_SERVER" ]; then
    echo "[Docker Init] PulseAudio server configured at: $PULSE_SERVER"
else
    echo "[Docker Init] No direct audio device forwarded. Running in Text/CLI or Cloud Mode."
fi

# Execute CMD passed from Dockerfile or docker-compose
exec "$@"
