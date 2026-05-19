# Build Instructions / ビルド手順

This document describes how to build standalone executables for AWS Default VPC Cleaner.

このドキュメントはAWS Default VPC Cleanerのスタンドアロン実行可能ファイルのビルド方法を説明します。

## Overview / 概要

We use PyInstaller to create standalone executables that can run on systems without Python installed.

Pythonがインストールされていないシステムで実行できるスタンドアロン実行可能ファイルを作成するためにPyInstallerを使用します。

## Prerequisites / 前提条件

### For Windows Builds / Windows用ビルド

- Windows 10 or later / Windows 10以降
- Python 3.10 or higher / Python 3.10以上
- PyInstaller / PyInstaller

### For Amazon Linux 2023 Builds / Amazon Linux 2023用ビルド

- Amazon Linux 2023 instance or container / Amazon Linux 2023インスタンスまたはコンテナ
- Python 3.10 or higher / Python 3.10以上
- PyInstaller / PyInstaller

## Building on Windows / Windowsでのビルド

### 1. Install Dependencies / 依存関係のインストール

```powershell
# Activate virtual environment / 仮想環境をアクティベート
.\build-venv\Scripts\Activate.ps1

# Install dependencies / 依存関係をインストール
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Build Executable / 実行可能ファイルのビルド

```powershell
# Build single-file executable / 単一ファイル実行可能ファイルをビルド
pyinstaller --onefile `
  --name aws-default-vpc-cleaner `
  --hidden-import=boto3 `
  --hidden-import=botocore `
  --hidden-import=awscrt `
  --collect-all boto3 `
  --collect-all botocore `
  --collect-all awscrt `
  src/main.py

# The executable will be in dist/ folder
# 実行可能ファイルはdist/フォルダに作成されます
```

### 3. Test the Executable / 実行可能ファイルのテスト

```powershell
# Test with dry-run / ドライランでテスト
.\dist\aws-default-vpc-cleaner.exe --dry-run --help
```

## Building on Amazon Linux 2023 / Amazon Linux 2023でのビルド

### 1. Prepare Environment / 環境の準備

```bash
# Update system / システムをアップデート
sudo dnf update -y

# Install Python 3.11 (default in AL2023) / Python 3.11をインストール（AL2023のデフォルト）
sudo dnf install python3 python3-pip -y

# Install development tools / 開発ツールをインストール
sudo dnf install gcc python3-devel -y
```

### 2. Setup Project / プロジェクトのセットアップ

```bash
# Create virtual environment / 仮想環境を作成
python3 -m venv build-venv

# Activate virtual environment / 仮想環境をアクティベート
source build-venv/bin/activate

# Install dependencies / 依存関係をインストール
pip install -r requirements.txt
pip install pyinstaller
```

### 3. Build Executable / 実行可能ファイルのビルド

```bash
# Build single-file executable / 単一ファイル実行可能ファイルをビルド
pyinstaller --onefile \
  --name aws-default-vpc-cleaner \
  --hidden-import=boto3 \
  --hidden-import=botocore \
  --hidden-import=awscrt \
  --collect-all boto3 \
  --collect-all botocore \
  --collect-all awscrt \
  src/main.py

# The executable will be in dist/ folder
# 実行可能ファイルはdist/フォルダに作成されます
```

### 4. Test the Executable / 実行可能ファイルのテスト

```bash
# Make executable / 実行可能にする
chmod +x dist/aws-default-vpc-cleaner

# Test with dry-run / ドライランでテスト
./dist/aws-default-vpc-cleaner --dry-run --help
```

## Building in CloudShell / CloudShellでのビルド

AWS CloudShell uses Amazon Linux 2023, so follow the Amazon Linux 2023 instructions.

AWS CloudShellはAmazon Linux 2023を使用するため、Amazon Linux 2023の手順に従ってください。

```bash
# Clone repository / リポジトリをクローン
git clone https://github.com/yourusername/aws-default-vpc-cleaner.git
cd aws-default-vpc-cleaner

# Create virtual environment / 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# Install dependencies / 依存関係をインストール
pip install -r requirements.txt
pip install pyinstaller

# Build / ビルド
pyinstaller --onefile \
  --name aws-default-vpc-cleaner \
  --hidden-import=boto3 \
  --hidden-import=botocore \
  --hidden-import=awscrt \
  --collect-all boto3 \
  --collect-all botocore \
  --collect-all awscrt \
  src/main.py

# Run / 実行
./dist/aws-default-vpc-cleaner --dry-run
```

## PyInstaller Spec File / PyInstaller仕様ファイル

For more complex builds, you can create a spec file:

より複雑なビルドには、仕様ファイルを作成できます:

```python
# aws-default-vpc-cleaner.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['boto3', 'botocore'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Collect boto3 and botocore data files
a.datas += collect_all('boto3')[1]
a.datas += collect_all('botocore')[1]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='aws-default-vpc-cleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

Then build using:

次にビルドします:

```bash
pyinstaller aws-default-vpc-cleaner.spec
```

## Build Script / ビルドスクリプト

### Windows Build Script / Windowsビルドスクリプト

Create `build.ps1`:

```powershell
# build.ps1
# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Clean previous builds
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# Build
pyinstaller --onefile `
  --name aws-default-vpc-cleaner `
  --hidden-import=boto3 `
  --hidden-import=botocore `
  --collect-all boto3 `
  --collect-all botocore `
  src/main.py

# Test
Write-Host "Testing build..."
& .\dist\aws-default-vpc-cleaner.exe --version

Write-Host "Build complete! Executable is in dist/ folder"
```

Run:

```powershell
.\build.ps1
```

### Linux Build Script / Linuxビルドスクリプト

Create `build.sh`:

```bash
#!/bin/bash
# build.sh

# Activate virtual environment
source venv/bin/activate

# Clean previous builds
rm -rf dist build

# Build
pyinstaller --onefile \
  --name aws-default-vpc-cleaner \
  --hidden-import=boto3 \
  --hidden-import=botocore \
  --collect-all boto3 \
  --collect-all botocore \
  src/main.py

# Test
echo "Testing build..."
./dist/aws-default-vpc-cleaner --version

echo "Build complete! Executable is in dist/ folder"
```

Run:

```bash
chmod +x build.sh
./build.sh
```

## Distribution / 配布

### Creating a Release Package / リリースパッケージの作成

```bash
# Create a distribution folder / 配布フォルダを作成
mkdir -p release

# Copy executable / 実行可能ファイルをコピー
cp dist/aws-default-vpc-cleaner release/

# Copy documentation / ドキュメントをコピー
cp README.md release/
cp LICENSE release/

# Create archive / アーカイブを作成
# On Windows:
Compress-Archive -Path release/* -DestinationPath aws-default-vpc-cleaner-windows.zip

# On Linux:
tar -czf aws-default-vpc-cleaner-linux.tar.gz -C release .
```

## Troubleshooting / トラブルシューティング

### "Module not found" Error / "モジュールが見つかりません"エラー

Add the missing module to hidden imports:

欠落しているモジュールを隠しインポートに追加します:

```bash
pyinstaller --onefile \
  --hidden-import=missing_module_name \
  src/main.py
```

### Large Executable Size / 実行可能ファイルのサイズが大きい

Use UPX compression:

UPX圧縮を使用します:

```bash
# Install UPX
# Windows: Download from https://upx.github.io/
# Linux: sudo dnf install upx

# Build with UPX
pyinstaller --onefile --upx-dir=/path/to/upx src/main.py
```

### Import Errors at Runtime / 実行時のインポートエラー

Use `--collect-all` for the problematic package:

問題のあるパッケージに対して`--collect-all`を使用します:

```bash
pyinstaller --onefile --collect-all package_name src/main.py
```

## Verification / 検証

After building, verify the executable works correctly:

ビルド後、実行可能ファイルが正しく動作することを確認します:

```bash
# Check version / バージョン確認
./dist/aws-default-vpc-cleaner --version

# Check help / ヘルプ確認
./dist/aws-default-vpc-cleaner --help

# Test with dry-run / ドライランでテスト
./dist/aws-default-vpc-cleaner --dry-run --regions us-east-1
```

## Best Practices / ベストプラクティス

1. **Build on Target Platform** / **ターゲットプラットフォームでビルド**: Always build on the same platform where you'll run the executable. PyInstaller binaries are not cross-platform.

   実行可能ファイルを実行するのと同じプラットフォームで必ずビルドしてください。PyInstallerのバイナリはクロスプラットフォームではありません。

2. **Test Thoroughly** / **徹底的にテスト**: Test the executable in a clean environment without Python installed.

   Pythonがインストールされていないクリーンな環境で実行可能ファイルをテストしてください。

3. **Document Dependencies** / **依存関係を文書化**: Keep track of any special PyInstaller flags or hooks needed.

   必要な特別なPyInstallerフラグやフックを記録しておいてください。

4. **Version Control** / **バージョン管理**: Tag releases in Git for traceability.

   追跡可能性のためにGitでリリースにタグを付けてください。

## Additional Resources / 追加リソース

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller Recipes](https://github.com/pyinstaller/pyinstaller/wiki/Recipes)
- [AWS CloudShell Documentation](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html)
