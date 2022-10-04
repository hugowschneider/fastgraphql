from pydantic import BaseModel

from fastgraphql.application import FastGraphQL
from fastgraphql.schema import SelfGraphQL


class TestMixedAnnotationsRendering:
    def test_type_input(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        @fast_graphql.input(name="ModelInput")
        class Model(BaseModel):
            t_int: int

        self_graphql = SelfGraphQL.introspect(Model)
        assert self_graphql
        assert self_graphql.as_type
        assert self_graphql.as_input
        assert self_graphql.as_type.name == "Model"
        assert self_graphql.as_input.name == "ModelInput"

    def test_input_type(self) -> None:
        fast_graphql = FastGraphQL()

        @fast_graphql.input(name="ModelInput")
        @fast_graphql.type()
        class Model(BaseModel):
            t_int: int

        self_graphql = SelfGraphQL.introspect(Model)
        assert self_graphql
        assert self_graphql.as_type
        assert self_graphql.as_input
        assert self_graphql.as_type.name == "Model"
        assert self_graphql.as_input.name == "ModelInput"
