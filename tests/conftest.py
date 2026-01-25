import numpy as np
import pytest
import stringalign


@pytest.fixture(autouse=True)
def reset_rng():
    stringalign.align.DEFAULT_RNG = np.random.default_rng(stringalign.align._DEFAULT_RANDOM_SEED)
