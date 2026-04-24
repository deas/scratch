# -*- coding: utf-8 -*-

# from time import sleep
import json
from argparse import ArgumentParser, Namespace  # , FileType
from os import environ
from pathlib import Path
from sys import exit, stderr

# from h8des.aria.session import AriaSession
from h8des.prom.vpc_export import VPCMetrics, serve


def main() -> None:
    """ """
    # args = __load_args()

    # session: AriaSession | None = None

    # try:
    #     session = AriaSession(
    #         args["hostname"], args["username"], args["password"]
    #     )
    # except LoginException:
    #     __exit_error(
    #         "Could not login to '%s' with user '%s'"
    #         % (args["hostname"], args["username"])
    #     )

    # Load test deployment data from JSON file
    tests_dir = Path(__file__).parent.parent / "tests"
    raw = json.loads((tests_dir / "deployment-by-id.json").read_text())
    properties = raw["content"][0]["properties"]
    metrics = VPCMetrics.from_properties(properties)
    serve(metrics, 8001)


def __load_args() -> Namespace:
    parser = ArgumentParser(
        description="This tool connects to VMware Aria and allows you to order and manage deployments",
        epilog="The Aria Client is developed and maintained by the HADES team.",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        help="Port, defaults to env.SRV_PORT",
        metavar="SRV_PORT",
        default=environ.get("SRV_PORT"),
        required=(environ.get("SRV_PORT") is None),
        type=int,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        dest="hostname",
        help="Aria hostname, defaults to env.ARIA_HOSTNAME",
        metavar="ARIA_HOSTNAME",
        default=environ.get("ARIA_HOSTNAME"),
        required=(environ.get("ARIA_HOSTNAME") is None),
        type=str,
    )
    parser.add_argument(
        "-u",
        "--username",
        dest="username",
        help="Aria username, defaults to env.ARIA_USERNAME",
        metavar="ARIA_USERNAME",
        default=environ.get("ARIA_USERNAME"),
        required=(environ.get("ARIA_USERNAME") is None),
        type=str,
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        help="Aria password, defaults to env.ARIA_PASSWORD",
        metavar="ARIA_PASSWORD",
        default=environ.get("ARIA_PASSWORD"),
        required=(environ.get("ARIA_PASSWORD") is None),
        type=str,
    )
    parser.add_argument(
        "-P",
        "--project",
        dest="project",
        help="Aria project, required when action=create, defaults to env.ARIA_PROJECT",
        metavar="ARIA_PROJECT",
        default=environ.get("ARIA_PROJECT"),
        required=False,
        type=str,
    )
    # parser.add_argument(
    #     "-a",
    #     "--action",
    #     dest="action",
    #     help="Action to execute [access_token, deployment, serve]",
    #     metavar="ACTION",
    #     required=True,
    #     type=str,
    #     choices=["access_token", "deployment", "serve"],
    # )
    parser.add_argument(
        "-d",
        "--deployment",
        dest="deployment",
        help="Name of Deyployment",
        metavar="DEPLOYMENT",
        # required=True,
        type=str,
    )

    args = parser.parse_args()

    # check args
    if args.action in ["create", "getProject"]:
        if not args.project:
            pass
    # if args.action in ["create", "update"]:

    return args


def __exit_error(msg: str) -> None:
    print(json.dumps({"error": msg}, indent=4), file=stderr)
    exit(1)


def __exit_okay(out: dict) -> None:
    print(json.dumps(out, indent=4))
    exit(0)


if __name__ == "__main__":
    main()
