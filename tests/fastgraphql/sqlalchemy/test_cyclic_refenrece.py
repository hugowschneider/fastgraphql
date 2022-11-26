from typing import Any, cast

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from fastgraphql import FastGraphQL


class TestSQLCyclicReference:
    def test_self_reference(self) -> None:

        fast_graphql = FastGraphQL()
        Base: Any = declarative_base()  # NOSONAR
        fast_graphql.set_sqlalchemy_base(Base)

        @fast_graphql.type()
        class Model1(Base):
            __tablename__ = "model1"
            id = Column(Integer, primary_key=True)
            model1_id = Column(Integer, ForeignKey("model1.id"))
            model1: "Model1" = cast("Model1", relationship("Model1"))  # noqa

        assert (
            fast_graphql.render()
            == """
type Model1 {
    id: Int!
    model1: Model1!
}
        """.strip()
        )
