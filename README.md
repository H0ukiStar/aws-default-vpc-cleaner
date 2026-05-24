# AWS Default VPC Cleaner

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A tool to delete default VPCs and related resources across all AWS regions.

AWSアカウント上のすべてのリージョンに存在するデフォルトVPCと関連リソースを削除するツール。

## Features / 機能

- **Multi-Region Support** / **複数リージョン対応**: Delete default VPCs across all AWS regions or specific regions / すべてのAWSリージョンまたは特定のリージョンのデフォルトVPCを削除
- **Dry Run Mode** / **ドライランモード**: List resources without deleting them / 削除せずにリソースをリスト表示
- **Safe Deletion** / **安全な削除**: Deletes resources in the correct order to avoid dependency issues / 依存関係の問題を回避するために正しい順序でリソースを削除
- **Multi-Language** / **多言語対応**: Supports English and Japanese output / 英語と日本語の出力をサポート
- **Verbose Mode** / **詳細モード**: Detailed logging of operations / 操作の詳細なログ出力

## Deleted Resources / 削除されるリソース

The tool deletes the following resources in order:
ツールは以下のリソースを順番に削除します:

1. Internet Gateways (detached then deleted) / インターネットゲートウェイ（デタッチ後に削除）
2. Subnets / サブネット
3. Route Tables (excluding main route table) / ルートテーブル（メインルートテーブルを除く）
4. Security Groups (excluding default security group) / セキュリティグループ（デフォルトセキュリティグループを除く）
5. Network ACLs (excluding default ACL) / ネットワークACL（デフォルトACLを除く）
6. VPC / VPC

## Installation / インストール

### Prerequisites / 前提条件

- Python 3.10 or higher / Python 3.10以上
- AWS CLI configured with appropriate credentials / 適切な認証情報で設定されたAWS CLI
- Sufficient IAM permissions / 十分なIAM権限

**Note for AWS SSO Users / AWS SSO ユーザーへの注意:**

If you use AWS SSO (Single Sign-On) with `aws login`, the `awscrt` package is automatically included in the requirements.

AWS SSO（シングルサインオン）を `aws login` で使用する場合、`awscrt` パッケージは requirements に自動的に含まれています。

### Required IAM Permissions / 必要なIAM権限

The following IAM permissions are required:
以下のIAM権限が必要です:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeRegions",
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeInternetGateways",
        "ec2:DescribeRouteTables",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeNetworkAcls",
        "ec2:DeleteVpc",
        "ec2:DeleteSubnet",
        "ec2:DetachInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:DeleteRouteTable",
        "ec2:DeleteSecurityGroup",
        "ec2:DeleteNetworkAcl"
      ],
      "Resource": "*"
    }
  ]
}
```

### Install from Source / ソースからインストール

```bash
# Clone the repository / リポジトリをクローン
git clone https://github.com/H0ukiStar/aws-default-vpc-cleaner.git
cd aws-default-vpc-cleaner

# Create virtual environment / 仮想環境を作成
python -m venv venv

# Activate virtual environment / 仮想環境をアクティベート
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies / 依存関係をインストール
pip install -e .

# Install development dependencies (optional) / 開発依存関係をインストール（オプション）
pip install -r requirements-dev.txt
```

After installation, the `aws-default-vpc-cleaner` command will be available in your PATH.

インストール後、`aws-default-vpc-cleaner` コマンドがPATHで利用可能になります。

### AWS Credentials Configuration / AWS認証情報の設定

This tool requires valid AWS credentials. Configure them using one of the following methods:

このツールには有効なAWS認証情報が必要です。以下のいずれかの方法で設定してください:

#### Option 1: AWS Login (Console Credentials) / オプション2: AWS Login（コンソール認証情報）

```bash
# Login using AWS Management Console credentials
# Requires AWS CLI v2.32.0 or later
aws login
```

#### Option 2: AWS CLI Configuration / オプション1: AWS CLI設定

```bash
# Configure AWS credentials
aws configure
```

#### Option 3: Environment Variables / オプション3: 環境変数

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1  # Optional
```

## Usage / 使用方法

### Basic Usage / 基本的な使用方法

After installing the package, use the `aws-default-vpc-cleaner` command:

パッケージをインストールした後、`aws-default-vpc-cleaner` コマンドを使用します:

```bash
# Delete default VPCs in all regions (with confirmation)
# すべてのリージョンのデフォルトVPCを削除（確認あり）
aws-default-vpc-cleaner

# Delete default VPCs in specific regions
# 特定リージョンのデフォルトVPCを削除
aws-default-vpc-cleaner --regions us-east-1 us-west-2

# List default VPCs without deleting (dry-run mode)
# 削除せずにデフォルトVPCをリスト（ドライランモード）
aws-default-vpc-cleaner --dry-run

# Delete without confirmation
# 確認なしで削除
aws-default-vpc-cleaner --yes

# Use Japanese language output
# 日本語出力を使用
aws-default-vpc-cleaner --lang ja

# Verbose output
# 詳細出力
aws-default-vpc-cleaner --verbose
```

Alternatively, you can run it as a Python module:

または、Pythonモジュールとして実行することもできます:

```bash
python -m src.main --help
```

### Command-Line Options / コマンドラインオプション

```
Options:
  --regions REGION [REGION ...]
                        Specify target regions (default: all regions)
                        対象リージョンを指定（デフォルト：全リージョン）

  --dry-run            List resources without deleting them
                        削除せずにリソースをリストアップ

  --yes, -y            Skip confirmation prompts
                        確認プロンプトをスキップ

  --lang {en,ja}       Language for output (en/ja)
                        出力言語（en/ja）

  --verbose, -v        Enable verbose output
                        詳細出力を有効化

  --version            Show version number
                        バージョン番号を表示

  --help, -h           Show help message
                        ヘルプメッセージを表示
```

### Examples / 使用例

#### Example 1: Dry-run to check what would be deleted / 例1: 削除対象を確認するドライラン

```bash
aws-default-vpc-cleaner --dry-run --verbose
```

Output:
```
Starting AWS Default VPC Cleaner...
DRY RUN MODE - No resources will be deleted
Fetching available regions...
Found 16 regions
Checking for default VPC in us-east-1...
Default VPC found: vpc-12345678
Would delete InternetGateway: igw-12345678
Would delete Subnet: subnet-12345678
Would delete VPC: vpc-12345678
...
```

#### Example 2: Delete default VPCs in specific regions / 例2: 特定リージョンのデフォルトVPCを削除

```bash
aws-default-vpc-cleaner --regions us-east-1 ap-northeast-1 --lang ja
```

Output:
```
AWS Default VPC Cleaner を起動しています...
us-east-1 のデフォルトVPCを確認中...
デフォルトVPCが見つかりました: vpc-12345678

すべてのデフォルトVPCを削除してもよろしいですか？ (yes/no): yes

リージョンを処理中: us-east-1
VPCを削除中: vpc-12345678
VPCの削除に成功しました: vpc-12345678
...
```

#### Example 3: Delete all default VPCs without confirmation / 例3: 確認なしですべてのデフォルトVPCを削除

```bash
aws-default-vpc-cleaner --yes
```

**Warning / 警告**: This will delete all default VPCs without asking for confirmation. Use with caution!
これは確認なしですべてのデフォルトVPCを削除します。慎重に使用してください！

## Development / 開発

### Running Tests / テストの実行

```bash
# Run all tests / すべてのテストを実行
pytest

# Run with coverage / カバレッジ付きで実行
pytest --cov=src --cov-report=html

# Run specific test file / 特定のテストファイルを実行
pytest tests/test_aws_client.py

# Run with verbose output / 詳細出力付きで実行
pytest -v
```

### Code Quality / コード品質

```bash
# Format code with Black / Blackでコードをフォーマット
black src/ tests/

# Sort imports with isort / isortでインポートをソート
isort src/ tests/

# Lint with flake8 / flake8でLint
flake8 src/ tests/

# Type check with mypy / mypyで型チェック
mypy src/
```

### Building Executable / 実行可能ファイルのビルド

See [BUILD.md](BUILD.md) for detailed instructions on building standalone executables.
Dedicated build scripts are available for Windows (`build.ps1`) and Amazon Linux 2023 (`build.sh`).

スタンドアロン実行可能ファイルのビルド手順の詳細は[BUILD.md](BUILD.md)を参照してください。
Windows用（`build.ps1`）とAmazon Linux 2023用（`build.sh`）の専用ビルドスクリプトを用意しています。

## Project Structure / プロジェクト構造

```
aws-default-vpc-cleaner/
├── src/
│   ├── __init__.py           # Package initializer / パッケージ初期化
│   ├── main.py               # CLI entry point / CLIエントリーポイント
│   ├── default_vpc_cleaner.py # Main deletion logic / メイン削除ロジック
│   ├── aws_client.py         # AWS API wrapper / AWS APIラッパー
│   ├── i18n.py               # Internationalization / 国際化
│   └── constants.py          # Constants / 定数
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration / Pytest設定
│   ├── test_aws_client.py    # AWS client tests / AWSクライアントテスト
│   ├── test_default_vpc_cleaner.py # Cleaner tests / クリーナーテスト
│   └── test_i18n.py          # I18n tests / i18nテスト
├── requirements.txt          # Production dependencies / 本番依存関係
├── requirements-dev.txt      # Development dependencies / 開発依存関係
├── pyproject.toml            # Project configuration / プロジェクト設定
├── pytest.ini                # Pytest configuration / Pytest設定
├── README.md                 # This file / このファイル
└── BUILD.md                  # Build instructions / ビルド手順
```

## Troubleshooting / トラブルシューティング

### "AWS credentials not found" Error / "AWS認証情報が見つかりません"エラー

Configure AWS CLI with your credentials:
AWS CLIに認証情報を設定してください:

```bash
aws configure
```

### Permission Denied Errors / 権限拒否エラー

Make sure your IAM user/role has the required permissions listed in the [Required IAM Permissions](#required-iam-permissions--必要なiam権限) section.

[必要なIAM権限](#required-iam-permissions--必要なiam権限)セクションに記載されている権限がIAMユーザー/ロールに付与されていることを確認してください。

## License / ライセンス

This project is licensed under the MIT License - see the LICENSE file for details.

このプロジェクトはMITライセンスの下でライセンスされています。詳細はLICENSEファイルを参照してください。

## Disclaimer / 免責事項

**WARNING / 警告**: This tool will permanently delete VPCs and associated resources. Use at your own risk. Always run with `--dry-run` first to verify what will be deleted.

このツールはVPCと関連リソースを完全に削除します。自己責任で使用してください。削除対象を確認するため、必ず最初に`--dry-run`を実行してください。

## Author / 著者

H0ukiStar ([X](https://x.com/H0ukiStar) | [GitHub](https://github.com/H0ukiStar))


## Acknowledgments / 謝辞

- Built with [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- Tested with [moto](https://github.com/getmoto/moto)
