import hypothesis.strategies as st
import numpy as np
from hypothesis import given
from stringalign.align import create_cost_matrix


@given(reference=st.text(), predicted=st.text())
def test_cost_matrix_shape(reference: str, predicted: str) -> None:
    cost_matrix = create_cost_matrix(list(reference), list(predicted))
    assert cost_matrix.shape == (len(reference) + 1, len(predicted) + 1)


@given(reference=st.text(), predicted=st.text())
def test_cost_matrix_first_row_and_column(reference: str, predicted: str) -> None:
    cost_matrix = create_cost_matrix(list(reference), list(predicted))
    assert np.array_equal(cost_matrix[0, :], np.arange(len(predicted) + 1))
    assert np.array_equal(cost_matrix[:, 0], np.arange(len(reference) + 1))


@given(reference=st.text(), predicted=st.text())
def test_cost_matrix_values(reference: str, predicted: str) -> None:
    cost_matrix = create_cost_matrix(list(reference), list(predicted))

    assert cost_matrix.max() <= max(len(reference), len(predicted))
    for i in range(1, len(reference) + 1):
        for j in range(1, len(predicted) + 1):
            assert cost_matrix[i, j] >= min(cost_matrix[i - 1, j], cost_matrix[i, j - 1], cost_matrix[i - 1, j - 1])
            assert cost_matrix[i, j] <= 1 + max(cost_matrix[i - 1, j], cost_matrix[i, j - 1], cost_matrix[i - 1, j - 1])


@given(text=st.text())
def test_cost_matrix_identical_strings(text: str) -> None:
    cost_matrix = create_cost_matrix(list(text), list(text))
    assert np.array_equal(np.diag(cost_matrix), np.zeros(len(text) + 1))
