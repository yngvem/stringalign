from stringalign.evaluation import FrozenDict


def test_simple_examples():
    fd = FrozenDict()
    assert len(fd) == 0

    fd = FrozenDict({"key": "value"})
    assert len(fd) == 1

    fd = FrozenDict({"key1": "value1", "key2": "value2"})
    assert len(fd) == 2
