import json
from datetime import datetime, timezone

import requests

from .exceptions import LoginException, RestRequestException


class AriaSession:
    def __init__(self, hostname: str, username: str, password: str) -> None:
        """Initializes a REST session with Aria (lazy authentication).

        Args:
            hostname (str): FQDN of Aria
            username (str): username to connect with
            password (str): password of user
        """
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.hostname = hostname
        self._username = username
        self._password = password
        self._token_acquired_at = None

    def _ensure_authenticated(self) -> None:
        """Authenticate if not already authenticated or token has expired."""
        now = datetime.now(timezone.utc)
        if (
            self._token_acquired_at is None
            or (now - self._token_acquired_at).total_seconds() >= 28800
        ):
            self.__authenticate(self._username, self._password)
            self._token_acquired_at = now

    def __authenticate(self, username: str, password: str) -> None:
        """Authenticate to Aria REST API

        Args:
            username (str): username to connect with
            password (str): password of user
        Raises:
            LoginException: when login was not successful
        """
        # remove authorization
        self.headers.pop("Authorization", None)

        # get refresh token
        payload = {"username": username, "password": password}
        url = (
            "https://%s/csp/gateway/am/api/login?access_token" % self.hostname
        )
        r = requests.post(
            url=url,
            data=json.dumps(payload),
            headers=self.headers,
            verify=False,
        )
        if r.status_code != 200:
            raise LoginException(
                "Could not get refresh token: [HTTP/%s]: %s"
                % (r.status_code, r.text)
            )
        refreshToken = r.json()["refresh_token"]

        # get access token
        payload = {"refreshToken": refreshToken}
        url = "https://%s/iaas/api/login" % self.hostname
        r = requests.post(
            url=url,
            data=json.dumps(payload),
            headers=self.headers,
            verify=False,
        )
        if r.status_code != 200:
            raise LoginException(
                "Could not get access token: [HTTP/%s]: %s"
                % (r.status_code, r.text)
            )
        self.token = r.json()

        # update header
        self.headers["Authorization"] = "%s %s" % (
            self.token["tokenType"],
            self.token["token"],
        )

    def get(self, uri: str, params: dict = {}) -> dict:
        """Executes a GET request

        Args:
            uri (str): URI of request
            params (dict): URL parameters as dict
        Returns:
            dict: JSON Object returned from API
        Raises:
            RestRequestException: raised when status code above 299
        """
        self._ensure_authenticated()
        url = "https://%s/%s" % (self.hostname, uri)
        if params:
            url = "%s?%s" % (
                url,
                requests.models.RequestEncodingMixin._encode_params(params),
            )

        r = requests.get(url=url, headers=self.headers, verify=False)
        if r.status_code > 299:
            raise RestRequestException(r.text, r.status_code)
        return r.json()

    def post(self, uri: str, payload: dict = {}) -> dict:
        """Executes a POST request

        Args:
            uri (str): URI of request
            payload (dict): Payload/Data to send
        Returns:
            dict: JSON Object returned from API
        Raises:
            RestRequestException: raised when status code above 299
        """
        self._ensure_authenticated()
        url = "https://%s/%s" % (self.hostname, uri)

        r = requests.post(
            url=url,
            data=json.dumps(payload),
            headers=self.headers,
            verify=False,
        )
        if r.status_code > 299:
            raise RestRequestException(r.text, r.status_code)
        return r.json()

    def delete(self, uri: str) -> dict:
        """Executes a DELETE request

        Args:
            uri (str): URI of request
        Returns:
            dict: JSON Object returned from API
        Raises:
            RestRequestException: raised when status code above 299
        """
        self._ensure_authenticated()
        url = "https://%s/%s" % (self.hostname, uri)

        r = requests.delete(url=url, headers=self.headers, verify=False)
        if r.status_code > 299:
            raise RestRequestException(r.text, r.status_code)
        return r.json()
