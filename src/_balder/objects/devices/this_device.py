from __future__ import annotations

from _balder.device import Device


class ThisDevice(Device):
    """
    This class describes the test computer on which this code is currently being executed. It represents an abstract
    class that must not be used directly. Rather, it serves as the large superclass over all Balder objects.

    Note that this is the parent class for the :class:`Setup` inner class :class:`Setup.DeviceThis`.
    """
