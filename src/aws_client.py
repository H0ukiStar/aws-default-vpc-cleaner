"""
AWS Client module.
AWSクライアントモジュール。

This module provides a wrapper around boto3 for AWS API operations.
boto3をラップしてAWS API操作を提供します。
"""

from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import NoCredentialsError
from mypy_boto3_ec2.client import EC2Client
from mypy_boto3_ec2.type_defs import (
    DescribeInternetGatewaysResultTypeDef,
    DescribeNetworkAclsResultTypeDef,
    DescribeRegionsResultTypeDef,
    DescribeRouteTablesResultTypeDef,
    DescribeSecurityGroupsResultTypeDef,
    DescribeSubnetsResultTypeDef,
    DescribeVpcsResultTypeDef,
    FilterTypeDef,
    InternetGatewayTypeDef,
    NetworkAclTypeDef,
    RouteTableTypeDef,
    SecurityGroupTypeDef,
    SubnetTypeDef,
    VpcTypeDef,
)

from src.constants import MAX_RETRIES


class AWSClient:
    """
    AWS API client wrapper.
    AWS APIクライアントラッパー。

    This class wraps boto3 EC2 client operations with automatic retry
    handling using boto3's native retry configuration.
    boto3のネイティブなリトライ設定を使用して、
    EC2クライアント操作を自動リトライ機能付きでラップします。

    Parameters
    ----------
    region_name : str
        AWS region name.
        AWSリージョン名。
    session : boto3.Session | None, optional
        Boto3 session. If None, creates a new session.
        Boto3セッション。Noneの場合は新しいセッションを作成します。

    Examples
    --------
    >>> client = AWSClient('us-east-1')
    >>> vpcs = client.describe_vpcs()
    """

    def __init__(
        self, region_name: str, session: boto3.Session | None = None
    ) -> None:
        """
        Initialize AWS client.
        AWSクライアントを初期化します。

        Parameters
        ----------
        region_name : str
            AWS region name.
            AWSリージョン名。
        session : boto3.Session | None, optional
            Boto3 session.
            Boto3セッション。
        """
        self.region_name: str = region_name
        self.session: boto3.Session = session or boto3.Session()

        # Configure retry strategy
        retry_config: Config = Config(
            retries={"max_attempts": MAX_RETRIES, "mode": "standard"}
        )

        self.ec2_client: EC2Client = self.session.client(
            "ec2", region_name=region_name, config=retry_config
        )

    def describe_vpcs(
        self, filters: list[FilterTypeDef] | None = None
    ) -> list[VpcTypeDef]:
        """
        Describe VPCs in the region.
        リージョン内のVPCを取得します。

        Parameters
        ----------
        filters : list[FilterTypeDef] | None, optional
            Filters to apply.
            適用するフィルター。

        Returns
        -------
        list[VpcTypeDef]
            List of VPC descriptions.
            VPC情報のリスト。
        """
        kwargs: dict[str, Any] = {}
        if filters:
            kwargs["Filters"] = filters

        response: DescribeVpcsResultTypeDef = (
            self.ec2_client.describe_vpcs(**kwargs)
        )
        return response.get("Vpcs", [])

    def describe_subnets(self, vpc_id: str) -> list[SubnetTypeDef]:
        """
        Describe subnets in a VPC.
        VPC内のサブネットを取得します。

        Parameters
        ----------
        vpc_id : str
            VPC ID.
            VPC ID。

        Returns
        -------
        list[SubnetTypeDef]
            List of subnet descriptions.
            サブネット情報のリスト。
        """
        response: DescribeSubnetsResultTypeDef = (
            self.ec2_client.describe_subnets(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}],
            )
        )
        return response.get("Subnets", [])

    def describe_internet_gateways(
        self, vpc_id: str
    ) -> list[InternetGatewayTypeDef]:
        """
        Describe internet gateways attached to a VPC.
        VPCに接続されたインターネットゲートウェイを取得します。

        Parameters
        ----------
        vpc_id : str
            VPC ID.
            VPC ID。

        Returns
        -------
        list[InternetGatewayTypeDef]
            List of internet gateway descriptions.
            インターネットゲートウェイ情報のリスト。
        """
        response: DescribeInternetGatewaysResultTypeDef = (
            self.ec2_client.describe_internet_gateways(
                Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}],
            )
        )
        return response.get("InternetGateways", [])

    def describe_route_tables(
        self, vpc_id: str
    ) -> list[RouteTableTypeDef]:
        """
        Describe route tables in a VPC.
        VPC内のルートテーブルを取得します。

        Parameters
        ----------
        vpc_id : str
            VPC ID.
            VPC ID。

        Returns
        -------
        list[RouteTableTypeDef]
            List of route table descriptions.
            ルートテーブル情報のリスト。
        """
        response: DescribeRouteTablesResultTypeDef = (
            self.ec2_client.describe_route_tables(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}],
            )
        )
        return response.get("RouteTables", [])

    def describe_security_groups(
        self, vpc_id: str
    ) -> list[SecurityGroupTypeDef]:
        """
        Describe security groups in a VPC.
        VPC内のセキュリティグループを取得します。

        Parameters
        ----------
        vpc_id : str
            VPC ID.
            VPC ID。

        Returns
        -------
        list[SecurityGroupTypeDef]
            List of security group descriptions.
            セキュリティグループ情報のリスト。
        """
        response: DescribeSecurityGroupsResultTypeDef = (
            self.ec2_client.describe_security_groups(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}],
            )
        )
        return response.get("SecurityGroups", [])

    def describe_network_acls(
        self, vpc_id: str
    ) -> list[NetworkAclTypeDef]:
        """
        Describe network ACLs in a VPC.
        VPC内のネットワークACLを取得します。

        Parameters
        ----------
        vpc_id : str
            VPC ID.
            VPC ID。

        Returns
        -------
        list[NetworkAclTypeDef]
            List of network ACL descriptions.
            ネットワークACL情報のリスト。
        """
        response: DescribeNetworkAclsResultTypeDef = (
            self.ec2_client.describe_network_acls(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}],
            )
        )
        return response.get("NetworkAcls", [])

    def detach_internet_gateway(self, igw_id: str, vpc_id: str) -> None:
        """
        Detach internet gateway from VPC.
        VPCからインターネットゲートウェイをデタッチします。

        Parameters
        ----------
        igw_id : str
            Internet Gateway ID.
            インターネットゲートウェイID。
        vpc_id : str
            VPC ID.
            VPC ID。
        """
        self.ec2_client.detach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id,
        )

    def delete_internet_gateway(self, igw_id: str) -> None:
        """
        Delete internet gateway.
        インターネットゲートウェイを削除します。

        Parameters
        ----------
        igw_id : str
            Internet Gateway ID.
            インターネットゲートウェイID。
        """
        self.ec2_client.delete_internet_gateway(InternetGatewayId=igw_id)

    def delete_subnet(self, subnet_id: str) -> None:
        """
        Delete subnet.
        サブネットを削除します。

        Parameters
        ----------
        subnet_id : str
            Subnet ID.
            サブネットID。
        """
        self.ec2_client.delete_subnet(SubnetId=subnet_id)

    def delete_route_table(self, route_table_id: str) -> None:
        """
        Delete route table.
        ルートテーブルを削除します。

        Parameters
        ----------
        route_table_id : str
            Route Table ID.
            ルートテーブルID。
        """
        self.ec2_client.delete_route_table(RouteTableId=route_table_id)

    def delete_security_group(self, security_group_id: str) -> None:
        """
        Delete security group.
        セキュリティグループを削除します。

        Parameters
        ----------
        security_group_id : str
            Security Group ID.
            セキュリティグループID。
        """
        self.ec2_client.delete_security_group(GroupId=security_group_id)

    def delete_network_acl(self, network_acl_id: str) -> None:
        """
        Delete network ACL.
        ネットワークACLを削除します。

        Parameters
        ----------
        network_acl_id : str
            Network ACL ID.
            ネットワークACL ID。
        """
        self.ec2_client.delete_network_acl(NetworkAclId=network_acl_id)

    def delete_vpc(self, vpc_id: str) -> None:
        """
        Delete VPC.
        VPCを削除します。

        Parameters
        ----------
        vpc_id : str
            VPC ID.
            VPC ID。
        """
        self.ec2_client.delete_vpc(VpcId=vpc_id)


class AWSClientFactory:
    """
    Factory for creating AWS clients.
    AWSクライアントを作成するファクトリ。

    This class provides methods to create AWS clients and retrieve
    region information.
    AWSクライアントを作成し、リージョン情報を取得する
    メソッドを提供します。

    Examples
    --------
    >>> factory = AWSClientFactory()
    >>> regions = factory.get_all_regions()
    >>> client = factory.create_client('us-east-1')
    """

    def __init__(self, session: boto3.Session | None = None) -> None:
        """
        Initialize AWS client factory.
        AWSクライアントファクトリを初期化します。

        Parameters
        ----------
        session : boto3.Session | None, optional
            Boto3 session.
            Boto3セッション。
        """
        self.session: boto3.Session = session or boto3.Session()

    def get_all_regions(self) -> list[str]:
        """
        Get all available EC2 regions.
        利用可能なすべてのEC2リージョンを取得します。

        Returns
        -------
        list[str]
            List of region names.
            リージョン名のリスト。

        Raises
        ------
        NoCredentialsError
            If AWS credentials are not configured.
            AWS認証情報が設定されていない場合。
        """
        try:
            ec2_client: EC2Client = self.session.client(
                "ec2", region_name="us-east-1"
            )
            response: DescribeRegionsResultTypeDef = (
                ec2_client.describe_regions()
            )
            return [
                region.get("RegionName", "")
                for region in response["Regions"]
                if region.get("RegionName")
            ]
        except NoCredentialsError:
            raise NoCredentialsError(
                msg="AWS credentials not found. Please configure AWS CLI."
            )

    def create_client(self, region_name: str) -> AWSClient:
        """
        Create an AWS client for the specified region.
        指定されたリージョンのAWSクライアントを作成します。

        Parameters
        ----------
        region_name : str
            AWS region name.
            AWSリージョン名。

        Returns
        -------
        AWSClient
            AWS client instance.
            AWSクライアントインスタンス。
        """
        return AWSClient(region_name, self.session)
