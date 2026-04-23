import time
from datetime import datetime, timezone

from prometheus_client import Gauge, start_http_server

from h8des.aria.session import AriaSession

# from kubernetes import client, config


def sample():
    return 0.1

    # return transform_timestamp_to_seconds(expiry)


def transform_timestamp_to_seconds(timestamp_input):
    dt = datetime.strptime(timestamp_input, "%Y-%m-%dT%H:%M:%SZ")
    dt = dt.replace(tzinfo=timezone.utc)

    unix_time = int(dt.timestamp())

    now = int(time.time())

    return unix_time - now


def serve(args: dict, port: int = 8000):
    print("Starting up Exporter at port %d" % port)
    # AriaSession(args["hostname"], args["username"], args["password"])
    # labelset = ["a", "b", "c"]
    # gauge_sample = Gauge("h8des_intern_vpc", "The ...", labelset)
    start_http_server(port)
    # print("Started up server on port 8000")

    # print("Start looping over metric gathering")
    # while True:
    #    gauge_sample.labels(a="a1", b="b1", c="c1").set(sample())
