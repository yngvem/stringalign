import sys

if sys.version_info >= (3, 12):
    from itertools import batched
else:
    from itertools import islice
    from typing import Iterable, Iterator, TypeVar

    T = TypeVar("T")

    def batched(iterable: Iterable[T], n: int) -> Generator[islice[T], None, None]:
        if n < 1:
            raise ValueError("n must be at least one")
        it = iter(iterable)
        while batch := islice(it, n):
            yield batch
