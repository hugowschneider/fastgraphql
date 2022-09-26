import io
from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar, cast, Union


class GraphQLSchemaException(BaseException):
    def __init__(self, *args):
        super().__init__(*args)


class GraphQLTypeEngine:
    def render(self) -> str:
        raise NotImplementedError  # pragma: no cover


class GraphQLDataType(GraphQLTypeEngine):
    def ref(self, nullable: bool = False) -> "GraphQLReference":
        raise NotImplementedError  # pragma: no cover


class GraphQLTypeAttribute:
    def __init__(self, name: str, attr_type: GraphQLDataType):
        self.name = name
        self.attr_type = attr_type

    def render(self) -> str:
        return f"{self.name}: {self.attr_type.render()}"


class GraphQLReference(GraphQLDataType):
    def __init__(self, reference: str, nullable: bool = False):
        self.reference = reference
        self.nullable = nullable

    def render(self) -> str:
        return f"{self.reference}{'' if self.nullable else '!'}"


class GraphQLType(GraphQLDataType):
    def __init__(
        self,
        name: str,
        attrs: Optional[List[GraphQLTypeAttribute]] = None,
        as_input: bool = False,
    ):
        self.name = name
        if not attrs:
            attrs = []
        self.attrs = attrs
        self.as_input = as_input

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


class GraphQLScalar(GraphQLDataType):
    def __init__(self, name: str):
        self.name = name
        self._default_scalar = False

    def render(self) -> str:
        return f"scalar {self.name}"

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLReference(self.name, nullable=nullable)


class GraphQLArray(GraphQLDataType):
    def __init__(self, item_type: GraphQLDataType):
        self.item_type = item_type

    def render(self) -> str:
        return f"[{self.item_type.render()}]"

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLReference(reference=self.render(), nullable=nullable)


class GraphQLBoolean(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__("Boolean")
        self._default_scalar = True


class GraphQLInteger(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__("Int")
        self._default_scalar = True


class GraphQLString(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__("String")
        self._default_scalar = True


class GraphQLFloat(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__("Float")
        self._default_scalar = True


class GraphQLID(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__("ID")
        self._default_scalar = True


class GraphQLSchema(GraphQLTypeEngine):
    CT = TypeVar("CT", GraphQLType, GraphQLScalar)

    def __init__(self) -> None:
        self.types: Dict[str, GraphQLType] = {}
        self.scalars: Dict[str, GraphQLScalar] = {}
        self.inputs: Dict[str, GraphQLType] = {}
        self.queries: Dict[str, GraphQLType] = {}
        self.mutations: Dict[str, GraphQLType] = {}

    def _add_to_container(
        self,
        container: Dict[str, CT],
        graphql_type: CT,
    ) -> None:
        self.check_name_conflict(graphql_type=graphql_type)
        container[graphql_type.name] = graphql_type

    def check_name_conflict(
        self, graphql_type: Union[GraphQLType, GraphQLScalar]
    ) -> None:
        if graphql_type.name in self.inputs:
            raise GraphQLSchemaException(
                f"Name {graphql_type.name} is already used as an input. Please specify another name!"
            )
        if graphql_type.name in self.types:
            raise GraphQLSchemaException(
                f"Name {graphql_type.name} is already used as an type. Please specify another name!"
            )
        if graphql_type.name in self.scalars and not isinstance(graphql_type, GraphQLScalar):
            raise GraphQLSchemaException(
                f"Name {graphql_type.name} is already used as an scalar. Please specify another name!"
            )

    def add_type(self, graphql_type: GraphQLType) -> None:
        self._add_to_container(container=self.types, graphql_type=graphql_type)

    def add_scalar(self, graphql_type: GraphQLScalar) -> None:
        self._add_to_container(container=self.scalars, graphql_type=graphql_type)

    def add_input_type(self, graphql_type: GraphQLType) -> None:
        self._add_to_container(container=self.inputs, graphql_type=graphql_type)

    def render(self) -> str:
        GT = TypeVar("GT", GraphQLScalar, GraphQLType)
        separator = "\n\n"

        def sort_and_write(types: Iterable[GT]) -> str:
            sorted_types = sorted(types, key=lambda x: x.name)
            return separator.join([s.render() for s in sorted_types])
        s = separator.join(
            sort_and_write(container.values())
            for container in [self.scalars, self.types, self.inputs] if len(container)
        )
        return s


class SelfGraphQL:
    def __init__(self) -> None:
        self.as_type: Optional[GraphQLType] = None
        self.as_input: Optional[GraphQLType] = None

    @staticmethod
    def introspect(type_: Type[Any]) -> Optional["SelfGraphQL"]:
        if hasattr(type_, "__graphql__"):
            return cast(SelfGraphQL, getattr(type_, "__graphql__"))
        return None