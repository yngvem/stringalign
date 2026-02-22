from importlib.metadata import version

import stringalign.align as align
import stringalign.evaluate as evaluate
import stringalign.normalize as normalize
import stringalign.statistics as statistics
import stringalign.tokenize as tokenize
import stringalign.visualize as visualize

__all__ = [
    "align",
    "evaluate",
    "normalize",
    "statistics",
    "tokenize",
    "visualize",
]

__version__ = version(__name__)
