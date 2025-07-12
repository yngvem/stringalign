from stringalign.evaluation import FrozenDict


def test_update_input_data_does_not_update_frozendict():
    """Updating the data used to initialize a FrozenDict should not update the FrozenDict"""

    data = {"key": "value"}
    fd = FrozenDict(data)

    data["key"] = "new value"
    data["new key"] = "hello"

    assert fd["key"] == "value"
    assert "new key" not in fd
