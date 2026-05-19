# build.ps1 - Build script for Windows
# Windows用ビルドスクリプト

Write-Host "AWS Default VPC Cleaner - Build Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "src\Scripts\python.exe")) {
    Write-Host "Error: Virtual environment not found in 'src' directory" -ForegroundColor Red
    Write-Host "Please activate the virtual environment first:" -ForegroundColor Yellow
    Write-Host "  .\src\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\src\Scripts\Activate.ps1

# Install/upgrade dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -e .
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

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "Executable location: dist\aws-default-vpc-cleaner.exe" -ForegroundColor Green
Write-Host ""
Write-Host "To test: .\dist\aws-default-vpc-cleaner.exe --help" -ForegroundColor Cyan
