import os
from http import HTTPStatus

import requests


class RestClient:
    GITHUB_URL = "https://api.github.com"

    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")

        if not token:
            raise KeyError("GITHUB_TOKEN environment variable is not set.")

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def delete(self, endpoint: str):
        return requests.delete(
            f"{self.GITHUB_URL}{endpoint}",
            headers=self.headers)

    def delete_repository(self, owner: str, repository_name: str):
        response = self.delete(f"/repos/{owner}/{repository_name}")
        assert (
            response.status_code == HTTPStatus.NO_CONTENT,
            f"Repository {repository_name} of {owner} hasn't been deleted."
        )