from .exceptions import DeploymentNotFoundException, RestRequestException
from .session import AriaSession


class AriaDeploymentAPI:
    def __init__(self, session: AriaSession) -> None:
        self.session = session

    def getDeploymentByName(self, name: str, resources: bool = True) -> dict:
        deployments = self.session.get(
            "deployment/api/deployments", {"name": name}
        )["content"]
        if len(deployments) != 1:
            raise DeploymentNotFoundException(
                "Deployment with name %s was not found" % name
            )
        return (
            self.getDeploymentById(deployments[0]["id"], resources)
            if resources
            else deployments[0]
        )

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
