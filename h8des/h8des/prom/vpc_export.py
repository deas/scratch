from dataclasses import dataclass
from typing import Any

from prometheus_client import REGISTRY, start_http_server
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector


def _to_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value)
    raise ValueError(f"Cannot convert {value!r} to float")


@dataclass
class VPCMetrics:
    """Extracted VPC quota metrics from deployment properties."""

    vpc_name: str
    vpc_id: str
    vm_quota_cpu_cores: float
    vm_quota_memory_mb: float
    s3_storage_quota_mb: float
    vm_quota_storage_mb: float
    file_storage_quota_mb: float
    namespace_quota_cpu_mhz: float
    namespace_quota_memory_mb: float
    namespace_quota_storage_mb: float

    @classmethod
    def from_properties(cls, properties: dict) -> "VPCMetrics":
        """Create a VPCMetrics instance from deployment properties.

        Args:
            properties: The "properties" dict from a deployment resource.

        Returns:
            VPCMetrics with all quota fields populated.
        """
        vpc = properties.get("vpc", {})
        return cls(
            vpc_name=vpc.get("name", ""),
            vpc_id=vpc.get("vpcId", ""),
            vm_quota_cpu_cores=_to_float(vpc.get("VM Quota CPU (Cores)", 0.0)),
            vm_quota_memory_mb=_to_float(vpc.get("VM Quota Memory (Mb)", 0.0)),
            s3_storage_quota_mb=_to_float(
                vpc.get("S3 Storage Quota (Mb)", 0.0)
            ),
            vm_quota_storage_mb=_to_float(
                vpc.get("VM Quota Storage (Mb)", 0.0)
            ),
            file_storage_quota_mb=_to_float(
                vpc.get("File Storage Quota (Mb)", 0.0)
            ),
            namespace_quota_cpu_mhz=_to_float(
                vpc.get("Namespace Quota CPU (Mhz)", 0.0)
            ),
            namespace_quota_memory_mb=_to_float(
                vpc.get("Namespace Quota Memory (Mb)", 0.0)
            ),
            namespace_quota_storage_mb=_to_float(
                vpc.get("Namespace Quota Storage (Mb)", 0.0)
            ),
        )

    def to_metrics(self) -> list[tuple[str, str, float]]:
        """Return list of (metric_name, description, value) tuples."""
        return [
            (
                "h8des_vpc_vm_quota_cpu_cores",
                "VM CPU quota in cores",
                self.vm_quota_cpu_cores,
            ),
            (
                "h8des_vpc_vm_quota_memory_mb",
                "VM memory quota in MB",
                self.vm_quota_memory_mb,
            ),
            (
                "h8des_vpc_s3_storage_quota_mb",
                "S3 storage quota in MB",
                self.s3_storage_quota_mb,
            ),
            (
                "h8des_vpc_vm_quota_storage_mb",
                "VM storage quota in MB",
                self.vm_quota_storage_mb,
            ),
            (
                "h8des_vpc_file_storage_quota_mb",
                "File storage quota in MB",
                self.file_storage_quota_mb,
            ),
            (
                "h8des_vpc_namespace_quota_cpu_mhz",
                "Namespace CPU quota in MHz",
                self.namespace_quota_cpu_mhz,
            ),
            (
                "h8des_vpc_namespace_quota_memory_mb",
                "Namespace memory quota in MB",
                self.namespace_quota_memory_mb,
            ),
            (
                "h8des_vpc_namespace_quota_storage_mb",
                "Namespace storage quota in MB",
                self.namespace_quota_storage_mb,
            ),
        ]


class VPCCollector(Collector):
    """On-demand collector for VPC metrics."""

    def __init__(self, metrics: VPCMetrics):
        self.metrics = metrics

    def collect(self):
        for name, description, value in self.metrics.to_metrics():
            g = GaugeMetricFamily(
                name,
                description,
                labels=["vpc_name", "vpc_id"],
            )
            g.add_metric([self.metrics.vpc_name, self.metrics.vpc_id], value)
            yield g


def serve(metrics: VPCMetrics, port: int = 8000):
    print(f"Starting up Exporter at port {port}")
    REGISTRY.register(VPCCollector(metrics))
    _, thread = start_http_server(port)
    thread.join()
