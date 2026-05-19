"""
Tests for AWS client module.
AWSクライアントモジュールのテスト。
"""

from moto import mock_aws

from src.aws_client import AWSClient, AWSClientFactory


class TestAWSClient:
    """
    Test cases for AWSClient class.
    AWSClientクラスのテストケース。
    """

    def test_describe_vpcs_no_filters(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test describing VPCs without filters.
        フィルターなしでVPCを取得するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        vpcs = aws_client.describe_vpcs()
        assert len(vpcs) > 0
        assert any(
            vpc.get("VpcId") == default_vpc["vpc_id"] for vpc in vpcs
        )

    def test_describe_vpcs_with_filters(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test describing VPCs with filters.
        フィルター付きでVPCを取得するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        vpcs = aws_client.describe_vpcs(
            filters=[{"Name": "vpc-id", "Values": [default_vpc["vpc_id"]]}]
        )
        assert len(vpcs) == 1
        assert vpcs[0].get("VpcId") == default_vpc["vpc_id"]

    def test_describe_subnets(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test describing subnets.
        サブネットを取得するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        subnets = aws_client.describe_subnets(default_vpc["vpc_id"])
        assert len(subnets) >= 1
        assert any(
            subnet.get("SubnetId") == default_vpc["subnet_id"]
            for subnet in subnets
        )

    def test_describe_internet_gateways(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test describing internet gateways.
        インターネットゲートウェイを取得するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        igws = aws_client.describe_internet_gateways(default_vpc["vpc_id"])
        assert len(igws) >= 1
        assert any(
            igw.get("InternetGatewayId") == default_vpc["igw_id"]
            for igw in igws
        )

    def test_describe_route_tables(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test describing route tables.
        ルートテーブルを取得するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        route_tables = aws_client.describe_route_tables(default_vpc["vpc_id"])
        assert len(route_tables) >= 1

    def test_describe_security_groups(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test describing security groups.
        セキュリティグループを取得するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        security_groups = aws_client.describe_security_groups(
            default_vpc["vpc_id"]
        )
        assert len(security_groups) >= 1

    def test_describe_network_acls(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test describing network ACLs.
        ネットワークACLを取得するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        network_acls = aws_client.describe_network_acls(default_vpc["vpc_id"])
        assert len(network_acls) >= 1

    def test_delete_subnet(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test deleting a subnet.
        サブネットを削除するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        aws_client.delete_subnet(default_vpc["subnet_id"])

        subnets = aws_client.describe_subnets(default_vpc["vpc_id"])
        assert not any(
            subnet.get("SubnetId") == default_vpc["subnet_id"]
            for subnet in subnets
        )

    def test_detach_and_delete_internet_gateway(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test detaching and deleting an internet gateway.
        インターネットゲートウェイをデタッチして削除するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        aws_client.detach_internet_gateway(
            default_vpc["igw_id"], default_vpc["vpc_id"]
        )
        aws_client.delete_internet_gateway(default_vpc["igw_id"])

        igws = aws_client.describe_internet_gateways(default_vpc["vpc_id"])
        assert len(igws) == 0

    def test_delete_route_table(
        self, aws_client: AWSClient, default_vpc: dict[str, str]
    ) -> None:
        """
        Test deleting a route table.
        ルートテーブルを削除するテスト。

        Parameters
        ----------
        aws_client : AWSClient
            AWS client fixture.
            AWSクライアントフィクスチャー。
        default_vpc : dict[str, str]
            Default VPC fixture.
            デフォルトVPCフィクスチャー。
        """
        aws_client.delete_route_table(default_vpc["rt_id"])

        route_tables = aws_client.describe_route_tables(default_vpc["vpc_id"])
        assert not any(
            rt.get("RouteTableId") == default_vpc["rt_id"]
            for rt in route_tables
        )


@mock_aws
class TestAWSClientFactory:
    """
    Test cases for AWSClientFactory class.
    AWSClientFactoryクラスのテストケース。
    """

    def test_get_all_regions(self, client_factory: AWSClientFactory) -> None:
        """
        Test getting all regions.
        すべてのリージョンを取得するテスト。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        """
        regions = client_factory.get_all_regions()
        assert len(regions) > 0
        assert "us-east-1" in regions

    def test_create_client(self, client_factory: AWSClientFactory) -> None:
        """
        Test creating a client.
        クライアントを作成するテスト。

        Parameters
        ----------
        client_factory : AWSClientFactory
            Client factory fixture.
            クライアントファクトリフィクスチャー。
        """
        client = client_factory.create_client("us-east-1")
        assert isinstance(client, AWSClient)
        assert client.region_name == "us-east-1"
