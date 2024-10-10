import random
from typing import cast


def interleave_strings(s1: str, s2: str, rng: random.Random) -> str:
    """Inserts the characters of the second string into the first string at random positions.
    The order of the characters in the strings is preserved.

    Example:
    --------
    >>> interleave_strings('abc', 'def', random.Random(0))
    'adebfc'
    >>> interleave_strings('Hello', 'sun', random.Random(0))
    'Hselunlo'
    """
    out: list[str | None] = [None] * (len(s1) + len(s2))
    s1_indices = sorted(rng.sample(range(len(out)), len(s1)))
    s2_indices = sorted(set(range(len(out))) - set(s1_indices))

    for c, i in zip(s1, s1_indices):
        out[i] = c
    for c, i in zip(s2, s2_indices):
        out[i] = c

    assert all(isinstance(c, str) for c in out)
    return "".join(cast(list[str], out))


def caseswap_n_randomly(s: str, n: int, rng: random.Random) -> str:
    """Randomly swaps the case of n characters in the string s."""
    indices = rng.sample(range(len(s)), n)
    lst = list(s)
    for i in indices:
        lst[i] = s[i].swapcase()
    return "".join(lst)


def remove_n_characters(s: str, n: int, rng: random.Random) -> str:
    """Removes n characters from the string s."""
    indices = sorted(rng.sample(range(len(s)), len(s) - n))
    return "".join(s[i] for i in indices)
