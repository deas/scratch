from .exceptions import DeploymentNotFoundException, RestRequestException
from .session import AriaSession


class AriaDeploymentAPI:
    def __init__(self, session: AriaSession) -> None:
        self.session = session

    def getDeploymentByType(
        self, type: str = "Custom.vpc", resources: bool = True
    ) -> list:
        deployments = self.session.get(
            "deployment/api/deployments", {"resourceType": type}
        )["content"]
        if resources:
            return [
                self.getDeploymentById(deployment["id"], resources)
                for deployment in deployments
            ]
        else:
            return deployments

    def getDeploymentById(self, id: str, resources: bool = True) -> dict:
        try:
            return self.session.get(
                "deployment/api/deployments/%s%s"
                % (id, "/resources" if resources else "")
            )
        except RestRequestException as e:
            if e.status_code == 404:
                raise DeploymentNotFoundException(
                    "Deployment with ID %s was not found" % id
                )
            else:
                raise e
