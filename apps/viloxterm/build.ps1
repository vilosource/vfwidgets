# ViloxTerm Build Script for Windows
# Creates a single executable binary using pyside6-deploy

$ErrorActionPreference = "Stop"  # Exit on error

Write-Host "======================================"
Write-Host "ViloXTerm Binary Build Script (Windows)"
Write-Host "======================================"
Write-Host ""

# Check if running in virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Warning: Not running in a virtual environment" -ForegroundColor Yellow
    Write-Host "   It's recommended to use a venv to avoid version conflicts"
    Write-Host ""
}

# Check if pyside6-deploy is available
if (-not (Get-Command pyside6-deploy -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: pyside6-deploy not found" -ForegroundColor Red
    Write-Host "   Install with: pip install PySide6"
    exit 1
}

Write-Host "✅ pyside6-deploy found" -ForegroundColor Green

# Check for required Python packages
Write-Host "📦 Checking build dependencies..."
python -c "import tomlkit" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Installing tomlkit (required by pyside6-deploy)..."
    pip install tomlkit -q
}
python -c "import nuitka" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Installing Nuitka (required for compilation)..."
    pip install nuitka -q
}
Write-Host "✅ Build dependencies ready" -ForegroundColor Green
Write-Host ""

# Clean previous builds
Write-Host "🧹 Cleaning previous builds..."
if (Test-Path "deployment") { Remove-Item -Path "deployment" -Recurse -Force }
if (Test-Path "ViloXTerm.exe") { Remove-Item -Path "ViloXTerm.exe" -Force }
if (Test-Path "ViloXTerm.bin") { Remove-Item -Path "ViloXTerm.bin" -Force }
if (Test-Path "ViloXTerm") { Remove-Item -Path "ViloXTerm" -Force }
if (Test-Path "ViloXTerm.app") { Remove-Item -Path "ViloXTerm.app" -Recurse -Force }
Write-Host "✅ Cleaned" -ForegroundColor Green
Write-Host ""

# Install dependencies in development mode if needed
Write-Host "📦 Ensuring all dependencies are installed..."
pip install -e . -q
Write-Host "✅ Dependencies ready" -ForegroundColor Green
Write-Host ""

# Run pyside6-deploy
Write-Host "🔨 Building ViloXTerm binary..."
Write-Host "   This may take several minutes..."
Write-Host ""

pyside6-deploy -c pysidedeploy.spec -f

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================"
    Write-Host "✅ Build Complete!" -ForegroundColor Green
    Write-Host "======================================"
    Write-Host ""

    # Find and report the created binary
    if (Test-Path "ViloXTerm.exe") {
        $size = (Get-Item "ViloXTerm.exe").Length / 1MB
        Write-Host "📦 Binary created: ViloXTerm.exe ($($size.ToString('F1')) MB)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Run with: .\ViloXTerm.exe"
    } elseif (Test-Path "ViloXTerm.bin") {
        $size = (Get-Item "ViloXTerm.bin").Length / 1MB
        Write-Host "📦 Binary created: ViloXTerm.bin ($($size.ToString('F1')) MB)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Run with: .\ViloXTerm.bin"
    } elseif (Test-Path "ViloXTerm") {
        $size = (Get-Item "ViloXTerm").Length / 1MB
        Write-Host "📦 Binary created: ViloXTerm ($($size.ToString('F1')) MB)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Run with: .\ViloXTerm"
    } else {
        Write-Host "⚠️  Warning: Binary not found at expected location" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "======================================"
    Write-Host "❌ Build Failed!" -ForegroundColor Red
    Write-Host "======================================"
    Write-Host ""
    Write-Host "Check the error messages above for details."
    exit 1
}
