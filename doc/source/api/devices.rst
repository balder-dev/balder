Devices API
***********

Every :class:`Scenario` and every :class:`Setup` describes a construction that consists of
:class:`Device`'s connected to each other via :class:`Connection` objects (connection-trees).

Basic ``Device``
================

The basic :class:`Device` class is the master class of every device object.

.. autoclass:: balder.Device
    :members:

Basic ``VDevice``
=================

For :class:`Feature` definitions you can define vDevices, the basic vDevice class is the class:`VDevice`.

.. autoclass:: balder.VDevice
    :members:
