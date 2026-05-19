"""
Main entry point for AWS Default VPC Cleaner.
AWS Default VPC Cleanerのメインエントリーポイント。

This module provides the command-line interface for the tool.
ツールのコマンドラインインターフェースを提供します。
"""

import argparse
import sys
from typing import Any

from botocore.exceptions import NoCredentialsError

from src.aws_client import AWSClientFactory
from src.constants import (
    EXIT_ERROR,
    EXIT_SUCCESS,
    EXIT_USER_CANCELLED,
    SUPPORTED_LANGUAGES,
)
from src.default_vpc_cleaner import DefaultVPCCleaner
from src.i18n import I18n


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    コマンドライン引数を解析します。

    Returns
    -------
    argparse.Namespace
        Parsed arguments.
        解析された引数。
    """
    # Create temporary i18n for help text
    temp_i18n: I18n = I18n()

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="aws-default-vpc-cleaner",
        description=temp_i18n.get("app_description"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / 使用例:
  # Delete default VPCs in all regions (with confirmation)
  # 全リージョンのデフォルトVPCを削除 (確認あり)
  aws-default-vpc-cleaner

  # Delete default VPCs in specific regions
  # 特定リージョンのデフォルトVPCを削除
  aws-default-vpc-cleaner --regions us-east-1 us-west-2

  # List default VPCs without deleting (dry-run)
  # 削除せずにデフォルトVPCをリストアップ (ドライラン)
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
        """,
    )

    parser.add_argument(
        "--regions",
        nargs="+",
        metavar="REGION",
        help=temp_i18n.get("arg_regions"),
    )

    parser.add_argument(
        "--dry-run", action="store_true", help=temp_i18n.get("arg_dry_run")
    )

    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        dest="skip_confirm",
        help=temp_i18n.get("arg_yes"),
    )

    parser.add_argument(
        "--lang",
        choices=SUPPORTED_LANGUAGES,
        default=None,
        help=temp_i18n.get("arg_lang"),
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=temp_i18n.get("arg_verbose"),
    )

    parser.add_argument(
        "--version", action="version", version="%(prog)s 1.0.0"
    )

    return parser.parse_args()


def print_summary(result: Any, i18n: I18n) -> None:
    """
    Print operation summary.
    操作のサマリーを出力します。

    Parameters
    ----------
    result : DeletionResult
        Result of the deletion operation.
        削除操作の結果。
    i18n : I18n
        Internationalization handler.
        国際化ハンドラー。
    """
    print()
    print(i18n.get("summary_title"))
    print(
        i18n.get("summary_regions_processed", count=result.regions_processed)
    )
    print(i18n.get("summary_vpcs_deleted", count=result.vpcs_deleted))
    print(
        i18n.get("summary_resources_deleted", count=result.resources_deleted)
    )
    print(i18n.get("summary_errors", count=len(result.errors)))

    if result.errors:
        print()
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")


def main() -> int:
    """
    Main function.
    メイン関数。

    Returns
    -------
    int
        Exit code.
        終了コード。
    """
    # Parse arguments
    args: argparse.Namespace = parse_args()

    # Initialize i18n
    i18n: I18n = I18n(args.lang)

    try:
        # Create AWS client factory
        client_factory: AWSClientFactory = AWSClientFactory()

        # Validate regions if specified
        if args.regions:
            all_regions: list[str] = client_factory.get_all_regions()
            invalid_regions: list[str] = [
                r for r in args.regions if r not in all_regions
            ]
            if invalid_regions:
                for region in invalid_regions:
                    print(
                        i18n.get("error_region_unavailable", region=region),
                        file=sys.stderr,
                    )
                return EXIT_ERROR

        # Create cleaner
        cleaner: DefaultVPCCleaner = DefaultVPCCleaner(
            client_factory=client_factory, i18n=i18n, verbose=args.verbose
        )

        # Run cleaner
        from src.default_vpc_cleaner import DeletionResult

        result: DeletionResult = cleaner.run(
            regions=args.regions,
            dry_run=args.dry_run,
            skip_confirm=args.skip_confirm,
        )

        # Print summary
        print_summary(result, i18n)

        # Determine exit code
        if result.errors:
            print()
            print(i18n.get("error", error="Some operations failed"))
            return EXIT_ERROR

        print()
        print(i18n.get("completed"))
        return EXIT_SUCCESS

    except NoCredentialsError:
        print(i18n.get("error_no_credentials"), file=sys.stderr)
        return EXIT_ERROR

    except KeyboardInterrupt:
        print()
        print(i18n.get("cancelled"))
        return EXIT_USER_CANCELLED

    except Exception as e:
        print(i18n.get("error", error=str(e)), file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
