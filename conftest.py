import os

import dotenv
import pytest

from client.client import Client
from client.services.repository_service import RepositoryService
from client.services.user_service import UserService

dotenv.load_dotenv()

@pytest.fixture(scope="session")
def viewer_username() -> str:
    name = os.getenv("GITHUB_USERNAME")

    if not name:
        pytest.fail("GITHUB_USERNAME environment variable is not set.")

    return name


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user_service(client):
    return UserService(client)


@pytest.fixture
def repository_service(client):
    return RepositoryService(client)