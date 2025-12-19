# SilentBot CLI - Perfect Local Installer (v6.5)
# Run with: powershell -ExecutionPolicy Bypass -File setup_silentbot.ps1

$InstallDir = "$HOME\SilentBot"
$RepoUrl = "https://github.com/Silentbotbd/Silentbot-AI.git"

Write-Host "--- SILENTBOT CLI PRODUCTION INSTALLER ---" -ForegroundColor Green

# 1. Create Directory
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir
    Write-Host "[1/4] Directory created: $InstallDir"
}

# 2. Clone/Update Repo
if (Test-Path "$InstallDir\.git") {
    Write-Host "[2/4] Updating existing installation..."
    Set-Location $InstallDir
    git pull origin main
} else {
    Write-Host "[2/4] Cloning SilentBot repository..."
    git clone $RepoUrl $InstallDir
    Set-Location $InstallDir
}

# 3. Setup Virtual Environment
if (!(Test-Path "$InstallDir\venv")) {
    Write-Host "[3/4] Creating Python Virtual Environment..."
    python -m venv venv
}
Write-Host "Installing dependencies..."
.\venv\Scripts\pip install -r requirements.txt --quiet

# 4. Add to PATH (Optional but recommended)
Write-Host "[4/4] Creating 'silentbot' command shortcut..."
$BatchFile = "$HOME\AppData\Local\Microsoft\WindowsApps\silentbot.bat"
"@echo off`n$InstallDir\venv\Scripts\python.exe $InstallDir\main.py %*" | Out-File -FilePath $BatchFile -Encoding ASCII

Write-Host "`n✅ INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "You can now use SilentBot anywhere in your terminal by typing:"
Write-Host "  silentbot --cli" -ForegroundColor Cyan
Write-Host "`nTo start the Web IDE:"
Write-Host "  silentbot" -ForegroundColor Cyan
