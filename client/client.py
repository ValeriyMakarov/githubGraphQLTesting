import os
from copy import deepcopy
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

    def set_token(self, token: str):
        auth_header = {"Authorization": f"Bearer {token}"}
        self.update_headers(auth_header)

    def remove_token(self):
        self.remove_headers("Authorization")

    def update_headers(self, headers: dict[str, str]):
        self.headers.update(headers)

    def remove_headers(self, header: str, *headers: str):
        for header in (header, *headers):
            self.headers.pop(header, None)

    def with_headers(self, headers: dict[str, str]) -> Self:
        _copy = deepcopy(self)
        _copy.update_headers(headers)
        return _copy

    def without_headers(self, header: str, *headers: str):
        _copy = deepcopy(self)
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

        response = requests.post(
            url=self.GITHUB_GRAPHQL_URL, json=json, headers=self.headers
        )

        return response