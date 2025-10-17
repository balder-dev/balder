Devices
*******

A device represents a single component within a :ref:`Scenario <Scenarios>` or a :ref:`Setup <Setups>`. In general,
devices act as container classes that hold a collection of :ref:`Features <Features>`.

Scenario-Device
===============

A Scenario-Device is a device that defines a subset of :ref:`Features` that a possible :ref:`Setup-Device` **should**
have to be appliable. Balder searches for matches (see also :ref:`Matching process of setups and scenarios (SOLVING)`),
where the potential :ref:`Setup-Device` provides an implementation for the :ref:`Features` of the
:ref:`Scenario-Device`.

So when is a :class:`Device` considered a scenario-device? This depends on its definition location. A :class:`Device`
is a :ref:`Scenario-Device` when it is defined as an inner class of a :class:`Scenario`.

.. code-block:: python

    # file `scenarios/scenario_basic.py`

    import balder
    from lib.scenario_features import SendFeature, RecvFeature

    class ScenarioBasic(balder.Scenario):
        ...

        class MyDevice(balder.Device):
            send = SendFeature()
            recv = RecvFeature()

        ...

The shown scenario ``ScenarioBasic`` has one Scenario-Device with the name ``MyDevice``, that requires two
:ref:`Features`: ``SendFeature`` and ``RecvFeature``. It is defined within a scenario, which make it a scenario-device.

Setup-Device
============

On the other hand, a Setup-Device is a :class:`Device`, that describes **what we have**. These devices contains
the final implementation of the :ref:`Features`, that will be used when a variation with a scenario is executed.
Setup-Devices looks similar to :ref:`Scenario-Devices <Scenario-Device>`, but are defined as
inner-classes in :ref:`Setups` of course.


.. code-block:: python

    # file `setups/setup_at_home.py`

    import balder
    # contains the absolute implementation of ``SendFeature`` and ``RecvFeature``
    from lib.setup_features import MySendFeatureImpl, MyRecvFeatureImpl

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

Often, the :ref:`Features` of a :ref:`Setup-Device` implement the complete logic, while the features of a
:ref:`Scenario-Device` only describe the abstract architecture. This is possible because the :ref:`Features` of the
:ref:`Setup-Devices <Setup-Device>` are subclasses of the :ref:`Features` from the :ref:`Scenario-Device`. For more
details on this, refer to the sections :ref:`Features` and :ref:`Matching process of setups and scenarios (SOLVING)`.

Connect Devices
===============

Regardless of whether it is a :ref:`Scenario-Device` or a :ref:`Setup-Device`, you can simply connect two devices using
the ``@balder.connect(..)`` decorator.

.. code-block:: python

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

Using this decorator, you can define how devices and over which type of connection these
devices are connected with each other. For more details on how the connection mechanism works, refer to the
:ref:`Connections` section.
