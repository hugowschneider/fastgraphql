# noqa

from pydantic import BaseModel

from fastgraphql import FastGraphQL


class TestInhiretance:
    def test_inheritance(self) -> None:

        fast_graphql = FastGraphQL()

        class Model(BaseModel):
            name: str

        @fast_graphql.type()
        class ChildModel(Model, BaseModel):
            last_name: str

        assert (
            fast_graphql.render()
            == """
type ChildModel {
    name: String!
    last_name: String!
}
        """.strip()
        )

    def test_inheritance_super_type(self) -> None:

        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        class Model(BaseModel):
            name: str

        @fast_graphql.type()
        class ChildModel(Model, BaseModel):
            last_name: str

        assert (
            fast_graphql.render()
            == """
type ChildModel {
    name: String!
    last_name: String!
}

type Model {
    name: String!
}
        """.strip()
        )
