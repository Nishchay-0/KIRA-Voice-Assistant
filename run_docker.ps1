<#
.SYNOPSIS
    KIRA Voice Assistant - Docker Management Helper for Windows / PowerShell

.DESCRIPTION
    Simplifies building, running, testing, and managing KIRA Docker containers.

.EXAMPLE
    .\run_docker.ps1 build
    .\run_docker.ps1 cli
    .\run_docker.ps1 run
    .\run_docker.ps1 test
    .\run_docker.ps1 down
#>

param (
    [Parameter(Position=0)]
    [ValidateSet("build", "run", "cli", "test", "down", "logs", "shell", "clean")]
    [string]$Action = "cli"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "   KIRA AI VOICE ASSISTANT - DOCKER RUNNER (PowerShell)                 " -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan

switch ($Action) {
    "build" {
        Write-Host "[Docker] Building KIRA Voice Assistant image..." -ForegroundColor Green
        docker compose build
    }
    "run" {
        Write-Host "[Docker] Launching KIRA Voice Assistant with Audio Pass-through..." -ForegroundColor Green
        docker compose run --rm kira
    }
    "cli" {
        Write-Host "[Docker] Launching KIRA in Interactive CLI / Text Mode..." -ForegroundColor Green
        docker compose run --rm kira-cli
    }
    "test" {
        Write-Host "[Docker] Running KIRA Diagnostics and Tests..." -ForegroundColor Green
        docker compose run --rm kira-test
    }
    "shell" {
        Write-Host "[Docker] Opening Bash shell inside KIRA container..." -ForegroundColor Green
        docker compose run --rm --entrypoint /bin/bash kira-cli
    }
    "logs" {
        Write-Host "[Docker] Viewing container logs..." -ForegroundColor Green
        docker compose logs -f
    }
    "down" {
        Write-Host "[Docker] Stopping and removing KIRA containers..." -ForegroundColor Yellow
        docker compose down
    }
    "clean" {
        Write-Host "[Docker] Cleaning up KIRA containers and images..." -ForegroundColor Yellow
        docker compose down --rmi local --volumes --remove-orphans
    }
}
