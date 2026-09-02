#!/usr/bin/env bash
# =========================================================================
# KIRA AI - Docker Management Helper for Linux / macOS / WSL
# =========================================================================

set -e

ACTION="${1:-cli}"

echo "========================================================================="
echo "   KIRA AI VOICE ASSISTANT - DOCKER RUNNER (Bash)                       "
echo "========================================================================="

case "$ACTION" in
    build)
        echo "[Docker] Building KIRA Voice Assistant image..."
        docker compose build
        ;;
    run)
        echo "[Docker] Launching KIRA Voice Assistant with Audio Pass-through..."
        docker compose run --rm kira
        ;;
    cli)
        echo "[Docker] Launching KIRA in Interactive CLI / Text Mode..."
        docker compose run --rm kira-cli
        ;;
    test)
        echo "[Docker] Running KIRA Diagnostics and Tests..."
        docker compose run --rm kira-test
        ;;
    shell)
        echo "[Docker] Opening Bash shell inside KIRA container..."
        docker compose run --rm --entrypoint /bin/bash kira-cli
        ;;
    logs)
        echo "[Docker] Viewing container logs..."
        docker compose logs -f
        ;;
    down)
        echo "[Docker] Stopping and removing KIRA containers..."
        docker compose down
        ;;
    clean)
        echo "[Docker] Cleaning up KIRA containers and images..."
        docker compose down --rmi local --volumes --remove-orphans
        ;;
    *)
        echo "Usage: ./run_docker.sh [build|run|cli|test|shell|logs|down|clean]"
        exit 1
        ;;
esac
