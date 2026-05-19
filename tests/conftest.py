"""
Pytest configuration and shared fixtures.
Pytest設定と共有フィクスチャー。
"""

from typing import Any

import boto3
import pytest
from moto import mock_aws

from src.aws_client import AWSClient, AWSClientFactory
from src.i18n import I18n


@pytest.fixture
def aws_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock AWS credentials for moto.
    moto用のモックAWS認証情報。

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest monkeypatch fixture.
        Pytestのmonkeypatchフィクスチャー。
    """
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def mock_ec2(aws_credentials: None) -> Any:
    """
    Create mock EC2 service.
    モックEC2サービスを作成します。

    Parameters
    ----------
    aws_credentials : None
        AWS credentials fixture.
        AWS認証情報フィクスチャー。

    Yields
    ------
    Any
        Mock EC2 service.
        モックEC2サービス。
    """
    with mock_aws():
        yield boto3.client("ec2", region_name="us-east-1")


@pytest.fixture
def aws_client(mock_ec2: Any) -> AWSClient:
    """
    Create AWS client for testing.
    テスト用のAWSクライアントを作成します。

    Parameters
    ----------
    mock_ec2 : Any
        Mock EC2 service.
        モックEC2サービス。

    Returns
    -------
    AWSClient
        AWS client instance.
        AWSクライアントインスタンス。
    """
    return AWSClient("us-east-1")


@pytest.fixture
def client_factory(aws_credentials: None) -> AWSClientFactory:
    """
    Create AWS client factory for testing.
    テスト用のAWSクライアントファクトリを作成します。

    Parameters
    ----------
    aws_credentials : None
        AWS credentials fixture.
        AWS認証情報フィクスチャー。

    Returns
    -------
    AWSClientFactory
        AWS client factory instance.
        AWSクライアントファクトリインスタンス。
    """
    return AWSClientFactory()


@pytest.fixture
def i18n_en() -> I18n:
    """
    Create English I18n instance.
    英語のI18nインスタンスを作成します。

    Returns
    -------
    I18n
        I18n instance configured for English.
        英語に設定されたI18nインスタンス。
    """
    return I18n("en")


@pytest.fixture
def i18n_ja() -> I18n:
    """
    Create Japanese I18n instance.
    日本語のI18nインスタンスを作成します。

    Returns
    -------
    I18n
        I18n instance configured for Japanese.
        日本語に設定されたI18nインスタンス。
    """
    return I18n("ja")


@pytest.fixture
def default_vpc(mock_ec2: Any) -> dict[str, str]:
    """
    Create a default VPC with resources for testing.
    テスト用のリソースを持つデフォルトVPCを作成します。

    Parameters
    ----------
    mock_ec2 : Any
        Mock EC2 service.
        モックEC2サービス。

    Returns
    -------
    dict[str, str]
        Dictionary containing created resource IDs.
        作成されたリソースIDを含む辞書。
    """
    # Create VPC
    vpc_response = mock_ec2.create_vpc(CidrBlock="10.0.0.0/16")
    vpc_id = vpc_response["Vpc"]["VpcId"]

    # Mark as default VPC
    mock_ec2.modify_vpc_attribute(
        VpcId=vpc_id, EnableDnsHostnames={"Value": True}
    )

    # Create subnet
    subnet_response = mock_ec2.create_subnet(
        VpcId=vpc_id, CidrBlock="10.0.1.0/24"
    )
    subnet_id = subnet_response["Subnet"]["SubnetId"]

    # Create and attach internet gateway
    igw_response = mock_ec2.create_internet_gateway()
    igw_id = igw_response["InternetGateway"]["InternetGatewayId"]
    mock_ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

    # Create route table
    rt_response = mock_ec2.create_route_table(VpcId=vpc_id)
    rt_id = rt_response["RouteTable"]["RouteTableId"]

    return {
        "vpc_id": vpc_id,
        "subnet_id": subnet_id,
        "igw_id": igw_id,
        "rt_id": rt_id,
    }
