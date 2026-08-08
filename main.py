
import os

import pytest
import requests


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


@pytest.fixture
def github_token() -> str:
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        pytest.fail("GITHUB_TOKEN environment variable is not set")

    return token


@pytest.fixture
def github_headers(github_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
    }


def test_github_authentication(github_headers):
    query = """
    query {
        viewer {
            login
        }
    }
    """

    response = requests.post(
        GITHUB_GRAPHQL_URL,
        headers=github_headers,
        json={"query": query},
    )

    assert response.status_code == 200

    body = response.json()

    assert "errors" not in body
    assert body["data"]["viewer"]["login"]


def test_get_current_user_data(github_headers):
    query = """
    query {
        viewer {
            login
            name
            email
            bio
            repositories(first: 5) {
                nodes {
                    name
                    url
                }
            }
        }
    }
    """

    response = requests.post(
        GITHUB_GRAPHQL_URL,
        headers=github_headers,
        json={"query": query},
    )

    assert response.status_code == 200

    body = response.json()

    assert "errors" not in body

    user = body["data"]["viewer"]

    assert user["login"]
    assert "repositories" in user
    assert len(user["repositories"]["nodes"]) <= 5

