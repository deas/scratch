import json
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


def _load_json(filename):
    return json.loads((TESTS_DIR / filename).read_text())


@pytest.fixture
def load_json():
    return _load_json


@pytest.fixture
def deployment_by_id():
    def loader(deployment_id):
        return _load_json(f"deployment-{deployment_id}.json")

    return loader


@pytest.fixture
def sample_properties(deployment_by_id):
    return deployment_by_id("c6795882")["content"][0]["properties"]
