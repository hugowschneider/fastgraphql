from pydantic import BaseModel
from fastgraphql import FastGraphQL


class TestForwardReference:

    def test_forward_reference(self) -> None:

        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        class Model(BaseModel):
            name: str
            ref: "Model"

        assert fast_graphql.render() == """
type Model {
    name: String!
    ref: Model!
}
        """.strip()