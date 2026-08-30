from pathlib import Path

GRAPHQL_DIR = Path("queries")
QUERIES_DIR_NAME = "queries"
MUTATIONS_DIR_NAME = "mutations"

def read_graphql_file(file_name: str):
    file_path = (GRAPHQL_DIR / QUERIES_DIR_NAME / file_name).with_suffix(".graphql")
    if not file_path.exists():
        file_path = (GRAPHQL_DIR / MUTATIONS_DIR_NAME / file_name).with_suffix(".graphql")

    data = file_path.read_text()
    return data