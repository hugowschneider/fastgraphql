from datetime import date, datetime, time
from typing import Any, Callable, Optional, Type

from fastgraphql.types import GraphQLDataType, GraphQLReference
from fastgraphql.utils import MutableString


class GraphQLScalar(GraphQLDataType):
    def __init__(self, name: str, python_type: Optional[Type[Any]] = None):
        super().__init__(name=name, python_type=python_type)
        self.default_scalar = False
        self.encoder: Optional[Callable[..., Any]] = None
        self.decoder: Optional[Callable[..., Any]] = None

    def render(self) -> str:
        return f"scalar {self.name}"

    def ref(self, nullable: bool = False) -> GraphQLReference:
        return GraphQLReference(self, nullable=nullable)


class GraphQLBoolean(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__(name="Boolean", python_type=bool)
        self.default_scalar = True


class GraphQLInteger(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__(name="Int", python_type=int)
        self.default_scalar = True


class GraphQLString(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__(name="String", python_type=str)
        self.default_scalar = True


class GraphQLFloat(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__(name="Float", python_type=float)
        self.default_scalar = True


class GraphQLID(GraphQLScalar):
    def __init__(self) -> None:
        super().__init__(name="ID", python_type=str)
        self.default_scalar = True


class GraphQLDateTime(GraphQLScalar):
    def __init__(self, date_time_format: MutableString) -> None:
        super().__init__("DateTime", python_type=datetime)

        def encoder(d: datetime) -> str:
            return d.strftime(date_time_format.get_value())

        def decoder(s: str) -> datetime:
            return datetime.strptime(s, date_time_format.get_value())

        self.encoder = encoder
        self.decoder = decoder


class GraphQLDate(GraphQLScalar):
    def __init__(self, date_format: MutableString) -> None:
        super().__init__(name="Date", python_type=date)

        def encoder(d: datetime) -> str:
            return d.strftime(date_format.get_value())

        def decoder(s: str) -> date:
            return datetime.strptime(s, date_format.get_value()).date()

        self.encoder = encoder
        self.decoder = decoder


class GraphQLTime(GraphQLScalar):
    def __init__(self, time_format: MutableString) -> None:
        super().__init__(name="Time", python_type=time)

        def encoder(d: datetime) -> str:
            return d.strftime(time_format.get_value())

        def decoder(s: str) -> time:
            return datetime.strptime(s, time_format.get_value()).time()

        self.encoder = encoder
        self.decoder = decoder
