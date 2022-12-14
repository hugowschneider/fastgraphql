from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from fastgraphql import FastGraphQL
from fastgraphql.scalars import GraphQLID
from fastgraphql.schema import SelfGraphQL

expected_scalar_def = """
scalar DateTime
        """.strip()


class TestPydanticInputRendering:
    def test_simple_type(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.input()
        class TypeWithoutReferences(BaseModel):
            t_int: int
            t_opt_int: Optional[int]
            t_str: str
            t_opt_str: Optional[str]
            t_float: float
            t_opt_float: Optional[float]
            t_datatime: datetime
            t_opt_datatime: Optional[datetime]
            t_boolean: bool
            t_opt_boolean: Optional[bool]

        expected_graphql_def = """
input TypeWithoutReferences {
    t_int: Int!
    t_opt_int: Int
    t_str: String!
    t_opt_str: String
    t_float: Float!
    t_opt_float: Float
    t_datatime: DateTime!
    t_opt_datatime: DateTime
    t_boolean: Boolean!
    t_opt_boolean: Boolean
}
        """.strip()
        self_graphql = SelfGraphQL.introspect(TypeWithoutReferences)
        assert self_graphql
        assert self_graphql.as_input

        assert self_graphql.as_input.render() == expected_graphql_def

        print(fast_graphql.render())

        assert (
            fast_graphql.render() == expected_scalar_def + "\n\n" + expected_graphql_def
        )

    def test_simple_type_with_name(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.input(name="Type1")
        class TypeWithoutReferences(BaseModel):
            t_int: int
            t_opt_int: Optional[int]
            t_str: str
            t_opt_str: Optional[str]
            t_float: float
            t_opt_float: Optional[float]
            t_datatime: datetime
            t_opt_datatime: Optional[datetime]

        expected_graphql_def = """
input Type1 {
    t_int: Int!
    t_opt_int: Int
    t_str: String!
    t_opt_str: String
    t_float: Float!
    t_opt_float: Float
    t_datatime: DateTime!
    t_opt_datatime: DateTime
}
            """.strip()

        self_graphql = SelfGraphQL.introspect(TypeWithoutReferences)
        assert self_graphql
        assert self_graphql.as_input

        assert self_graphql.as_input.render() == expected_graphql_def

        assert (
            fast_graphql.render() == expected_scalar_def + "\n\n" + expected_graphql_def
        )

    def test_nested_type(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.input()
        class TypeWithoutReferences(BaseModel):
            t_int: int
            t_str: str
            t_float: float
            t_datatime: datetime

        @fast_graphql.input()
        class TypeWithReference(BaseModel):
            t_int: int
            t_type_with_references: TypeWithoutReferences

        expected_graphql_def = """
input TypeWithReference {
    t_int: Int!
    t_type_with_references: TypeWithoutReferences!
}
        """.strip()
        self_graphql = SelfGraphQL.introspect(TypeWithReference)
        assert self_graphql
        assert self_graphql.as_input

        assert self_graphql.as_input.render() == expected_graphql_def

        self_graphql = SelfGraphQL.introspect(TypeWithoutReferences)
        assert self_graphql
        assert self_graphql.as_input
        assert (
            fast_graphql.render()
            == expected_scalar_def
            + "\n\n"
            + expected_graphql_def
            + "\n\n"
            + self_graphql.as_input.render()
        )

    def test_nested_type_with_name(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.input(name="Type1")
        class TypeWithoutReferences(BaseModel):
            t_int: int
            t_str: str
            t_float: float
            t_datatime: datetime

        @fast_graphql.input(name="Type2")
        class TypeWithReference(BaseModel):
            t_int: int
            t_type_with_references: TypeWithoutReferences

        expected_graphql_def = """
input Type2 {
    t_int: Int!
    t_type_with_references: Type1!
}
        """.strip()
        self_graphql = SelfGraphQL.introspect(TypeWithReference)
        assert self_graphql
        assert self_graphql.as_input

        assert self_graphql.as_input.render() == expected_graphql_def
        self_graphql = SelfGraphQL.introspect(TypeWithoutReferences)

        assert self_graphql
        assert self_graphql.as_input
        assert (
            fast_graphql.render()
            == expected_scalar_def
            + "\n\n"
            + self_graphql.as_input.render()
            + "\n\n"
            + expected_graphql_def
        )

    def test_simple_type_exclude_attr(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.input(exclude_model_attrs=["t_int", "t_str"])
        class TypeWithoutReferences(BaseModel):
            t_int: int
            t_opt_int: Optional[int]
            t_str: str
            t_opt_str: Optional[str]
            t_float: float
            t_opt_float: Optional[float]
            t_datatime: datetime
            t_opt_datatime: Optional[datetime]

        expected_graphql_def = """
input TypeWithoutReferences {
    t_opt_int: Int
    t_opt_str: String
    t_float: Float!
    t_opt_float: Float
    t_datatime: DateTime!
    t_opt_datatime: DateTime
}
        """.strip()
        self_graphql = SelfGraphQL.introspect(TypeWithoutReferences)
        assert self_graphql
        assert self_graphql.as_input

        assert self_graphql.as_input.render() == expected_graphql_def

        assert (
            fast_graphql.render() == expected_scalar_def + "\n\n" + expected_graphql_def
        )

    def test_model_with_generic_types(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.input()
        class ModelWithGenericTypes(BaseModel):
            t_ints: List[int]
            t_str: List[str]
            t_float: List[float]
            t_dates: List[datetime]
            t_opt_ints: Optional[List[int]]
            t_opt_str: Optional[List[str]]
            t_opt_float: Optional[List[float]]
            t_opt_dates: Optional[List[datetime]]
            t_ints_opt: List[Optional[int]]
            t_str_opt: List[Optional[str]]
            t_float_opt: List[Optional[float]]
            t_dates_opt: List[Optional[datetime]]

        expected_graphql_def = """
input ModelWithGenericTypes {
    t_ints: [Int!]!
    t_str: [String!]!
    t_float: [Float!]!
    t_dates: [DateTime!]!
    t_opt_ints: [Int!]
    t_opt_str: [String!]
    t_opt_float: [Float!]
    t_opt_dates: [DateTime!]
    t_ints_opt: [Int]!
    t_str_opt: [String]!
    t_float_opt: [Float]!
    t_dates_opt: [DateTime]!
}
    """.strip()
        self_graphql = SelfGraphQL.introspect(ModelWithGenericTypes)
        assert self_graphql
        assert self_graphql.as_input

        assert self_graphql.as_input.render() == expected_graphql_def

    def test_graphql_id(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.input()
        class ModelWithId(BaseModel):
            t_id: str = Field(..., graphql_type=GraphQLID())

        expected_graphql_def = """
input ModelWithId {
    t_id: ID!
}""".strip()
        self_graphql = SelfGraphQL.introspect(ModelWithId)
        assert self_graphql
        assert self_graphql.as_input
        assert self_graphql.as_input.render() == expected_graphql_def

    def test_inherited_types(self) -> None:
        fast_graphql = FastGraphQL()

        class ParentModel(BaseModel):
            t_id: int

        @fast_graphql.input()
        class ChildModel(ParentModel):
            t_str: str

        expected_graphql_def = """
input ChildModel {
    t_id: Int!
    t_str: String!
}""".strip()

        assert not hasattr(ParentModel, "__graphql__")

        self_graphql = SelfGraphQL.introspect(ChildModel)
        assert self_graphql
        assert self_graphql.as_input
        assert self_graphql.as_input.render() == expected_graphql_def
