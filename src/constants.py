"""Constants module.

定数モジュール。

This module defines constants used throughout the application.
アプリケーション全体で使用される定数を定義します。
"""

from typing import Final

# Exit codes / 終了コード
EXIT_SUCCESS: Final[int] = 0
EXIT_ERROR: Final[int] = 1
EXIT_USER_CANCELLED: Final[int] = 2

# AWS resource types / AWSリソースタイプ
RESOURCE_TYPE_VPC: Final[str] = "VPC"
RESOURCE_TYPE_SUBNET: Final[str] = "Subnet"
RESOURCE_TYPE_IGW: Final[str] = "InternetGateway"
RESOURCE_TYPE_ROUTE_TABLE: Final[str] = "RouteTable"
RESOURCE_TYPE_SECURITY_GROUP: Final[str] = "SecurityGroup"
RESOURCE_TYPE_NETWORK_ACL: Final[str] = "NetworkACL"

# Default values / デフォルト値
DEFAULT_LANGUAGE: Final[str] = "en"
SUPPORTED_LANGUAGES: Final[list[str]] = ["en", "ja"]

# AWS API retry configuration / AWS API リトライ設定
# boto3's Config retries parameter
MAX_RETRIES: Final[int] = 3

# Parallel processing / 並列処理設定
MAX_WORKERS: Final[int] = 10
