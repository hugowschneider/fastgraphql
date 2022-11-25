# noqa
from typing import List, Optional

from pydantic import BaseModel

from fastgraphql import FastGraphQL


class TestForwardReference:
    def test_self_reference(self) -> None:

        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        class Model(BaseModel):
            name: str
            ref: "Model"

        assert (
            fast_graphql.render()
            == """
type Model {
    name: String!
    ref: Model!
}
        """.strip()
        )

    def test_cyclic_reference(self) -> None:

        fast_graphql = FastGraphQL()

        @fast_graphql.type(name="model_1")
        class Model1(BaseModel):
            name: str
            ref: "Model2"
            ref_null: Optional["Model2"]  # noqa

        @fast_graphql.type(name="model_2")
        class Model2(BaseModel):
            name: str
            ref: Model1

        assert (
            fast_graphql.render()
            == """
type model_1 {
    name: String!
    ref: model_2!
    ref_null: model_2
}

type model_2 {
    name: String!
    ref: model_1!
}
        """.strip()
        )

    def test_cyclic_reference_inside_list(self) -> None:

        fast_graphql = FastGraphQL()

        @fast_graphql.type(name="model_1")
        class Model1(BaseModel):
            name: str
            ref: List["Model2"]  # noqa

        @fast_graphql.type(name="model_2")
        class Model2(BaseModel):
            name: str
            ref: Model1

        assert (
            fast_graphql.render()
            == """
type model_1 {
    name: String!
    ref: [model_2!]!
}

type model_2 {
    name: String!
    ref: model_1!
}
        """.strip()
        )

    def test_cyclic_reference_nullability(self) -> None:

        fast_graphql = FastGraphQL()

        @fast_graphql.type(name="model_1")
        class Model1(BaseModel):
            name: str
            ref_null: Optional["Model2"]  # noqa
            ref_list: List["Model2"]  # noqa
            ref_list_null: Optional[List["Model2"]]  # noqa
            ref_list_item_null: List[Optional["Model2"]]  # noqa

        @fast_graphql.type(name="model_2")
        class Model2(BaseModel):
            name: str
            ref: Model1

        assert (
            fast_graphql.render()
            == """
type model_1 {
    name: String!
    ref_null: model_2
    ref_list: [model_2!]!
    ref_list_null: [model_2!]
    ref_list_item_null: [model_2]!
}

type model_2 {
    name: String!
    ref: model_1!
}
        """.strip()
        )

    def test_longer_cyclic_reference(self) -> None:

        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        class Model1(BaseModel):
            name: str
            ref: "Model2"

        @fast_graphql.type()
        class Model2(BaseModel):
            name: str
            ref: "Model3"

        @fast_graphql.type()
        class Model3(BaseModel):
            name: str
            ref: Model1

        assert (
            fast_graphql.render()
            == """
type Model1 {
    name: String!
    ref: Model2!
}

type Model2 {
    name: String!
    ref: Model3!
}

type Model3 {
    name: String!
    ref: Model1!
}
        """.strip()
        )
