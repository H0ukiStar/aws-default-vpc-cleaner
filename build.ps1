# build.ps1 - Build script for Windows
# Windows用ビルドスクリプト

Write-Host "AWS Default VPC Cleaner - Build Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "build-venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv build-venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\build-venv\Scripts\Activate.ps1

# Install/upgrade dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# Build
Write-Host "Building executable..." -ForegroundColor Yellow
pyinstaller --onefile `
  --name aws-default-vpc-cleaner `
  --hidden-import=boto3 `
  --hidden-import=botocore `
  --hidden-import=awscrt `
  --collect-all boto3 `
  --collect-all botocore `
  --collect-all awscrt `
  src/main.py

# Test
Write-Host ""
Write-Host "Testing build..." -ForegroundColor Yellow
& .\dist\aws-default-vpc-cleaner.exe --version

# Deactivate and clean up virtual environment
Write-Host ""
Write-Host "Cleaning up virtual environment..." -ForegroundColor Yellow
deactivate
Remove-Item -Recurse -Force build-venv -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "Executable location: dist\aws-default-vpc-cleaner.exe" -ForegroundColor Green
Write-Host ""
Write-Host "To test: .\dist\aws-default-vpc-cleaner.exe --help" -ForegroundColor Cyan
