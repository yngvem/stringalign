from stringalign.evaluation import FrozenDict


def test_simple_example():
    fd = FrozenDict({"key1": "value1", "key2": "value2"})
    assert repr(fd) == "FrozenDict({'key1': 'value1', 'key2': 'value2'})"
