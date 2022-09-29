from typing import Type, Optional, List, Callable, TypeVar, Any

from pydantic import BaseModel

T_ANY = TypeVar("T_ANY")
T = TypeVar("T", bound=BaseModel)


class InjectedFunctionParameter:
    def __init__(self, name: Optional[str] = None):
        self.resolver: Optional[Callable[..., Any]] = None
        self.name = name

    def resolve(self, input: Any) -> Any:
        if r := self.resolver:
            return r(input)
        return input


class GraphQLTypeEngine:
    def render(self) -> str:
        raise NotImplementedError  # pragma: no cover


class GraphQLDataType(GraphQLTypeEngine):
    def __init__(self) -> None:
        super().__init__()

    def ref(self, nullable: bool = False) -> "GraphQLReference":
        raise NotImplementedError  # pragma: no cover


class GraphQLTypeAttribute:
    def __init__(self, name: str, attr_type: GraphQLDataType):
        self.name = name
        self.attr_type = attr_type

    def render(self) -> str:
        return f"{self.name}: {self.attr_type.render()}"


class GraphQLReference(GraphQLDataType):
    def __init__(self, reference: str, nullable: bool = False) -> None:
        super().__init__()
        self.reference = reference
        self.nullable = nullable

    def render(self) -> str:
        return f"{self.reference}{'' if self.nullable else '!'}"


class GraphQLType(GraphQLDataType):
    def __init__(
        self,
        name: str,
        python_type: Type[T],
        attrs: Optional[List[GraphQLTypeAttribute]] = None,
        as_input: bool = False,
    ):
        super().__init__()
        self.name = name
        if not attrs:
            attrs = []
        self.attrs = attrs
        self.as_input = as_input
        self.resolver = lambda attrs: python_type(**attrs)

    def add_attribute(self, field: GraphQLTypeAttribute) -> None:
        self.attrs.append(field)

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLReference(self.name, nullable=nullable)

    def render(self) -> str:
        separator = "\n    "
        decl = "input" if self.as_input else "type"
        return f"""
{decl} {self.name} {{
    {separator.join([attr.render() for attr in self.attrs])}
}}
        """.strip()


class GraphQLArray(GraphQLDataType):
    def __init__(self, item_type: GraphQLDataType):
        super().__init__()
        self.item_type = item_type

    def render(self) -> str:
        return f"[{self.item_type.render()}]"

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLReference(reference=self.render(), nullable=nullable)


class GraphQLFunctionField(GraphQLTypeEngine, InjectedFunctionParameter):
    def __init__(
        self, graphql_type: Optional[GraphQLDataType] = None, name: Optional[str] = None
    ):
        super().__init__(name=name)
        self.type = graphql_type
        self.python_name: str = ""

    def set_name(self, name: str) -> None:
        self.name = name

    def set_python_name(self, python_name: str) -> None:
        self.python_name = python_name

    def render(self) -> str:
        assert self.type
        return f"{self.name}: {self.type.render()}"


class GraphQLQueryField(GraphQLFunctionField):
    ...


class GraphQLFunction(GraphQLTypeEngine):
    def __init__(
        self,
        name: str,
        return_type: GraphQLDataType,
        parameters: Optional[List[GraphQLFunctionField]] = None,
    ):
        self.name = name
        self.return_type = return_type
        self.parameters: List[GraphQLFunctionField] = parameters if parameters else []
        self.resolver: Optional[Callable[..., T_ANY]] = None
        self.injected_parameters: List[InjectedFunctionParameter] = []

    def add_parameter(self, parameter: GraphQLFunctionField) -> None:
        self.parameters.append(parameter)

    def add_injected_parameter(self, parameter: InjectedFunctionParameter) -> None:
        self.injected_parameters.append(parameter)

    def render(self) -> str:
        parameters = ", ".join([p.render() for p in self.parameters])
        if parameters:
            parameters = f"({parameters})"
        return f"{self.name}{parameters}: {self.return_type.render()}"
