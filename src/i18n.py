"""
Internationalization module.
国際化モジュール。

This module provides multi-language support for the application.
アプリケーションの多言語サポートを提供します。
"""

import locale
import os
from typing import Final

from src.constants import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

# Translation dictionary / 翻訳辞書
TRANSLATIONS: Final[dict[str, dict[str, str]]] = {
    "en": {
        # General messages
        "app_description": (
            "Delete default VPCs and related resources "
            "across AWS regions"
        ),
        "starting": "Starting AWS Default VPC Cleaner...",
        "completed": "Operation completed successfully",
        "cancelled": "Operation cancelled by user",
        "error": "Error occurred: {error}",
        # CLI arguments
        "arg_regions": "Specify target regions (default: all regions)",
        "arg_dry_run": "List resources without deleting them",
        "arg_yes": "Skip confirmation prompts",
        "arg_lang": "Language for output (en/ja)",
        "arg_verbose": "Enable verbose output",
        # Region operations
        "fetching_regions": "Fetching available regions...",
        "found_regions": "Found {count} regions",
        "processing_region": "Processing region: {region}",
        "region_completed": "Region {region} completed",
        "region_failed": "Region {region} failed: {error}",
        # VPC operations
        "checking_default_vpc": "Checking for default VPC in {region}...",
        "default_vpc_found": "Default VPC found: {vpc_id}",
        "no_default_vpc": "No default VPC found in {region}",
        "deleting_vpc": "Deleting VPC: {vpc_id}",
        "vpc_deleted": "VPC deleted successfully: {vpc_id}",
        # Resource operations
        "listing_resources": "Listing resources in VPC {vpc_id}...",
        "found_resource": "Found {resource_type}: {resource_id}",
        "deleting_resource": "Deleting {resource_type}: {resource_id}",
        "resource_deleted": "Deleted {resource_type}: {resource_id}",
        "detaching_igw": "Detaching Internet Gateway: {igw_id}",
        "igw_detached": "Internet Gateway detached: {igw_id}",
        # Dry run mode
        "dry_run_mode": "DRY RUN MODE - No resources will be deleted",
        "would_delete": "Would delete {resource_type}: {resource_id}",
        # Confirmation
        "confirm_deletion": (
            "Are you sure you want to delete all default VPCs? "
            "(yes/no): "
        ),
        "confirm_yes": "yes",
        "invalid_input": "Invalid input. Please enter 'yes' or 'no'.",
        # Summary
        "summary_title": "=== Summary ===",
        "summary_regions_processed": "Regions processed: {count}",
        "summary_vpcs_deleted": "VPCs deleted: {count}",
        "summary_resources_deleted": "Resources deleted: {count}",
        "summary_errors": "Errors: {count}",
        # Errors
        "error_no_credentials": (
            "AWS credentials not found. "
            "Please configure AWS CLI."
        ),
        "error_permission_denied": (
            "Permission denied. Please check IAM permissions."
        ),
        "error_region_unavailable": "Region {region} is not available",
        "error_resource_in_use": "Resource {resource_id} is still in use",
        "error_dependency_violation": (
            "Cannot delete {resource_type}: dependency violation"
        ),
    },
    "ja": {
        # 一般メッセージ
        "app_description": "AWSリージョン全体のデフォルトVPCと関連リソースを削除します",
        "starting": "AWS Default VPC Cleaner を起動しています...",
        "completed": "操作が正常に完了しました",
        "cancelled": "ユーザーによって操作がキャンセルされました",
        "error": "エラーが発生しました: {error}",
        # CLIオプション
        "arg_regions": "対象リージョンを指定 (デフォルト: 全リージョン)",
        "arg_dry_run": "削除せずにリソースをリストアップ",
        "arg_yes": "確認プロンプトをスキップ",
        "arg_lang": "出力言語 (en/ja)",
        "arg_verbose": "詳細出力を有効化",
        # リージョン操作
        "fetching_regions": "利用可能なリージョンを取得中...",
        "found_regions": "{count}個のリージョンが見つかりました",
        "processing_region": "リージョンを処理中: {region}",
        "region_completed": "リージョン {region} の処理が完了しました",
        "region_failed": "リージョン {region} の処理に失敗しました: {error}",
        # VPC操作
        "checking_default_vpc": "{region} のデフォルトVPCを確認中...",
        "default_vpc_found": "デフォルトVPCが見つかりました: {vpc_id}",
        "no_default_vpc": "{region} にデフォルトVPCが見つかりません",
        "deleting_vpc": "VPCを削除中: {vpc_id}",
        "vpc_deleted": "VPCの削除に成功しました: {vpc_id}",
        # リソース操作
        "listing_resources": "VPC {vpc_id} のリソースをリスト中...",
        "found_resource": "{resource_type} が見つかりました: {resource_id}",
        "deleting_resource": "{resource_type} を削除中: {resource_id}",
        "resource_deleted": "{resource_type} を削除しました: {resource_id}",
        "detaching_igw": "インターネットゲートウェイをデタッチ中: {igw_id}",
        "igw_detached": "インターネットゲートウェイをデタッチしました: {igw_id}",
        # ドライランモード
        "dry_run_mode": "ドライランモード - リソースは削除されません",
        "would_delete": "削除対象 {resource_type}: {resource_id}",
        # 確認
        "confirm_deletion": "すべてのデフォルトVPCを削除してもよろしいですか？ (yes/no): ",
        "confirm_yes": "yes",
        "invalid_input": "無効な入力です。'yes' または 'no' を入力してください。",
        # サマリー
        "summary_title": "=== サマリー ===",
        "summary_regions_processed": "処理したリージョン: {count}個",
        "summary_vpcs_deleted": "削除したVPC: {count}個",
        "summary_resources_deleted": "削除したリソース: {count}個",
        "summary_errors": "エラー: {count}個",
        # エラー
        "error_no_credentials": "AWS認証情報が見つかりません。AWS CLIを設定してください。",
        "error_permission_denied": "アクセス権限がありません。IAM権限を確認してください。",
        "error_region_unavailable": "リージョン {region} は利用できません",
        "error_resource_in_use": "リソース {resource_id} はまだ使用中です",
        "error_dependency_violation": "{resource_type} を削除できません: 依存関係違反",
    },
}


class I18n:
    """
    Internationalization handler.
    国際化ハンドラー。

    Provides methods to get translated messages based on the selected language.
    選択された言語に基づいて翻訳されたメッセージを取得するメソッドを提供します。

    Parameters
    ----------
    language : str, optional
        Language code ('en' or 'ja'). If not specified,
        auto-detects from environment.
        言語コード ('en' または 'ja')。
        指定されない場合は環境から自動検出します。

    Examples
    --------
    >>> i18n = I18n('ja')
    >>> print(i18n.get('starting'))
    AWS Default VPC Cleaner を起動しています...
    """

    def __init__(self, language: str | None = None) -> None:
        """
        Initialize I18n instance.
        I18nインスタンスを初期化します。

        Parameters
        ----------
        language : str | None, optional
            Language code. If None, auto-detects from environment.
            言語コード。Noneの場合は環境から自動検出します。
        """
        if language is None:
            language = self._detect_language()

        self.language: str = (
            language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        )

    def _detect_language(self) -> str:
        """
        Detect language from environment variables.
        環境変数から言語を検出します。

        Returns
        -------
        str
            Detected language code.
            検出された言語コード。
        """
        # Check LANG environment variable first (highest priority)
        # LANG環境変数を最初にチェック（最優先）
        lang_env: str = os.environ.get("LANG", "")
        if lang_env:
            if lang_env.startswith("ja"):
                return "ja"
            elif lang_env.startswith("en"):
                return "en"

        # Check system locale as fallback
        # システムロケールをフォールバックとしてチェック
        try:
            system_locale: str | None = locale.getlocale()[0]
            if system_locale and system_locale.startswith("ja"):
                return "ja"
        except Exception:
            pass

        return DEFAULT_LANGUAGE

    def get(self, key: str, **kwargs: str | int) -> str:
        """
        Get translated message.
        翻訳されたメッセージを取得します。

        Parameters
        ----------
        key : str
            Message key.
            メッセージキー。
        **kwargs : str | int
            Format parameters for the message.
            メッセージのフォーマットパラメータ。

        Returns
        -------
        str
            Translated and formatted message.
            翻訳およびフォーマットされたメッセージ。

        Examples
        --------
        >>> i18n = I18n('en')
        >>> i18n.get('found_regions', count=5)
        'Found 5 regions'
        """
        translations: dict[str, str] = TRANSLATIONS[self.language]
        message: str = translations.get(key, key)

        if kwargs:
            return message.format(**kwargs)
        return message

    def set_language(self, language: str) -> None:
        """
        Change the current language.
        現在の言語を変更します。

        Parameters
        ----------
        language : str
            Language code to set.
            設定する言語コード。
        """
        if language in SUPPORTED_LANGUAGES:
            self.language = language
