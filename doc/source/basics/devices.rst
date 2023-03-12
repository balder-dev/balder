Devices
*******

.. important::

    .. todo complete reworking of this section

    Please note that this part of the documentation is not yet finished. It will still be revised and updated.

A device describes a single component of a :ref:`Scenario <Scenarios>` or of a :ref:`Setup <Setups>`. Generally they are
container classes for a collection of :ref:`Features`.

Scenario-Device
===============

A :ref:`Scenario-Device` is a device, that defines a subset of :ref:`Features`, a possible :ref:`Setup-Device` should
have. Balder searches for matches (see also :ref:`Matching process of setups and scenarios (SOLVING)`), where the
potential :ref:`Setup-Device` has an implementation for the :ref:`Features` of the :ref:`Scenario-Device`.

So when is a :class:`Device` a scenario-device? - This depends one the definition location. A :class:`Device` is
a :ref:`Scenario-Device` when it is an inner-class of a :class:`Scenario`.

.. code-block:: py

    # file `scenario_basic/scenario_basic.py`

    import balder
    from .features import SendFeature, RecvFeature

    class ScenarioBasic(balder.Scenario):
        ...

        class MyDevice(balder.Device):
            send = SendFeature()
            recv = RecvFeature()

        ...

The shown scenario ``ScenarioBasic`` has one :ref:`Scenario-Device` with the name ``MyDevice``, that requires two
:ref:`Features`: ``SendFeature`` and ``RecvFeature``.

Setup-Device
============

On the other hand, a :ref:`Setup-Device` is a :class:`Device`, that describes what we have. These devices contains
the absolute implementation of the :ref:`Features`, that will be used for the scenarios later.
:ref:`Setup-Devices <Setup-Device>` looks similar to :ref:`Scenario-Devices <Scenario-Device>`, but are defined as
inner-classes in :ref:`Setups` of course.


.. code-block:: py

    # file `setup_at_home/setup_at_home.py`

    import balder
    # contains the absolute implementation of ``SendFeature`` and ``RecvFeature``
    from .setup_features import MySendFeatureImpl, MyRecvFeatureImpl

    class SetupAtHome(balder.Setup):
        ...

        class MainDevice(balder.Device):

            send = MySendFeatureImpl()
            recv = MyRecvFeatureImpl()
            ...
        ...

Often the :ref:`Features` of a :ref:`Setup-Device` implement the complete logic, while the features of the
:ref:`Scenario-Device` only describes the abstract architecture. This can be done, because the :ref:`Features` of the
:ref:`Setup-Devices <Setup-Device>` are subclasses of the scenario-device :ref:`Features`. You can find more
information about this in the sections :ref:`Features` and :ref:`Matching process of setups and scenarios (SOLVING)`.


Connect Devices
===============

Regardless of whether is a :ref:`Scenario-Device` or a :ref:`Setup-Device` you can simply connect two
devices with the ``@balder.connect(..)`` decorator.

.. code-block:: py

    import balder
    import balder.connections as conn

    class MyScenario(balder.Scenario):

        class DeviceA(balder.Device):
            ...

        @balder.connect(DeviceA, over_connection=conn.TcpConnection)
        class DeviceB(balder.Device):
            ...

        ..

Over this decorator you can define different sub :ref:`Connections` within the ``over_connection`` argument. For more
information how the connection mechanism works, see :ref:`Connections`.
