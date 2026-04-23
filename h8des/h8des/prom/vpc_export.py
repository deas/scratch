import time
from datetime import datetime, timezone

from prometheus_client import Gauge, start_http_server

# from kubernetes import client, config


def sample():
    """ """
    return 0.1

    # return transform_timestamp_to_seconds(expiry)


def transform_timestamp_to_seconds(timestamp_input):
    """Function to transform a timestamp of type YYYY-mm-ddTHH:MM:SSZ into seconds
    Args:
        timestamp_input (str): timestamp to transform

    Returns:
        result: formatted timestamp as seconds
    """

    dt = datetime.strptime(timestamp_input, "%Y-%m-%dT%H:%M:%SZ")
    dt = dt.replace(tzinfo=timezone.utc)

    unix_time = int(dt.timestamp())

    now = int(time.time())

    return unix_time - now


if __name__ == "__main__":
    print("Starting up Exporter")
    labelset = ["a", "b", "c"]
    gauge_sample = Gauge("h8des_intern_vpc", "The ...", labelset)
    start_http_server(8000)
    print("Started up server on port 8000")

    print("Start looping over metric gathering")
    while True:
        gauge_sample.labels(a="a1", b="b1", c="c1").set(sample())
