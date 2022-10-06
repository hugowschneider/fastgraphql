from datetime import datetime

from pydantic import BaseModel

from fastgraphql import FastGraphQL
from fastgraphql.scalars import GraphQLDateTime
from fastgraphql.utils import MutableString


class TestCustomScalar:
    def test_custom_scalar_registration(self) -> None:

        fast_graphql = FastGraphQL()

        class Model(BaseModel):
            t_datetime: datetime

        @fast_graphql.type()
        class ReferingModel(BaseModel):  # NOSONAR
            model: Model

        assert len(fast_graphql.schema.scalars)
        assert isinstance(
            fast_graphql.schema.scalars[
                GraphQLDateTime(date_time_format=MutableString("")).name
            ],
            GraphQLDateTime,
        )
