from typing import Any, cast

from assertpy import assert_that
from graphql import (
    GraphQLObjectType, GraphQLNonNull, GraphQLScalarType, GraphQLList,
    FieldNode, SelectionNode, OperationType, GraphQLOutputType,
    GraphQLInterfaceType, GraphQLEnumType, GraphQLUnionType,
    InlineFragmentNode)

from utils.schema_reader import SCHEMA


OPERATION_TYPES = {
        OperationType.QUERY: SCHEMA.query_type,
        OperationType.MUTATION: SCHEMA.mutation_type,
        OperationType.SUBSCRIPTION: SCHEMA.subscription_type,
    }


def _assert_inline_fragment(actual_data: Any, fragment: InlineFragmentNode):
    fragment_type = fragment.type_condition.name.value
    type_name = actual_data.get("__typename")
    if not type_name:
        raise AssertionError(
            f"Response does not contain '__typename' for inline fragment '{fragment_type}'."
        )

    if type_name != fragment_type:
        return
    assert_response_fields_match_selections(actual_data,
                                            fragment.selection_set.selections)


def assert_response_fields_match_selections(
        actual_data: Any, selections: tuple[SelectionNode, ...]
):
    """
    Asserts that response data matches a GraphQL selection set.

    Supports: list, str, bool, int, float, None, dict.
    """
    # handle special primitive types
    if isinstance(actual_data, list):
        for list_element in actual_data:
            assert_response_fields_match_selections(list_element, selections)
        return
    if isinstance(actual_data, (str, bool, int, float, type(None))):
        return

    # handle unexpected selection types
    if not isinstance(actual_data, dict):
        raise TypeError(f"Unexpected response type: {type(actual_data)}")

    # handle object selection types
    for selection in selections:
        if isinstance(selection, InlineFragmentNode):
            _assert_inline_fragment(actual_data, selection)
            continue
        if not isinstance(selection, FieldNode):
            raise TypeError(
                f"Unexpected selection type: {type(selection)}"
            )

        field_name = selection.name.value
        assert_that(actual_data).contains_key(field_name)

        if selection.selection_set:
            assert_response_fields_match_selections(
                actual_data[field_name], selection.selection_set.selections
            )


def assert_value_matches_graphql_type(actual_value: Any, graphql_type: GraphQLOutputType):
    """
    Asserts that response value corresponds to the provided GraphQL output type.

    Supports: GraphQLOutputType, GraphQLNonNull, null, GraphQLList, GraphQLScalarType,
    GraphQLEnumType, GraphQLUnionType, GraphQLObjectType, GraphQLInterfaceType.
    """
    # handle nullability
    if isinstance(graphql_type, GraphQLNonNull):
        if actual_value is None:
            raise AssertionError(
                f"Expected non-null GraphQL type '{graphql_type.of_type}', but got None."
            )
        assert_value_matches_graphql_type(actual_value, graphql_type.of_type)
        return
    if actual_value is None:
        return

    # handle iterables
    if isinstance(graphql_type, GraphQLList):
        if not isinstance(actual_value, list):
            raise AssertionError(
                f"Expected GraphQL list, but got {type(actual_value)}."
            )
        for list_item in actual_value:
            assert_value_matches_graphql_type(list_item, graphql_type.of_type)
        return

    # handle other types
    if isinstance(graphql_type, GraphQLScalarType):
        try:
            graphql_type.serialize(actual_value)
        except Exception as e:
            raise AssertionError(
                f"Value {actual_value} does not match GraphQL type '{graphql_type.name}'."
            ) from e
        return
    if isinstance(graphql_type, GraphQLEnumType):
        try:
            graphql_type.serialize(actual_value)
        except Exception as e:
            raise AssertionError(
                f"Value {actual_value} does not match GraphQL enum '{graphql_type.name}'. "
                f"Available values: {', '.join(graphql_type.values)}."
            ) from e
        return

    # handle unions
    if isinstance(graphql_type, GraphQLUnionType):
        type_name = actual_value.get("__typename")
        if not type_name:
            raise AssertionError(
                f"Response does not contain '__typename' for union '{graphql_type.name}'."
            )

        type_object = SCHEMA.get_type(type_name)
        if not type_object:
            raise AssertionError(
                f"Type '{type_name}' is not defined in the schema."
            )
        if not SCHEMA.is_sub_type(graphql_type, type_object):
            raise AssertionError(
                f"Type {type_name} is not a possible type of union '{graphql_type.name}'."
            )

        assert_value_matches_graphql_type(
            actual_value, cast(GraphQLOutputType, type_object)
        )
        return

    # handle unexpected types
    if not isinstance(graphql_type, (GraphQLObjectType, GraphQLInterfaceType)):
        raise TypeError(f"Unexpected response type: {type(graphql_type)}")

    # handle objects and interfaces
    for field_name, value in actual_value.items():
        # ignore metadata for union validation
        if field_name == "__typename":
            continue

        field = graphql_type.fields.get(field_name)
        if not field:
            raise AssertionError(
                f"Field '{field_name}' is not defined in "
                f"GraphQL type '{graphql_type.name}'."
            )
        assert_value_matches_graphql_type(value, field.type)
