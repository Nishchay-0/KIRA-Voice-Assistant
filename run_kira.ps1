$python = "C:\Users\saini\AppData\Local\Programs\Python\Python313\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python 3.13 was not found at $python. Install Python 3.13 with PyAudio support first."
    exit 1
}

& $python "$PSScriptRoot\main.py"
exit $LASTEXITCODE