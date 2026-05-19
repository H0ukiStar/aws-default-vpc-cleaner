#!/bin/bash
# build.sh - Build script for Linux/Mac
# Linux/Mac用ビルドスクリプト

set -e

echo "AWS Default VPC Cleaner - Build Script"
echo "======================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist build

# Build
echo "Building executable..."
pyinstaller --onefile \
  --name aws-default-vpc-cleaner \
  --hidden-import=boto3 \
  --hidden-import=botocore \
  --hidden-import=awscrt \
  --collect-all boto3 \
  --collect-all botocore \
  --collect-all awscrt \
  src/main.py

# Make executable
chmod +x dist/aws-default-vpc-cleaner

# Test
echo ""
echo "Testing build..."
./dist/aws-default-vpc-cleaner --version

echo ""
echo "Build complete!"
echo "Executable location: dist/aws-default-vpc-cleaner"
echo ""
echo "To test: ./dist/aws-default-vpc-cleaner --help"
