"""
Tests for default VPC cleaner module.
デフォルトVPCクリーナーモジュールのテスト。
"""

from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from src.aws_client import AWSClient, AWSClientFactory
from src.default_vpc_cleaner import DefaultVPCCleaner
from src.i18n import I18n


@mock_aws
class TestDefaultVPCCleaner:
    """
    Test cases for DefaultVPCCleaner class.
    DefaultVPCCleanerクラスのテストケース。
    """

    def test_list_default_vpcs_found(
        self,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test listing default VPCs when found.
        デフォルトVPCが見つかった場合の一覧取得テスト。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        # Mock the describe_vpcs to return default VPC
        with patch.object(AWSClient, "describe_vpcs") as mock_describe:
            mock_describe.return_value = [
                {"VpcId": default_vpc["vpc_id"], "IsDefault": True}
            ]

            default_vpcs = cleaner.list_default_vpcs(["us-east-1"])

            assert "us-east-1" in default_vpcs
            assert default_vpcs["us-east-1"] == default_vpc["vpc_id"]

    def test_list_default_vpcs_not_found(
        self, client_factory: AWSClientFactory, i18n_en: I18n
    ) -> None:
        """
        Test listing default VPCs when not found.
        デフォルトVPCが見つからない場合の一覧取得テスト。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        with patch.object(AWSClient, "describe_vpcs") as mock_describe:
            mock_describe.return_value = []

            default_vpcs = cleaner.list_default_vpcs(["us-east-1"])

            assert len(default_vpcs) == 0

    def test_list_vpc_resources(
        self,
        aws_client: AWSClient,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test listing VPC resources.
        VPCリソースの一覧取得テスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        resources = cleaner.list_vpc_resources(
            aws_client, default_vpc["vpc_id"], "us-east-1"
        )

        # Should find IGW, Subnet, and RouteTable
        assert len(resources) >= 3

        resource_types = [r.resource_type for r in resources]
        assert "InternetGateway" in resource_types
        assert "Subnet" in resource_types
        assert "RouteTable" in resource_types

    def test_delete_vpc_resources_dry_run(
        self,
        aws_client: AWSClient,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test deleting VPC resources in dry-run mode.
        ドライランモードでのVPCリソース削除テスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        resources = cleaner.list_vpc_resources(
            aws_client, default_vpc["vpc_id"], "us-east-1"
        )

        errors: list[str] = []
        deleted_count = cleaner.delete_vpc_resources(
            aws_client,
            resources,
            default_vpc["vpc_id"],
            dry_run=True,
            errors=errors,
        )

        # In dry-run mode, nothing should be deleted
        assert deleted_count == 0

        # Verify resources still exist
        subnets = aws_client.describe_subnets(default_vpc["vpc_id"])
        assert len(subnets) >= 1

    def test_delete_vpc_resources_real_deletion(
        self,
        aws_client: AWSClient,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test actually deleting VPC resources.
        実際のVPCリソース削除テスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        resources = cleaner.list_vpc_resources(
            aws_client, default_vpc["vpc_id"], "us-east-1"
        )

        errors: list[str] = []
        deleted_count = cleaner.delete_vpc_resources(
            aws_client,
            resources,
            default_vpc["vpc_id"],
            dry_run=False,
            errors=errors,
        )

        # Should delete resources
        assert deleted_count > 0

    def test_delete_vpc_with_resources(
        self,
        aws_client: AWSClient,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test deleting a VPC with all its resources.
        VPCとそのすべてのリソースを削除するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        errors: list[str] = []
        success, deleted_count = cleaner.delete_vpc(
            aws_client,
            default_vpc["vpc_id"],
            "us-east-1",
            dry_run=False,
            errors=errors,
        )

        assert success is True
        assert deleted_count > 0

        # Verify VPC is deleted
        vpcs = aws_client.describe_vpcs(
            filters=[{"Name": "vpc-id", "Values": [default_vpc["vpc_id"]]}]
        )
        assert len(vpcs) == 0

    def test_run_with_dry_run(
        self,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test running cleaner in dry-run mode.
        ドライランモードでクリーナーを実行するテスト。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        with patch.object(cleaner, "list_default_vpcs") as mock_list:
            mock_list.return_value = {"us-east-1": default_vpc["vpc_id"]}

            with patch.object(cleaner, "delete_vpc") as mock_delete:
                # dry-run: success, 0 resources deleted
                mock_delete.return_value = (True, 0)

                result = cleaner.run(
                    regions=["us-east-1"], dry_run=True, skip_confirm=True
                )

                assert result.regions_processed == 1
                # In dry-run mode, VPCs are not counted as deleted
                assert result.vpcs_deleted == 0

    def test_run_with_confirmation_skip(
        self,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test running cleaner with confirmation skip.
        確認スキップでクリーナーを実行するテスト。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        with patch.object(cleaner, "list_default_vpcs") as mock_list:
            mock_list.return_value = {"us-east-1": default_vpc["vpc_id"]}

            with patch.object(cleaner, "delete_vpc") as mock_delete:
                # success, 5 resources deleted
                mock_delete.return_value = (True, 5)

                result = cleaner.run(
                    regions=["us-east-1"], dry_run=False, skip_confirm=True
                )

                assert result.regions_processed == 1
                assert result.vpcs_deleted == 1
                assert result.resources_deleted == 5

    def test_verbose_mode(
        self,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        Test verbose mode output.
        詳細モード出力のテスト。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        capsys : pytest.CaptureFixture[str]
            Pytest capture fixture.
            Pytestキャプチャフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=True)

        cleaner._print("Test message")

        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_non_verbose_mode(
        self,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        Test non-verbose mode output.
        非詳細モード出力のテスト。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        capsys : pytest.CaptureFixture[str]
            Pytest capture fixture.
            Pytestキャプチャフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        cleaner._print("Test message", force=False)

        captured = capsys.readouterr()
        assert "Test message" not in captured.out

    def test_delete_vpc_resources_with_error(
        self,
        aws_client: AWSClient,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test error handling during resource deletion.
        リソース削除時のエラーハンドリングのテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        resources = cleaner.list_vpc_resources(
            aws_client, default_vpc["vpc_id"], "us-east-1"
        )

        # Mock delete_subnet to raise an error
        error = ClientError(
            {
                "Error": {
                    "Code": "DependencyViolation",
                    "Message": "Test error",
                }
            },
            "DeleteSubnet",
        )

        with patch.object(aws_client, "delete_subnet", side_effect=error):
            errors: list[str] = []
            deleted_count = cleaner.delete_vpc_resources(
                aws_client,
                resources,
                default_vpc["vpc_id"],
                dry_run=False,
                errors=errors,
            )

            # Error should be recorded
            assert len(errors) > 0
            assert "Failed to delete" in errors[0]
            # Some resources might still be deleted
            assert deleted_count >= 0

    def test_delete_vpc_with_error(
        self,
        aws_client: AWSClient,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test error handling during VPC deletion.
        VPC削除時のエラーハンドリングのテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        # Mock delete_vpc to raise an error
        error = ClientError(
            {
                "Error": {
                    "Code": "DependencyViolation",
                    "Message": "Test error",
                }
            },
            "DeleteVpc",
        )

        with patch.object(aws_client, "delete_vpc", side_effect=error):
            errors: list[str] = []
            success, deleted_count = cleaner.delete_vpc(
                aws_client,
                default_vpc["vpc_id"],
                "us-east-1",
                dry_run=False,
                errors=errors,
            )

            # Operation should fail
            assert success is False
            # Error should be recorded
            assert len(errors) == 1
            assert "us-east-1" in errors[0]

    def test_run_with_deletion_errors(
        self,
        client_factory: AWSClientFactory,
        i18n_en: I18n,
        default_vpc: dict[str, str],
    ) -> None:
        """
        Test run with deletion errors.
        削除エラーが発生した場合のrun()のテスト。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        cleaner = DefaultVPCCleaner(client_factory, i18n_en, verbose=False)

        with patch.object(cleaner, "list_default_vpcs") as mock_list:
            mock_list.return_value = {"us-east-1": default_vpc["vpc_id"]}

            with patch.object(cleaner, "delete_vpc") as mock_delete:
                # Simulate failure with errors
                mock_delete.return_value = (False, 0)

                # Create a mock to add errors to the errors list
                def side_effect(client, vpc_id, region, dry_run, errors):
                    errors.append("us-east-1: DependencyViolation")
                    return (False, 0)

                mock_delete.side_effect = side_effect

                result = cleaner.run(
                    regions=["us-east-1"],
                    dry_run=False,
                    skip_confirm=True,
                )

                # Region should be processed
                assert result.regions_processed == 1
                # VPC should not be deleted
                assert result.vpcs_deleted == 0
                # No resources deleted
                assert result.resources_deleted == 0
                # Error should be recorded
                assert len(result.errors) == 1
                assert "us-east-1" in result.errors[0]
