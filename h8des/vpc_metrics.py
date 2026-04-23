#!/usr/bin/python3 
# -*- coding: utf-8 -*-

from os import environ
from sys import exit, stderr
from time import sleep
import json
import yaml
from argparse import ArgumentParser, FileType

from h8des.aria.session import AriaSession  
from h8des.aria.deployment import AriaDeploymentAPI
from h8des.aria.exceptions import DeploymentNotFoundException,\
                                  ProjectNotFoundException,\
                                  BlueprintFailedException,\
                                  LoginException,\
                                  RestRequestException



def main() -> None:
    """
    """
    args = __load_args()
    
    try:
        session = AriaSession(args.hostname, args.username, args.password)
    except LoginException:
        __exit_error("Could not login to '%s' with user '%s'" % (args.hostname, args.username))
    
    try:
        if args.action == "access_token":
            __action_show_token(session)
        elif args.action == "deployment":
            __action_getProject(session,args.project)
        elif args.action == "serve":
            pass
        # elif args.action == "getProjectById":
        #     __action_getProjectById(session,args.project)
    except RestRequestException as e:
        __exit_error("API Request failed with HTTP/%s and message '%s'" % (e.status_code, e.value))

def __action_show_token(session: AriaSession) -> None:
    """Show a token

    Args:
        session (AriaSession): AriaSession object
    """

    __exit_okay(session.token)

def __action_show(session: AriaSession, deployment: str) -> None:
    """Show an Aria Deployment

    Args:
        session (AriaSession): AriaSession object
        deployment (str): name of Aria Deployment to delete
    """
    deploymentApi = AriaDeploymentAPI(session)

    try:
        __exit_okay(deploymentApi.getDeploymentByName(deployment))
    except DeploymentNotFoundException as e:
        __exit_error("Deployment '%s' was not found" % deployment)

def __exit_error(msg: str) -> None:
    """Helper to print a error json to stderr and exit with code 1

    Args:
        msg (str): message to print as value of error key
    """
    print(json.dumps({ "error": msg }, indent=4), file=stderr)
    exit(1)

def __exit_okay(out: dict) -> None:
    """Helper to print a json to stdout and exit with code 0

    Args:
        out (dict): to print as json string
    """
    print(json.dumps(out, indent=4))
    exit(0)

def __load_args() -> dict:
    """Helper to define, parse and validate CLI arguments

    Returns:
        dict: parsed arguments
    """
    parser = ArgumentParser(
        description="This tool connects to VMware Aria and allows you to order and manage deployments",
        epilog="The Aria Client is developed and maintained by the HADES team."
    )   
    parser.add_argument(
        "-H",
        "--hostname",
        dest="hostname",
        help="Aria hostname, defaults to env.ARIA_HOSTNAME",
        metavar="ARIA_HOSTNAME",
        default=environ.get('ARIA_HOSTNAME'),
        required=(environ.get('ARIA_HOSTNAME') is None),
        type=str
    )
    parser.add_argument(
        "-u",
        "--username",
        dest="username",
        help="Aria username, defaults to env.ARIA_USERNAME",
        metavar="ARIA_USERNAME",
        default=environ.get('ARIA_USERNAME'),
        required=(environ.get('ARIA_USERNAME') is None),
        type=str
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        help="Aria password, defaults to env.ARIA_PASSWORD",
        metavar="ARIA_PASSWORD",
        default=environ.get('ARIA_PASSWORD'),
        required=(environ.get('ARIA_PASSWORD') is None),
        type=str
    )
    parser.add_argument(
        "-P",
        "--project",
        dest="project",
        help="Aria project, required when action=create, defaults to env.ARIA_PROJECT",
        metavar="ARIA_PROJECT",
        default=environ.get('ARIA_PROJECT'),
        required=False,
        type=str
    )
    parser.add_argument(
        "-a",
        "--action",
        dest="action",
        help="Action to execute [access_token, deployment, serve]"
        metavar="ACTION",
        required=True,
        type=str,
        choices=["access_token", "deployment", "serve"]
    )
    parser.add_argument(
        "-d",
        "--deployment",
        dest="deployment",
        help="Name of Deyployment",
        metavar="DEPLOYMENT",
        # required=True,
        type=str
    )

    args = parser.parse_args()

    # check args
    if args.action in ["create","getProject"]:
        if not args.project:
            __exit_error("Argument 'project' is needed, when action=%s was selected" % args.action)
    # if args.action in ["create", "update"]:


        
    return args

if __name__ == '__main__':
    main()
