import os

from typing import Callable, Optional

FAST_GRAPHQL_DEBUG = "FAST_GRAPHQL_DEBUG"
DEFAULT_TAB = "    "


def to_camel_case(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class DefaultCase:
    def __init__(self, convert_func: Callable[[str], str]) -> None:
        self.conver_func = convert_func

    def __call__(self, name: str) -> str:
        return self.conver_func(name)


class DefaultUnchanged(DefaultCase):
    def __init__(self) -> None:
        super().__init__(convert_func=str)


class DefaultToCamelCase(DefaultCase):
    def __init__(self) -> None:
        super().__init__(convert_func=to_camel_case)


class MutableString:
    def __init__(self, value: str) -> None:
        self.value = value

    def set_value(self, value: str) -> None:
        self.value = value

    def get_value(self) -> str:
        return self.value


def get_env_bool(name: str, default_value: Optional[bool] = None) -> bool:
    true_ = ("true", "1", "t")  # Add more entries if you want, like: `y`, `yes`, ...
    false_ = ("false", "0", "f")
    value: Optional[str] = os.getenv(name, None)
    if value is None:
        if default_value is None:
            raise ValueError(f"Variable `{name}` not set!")
        else:
            return default_value

    if value.lower() not in true_ + false_:
        return False
    return value in true_
