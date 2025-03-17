from __future__ import annotations
from _balder.utils.inner_device_managing_metaclass import InnerDeviceManagingMetaclass


class Scenario(metaclass=InnerDeviceManagingMetaclass):
    """
    This is the basic scenario class. It represents an abstract class that should be the base class for all scenarios.
    """
    SKIP = []
    IGNORE = []

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------
