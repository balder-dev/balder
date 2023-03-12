Features API
************

:class:`Feature`'s are objects that defines the necessary implementation and settings that a :class:`Device`
should or do implement. The :class:`Device` class of a :class:`Scenario` instantiates a
:class:`Feature` and uses the (mostly abstract) interface to implement the test :class:`Scenario`.

On the other side the :class:`Device` class of a :class:`Setup` overwrites the (mostly abstract)
:class:`Feature` implementations and defines the real properties and implementation methods in that overwritten
class.

Basic ``Feature``
=================

The basic :class:`Feature` class is the master class of every scenario.

.. autoclass:: balder.Feature
    :members:
