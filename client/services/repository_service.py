from dataclasses import dataclass
from http import HTTPStatus
from typing import Literal

from assertpy import assert_that
from requests import Response

from client.logger_helper import log_all_methods
from client.query_reader_helper import read_graphql_file
from client.services.base_service import BaseService
from utils.validators import verify_status_code, verify_graphql_has_no_errors

RepositoryVisibility = Literal["PUBLIC", "PRIVATE", "INTERNAL"]

OrderDirection = Literal["ASC", "DESC"]
RepositoryOrderField = Literal["CREATED_AT", "NAME", "PUSHED_AT", "STARGAZERS", "UPDATED_AT"]
ORDER_RESPONSE_FIELDS = {
    "UPDATED_AT": "updatedAt",
    "NAME": "name",
}

@dataclass
class OrderBy:
    order_direction: OrderDirection
    repository_order_field: RepositoryOrderField


@log_all_methods
class RepositoryService(BaseService):
    def query_create_repository(
            self, name: str, visibility: RepositoryVisibility,
            owner_id: str, description: str
    ) -> Response:
        variables = {
            "input": {
                "name": name,
                "visibility": visibility,
                "ownerId": owner_id,
                "description": description
            }
        }
        query = read_graphql_file("mutation_create_repository")

        response = self.client.execute(query, variables)
        return response

    def query_viewer_watching_repositories(
        self, first: int = 100,
        after: str | None = None, order_by: OrderBy | None = None
    ) -> Response:
        variables: dict = {
            "first": first,
            "after": after
        }
        if order_by:
            variables["orderBy"] = {
                "direction": order_by.order_direction,
                "field": order_by.repository_order_field
            }

        query = read_graphql_file("query_viewer_watching_repositories")

        response = self.client.execute(query, variables)
        return response

    def get_all_viewer_watching_repositories(
        self, page_amount: int = 100, order_by: OrderBy | None = None
    ) -> list[dict]:
        after = None
        has_next_page = True
        repositories = []
        while has_next_page:
            response = self.query_viewer_watching_repositories(
                first=page_amount, after=after, order_by=order_by)
            body = response.json()

            verify_status_code(response, HTTPStatus.OK)
            verify_graphql_has_no_errors(body)
            watching_data = body["data"]["viewer"]["watching"]

            repositories.extend(watching_data["nodes"])
            has_next_page = watching_data["pageInfo"]["hasNextPage"]
            after = watching_data["pageInfo"]["endCursor"]

        return repositories

    def get_last_cursor_for_viewer_watching_repositories(self):
        after = None
        has_next_page = True
        while has_next_page:
            response = self.query_viewer_watching_repositories(after=after)

            watching_data = response.json()["data"]["viewer"]["watching"]

            has_next_page = watching_data["pageInfo"]["hasNextPage"]
            after = watching_data["pageInfo"]["endCursor"]

        return after

    def query_viewer_watching_repositories_count(self):
        query = read_graphql_file("query_viewer_watching_repositories_count")

        response = self.client.execute(query)
        return response

    def get_viewer_watching_repositories_count(self):
        response = self.query_viewer_watching_repositories_count()

        total_count = response.json()["data"]["viewer"]["watching"]["totalCount"]
        return total_count

    @staticmethod
    def verify_created_repository(payload: dict, expected: dict):
        assert_that(payload).contains(
            "owner", "id", "name", "visibility", "description"
        )

        owner = payload["owner"]
        assert_that(owner).contains("id")
        assert_that(owner["id"]).is_equal_to(expected["owner_id"])

        assert_that(payload["id"]).is_not_none()
        assert_that(payload["name"]).is_equal_to(expected["name"])
        assert_that(payload["visibility"]).is_equal_to(expected["visibility"])
        assert_that(payload["description"]).is_equal_to(expected["description"])

    @staticmethod
    def verify_repositories_count(repositories: list[dict], expected_count: int):
        assert_that(repositories).is_length(expected_count)

    @staticmethod
    def verify_repositories_structure(repositories: list[dict], *keys: str):
        for rep in repositories:
            assert_that(rep).contains_key(*keys)

    @staticmethod
    def verify_page_info_structure(page_info: dict):
        assert_that(page_info).contains_key("endCursor", "hasNextPage")

    @staticmethod
    def verify_end_cursor_is_empty(page_info: dict):
        assert_that(page_info).contains_key("endCursor")
        assert_that(page_info["endCursor"]).is_none()

    @staticmethod
    def verify_no_next_page(page_info: dict):
        assert_that(page_info).contains_key("hasNextPage")
        assert_that(page_info["hasNextPage"]).is_false()

    @staticmethod
    def verify_has_next_page(page_info: dict):
        assert_that(page_info).contains_key("hasNextPage")
        assert_that(page_info["hasNextPage"]).is_true()

    @staticmethod
    def verify_repositories_lists_have_no_duplicates(
        first: list[dict], second: list[dict]
    ):
        for repo in second:
            assert_that(repo).is_not_in(*first)

    @staticmethod
    def verify_repositories_order(repositories: list[dict], order_by: OrderBy):
        field_name = ORDER_RESPONSE_FIELDS[order_by.repository_order_field]

        reverse = order_by.order_direction == "DESC" or False
        key = lambda repo: repo[field_name]

        assert_that(repositories).is_sorted(key, reverse) # type: ignore
