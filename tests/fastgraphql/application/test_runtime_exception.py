from typing import ForwardRef

import pytest

from fastgraphql.exceptions import GraphQLRuntimeError
from fastgraphql.types import GraphQLDelayedType


class TestRuntimeExceptions:
    def test_delayed_type_rendering(self) -> None:
        with pytest.raises(GraphQLRuntimeError):
            GraphQLDelayedType(ForwardRef(arg="XYZ")).render()

    def test_delayed_ref_rendering(self) -> None:
        with pytest.raises(GraphQLRuntimeError):
            GraphQLDelayedType(ForwardRef(arg="XYZ")).ref(False).render()
