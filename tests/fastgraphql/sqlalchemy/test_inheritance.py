from typing import Any, cast

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from fastgraphql import FastGraphQL


class TestSQLInheritance:
    def test_inheritance_mixin(self) -> None:

        fast_graphql = FastGraphQL()
        Base: Any = declarative_base()  # NOSONAR
        fast_graphql.set_sqlalchemy_base(Base)

        class ModelMixin:
            id = Column(Integer, primary_key=True)

            @declared_attr
            def model1_id(self) -> Column[Integer]:
                return Column(Integer, ForeignKey("model1.id"))

            @declared_attr
            def model1(self) -> "Model1":
                return cast("Model1", relationship("Model1"))  # noqa

        @fast_graphql.type()
        class Model1(ModelMixin, Base):
            __tablename__ = "model1"
            extra_id = Column(Integer)

        assert (
            fast_graphql.render()
            == """
type Model1 {
    id: Int!
    extra_id: Int
    model1: Model1!
}
        """.strip()
        )
