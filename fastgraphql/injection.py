import inspect
from typing import Any, Callable, Dict, Optional, Tuple, Type
from graphql import GraphQLResolveInfo


class Injectable:
    def __call__(
        self, *args: Tuple[Any], **kwargs: Dict[str, Any]
    ) -> Any:  # pragma: no cover
        raise NotImplementedError

    def is_callable(self) -> bool:  # pragma: no cover
        raise NotImplementedError


class InjectableRequestType(Injectable):
    def __init__(
        self,
        python_type: Optional[Type[Any]],
    ):
        self.python_type = python_type

    def is_callable(self) -> bool:
        return self.python_type is not None

    def map_from_input(
        self, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    def __call__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
        if python_type := self.python_type:
            return python_type(*args, **self.map_from_input(kwargs))
        return None  # pragma: no cover


class InjectableFunction(Injectable):
    def __init__(self, callable: Optional[Callable[..., Any]] = None):
        self.callable = callable
        self.dependencies: Dict[str, Callable[..., Any]] = {}

    def __call__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
        if c := self.callable:
            resolved_kwargs = {}
            for name, dependency in self.dependencies.items():
                resolved_kwargs[name] = dependency(*args, **kwargs)
            value = c(**resolved_kwargs)
            if inspect.isgenerator(value):
                value = next(value)

            return value


class InjectableType(Injectable):
    def __init__(self, python_type: type) -> None:
        self.python_type = python_type

    def __call__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
        for arg in args:
            if isinstance(arg, self.python_type):
                return arg

        for key, value in kwargs.items():
            if isinstance(value, self.python_type):
                return value

        return None


class InjectableContext(InjectableType):
    def __init__(self) -> None:
        super().__init__(python_type=GraphQLResolveInfo)
