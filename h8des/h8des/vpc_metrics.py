# -*- coding: utf-8 -*-

import json
from argparse import ArgumentParser, Namespace
from os import environ
from pathlib import Path
from sys import exit, stderr

from h8des.aria.deployment import AriaDeploymentAPI
from h8des.aria.exceptions import LoginException
from h8des.aria.session import AriaSession
from h8des.prom.vpc_export import VPCMetrics, serve


def main() -> None:
    """Entry point for the VPC metrics exporter."""
    args = __load_args()

    if args.serve_port is None:
        __exit_error(
            "Port is required (use -s/--serve-port or set SERVE_PORT)"
        )

    if args.hostname == "mock":
        tests_dir = Path(__file__).parent.parent / "tests"
        raw = json.loads((tests_dir / "deployment-by-id.json").read_text())
        properties = raw["content"][0]["properties"]

        def _metrics_factory() -> VPCMetrics:
            return VPCMetrics.from_properties(properties)
    else:
        if not args.hostname:
            __exit_error(
                "Hostname is required (use -H/--hostname or set ARIA_HOSTNAME)"
            )
        if not args.username:
            __exit_error(
                "Username is required (use -u/--username or set ARIA_USERNAME)"
            )
        if not args.password:
            __exit_error(
                "Password is required (use -p/--password or set ARIA_PASSWORD)"
            )
        if not args.deployment:
            __exit_error(
                "Deployment name is required in live mode (use -d/--deployment)"
            )

        try:
            session = AriaSession(args.hostname, args.username, args.password)
        except LoginException:
            __exit_error(
                "Could not login to '%s' with user '%s'"
                % (args.hostname, args.username)
            )

        api = AriaDeploymentAPI(session)

        def _metrics_factory() -> VPCMetrics:
            deployment = api.getDeploymentByName(args.deployment)
            props = deployment["content"][0]["properties"]
            return VPCMetrics.from_properties(props)

    serve(_metrics_factory, args.serve_port)


def __load_args() -> Namespace:
    parser = ArgumentParser(
        description="This tool connects to VMware Aria and allows you to order and manage deployments",
        epilog="The Aria Client is developed and maintained by the HADES team.",
    )
    parser.add_argument(
        "-s",
        "--serve-port",
        dest="serve_port",
        help="Port, defaults to env.SERVE_PORT",
        metavar="SERVE_PORT",
        default=environ.get("SERVE_PORT"),
        type=int,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        dest="hostname",
        help="Aria hostname, defaults to env.ARIA_HOSTNAME. Use MOCK for static test data.",
        metavar="ARIA_HOSTNAME",
        default=environ.get("ARIA_HOSTNAME"),
        type=str,
    )
    parser.add_argument(
        "-u",
        "--username",
        dest="username",
        help="Aria username, defaults to env.ARIA_USERNAME",
        metavar="ARIA_USERNAME",
        default=environ.get("ARIA_USERNAME"),
        type=str,
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        help="Aria password, defaults to env.ARIA_PASSWORD",
        metavar="ARIA_PASSWORD",
        default=environ.get("ARIA_PASSWORD"),
        type=str,
    )
    parser.add_argument(
        "-P",
        "--project",
        dest="project",
        help="Aria project, defaults to env.ARIA_PROJECT",
        metavar="ARIA_PROJECT",
        default=environ.get("ARIA_PROJECT"),
        type=str,
    )
    parser.add_argument(
        "-d",
        "--deployment",
        dest="deployment",
        help="Name of Deployment",
        metavar="DEPLOYMENT",
        type=str,
    )

    return parser.parse_args()


def __exit_error(msg: str) -> None:
    print(json.dumps({"error": msg}, indent=4), file=stderr)
    exit(1)


def __exit_okay(out: dict) -> None:
    print(json.dumps(out, indent=4))
    exit(0)


if __name__ == "__main__":
    main()
