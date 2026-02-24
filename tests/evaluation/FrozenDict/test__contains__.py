from stringalign.evaluate import FrozenDict


def test_simple_example():
    fd = FrozenDict({"key1": "value1", "key2": "value2"})
    assert "key1" in fd
    assert "key2" in fd
    assert "key3" not in fd
