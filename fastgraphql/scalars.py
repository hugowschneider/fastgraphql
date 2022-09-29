from datetime import datetime, date, time
from typing import Optional, Callable, Any

from fastgraphql.types import GraphQLDataType, GraphQLReference
from fastgraphql.utils import MutableString


class GraphQLScalar(GraphQLDataType):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self._default_scalar = False
        self.encoder: Optional[Callable[..., Any]] = None
        self.decoder: Optional[Callable[..., Any]] = None

    def render(self) -> str:
        return f"scalar {self.name}"

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLReference(self.name, nullable=nullable)


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


class GraphQLDateTime(GraphQLScalar):
    def __init__(self, date_time_format: MutableString) -> None:
        super().__init__("DateTime")

        def encoder(d: datetime) -> str:
            return d.strftime(date_time_format.get_value())

        def decoder(s: str) -> datetime:
            return datetime.strptime(s, date_time_format.get_value())

        self.encoder = encoder
        self.decoder = decoder


class GraphQLDate(GraphQLScalar):
    def __init__(self, date_format: MutableString) -> None:
        super().__init__("Date")

        def encoder(d: datetime) -> str:
            return d.strftime(date_format.get_value())

        def decoder(s: str) -> date:
            return datetime.strptime(s, date_format.get_value()).date()

        self.encoder = encoder
        self.decoder = decoder


class GraphQLTime(GraphQLScalar):
    def __init__(self, time_format: MutableString) -> None:
        super().__init__("Time")

        def encoder(d: datetime) -> str:
            return d.strftime(time_format.get_value())

        def decoder(s: str) -> time:
            return datetime.strptime(s, time_format.get_value()).time()

        self.encoder = encoder
        self.decoder = decoder
