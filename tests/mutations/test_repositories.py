from http import HTTPStatus

import pytest

from client.rest_client import RestClient
from utils.validators import verify_status_code


@pytest.fixture
def viewer_id(user_service):
    return user_service.get_viewer_id()


@pytest.fixture
def repository_data(viewer_username, viewer_id, faker):
    repository_data = {
        "owner": viewer_username,
        "owner_id": viewer_id,
        "visibility": "PUBLIC",
        "name": faker.slug(),
        "description": faker.slug()
    }
    yield repository_data
    RestClient().delete_repository(viewer_username, repository_data["name"])


def test_create_repository(repository_service, repository_data):
    response = repository_service.query_create_repository(
        name=repository_data["name"],
        owner_id=repository_data["owner_id"],
        visibility=repository_data["visibility"],
        description=repository_data["description"]
    )
    verify_status_code(response, HTTPStatus.OK)

    body = response.json()
    payload = body["data"]["createRepository"]["repository"]

    repository_service.verify_created_repository(payload, repository_data)
