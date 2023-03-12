Scenario API
************

Scenarios represents a abstract test setup, that is required to run a testmethod (testmethods are defined in
:class:`Scenario`'s). Just like the :class:`Setup` the :class:`Scenario` consists of one or more
:class:`Device`'s, which in turn instantiate the required :class:`Feature`'s.

Basic ``Scenario``
==================

The basic :class:`Scenario` class is the master class of every scenario.

.. autoclass:: balder.Scenario
    :members:

