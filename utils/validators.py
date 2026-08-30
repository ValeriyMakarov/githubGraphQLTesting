from http import HTTPStatus

from assertpy import assert_that
from requests import Response

from client.logger_helper import log_function


@log_function
def verify_status_code(response: Response, status_code: HTTPStatus | int):
    assert_that(response.status_code).is_equal_to(status_code)


@log_function
def verify_graphql_has_no_errors(body: dict):
    assert_that(body).does_not_contain_key("errors")


@log_function
def verify_http_message(body: dict, message: str):
    assert_that(body["message"]).is_equal_to(message)


@log_function
def verify_http_message_contains(body: dict, message: str):
    assert_that(body["message"]).contains(message)
