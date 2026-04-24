import json
from pathlib import Path
from unittest.mock import patch

import pytest
import requests_mock

from h8des.aria.deployment import AriaDeploymentAPI
from h8des.aria.session import AriaSession

TESTS_DIR = Path(__file__).parent


@pytest.fixture
def session():
    with patch.object(AriaSession, "_AriaSession__authenticate"):
        return AriaSession("example.com", "user", "pass")


def load_json(filename):
    return json.loads((TESTS_DIR / filename).read_text())


def test_get_deployment_by_type(session):
    refresh_token = load_json("refresh-token.json")
    deployment_by_type = load_json("deployment-by-type.json")
    deployment_by_id = load_json("deployment-by-id.json")

    with requests_mock.Mocker() as m:
        m.post(
            "https://example.com/csp/gateway/am/api/login?access_token",
            json=refresh_token,
        )
        m.post(
            "https://example.com/iaas/api/login",
            json={"tokenType": "Bearer", "token": "access-token"},
        )
        m.get(
            "https://example.com/deployment/api/deployments?resourceType=Custom.vpc",
            json=deployment_by_type,
        )
        m.get(
            "https://example.com/deployment/api/deployments/7b6fa433/resources",
            json=deployment_by_id,
        )
        m.get(
            "https://example.com/deployment/api/deployments/c6795882/resources",
            json=deployment_by_id,
        )

        api = AriaDeploymentAPI(session)
        result = api.getDeploymentByType()

    assert result == [deployment_by_id, deployment_by_id]


def test_get_deployment_by_type_not_found(session):
    refresh_token = load_json("refresh-token.json")

    with requests_mock.Mocker() as m:
        m.post(
            "https://example.com/csp/gateway/am/api/login?access_token",
            json=refresh_token,
        )
        m.post(
            "https://example.com/iaas/api/login",
            json={"tokenType": "Bearer", "token": "access-token"},
        )
        m.get(
            "https://example.com/deployment/api/deployments?resourceType=Custom.vpc",
            json={"content": [], "totalElements": 0},
        )

        api = AriaDeploymentAPI(session)
        result = api.getDeploymentByType()

    assert result == []


def test_get_deployment_by_type_no_resources(session):
    refresh_token = load_json("refresh-token.json")
    deployment_by_type = load_json("deployment-by-type.json")

    with requests_mock.Mocker() as m:
        m.post(
            "https://example.com/csp/gateway/am/api/login?access_token",
            json=refresh_token,
        )
        m.post(
            "https://example.com/iaas/api/login",
            json={"tokenType": "Bearer", "token": "access-token"},
        )
        m.get(
            "https://example.com/deployment/api/deployments?resourceType=Custom.vpc",
            json=deployment_by_type,
        )

        api = AriaDeploymentAPI(session)
        result = api.getDeploymentByType(resources=False)

    assert result == deployment_by_type["content"]
