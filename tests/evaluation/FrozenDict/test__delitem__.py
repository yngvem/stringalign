import pytest
from stringalign.evaluation import FrozenDict


def test_frozendict_immutable() -> None:
    fd = FrozenDict({"key": "value"})

    with pytest.raises(TypeError):
        del fd["new_key"]  # type: ignore
