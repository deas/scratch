import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from h8des.aria.exceptions import LoginException
from h8des.aria.session import AriaSession
from h8des.prom.vpc_export import VPCMetrics
from h8des.vpc_metrics import main

TESTS_DIR = Path(__file__).parent


def load_json(filename):
    return json.loads((TESTS_DIR / filename).read_text())


@pytest.fixture
def deployment_by_id():
    return load_json("deployment-by-id.json")


class TestMain:
    @patch("h8des.vpc_metrics.serve")
    @patch("h8des.vpc_metrics.__load_args")
    def test_mock_mode_loads_static_data(
        self, mock_load_args, mock_serve, deployment_by_id
    ):
        mock_load_args.return_value = MagicMock(
            hostname="mock",
            serve_port=8001,
            username=None,
            password=None,
        )
        main()
        mock_serve.assert_called_once()
        factory = mock_serve.call_args[0][0]
        metrics = factory()
        assert isinstance(metrics, list)
        assert len(metrics) == 1
        assert isinstance(metrics[0], VPCMetrics)
        assert metrics[0].vpc_name == "vpc-name"
        assert metrics[0].vm_quota_cpu_cores == 96.0

    @patch("h8des.vpc_metrics.serve")
    @patch("h8des.vpc_metrics.__load_args")
    def test_mock_mode_requires_port(self, mock_load_args, mock_serve):
        mock_load_args.return_value = MagicMock(
            hostname="MOCK",
            serve_port=None,
            username=None,
            password=None,
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
            serve_port=8001,
        )
        main()
        mock_serve.assert_called_once()
        factory = mock_serve.call_args[0][0]
        with pytest.raises(LoginException):
            factory()

    @patch("h8des.vpc_metrics.serve")
    @patch("h8des.vpc_metrics.__load_args")
    @patch.object(AriaSession, "_AriaSession__authenticate")
    def test_live_mode_factory_fetches_deployment(
        self,
        mock_auth,
        mock_load_args,
        mock_serve,
        deployment_by_id,
    ):
        mock_load_args.return_value = MagicMock(
            hostname="example.com",
            username="user",
            password="pass",
            serve_port=8001,
        )
        main()
        mock_serve.assert_called_once()
        factory = mock_serve.call_args[0][0]
        with patch(
            "h8des.vpc_metrics.AriaDeploymentAPI.getDeploymentByType",
            return_value=[deployment_by_id],
        ):
            metrics = factory()
        assert isinstance(metrics, list)
        assert len(metrics) == 1
        assert isinstance(metrics[0], VPCMetrics)
        assert metrics[0].vpc_name == "vpc-name"
        assert metrics[0].vm_quota_cpu_cores == 96.0
