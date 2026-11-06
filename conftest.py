import os

import dotenv
import pytest

from client.client import Client
from client.query_reader_helper import read_graphql_file
from client.services.repository_service import RepositoryService
from client.services.user_service import UserService

dotenv.load_dotenv()

@pytest.fixture(scope="session")
def viewer_username() -> str:
    name = os.getenv("GITHUB_USERNAME")

    if not name:
        pytest.fail("GITHUB_USERNAME environment variable is not set.")

    return name


@pytest.fixture(scope="session")
def client():
    return Client()


@pytest.fixture
def user_service(client):
    _user_service = UserService(client.copy())
    return _user_service


@pytest.fixture
def repository_service(client):
    _repository_service = RepositoryService(client.copy())
    return _repository_service


@pytest.fixture
def query_reader():
    return read_graphql_file
