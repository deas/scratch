import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from h8des.aria.deployment import AriaDeploymentAPI
from h8des.aria.exceptions import DeploymentNotFoundException, LoginException
from h8des.aria.session import AriaSession
from h8des.prom.vpc_export import VPCMetrics
from h8des.vpc_metrics import fetch_vpc_metrics, main

TESTS_DIR = Path(__file__).parent


def load_json(filename):
    return json.loads((TESTS_DIR / filename).read_text())


@pytest.fixture
def deployment_by_id():
    return load_json("deployment-by-id.json")


@pytest.fixture
def session():
    with patch.object(AriaSession, "_AriaSession__authenticate"):
        return AriaSession("example.com", "user", "pass")


class TestFetchVpcMetrics:
    def test_returns_metrics_from_deployment(self, session, deployment_by_id):
        api = AriaDeploymentAPI(session)
        with patch.object(
            api, "getDeploymentByName", return_value=deployment_by_id
        ):
            metrics = fetch_vpc_metrics(api, "test-deployment")
            assert isinstance(metrics, VPCMetrics)
            assert metrics.vpc_name == "vpc-name"
            assert metrics.vm_quota_cpu_cores == 96.0

    def test_raises_on_not_found(self, session):
        api = AriaDeploymentAPI(session)
        with patch.object(
            api,
            "getDeploymentByName",
            side_effect=DeploymentNotFoundException("not found"),
        ):
            with pytest.raises(DeploymentNotFoundException):
                fetch_vpc_metrics(api, "missing")


class TestMain:
    @patch("h8des.vpc_metrics.serve")
    @patch("h8des.vpc_metrics.__load_args")
    def test_mock_mode_loads_static_data(
        self, mock_load_args, mock_serve, deployment_by_id
    ):
        mock_load_args.return_value = MagicMock(
            hostname="MOCK",
            srv_port=8001,
            username=None,
            password=None,
            deployment=None,
        )
        main()
        mock_serve.assert_called_once()
        metrics = mock_serve.call_args[0][0]
        assert isinstance(metrics, VPCMetrics)
        assert metrics.vpc_name == "vpc-name"
        assert metrics.vm_quota_cpu_cores == 96.0

    @patch("h8des.vpc_metrics.serve")
    @patch("h8des.vpc_metrics.__load_args")
    def test_mock_mode_requires_port(self, mock_load_args, mock_serve):
        mock_load_args.return_value = MagicMock(
            hostname="MOCK",
            srv_port=None,
            username=None,
            password=None,
            deployment=None,
        )
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        mock_serve.assert_not_called()

    @patch("h8des.vpc_metrics.serve")
    @patch("h8des.vpc_metrics.__load_args")
    @patch.object(AriaSession, "_AriaSession__authenticate")
    def test_live_mode_requires_deployment(
        self, mock_auth, mock_load_args, mock_serve
    ):
        mock_load_args.return_value = MagicMock(
            hostname="example.com",
            username="user",
            password="pass",
            srv_port=8001,
            deployment=None,
        )
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        mock_serve.assert_not_called()

    @patch("h8des.vpc_metrics.serve")
    @patch("h8des.vpc_metrics.__load_args")
    @patch.object(AriaSession, "_AriaSession__authenticate")
    def test_live_mode_login_failure(
        self, mock_auth, mock_load_args, mock_serve
    ):
        mock_auth.side_effect = LoginException("bad creds")
        mock_load_args.return_value = MagicMock(
            hostname="example.com",
            username="user",
            password="pass",
            srv_port=8001,
            deployment="test",
        )
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        mock_serve.assert_not_called()

    @patch("h8des.vpc_metrics.serve")
    @patch("h8des.vpc_metrics.__load_args")
    @patch("h8des.vpc_metrics.fetch_vpc_metrics")
    @patch.object(AriaSession, "_AriaSession__authenticate")
    def test_live_mode_deployment_not_found(
        self, mock_auth, mock_fetch, mock_load_args, mock_serve
    ):
        mock_fetch.side_effect = DeploymentNotFoundException("not found")
        mock_load_args.return_value = MagicMock(
            hostname="example.com",
            username="user",
            password="pass",
            srv_port=8001,
            deployment="missing",
        )
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        mock_serve.assert_not_called()

    @patch("h8des.vpc_metrics.serve")
    @patch("h8des.vpc_metrics.__load_args")
    @patch("h8des.vpc_metrics.fetch_vpc_metrics")
    @patch.object(AriaSession, "_AriaSession__authenticate")
    def test_live_mode_success(
        self,
        mock_auth,
        mock_fetch,
        mock_load_args,
        mock_serve,
        deployment_by_id,
    ):
        mock_fetch.return_value = VPCMetrics.from_properties(
            deployment_by_id["content"][0]["properties"]
        )
        mock_load_args.return_value = MagicMock(
            hostname="example.com",
            username="user",
            password="pass",
            srv_port=8001,
            deployment="test",
        )
        main()
        mock_serve.assert_called_once()
        metrics = mock_serve.call_args[0][0]
        assert isinstance(metrics, VPCMetrics)
