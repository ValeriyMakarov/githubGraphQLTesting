from http import HTTPStatus

from utils.validators import (
    verify_status_code, verify_graphql_has_no_errors,
    verify_http_message, verify_http_message_contains)


def test_get_login_without_token(user_service):
    user_service.client.remove_token()

    response = user_service.query_viewer_login()
    body = response.json()

    verify_status_code(response, HTTPStatus.FORBIDDEN)
    verify_http_message_contains(body, "API rate limit exceeded")


def test_get_login(viewer_username, user_service):
    response = user_service.query_viewer_login()
    body = response.json()

    verify_status_code(response, HTTPStatus.OK)
    verify_graphql_has_no_errors(body)

    viewer = body["data"]["viewer"]
    user_service.verify_viewer_login(viewer, viewer_username)


def test_get_login_with_invalid_token(user_service):
    user_service.client.set_token("github_pat_")

    response = user_service.query_viewer_login()
    body = response.json()

    verify_status_code(response, HTTPStatus.UNAUTHORIZED)
    verify_http_message(body, "Bad credentials")

