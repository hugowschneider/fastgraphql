import os

import pytest

from fastgraphql.utils import get_env_bool


class TestUtils:
    def test_not_set(self) -> None:
        with pytest.raises(ValueError):
            get_env_bool("DO_NOT_EXIST")

    def test_default(self) -> None:
        value = get_env_bool("DO_NOT_EXIST", default_value=False)
        assert not value

        value = get_env_bool("DO_NOT_EXIST", default_value=True)
        assert value

    def test_false(self) -> None:
        key = "FALSE_VALUE"
        os.environ[key] = "0"
        value = get_env_bool(key, default_value=False)
        assert not value

        os.environ[key] = "f"
        value = get_env_bool(key, default_value=False)
        assert not value

        os.environ[key] = "false"
        value = get_env_bool(key, default_value=False)
        assert not value

    def test_true(self) -> None:
        key = "TRUE_VALUE"
        os.environ[key] = "1"
        value = get_env_bool(key, default_value=False)
        assert value

        os.environ[key] = "t"
        value = get_env_bool(key, default_value=False)
        assert value

        os.environ[key] = "true"
        value = get_env_bool(key, default_value=False)
        assert value

    def test_funky_value(self) -> None:
        key = "FUNKY_VALUE"
        os.environ[key] = "x"
        value = get_env_bool(key, default_value=False)
        assert not value
