import json
from pathlib import Path

import pytest

from h8des.prom.vpc_export import VPCCollector, VPCMetrics

TESTS_DIR = Path(__file__).parent


def load_json(filename):
    return json.loads((TESTS_DIR / filename).read_text())


@pytest.fixture
def sample_properties():
    raw = load_json("deployment-by-id.json")
    return raw["content"][0]["properties"]


class TestVPCMetrics:
    def test_from_properties_parses_all_quotas(self, sample_properties):
        metrics = VPCMetrics.from_properties(sample_properties)

        assert metrics.vpc_name == "vpc-name"
        assert metrics.vpc_id == "vpc-id"
        assert metrics.vm_quota_cpu_cores == 96.0
        assert metrics.vm_quota_memory_mb == 163840.0
        assert metrics.s3_storage_quota_mb == 0.0
        assert metrics.vm_quota_storage_mb == 10240000.0
        assert metrics.file_storage_quota_mb == 0.0
        assert metrics.namespace_quota_cpu_mhz == 300000.0
        assert metrics.namespace_quota_memory_mb == 4194000.0
        assert metrics.namespace_quota_storage_mb == 20000000.0

    def test_from_properties_missing_vpc_defaults_to_zero(self):
        props = {"vpc": {}}
        metrics = VPCMetrics.from_properties(props)

        assert metrics.vpc_name == ""
        assert metrics.vpc_id == ""
        assert metrics.vm_quota_cpu_cores == 0.0
        assert metrics.vm_quota_memory_mb == 0.0

    def test_from_properties_handles_numeric_strings_and_scientific(
        self, sample_properties
    ):
        metrics = VPCMetrics.from_properties(sample_properties)
        assert metrics.vm_quota_storage_mb == 10240000.0
        assert metrics.namespace_quota_storage_mb == 20000000.0

    def test_to_metrics_returns_all_entries(self, sample_properties):
        metrics = VPCMetrics.from_properties(sample_properties)
        result = metrics.to_metrics()

        assert len(result) == 8
        names = [name for name, _, _ in result]
        assert "h8des_vpc_vm_quota_cpu_cores" in names
        assert "h8des_vpc_namespace_quota_storage_mb" in names


class TestVPCCollector:
    def test_collect_yields_gauge_metric_families(self, sample_properties):
        metrics = VPCMetrics.from_properties(sample_properties)
        collector = VPCCollector(lambda: metrics)
        results = list(collector.collect())

        assert len(results) == 8
        for family in results:
            assert family.type == "gauge"
            assert family.samples[0].labels == {
                "vpc_name": "vpc-name",
                "vpc_id": "vpc-id",
            }

    def test_collect_values_match_metrics(self, sample_properties):
        metrics = VPCMetrics.from_properties(sample_properties)
        collector = VPCCollector(lambda: metrics)
        results = {r.name: r.samples[0].value for r in collector.collect()}

        assert results["h8des_vpc_vm_quota_cpu_cores"] == 96.0
        assert results["h8des_vpc_vm_quota_memory_mb"] == 163840.0
        assert results["h8des_vpc_s3_storage_quota_mb"] == 0.0
        assert results["h8des_vpc_vm_quota_storage_mb"] == 10240000.0
        assert results["h8des_vpc_file_storage_quota_mb"] == 0.0
        assert results["h8des_vpc_namespace_quota_cpu_mhz"] == 300000.0
        assert results["h8des_vpc_namespace_quota_memory_mb"] == 4194000.0
        assert results["h8des_vpc_namespace_quota_storage_mb"] == 20000000.0

    def test_collect_calls_factory_on_every_scrape(self, sample_properties):
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return VPCMetrics.from_properties(sample_properties)

        collector = VPCCollector(factory)
        list(collector.collect())
        list(collector.collect())
        assert call_count == 2
