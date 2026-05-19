"""
Default VPC Cleaner module.
デフォルトVPCクリーナーモジュール。

This module provides the main logic for deleting default VPCs
and related resources.
デフォルトVPCと関連リソースを削除するメインロジックを提供します。
"""

from dataclasses import dataclass, field
from typing import Any

from botocore.exceptions import ClientError
from mypy_boto3_ec2.type_defs import (
    InternetGatewayTypeDef,
    NetworkAclTypeDef,
    RouteTableTypeDef,
    SecurityGroupTypeDef,
    SubnetTypeDef,
    VpcTypeDef,
)

from src.aws_client import AWSClient, AWSClientFactory
from src.constants import (
    RESOURCE_TYPE_IGW,
    RESOURCE_TYPE_NETWORK_ACL,
    RESOURCE_TYPE_ROUTE_TABLE,
    RESOURCE_TYPE_SECURITY_GROUP,
    RESOURCE_TYPE_SUBNET,
    RESOURCE_TYPE_VPC,
)
from src.i18n import I18n


@dataclass
class VPCResource:
    """
    Represents a VPC resource to be deleted.
    削除対象のVPCリソースを表します。

    Attributes
    ----------
    resource_type : str
        Type of the resource (e.g., 'Subnet', 'InternetGateway').
        リソースのタイプ (例: 'Subnet', 'InternetGateway')。
    resource_id : str
        Resource identifier.
        リソース識別子。
    vpc_id : str
        VPC ID this resource belongs to.
        このリソースが属するVPC ID。
    region : str
        AWS region.
        AWSリージョン。
    metadata : dict[str, Any]
        Additional resource metadata.
        追加のリソースメタデータ。
    """

    resource_type: str
    resource_id: str
    vpc_id: str
    region: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeletionResult:
    """
    Result of deletion operation.
    削除操作の結果。

    Attributes
    ----------
    regions_processed : int
        Number of regions processed.
        処理したリージョン数。
    vpcs_deleted : int
        Number of VPCs deleted.
        削除したVPC数。
    resources_deleted : int
        Number of resources deleted.
        削除したリソース数。
    errors : list[str]
        List of error messages.
        エラーメッセージのリスト。
    """

    regions_processed: int = 0
    vpcs_deleted: int = 0
    resources_deleted: int = 0
    errors: list[str] = field(default_factory=list)


class DefaultVPCCleaner:
    """
    Main class for deleting default VPCs and related resources.
    デフォルトVPCと関連リソースを削除するメインクラス。

    This class orchestrates the deletion of default VPCs across AWS regions.
    AWSリージョン全体のデフォルトVPCの削除をオーケストレートします。

    Parameters
    ----------
    client_factory : AWSClientFactory
        Factory for creating AWS clients.
        AWSクライアントを作成するファクトリ。
    i18n : I18n
        Internationalization handler.
        国際化ハンドラー。
    verbose : bool, optional
        Enable verbose output (default: False).
        詳細出力を有効にする (デフォルト: False)。

    Examples
    --------
    >>> factory = AWSClientFactory()
    >>> i18n = I18n('en')
    >>> cleaner = DefaultVPCCleaner(factory, i18n, verbose=True)
    >>> result = cleaner.run(['us-east-1'], dry_run=False, skip_confirm=False)
    """

    def __init__(
        self,
        client_factory: AWSClientFactory,
        i18n: I18n,
        verbose: bool = False,
    ) -> None:
        """
        Initialize DefaultVPCCleaner.
        DefaultVPCCleanerを初期化します。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Factory for creating AWS clients.
            AWSクライアントを作成するファクトリ。
        i18n : I18n
            Internationalization handler.
            国際化ハンドラー。
        verbose : bool, optional
            Enable verbose output.
            詳細出力を有効にする。
        """
        self.client_factory: AWSClientFactory = client_factory
        self.i18n: I18n = i18n
        self.verbose: bool = verbose

    def _print(self, message: str, force: bool = False) -> None:
        """
        Print message if verbose mode is enabled.
        詳細モードが有効な場合にメッセージを出力します。

        Parameters
        ----------
        message : str
            Message to print.
            出力するメッセージ。
        force : bool, optional
            Force print even if verbose is False.
            詳細モードでなくても強制的に出力。
        """
        if self.verbose or force:
            print(message)

    def list_default_vpcs(self, regions: list[str]) -> dict[str, str]:
        """
        List default VPCs in specified regions.
        指定されたリージョンのデフォルトVPCをリストします。

        Parameters
        ----------
        regions : list[str]
            List of region names.
            リージョン名のリスト。

        Returns
        -------
        dict[str, str]
            Dictionary mapping region names to default VPC IDs.
            リージョン名からデフォルトVPC IDへのマッピング辞書。
        """
        default_vpcs: dict[str, str] = {}

        for region in regions:
            self._print(self.i18n.get("checking_default_vpc", region=region))

            try:
                client: AWSClient = self.client_factory.create_client(region)
                vpcs: list[VpcTypeDef] = client.describe_vpcs(
                    filters=[{"Name": "isDefault", "Values": ["true"]}]
                )

                if vpcs:
                    vpc_id: str = vpcs[0].get("VpcId", "")
                    if not vpc_id:
                        continue
                    default_vpcs[region] = vpc_id
                    self._print(
                        self.i18n.get("default_vpc_found", vpc_id=vpc_id),
                        force=True,
                    )
                else:
                    self._print(self.i18n.get("no_default_vpc", region=region))

            except ClientError as e:
                self._print(
                    self.i18n.get(
                        "region_failed", region=region, error=str(e)
                    ),
                    force=True,
                )

        return default_vpcs

    def list_vpc_resources(
        self, client: AWSClient, vpc_id: str, region: str
    ) -> list[VPCResource]:
        """
        List all resources in a VPC.
        VPC内のすべてのリソースをリストします。

        Parameters
        ----------
        client : AWSClient
            AWS client for the region.
            リージョンのAWSクライアント。
        vpc_id : str
            VPC ID.
            VPC ID。
        region : str
            AWS region name.
            AWSリージョン名。

        Returns
        -------
        list[VPCResource]
            List of VPC resources.
            VPCリソースのリスト。
        """
        resources: list[VPCResource] = []

        self._print(self.i18n.get("listing_resources", vpc_id=vpc_id))

        # Internet Gateways
        try:
            igws: list[InternetGatewayTypeDef] = (
                client.describe_internet_gateways(vpc_id)
            )
            for igw in igws:
                igw_id: str = igw.get("InternetGatewayId", "")
                if not igw_id:
                    continue
                resources.append(
                    VPCResource(
                        resource_type=RESOURCE_TYPE_IGW,
                        resource_id=igw_id,
                        vpc_id=vpc_id,
                        region=region,
                        metadata={"attachments": igw.get("Attachments", [])},
                    )
                )
                self._print(
                    self.i18n.get(
                        "found_resource",
                        resource_type=RESOURCE_TYPE_IGW,
                        resource_id=igw_id,
                    )
                )
        except ClientError as e:
            self._print(f"Error listing IGWs: {e}")

        # Subnets
        try:
            subnets: list[SubnetTypeDef] = client.describe_subnets(vpc_id)
            for subnet in subnets:
                subnet_id: str = subnet.get("SubnetId", "")
                if not subnet_id:
                    continue
                resources.append(
                    VPCResource(
                        resource_type=RESOURCE_TYPE_SUBNET,
                        resource_id=subnet_id,
                        vpc_id=vpc_id,
                        region=region,
                    )
                )
                self._print(
                    self.i18n.get(
                        "found_resource",
                        resource_type=RESOURCE_TYPE_SUBNET,
                        resource_id=subnet_id,
                    )
                )
        except ClientError as e:
            self._print(f"Error listing subnets: {e}")

        # Route Tables (excluding main route table)
        try:
            route_tables: list[RouteTableTypeDef] = (
                client.describe_route_tables(vpc_id)
            )
            for rt in route_tables:
                # Skip main route table
                is_main: bool = any(
                    assoc.get("Main", False)
                    for assoc in rt.get("Associations", [])
                )
                if not is_main:
                    rt_id: str = rt.get("RouteTableId", "")
                    if not rt_id:
                        continue
                    resources.append(
                        VPCResource(
                            resource_type=RESOURCE_TYPE_ROUTE_TABLE,
                            resource_id=rt_id,
                            vpc_id=vpc_id,
                            region=region,
                        )
                    )
                    self._print(
                        self.i18n.get(
                            "found_resource",
                            resource_type=RESOURCE_TYPE_ROUTE_TABLE,
                            resource_id=rt_id,
                        )
                    )
        except ClientError as e:
            self._print(f"Error listing route tables: {e}")

        # Security Groups (excluding default security group)
        try:
            security_groups: list[SecurityGroupTypeDef] = (
                client.describe_security_groups(vpc_id)
            )
            for sg in security_groups:
                group_name: str = sg.get("GroupName", "")
                if group_name != "default":
                    sg_id: str = sg.get("GroupId", "")
                    if not sg_id:
                        continue
                    resources.append(
                        VPCResource(
                            resource_type=RESOURCE_TYPE_SECURITY_GROUP,
                            resource_id=sg_id,
                            vpc_id=vpc_id,
                            region=region,
                        )
                    )
                    self._print(
                        self.i18n.get(
                            "found_resource",
                            resource_type=RESOURCE_TYPE_SECURITY_GROUP,
                            resource_id=sg_id,
                        )
                    )
        except ClientError as e:
            self._print(f"Error listing security groups: {e}")

        # Network ACLs (excluding default ACL)
        try:
            network_acls: list[NetworkAclTypeDef] = (
                client.describe_network_acls(vpc_id)
            )
            for nacl in network_acls:
                if not nacl.get("IsDefault", False):
                    nacl_id: str = nacl.get("NetworkAclId", "")
                    if not nacl_id:
                        continue
                    resources.append(
                        VPCResource(
                            resource_type=RESOURCE_TYPE_NETWORK_ACL,
                            resource_id=nacl_id,
                            vpc_id=vpc_id,
                            region=region,
                        )
                    )
                    self._print(
                        self.i18n.get(
                            "found_resource",
                            resource_type=RESOURCE_TYPE_NETWORK_ACL,
                            resource_id=nacl_id,
                        )
                    )
        except ClientError as e:
            self._print(f"Error listing network ACLs: {e}")

        return resources

    def delete_vpc_resources(
        self,
        client: AWSClient,
        resources: list[VPCResource],
        vpc_id: str,
        dry_run: bool,
        errors: list[str],
    ) -> int:
        """
        Delete VPC resources in the correct order.
        正しい順序でVPCリソースを削除します。

        Parameters
        ----------
        client : AWSClient
            AWS client for the region.
            リージョンのAWSクライアント。
        resources : list[VPCResource]
            List of resources to delete.
            削除するリソースのリスト。
        vpc_id : str
            VPC ID.
            VPC ID。
        dry_run : bool
            If True, only list resources without deleting.
            Trueの場合、削除せずにリソースをリスト表示のみ。
        errors : list[str]
            List to append error messages.
            エラーメッセージを追加するリスト。

        Returns
        -------
        int
            Number of resources deleted.
            削除したリソース数。
        """
        deleted_count: int = 0

        # Delete in order:
        # IGW -> Subnets -> RouteTables -> SecurityGroups -> NetworkACLs
        resource_order: list[str] = [
            RESOURCE_TYPE_IGW,
            RESOURCE_TYPE_SUBNET,
            RESOURCE_TYPE_ROUTE_TABLE,
            RESOURCE_TYPE_SECURITY_GROUP,
            RESOURCE_TYPE_NETWORK_ACL,
        ]

        for resource_type in resource_order:
            for resource in [
                r for r in resources if r.resource_type == resource_type
            ]:
                try:
                    if dry_run:
                        self._print(
                            self.i18n.get(
                                "would_delete",
                                resource_type=resource.resource_type,
                                resource_id=resource.resource_id,
                            ),
                            force=True,
                        )
                    else:
                        self._delete_resource(client, resource)
                        deleted_count += 1
                        self._print(
                            self.i18n.get(
                                "resource_deleted",
                                resource_type=resource.resource_type,
                                resource_id=resource.resource_id,
                            ),
                            force=True,
                        )
                except ClientError as e:
                    error_msg: str = (
                        f"Failed to delete {resource.resource_type} "
                        f"{resource.resource_id}: {e}"
                    )
                    self._print(error_msg, force=True)
                    errors.append(error_msg)

        return deleted_count

    def _delete_resource(
        self, client: AWSClient, resource: VPCResource
    ) -> None:
        """
        Delete a single resource.
        単一のリソースを削除します。

        Parameters
        ----------
        client : AWSClient
            AWS client.
            AWSクライアント。
        resource : VPCResource
            Resource to delete.
            削除するリソース。
        """
        if resource.resource_type == RESOURCE_TYPE_IGW:
            # Detach before deleting
            self._print(
                self.i18n.get("detaching_igw", igw_id=resource.resource_id)
            )
            client.detach_internet_gateway(
                resource.resource_id, resource.vpc_id
            )
            self._print(
                self.i18n.get("igw_detached", igw_id=resource.resource_id)
            )
            self._print(
                self.i18n.get(
                    "deleting_resource",
                    resource_type=resource.resource_type,
                    resource_id=resource.resource_id,
                )
            )
            client.delete_internet_gateway(resource.resource_id)

        elif resource.resource_type == RESOURCE_TYPE_SUBNET:
            self._print(
                self.i18n.get(
                    "deleting_resource",
                    resource_type=resource.resource_type,
                    resource_id=resource.resource_id,
                )
            )
            client.delete_subnet(resource.resource_id)

        elif resource.resource_type == RESOURCE_TYPE_ROUTE_TABLE:
            self._print(
                self.i18n.get(
                    "deleting_resource",
                    resource_type=resource.resource_type,
                    resource_id=resource.resource_id,
                )
            )
            client.delete_route_table(resource.resource_id)

        elif resource.resource_type == RESOURCE_TYPE_SECURITY_GROUP:
            self._print(
                self.i18n.get(
                    "deleting_resource",
                    resource_type=resource.resource_type,
                    resource_id=resource.resource_id,
                )
            )
            client.delete_security_group(resource.resource_id)

        elif resource.resource_type == RESOURCE_TYPE_NETWORK_ACL:
            self._print(
                self.i18n.get(
                    "deleting_resource",
                    resource_type=resource.resource_type,
                    resource_id=resource.resource_id,
                )
            )
            client.delete_network_acl(resource.resource_id)

    def delete_vpc(
        self,
        client: AWSClient,
        vpc_id: str,
        region: str,
        dry_run: bool,
        errors: list[str],
    ) -> tuple[bool, int]:
        """
        Delete a VPC and all its resources.
        VPCとそのすべてのリソースを削除します。

        Parameters
        ----------
        client : AWSClient
            AWS client for the region.
            リージョンのAWSクライアント。
        vpc_id : str
            VPC ID to delete.
            削除するVPC ID。
        region : str
            AWS region name.
            AWSリージョン名。
        dry_run : bool
            If True, only list resources without deleting.
            Trueの場合、削除せずにリソースをリスト表示のみ。
        errors : list[str]
            List to append error messages.
            エラーメッセージを追加するリスト。

        Returns
        -------
        tuple[bool, int]
            Tuple of (success, deleted_count). Success is True if VPC
            was deleted, deleted_count is the number of resources
            deleted.
            (success, deleted_count)のタプル。
            successはVPCが削除された場合True、
            deleted_countは削除されたリソース数。
        """
        deleted_count: int = 0
        try:
            # List all resources in the VPC
            resources: list[VPCResource] = self.list_vpc_resources(
                client, vpc_id, region
            )

            # Delete resources
            deleted_count = self.delete_vpc_resources(
                client, resources, vpc_id, dry_run, errors
            )

            # Delete VPC itself
            if dry_run:
                self._print(
                    self.i18n.get(
                        "would_delete",
                        resource_type=RESOURCE_TYPE_VPC,
                        resource_id=vpc_id,
                    ),
                    force=True,
                )
            else:
                self._print(
                    self.i18n.get("deleting_vpc", vpc_id=vpc_id), force=True
                )
                client.delete_vpc(vpc_id)
                self._print(
                    self.i18n.get("vpc_deleted", vpc_id=vpc_id), force=True
                )
                # VPC itself counts as one resource
                deleted_count += 1

            return True, deleted_count

        except ClientError as e:
            error_msg: str = f"{region}: {str(e)}"
            self._print(
                self.i18n.get("region_failed", region=region, error=str(e)),
                force=True,
            )
            errors.append(error_msg)
            return False, deleted_count

    def run(
        self, regions: list[str] | None, dry_run: bool, skip_confirm: bool
    ) -> DeletionResult:
        """
        Run the default VPC cleaner.
        デフォルトVPCクリーナーを実行します。

        Parameters
        ----------
        regions : list[str] | None
            List of regions to process. If None, processes all regions.
            処理するリージョンのリスト。Noneの場合はすべてのリージョンを処理。
        dry_run : bool
            If True, only list resources without deleting.
            Trueの場合、削除せずにリソースをリスト表示のみ。
        skip_confirm : bool
            If True, skip confirmation prompt.
            Trueの場合、確認プロンプトをスキップ。

        Returns
        -------
        DeletionResult
            Result of the deletion operation.
            削除操作の結果。
        """
        result: DeletionResult = DeletionResult()

        # Print start message
        self._print(self.i18n.get("starting"), force=True)

        if dry_run:
            self._print(self.i18n.get("dry_run_mode"), force=True)

        # Get regions to process
        if regions is None:
            self._print(self.i18n.get("fetching_regions"), force=True)
            try:
                regions = self.client_factory.get_all_regions()
                self._print(
                    self.i18n.get("found_regions", count=len(regions)),
                    force=True,
                )
            except Exception as e:
                result.errors.append(str(e))
                return result

        # List default VPCs
        default_vpcs: dict[str, str] = self.list_default_vpcs(regions)

        if not default_vpcs:
            self._print("No default VPCs found.", force=True)
            return result

        # Confirm deletion
        if not dry_run and not skip_confirm:
            print()
            response: str = input(self.i18n.get("confirm_deletion"))
            if response.strip().lower() != self.i18n.get("confirm_yes"):
                self._print(self.i18n.get("cancelled"), force=True)
                return result

        # Process each region
        for region, vpc_id in default_vpcs.items():
            self._print(
                self.i18n.get("processing_region", region=region), force=True
            )

            try:
                client: AWSClient = self.client_factory.create_client(region)
                success: bool
                deleted_count: int
                success, deleted_count = self.delete_vpc(
                    client, vpc_id, region, dry_run, result.errors
                )

                result.regions_processed += 1
                if success and not dry_run:
                    result.vpcs_deleted += 1
                    result.resources_deleted += deleted_count

                self._print(
                    self.i18n.get("region_completed", region=region),
                    force=True,
                )

            except Exception as e:
                error_msg: str = f"{region}: {str(e)}"
                result.errors.append(error_msg)
                self._print(
                    self.i18n.get(
                        "region_failed", region=region, error=str(e)
                    ),
                    force=True,
                )

        return result
