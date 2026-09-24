from http import HTTPStatus

import pytest

from utils import validators


@pytest.fixture
def viewer_leaf_fields_query(query_reader):
    return query_reader("query_viewer_leaf_fields")

def test_viewer_leaf_fields_schema_validation(user_service, viewer_leaf_fields_query):
    response = user_service.query_viewer_leaf_fields()
    body = response.json()

    validators.verify_status_code(response, HTTPStatus.OK)
    validators.verify_graphql_has_no_errors(body)
    validators.verify_body_has_data(body)

    data = body["data"]

    validators.verify_response_structure_matches_query(data, viewer_leaf_fields_query)
    validators.verify_response_matches_schema(data, viewer_leaf_fields_query)