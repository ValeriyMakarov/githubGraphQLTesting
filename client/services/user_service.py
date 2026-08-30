from assertpy import assert_that
from requests import Response

from client.helpers import read_graphql_file
from client.services.base_service import BaseService


class UserService(BaseService):
    def query_viewer_login(self) -> Response:
        query = read_graphql_file("query_viewer_login")
        response = self.client.execute(query)
        return response

    def query_viewer_id(self) -> Response:
        query = read_graphql_file("query_viewer_id")
        response = self.client.execute(query)
        return response

    def get_viewer_id(self) -> str:
        response = self.query_viewer_id()
        body = response.json()
        _id = body["data"]["viewer"]["id"]
        return _id

    @staticmethod
    def verify_viewer_login(viewer: dict, expected: str):
        assert_that(viewer["login"]).is_equal_to(expected)