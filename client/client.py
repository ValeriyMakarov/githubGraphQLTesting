import os
from copy import copy
from typing import Self

import requests


class Client:
    GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")

        if not token:
            raise KeyError("GITHUB_TOKEN environment variable is not set.")

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self._session = requests.sessions.Session()

        self.connection_timeout = 3
        self.response_timeout = 10

    def copy(self):
        _copy = copy(self)
        _copy.headers = self.headers.copy()
        return _copy

    def set_token(self, token: str):
        auth_header = {"Authorization": f"Bearer {token}"}
        self.update_headers(auth_header)

    def remove_token(self):
        self.remove_headers("Authorization")

    def update_headers(self, headers: dict[str, str]):
        self.headers.update(headers)

    def remove_headers(self, header: str, *headers: str):
        for header_ in (header, *headers):
            self.headers.pop(header_, None)

    def with_headers(self, headers: dict[str, str]) -> Self:
        _copy = self.copy()
        _copy.update_headers(headers)
        return _copy

    def without_headers(self, header: str, *headers: str):
        _copy = self.copy()
        _copy.remove_headers(header, *headers)
        return _copy

    def execute(
            self, query: str, variables: dict | None = None
    ):
        variables = variables or {}

        json = {
            "query": query,
            "variables": variables
        }

        response = self._session.post(
            url=self.GITHUB_GRAPHQL_URL, json=json, headers=self.headers,
            timeout=(self.connection_timeout, self.response_timeout)
        )

        return response