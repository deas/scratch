import time

from prometheus_client import REGISTRY, start_http_server
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector


class VPCCollector(Collector):
    """On-demand collector for VPC metrics."""

    def collect(self):
        g = GaugeMetricFamily(
            "h8des_intern_vpc",
            "The ...",
            labels=["a", "b", "c"],
        )
        g.add_metric(["a1", "b1", "c1"], 0.1)
        yield g


def serve(args: dict, port: int = 8000):
    print(f"Starting up Exporter at port {port}")
    REGISTRY.register(VPCCollector())
    start_http_server(port)

    while True:
        time.sleep(1)
