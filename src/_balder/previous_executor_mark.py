from __future__ import annotations
from enum import Enum


class PreviousExecutorMark(Enum):
    """
    This enum defines the previous state of an executor object. It allows to set a pre-state to an executor, that
    describes if it is executable before the executor-tree will be called
    """
    #: this is the normal state, where all sub elements are allowed to be executed
    RUNNABLE = 1

    #: this marks the element and all of its sub elements as skip-able
    SKIP = 2

    #: this marks the element and all of its sub elements as NOT RUNNABLE, because this element is covered_by another
    COVERED_BY = 3

    #: this marks that the element should be ignored from the executor mechanism
    IGNORE = -1

    #: this marks that the element was already discarded because its variation is not applicable
    DISCARDED = -2
