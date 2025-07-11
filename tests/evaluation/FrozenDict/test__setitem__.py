import pytest
from stringalign.evaluation import FrozenDict


def test_frozendict_immutable() -> None:
    fd = FrozenDict({"key": "value"})

    with pytest.raises(TypeError):
        fd["new_key"] = "new_value"  # type: ignore
