import json
from pathlib import Path

from graphql import build_client_schema, GraphQLSchema

SCHEMA_PATH = Path("schemas/schema.json")


def read_json_schema(path: Path) -> GraphQLSchema:
    """
    Use "from schema_reader import schema" instead.

    :param path: Path to introspection in JSON format.
    :return: GraphQLSchema
    """
    with path.open(encoding="utf-8") as file:
        schema_json = json.load(file)

    return build_client_schema(schema_json)


SCHEMA: GraphQLSchema = read_json_schema(SCHEMA_PATH)