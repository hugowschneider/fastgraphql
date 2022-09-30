import io
from typing import Dict, Any


def render_graphql_error_response(data: Dict[str, Any]) -> str:  # pragma: no cover
    if "errors" not in data:
        return ""

    strio = io.StringIO()
    errors = data["errors"]

    for error in errors:
        strio.write(error["message"])
        strio.write("\n")
        strio.write("\n".join(error["extensions"]["exception"]["stacktrace"]))
        strio.write("\n")

    return strio.getvalue()
