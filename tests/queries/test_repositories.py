from http import HTTPStatus

import pytest

from client.services.repository_service import OrderBy
from utils.validators import verify_status_code, verify_graphql_has_no_errors

@pytest.fixture
def viewer_watching_repositories_count(repository_service):
    count = repository_service.get_viewer_watching_repositories_count()
    return count

@pytest.fixture
def viewer_has_watching_repositories(
    viewer_watching_repositories_count, repository_service
):
    def check(required_count: int = 1):
        if viewer_watching_repositories_count < required_count:
            pytest.skip(f"User must have {required_count} or more watching repositories.")
    return check


@pytest.fixture
def last_cursor_for_viewer_watching_repositories(repository_service):
    last_cursor = repository_service.get_last_cursor_for_viewer_watching_repositories()
    return last_cursor


@pytest.mark.requires_watching_repositories
def test_get_first_five_viewer_watching_repositories(
    viewer_has_watching_repositories, repository_service
):
    viewer_has_watching_repositories(5)

    response = repository_service.query_viewer_watching_repositories(first=5, after=None)
    body = response.json()

    verify_status_code(response, HTTPStatus.OK)
    verify_graphql_has_no_errors(body)

    watching_data = body["data"]["viewer"]["watching"]
    repositories = watching_data["nodes"]

    repository_service.verify_repositories_count(repositories, 5)
    repository_service.verify_repositories_structure(repositories, "name", "updatedAt")


@pytest.mark.requires_watching_repositories
def test_viewer_watching_repositories_pagination_after_last_cursor(
    viewer_has_watching_repositories,
    last_cursor_for_viewer_watching_repositories,
    repository_service
):
    viewer_has_watching_repositories(1)

    response = repository_service.query_viewer_watching_repositories(
        after=last_cursor_for_viewer_watching_repositories
    )
    body = response.json()

    verify_status_code(response, HTTPStatus.OK)
    verify_graphql_has_no_errors(body)

    watching_data = body["data"]["viewer"]["watching"]
    repositories = watching_data["nodes"]
    page_info = watching_data["pageInfo"]

    repository_service.verify_repositories_count(repositories, 0)
    repository_service.verify_end_cursor_is_empty(page_info)
    repository_service.verify_no_next_page(page_info)


@pytest.mark.requires_watching_repositories
def test_viewer_watching_repositories_pagination_no_duplicates(
    viewer_has_watching_repositories, repository_service
):
    viewer_has_watching_repositories(10)

    response = repository_service.query_viewer_watching_repositories(first=5)
    body = response.json()

    verify_status_code(response, HTTPStatus.OK)
    verify_graphql_has_no_errors(body)

    watching_data = body["data"]["viewer"]["watching"]
    first_five_repositories = watching_data["nodes"]
    end_cursor = watching_data["pageInfo"]["endCursor"]

    response = repository_service.query_viewer_watching_repositories(
        first=5, after=end_cursor
    )
    body = response.json()

    watching_data = body["data"]["viewer"]["watching"]
    last_five_repositories = watching_data["nodes"]

    repository_service.verify_repositories_lists_have_no_duplicates(
        first_five_repositories, last_five_repositories
    )


@pytest.mark.requires_watching_repositories
def test_viewer_watching_repositories_pagination_with_one_item(
    viewer_has_watching_repositories,
    viewer_watching_repositories_count, repository_service
):
    viewer_has_watching_repositories(2)

    repositories = repository_service.get_all_viewer_watching_repositories(
        page_amount=1
    )

    repository_service.verify_repositories_count(
        repositories, viewer_watching_repositories_count
    )


@pytest.mark.parametrize(
    "order_by",
    [
        OrderBy(order_direction="ASC", repository_order_field="NAME"),
        OrderBy(order_direction="ASC", repository_order_field="UPDATED_AT"),
        OrderBy(order_direction="DESC", repository_order_field="NAME"),
        OrderBy(order_direction="ASC", repository_order_field="UPDATED_AT")
    ]
)
@pytest.mark.requires_watching_repositories
def test_get_viewer_watching_repositories_sorted(
    viewer_has_watching_repositories,
    repository_service, order_by
):
    viewer_has_watching_repositories(2)

    response = repository_service.query_viewer_watching_repositories(
        order_by=order_by
    )
    body = response.json()

    verify_status_code(response, HTTPStatus.OK)
    verify_graphql_has_no_errors(body)

    repositories = body["data"]["viewer"]["watching"]["nodes"]

    repository_service.verify_repositories_order(repositories, order_by)
