import re
from unittest.mock import patch

import pytest
import requests_mock

from h8des.aria.deployment import AriaDeploymentAPI
from h8des.aria.session import AriaSession

DEPLOYMENT_RESOURCES_URL = re.compile(
    r"https://example\.com/deployment/api/deployments/(?P<id>[^/]+)/resources$"
)


@pytest.fixture
def session():
    with patch.object(AriaSession, "_AriaSession__authenticate"):
        return AriaSession("example.com", "user", "pass")


def mock_login(m, load_json):
    m.post(
        "https://example.com/csp/gateway/am/api/login?access_token",
        json=load_json("refresh-token.json"),
    )
    m.post(
        "https://example.com/iaas/api/login",
        json={"tokenType": "Bearer", "token": "access-token"},
    )


def test_get_deployment_by_type(session, load_json):
    deployment_by_type = load_json("deployment-by-type.json")

    def deployment_by_id_response(request, context):
        match = DEPLOYMENT_RESOURCES_URL.match(request.url)
        return load_json(f"deployment-{match.group('id')}.json")

    with requests_mock.Mocker() as m:
        mock_login(m, load_json)
        m.get(
            "https://example.com/deployment/api/deployments?resourceType=Custom.vpc",
            json=deployment_by_type,
        )
        m.get(DEPLOYMENT_RESOURCES_URL, json=deployment_by_id_response)

        api = AriaDeploymentAPI(session)
        result = api.getDeploymentByType()

    assert result == [
        load_json("deployment-7b6fa433.json"),
        load_json("deployment-c6795882.json"),
    ]


def test_get_deployment_by_type_not_found(session, load_json):
    with requests_mock.Mocker() as m:
        mock_login(m, load_json)
        m.get(
            "https://example.com/deployment/api/deployments?resourceType=Custom.vpc",
            json={"content": [], "totalElements": 0},
        )

        api = AriaDeploymentAPI(session)
        result = api.getDeploymentByType()

    assert result == []


def test_get_deployment_by_type_no_resources(session, load_json):
    deployment_by_type = load_json("deployment-by-type.json")

    with requests_mock.Mocker() as m:
        mock_login(m, load_json)
        m.get(
            "https://example.com/deployment/api/deployments?resourceType=Custom.vpc",
            json=deployment_by_type,
        )

        api = AriaDeploymentAPI(session)
        result = api.getDeploymentByType(resources=False)

    assert result == deployment_by_type["content"]
