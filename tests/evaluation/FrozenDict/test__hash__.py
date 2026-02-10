import builtins
from typing import Any

import pytest
from stringalign.evaluation import FrozenDict


def test_simple_example_equal() -> None:
    """Two FrozenDicts with the same content should have same hash."""
    fd1 = FrozenDict({"key1": "value1", "key2": "value2"})
    fd2 = FrozenDict({"key1": "value1", "key2": "value2"})
    assert hash(fd1) == hash(fd2)


def test_simple_example_not_equal() -> None:
    """Two FrozenDicts with different content should have different hashes."""
    fd1 = FrozenDict({"key1": "value1", "key2": "value2"})
    fd2 = FrozenDict({"key1": "value1", "key2": "value3"})
    assert hash(fd1) != hash(fd2)


def test_works_with_unhashable_values() -> None:
    """We can compute the hash of a FrozenDict even if it has unhashable values."""
    unhashable = ["hello"]
    fd = FrozenDict({"key": unhashable})

    with pytest.raises(TypeError):
        hash(unhashable)

    assert hash(fd) is not None  # This should not raise a type error


def test_hash_twice(monkeypatch: pytest.MonkeyPatch) -> None:
    """When you hash a Frozendict twice, the hash is cached"""
    hash_counter = 0

    def mocked_hash(object: Any) -> int:
        nonlocal hash_counter
        hash_counter += 1
        return 0

    monkeypatch.setattr(builtins, "hash", mocked_hash)
    fd1 = FrozenDict({"key1": "value1", "key2": "value2"})
    hash_value1 = fd1.__hash__()

    # The two values are hashed seperately, and then
    # the keys and values are hashed together
    assert hash_counter == 3

    hash_value2 = fd1.__hash__()

    assert hash_counter == 3
    assert hash_value2 == hash_value1 == 0
