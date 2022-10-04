from typing import Any, Callable, Dict, Optional, Tuple, Type


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
            for name, dependency in self.dependencies.items():
                kwargs[name] = dependency(*kwargs)
            return c(**kwargs)


class InjectableType(Injectable):
    ...
