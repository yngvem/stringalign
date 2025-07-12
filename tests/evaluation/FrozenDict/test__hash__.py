import pytest
from stringalign.evaluation import FrozenDict


def test_simple_example_equal():
    """Two FrozenDicts with the same content should have same hash."""
    fd1 = FrozenDict({"key1": "value1", "key2": "value2"})
    fd2 = FrozenDict({"key1": "value1", "key2": "value2"})
    assert hash(fd1) == hash(fd2)


def test_simple_example_not_equal():
    """Two FrozenDicts with different content should have different hashes."""
    fd1 = FrozenDict({"key1": "value1", "key2": "value2"})
    fd2 = FrozenDict({"key1": "value1", "key2": "value3"})
    assert hash(fd1) != hash(fd2)


def test_works_with_unhashable_values():
    """We can compute the hash of a FrozenDict even if it has unhashable values."""
    unhashable = ["hello"]
    fd = FrozenDict({"key": unhashable})

    with pytest.raises(TypeError):
        hash(unhashable)

    assert hash(fd) is not None  # This should not raise a type error
