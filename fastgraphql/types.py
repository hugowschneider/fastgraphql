from typing import Any, Callable, List, Optional, Type, TypeVar, Dict

from fastgraphql.injection import Injectable, InjectableRequestType

T_ANY = TypeVar("T_ANY")
T = TypeVar("T")


class GraphQLDataType:
    def __init__(self, name: str, python_type: Optional[Type[Any]]):
        self.name = name
        self.python_type = python_type

    def ref(self, nullable: bool = False) -> "GraphQLReference":
        raise NotImplementedError  # pragma: no cover

    def render(self) -> str:
        raise NotImplementedError  # pragma: no cover


class GraphQLReference:
    def __init__(
        self, referenced_type: GraphQLDataType, nullable: bool = False
    ) -> None:
        self.python_type = referenced_type.python_type
        self.referenced_type = referenced_type
        self.nullable = nullable

    def render(self) -> str:
        return f"{self.referenced_type.name}{'' if self.nullable else '!'}"


class GraphQLTypeAttribute:
    def __init__(self, name: str, attr_type: GraphQLReference):
        self.name = name
        self.attr_type = attr_type

    def render(self) -> str:
        return f"{self.name}: {self.attr_type.render()}"


class GraphQLType(GraphQLDataType):
    def __init__(
        self,
        name: str,
        python_type: Type[T],
        attrs: Optional[List[GraphQLTypeAttribute]] = None,
        as_input: bool = False,
    ):
        super().__init__(name=name, python_type=python_type)
        if not attrs:
            attrs = []
        self.attrs = attrs
        self.as_input = as_input

    def add_attribute(self, field: GraphQLTypeAttribute) -> None:
        self.attrs.append(field)

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLReference(self, nullable=nullable)

    def render(self) -> str:
        separator = "\n    "
        decl = "input" if self.as_input else "type"
        return f"""
{decl} {self.name} {{
    {separator.join([attr.render() for attr in self.attrs])}
}}
        """.strip()


class GraphQLArray(GraphQLDataType):
    def __init__(self, item_type: GraphQLReference):
        super().__init__(python_type=list, name=f"[{item_type.render()}]")

        self.item_type = item_type

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLReference(referenced_type=self, nullable=nullable)


class GraphQLFunctionField(InjectableRequestType):
    def __init__(
        self,
        graphql_type: Optional[GraphQLReference] = None,
        name: Optional[str] = None,
    ):
        super().__init__(python_type=graphql_type.python_type if graphql_type else None)
        self.name = name
        self.reference = graphql_type
        self.python_name: str = ""

    def set_name(self, name: str) -> None:
        self.name = name

    def set_python_name(self, python_name: str) -> None:
        self.python_name = python_name

    def render(self) -> str:
        assert self.reference
        return f"{self.name}: {self.reference.render()}"


class GraphQLQueryField(GraphQLFunctionField):
    ...


class GraphQLFunction:
    def __init__(
        self,
        name: str,
        return_type: GraphQLReference,
        parameters: Optional[List[GraphQLFunctionField]] = None,
    ):
        self.name = name
        self.return_type = return_type
        self.parameters: List[GraphQLFunctionField] = parameters if parameters else []
        self.resolver: Optional[Callable[..., T_ANY]] = None
        self.injected_parameters: Dict[str, Injectable] = {}

    def add_parameter(self, parameter: GraphQLFunctionField) -> None:
        self.parameters.append(parameter)

    def add_injected_parameter(self, name: str, injectable: Injectable) -> None:
        self.injected_parameters[name] = injectable

    def render(self) -> str:
        parameters = ", ".join([p.render() for p in self.parameters])
        if parameters:
            parameters = f"({parameters})"
        return f"{self.name}{parameters}: {self.return_type.render()}"
