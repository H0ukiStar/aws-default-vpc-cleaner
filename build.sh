#!/bin/bash
# build.sh - Build script for Linux/Mac
# Linux/Mac用ビルドスクリプト

set -e

echo "AWS Default VPC Cleaner - Build Script"
echo "======================================="
echo ""

# Check if virtual environment exists
if [ ! -d "build-venv" ]; then
    echo "Creating virtual environment..."

    # Try to find Python 3.10-3.14 (to avoid overwriting system python3 which is 3.9 on Amazon Linux 2023)
    PYTHON_CMD=""
    for version in 3.14 3.13 3.12 3.11 3.10; do
        if command -v python${version} &> /dev/null; then
            PYTHON_CMD="python${version}"
            echo "Found $PYTHON_CMD"
            break
        fi
    done

    if [ -z "$PYTHON_CMD" ]; then
        echo "Error: Python 3.10 or higher not found."
        echo "Please install Python 3.10-3.14 (python3.10 to python3.14 command)"
        echo "Amazon Linux 2023: sudo dnf install python3.14"
        exit 1
    fi

    $PYTHON_CMD -m venv build-venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source build-venv/bin/activate

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

# Deactivate and clean up virtual environment
echo ""
echo "Cleaning up virtual environment..."
deactivate
rm -rf build-venv

echo ""
echo "Build complete!"
echo "Executable location: dist/aws-default-vpc-cleaner"
echo ""
echo "To test: ./dist/aws-default-vpc-cleaner --help"
