import os
from typing import Optional

FAST_GRAPHQL_DEBUG = "FAST_GRAPHQL_DEBUG"


def get_env_bool(name: str, default_value: Optional[bool] = None) -> bool:
    true_ = ("true", "1", "t")  # Add more entries if you want, like: `y`, `yes`, ...
    false_ = ("false", "0", "f")
    value: Optional[str] = os.getenv(name, None)
    if value is None:
        if default_value is None:
            raise ValueError(f"Variable `{name}` not set!")
        else:
            value = str(default_value)
    if value.lower() not in true_ + false_:
        return False
    return value in true_
