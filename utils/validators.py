from http import HTTPStatus
from typing import Any

from assertpy import assert_that
from graphql import GraphQLObjectType, parse, OperationDefinitionNode
from requests import Response

from client.logger_helper import log_function
from utils.schema_validation_helpers import assert_value_matches_graphql_type, \
    assert_response_fields_match_selections, OPERATION_TYPES


@log_function
def verify_status_code(response: Response, status_code: HTTPStatus | int):
    assert_that(response.status_code).is_equal_to(status_code)


@log_function
def verify_body_has_data(body: dict):
    assert_that(body).contains_key("data")


@log_function
def verify_graphql_has_no_errors(body: dict):
    assert_that(body).does_not_contain_key("errors")


@log_function
def verify_http_message(body: dict, message: str):
    assert_that(body["message"]).is_equal_to(message)


@log_function
def verify_http_message_contains(body: dict, message: str):
    assert_that(body["message"]).contains(message)



def _get_operation_type(definition: OperationDefinitionNode) -> GraphQLObjectType:
    operation_name = definition.operation

    operation_type = OPERATION_TYPES.get(operation_name)
    if not operation_type:
        raise KeyError(f"No '{operation_name}' operation in schema.")
    return operation_type


def _parse_single_operation(query: str) -> OperationDefinitionNode:
    parsed_query = parse(query)
    definitions = parsed_query.definitions
    if len(definitions) != 1:
        raise RuntimeError(
            f"Expected operations amount is 1, got {len(definitions)}."
        )

    definition = definitions[0]
    if not isinstance(definition, OperationDefinitionNode):
        raise TypeError(f"Unexpected type {type(definition)}")
    return definition



@log_function
def verify_response_matches_schema(data: Any, query: str):
    """
    Asserts that a GraphQL response matches the GraphQL API schema.

    :param data: response.json()["data"]
    :param query: query as str
    """
    operation_definition = _parse_single_operation(query)
    operation = _get_operation_type(operation_definition)
    assert_value_matches_graphql_type(data, operation)

@log_function
def verify_response_structure_matches_query(data: Any, query: str):
    """
    Asserts that a GraphQL response structure matches the GraphQL API request schema.

    :param data: response.json()["data"]
    :param query: query as str
    """
    operation_definition = _parse_single_operation(query)
    assert_response_fields_match_selections(
        data, operation_definition.selection_set.selections
    )
