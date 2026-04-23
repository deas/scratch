from .exceptions import DeploymentNotFoundException, RestRequestException
from .session import AriaSession


class AriaDeploymentAPI():
    def __init__(self, session: AriaSession) -> None:
        """Handles access to the Aria Deployment API endpoint

        Args:
            session (AriaSession): Aria REST Session to use
        """
        self.session = session

    def getDeploymentByName(self, name: str) -> dict:
        """Gets a Deployment by its name

        Args:
            name (str): Name of the Deployment
        Returns:
            dict: Representation of the Deployment
        Raises:
            DeploymentNotFoundException: when Deployment was not found
        """
        deployments = self.session.get("deployment/api/deployments", {"name": name})["content"]
        if len(deployments) != 1:
            raise DeploymentNotFoundException("Deployment with name %s was not found" % name)
        return deployments[0]

    def getDeploymentById(self, id: str) -> dict:
        """Gets a Deployment by its id

        Args:
            id (str): ID of the Deployment
        Returns:
            dict: Representation of the Deployment
        Raises:
            DeploymentNotFoundException: when Deployment was not found
        """
        try:
            return(self.session.get("deployment/api/deployments/%s" % id))
        except RestRequestException as e:
            if e.status_code == 404:
                raise DeploymentNotFoundException("Deployment with ID %s was not found" % id)
            else:
                raise e

    def deleteDeployment(self, id: str) -> bool:
        """Deletes a Deployment by its id

        Args:
            id (str): ID of the Deployment
        Returns:
            bool: True if successful, else False
        Raises:
            DeploymentNotFoundException: when Deployment was not found
        """
        try:
            self.session.delete("deployment/api/deployments/%s" % id)
            return True
        except RestRequestException as e:
            if e.status_code == 404:
                raise DeploymentNotFoundException("Deployment with ID %s was not found" % id)
            else:
                return False
