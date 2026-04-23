class LoginException(Exception):
    def __init__(self, value: str) -> None:
        """Class to handle failed logins

        Args:
            value (str): Error message
        """
        self.value = value

    def __str__(self) -> None:
        return repr(self.value)


class RestRequestException(Exception):
    def __init__(self, value: str, status_code: int) -> None:
        """Class to handle failed REST requests

        Args:
            value (str): Error message
            status_code (int): HTTP status code
        """
        self.value = value
        self.status_code = status_code

    def __str__(self) -> None:
        return repr(self.value)


class DeploymentNotFoundException(Exception):
    def __init__(self, value: str) -> None:
        """Class to handle not existent deployments

        Args:
            value (str): Error message
        """
        self.value = value

    def __str__(self) -> None:
        return repr(self.value)
