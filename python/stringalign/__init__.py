from importlib.metadata import version

import stringalign.align as align
import stringalign.evaluation as evaluation
import stringalign.normalize as normalize
import stringalign.statistics as statistics
import stringalign.tokenize as tokenize
import stringalign.visualize as visualize

__all__ = [
    "align",
    "evaluation",
    "normalize",
    "statistics",
    "tokenize",
    "visualize",
]

__version__ = version(__name__)
