from typing import Any

import pytest
from sqlalchemy import (
    Column,
    Integer,
)
from sqlalchemy.orm import query_expression

from fastgraphql import FastGraphQL
from sqlalchemy.ext.declarative import declarative_base

from fastgraphql.schema import SelfGraphQL

TEST_TABLE_ID = "test1.id"

expected_scalar_def = """
scalar DateTime
        """.strip()


@pytest.fixture(scope="function")
def fast_graphql() -> FastGraphQL:
    fast_graphql_ = FastGraphQL()
    return fast_graphql_


class TestSQLQueryExpression:
    def test_query_expression(self, fast_graphql: FastGraphQL) -> None:
        Base = declarative_base()  # type: Any # NOSONAR
        fast_graphql.set_sqlalchemy_base(Base)

        @fast_graphql.type()
        class TypeWithoutReferences(Base):
            __tablename__ = "test"
            t_int = Column(Integer, primary_key=True)
            t_query = query_expression()

        expected_graphql_def = """
type TypeWithoutReferences {
    t_int: Int!
} 
            """.strip()
        self_graphql = SelfGraphQL.introspect(TypeWithoutReferences)
        assert self_graphql
        assert self_graphql.as_type

        assert self_graphql.as_type.render() == expected_graphql_def
