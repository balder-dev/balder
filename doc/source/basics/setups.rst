Setups
******

Setup classes describe your real-world test environment. They explain **what you have** (in contrast to
:ref:`Scenarios`, which describe **what you need**). A :class:`Setup` outlines the structure of :ref:`Devices` and their
relationships to each other. It also includes the final implementation of all :ref:`Features` that the :ref:`Devices`
should provide.

Add devices
===========

You develop a :class:`Setup`, by defining all :ref:`Setup-Devices <Setup-Device>` you have in your test rack or in your
current test environment. If you want to test a real device, you normally has a computer, you device-under-test and so
on. These are connected with each other. In the setup, you describe everything you have. This can also mean, that you
have a client and a server, where the server may not be near you, but it is connected over the internet. You could also
test a local installed program, so your setup could be this test-process-device and the program-process-device while
both are connected over an inter-process-connection or an file. The term **Setup** is very broad and flexible.

You can start with the device that executes these tests. Often this is a normal computer or a server. This is your
first device, that you can register to your :class:`Setup`.

To develop a :class:`Setup`, start by defining all the :ref:`Setup-Devices <Setup-Device>` available in your test
rack or current test environment. For example, if you want to test a real device, you normally have a computer, your
device-under-test, and so on. These components are connected to each other. In the setup, you describe
**everything you have**. This could include a client and a server, where the server might not be physically near you
but is connected over the internet. You could also test a locally installed program, so your setup might consist of a
test-process device and a program-process device, with both connected via inter-process communication or a shared file.
The term Setup is very broad and flexible.

Defining your first Device
--------------------------

Similar to :ref:`Scenarios`, you can create a new :class:`Device` in your setup by simply defining a new inner class
and inheriting from :class:`Device`.

.. code-block:: python

    import balder

    class SetupBasic(balder.Setup):

        class ThisDevice(balder.Device):
            ...
        ...


Add other device
----------------
Feel free to create additional devices as needed. You should include all the devices you intend to use in your tests
within this setup. Balder will automatically identify matching variations between your setups and scenarios.

To expand our previous example, let's add a new :class:`Device` called ``DeviceUnderTest`` and connect it to the existing
device using a ``Connection``.

.. code-block:: py

    import balder

    class SetupBasic(balder.Setup):

        class ThisDevice(balder.Device):
            ...

        @balder.connect(ThisDevice, over_connection=balder.Connection)
        class DeviceUnderTest(balder.Device):
            ...

        ...

That's all for now. We have defined our devices and their relationships with each other. In the next step, we just need
to add the supported :ref:`Features` for these devices.

Add setup-device features
=========================

Last but not least, we need to add some features to our devices. These features typically come from the definitions in
the scenario. A scenario specifies the features it requires, so for a setup to match a scenario, the setup must provide
implementations for those features.

If we have a scenario like the following:

.. code-block:: python

    # file `scenarios/scenario_simple_send_msg.py`

    import balder
    from lib.scenario_features.messaging_features import SendMessageFeature, RecvMessageFeature

    class ScenarioSimpleSendMsg(balder.Scenario):

        class SendDevice(balder.Device):
            send = SendMessageFeature()

        @balder.connect(SendDevice, over_connection=balder.Connection)
        class RecvDevice(balder.Device):
            recv = RecvMessageFeature()

    ...

We need a setup, that has two similar devices, but with features that provides an implementation. This can be realized
by overwriting the abstract features ``SendMessageFeature`` and ``RecvMessageFeature``, like shown in the following
snippet:

We need a setup that includes two similar devices, each equipped with features that provide concrete implementations.
This can be achieved by overriding the abstract features ``SendMessageFeature`` and ``RecvMessageFeature``, as shown in
the following snippet:

.. code-block:: python

    # file: lib/setup_features/messaging_features.py

    from lib.scenario_features.messaging_features import SendMessageFeature, RecvMessageFeature

    class SendMessageFeatureImpl(SendMessageFeature):
        ... # provide an implementation for all abstract properties / methods

    class RecvMessageImplFeature(RecvMessageFeature):
        ... # provide an implementation for all abstract properties / methods


We can now use our final implemented features within our setup:

.. code-block:: python

    import balder
    import balder.connections as conn
    # contains the implementation of the scenario features above (non abstract methods anymore
    from lib.setup_features.messaging_features import SendMessageFeatureImpl, RecvMessageImplFeature

    class SetupBasic(balder.Setup):

        class ThisDevice(balder.Device):
            send_impl = SendMessageFeatureImpl()

        @balder.connect(ThisDevice, over_connection=conn.HttpConnection)
        class DeviceUnderTest(balder.Device):
            recv_impl = RecvMessageImplFeature()

        ...

As soon as Balder is executed it will detect the variation between the ``SetupBasic`` and ``ScenarioSimpleSendMsg`` and
runs the test ceases from ``ScenarioSimpleSendMsg``. Internally it will replaces the feature attributes
``ScenarioSimpleSendMsg.SendDevice.send`` and ``ScenarioSimpleSendMsg.RecvDevice.recv`` with the setup instances of
these final matching feature implementations ``SendMessageFeatureImpl`` and ``RecvMessageImplFeature``.

Setup inheritance
=================

Similar to scenarios, Balder supports inheritance for setup classes too, just like in standard Python class inheritance.
This allows you to create a base setup with common elements—such as devices, features, connections, and test methods
and then extend or modify it in child setup. It's particularly helpful when you have similar test environments that
share a lot of setup but differ in specific details. For example, you might have a general scenario for testing network
communication, and then create child setups for specific protocols like HTTP or MQTT.


To use inheritance, simply subclass your new setup from an existing one. Balder will automatically inherit all the
devices, features, connections, and test methods from the parent class. You can add new elements or override existing
ones in the subclass.

Overwriting Setup-Devices
-------------------------

Similar to scenarios, you can overwrite devices and **extend** their feature set. Beside of providing the device parent
class it is also important to use the same device names for the overwritten device like the name that is used in the
parent class.
This ensures that Balder can properly map, connect, and resolve the devices across the inheritance chain without
conflicts.

Extending Features
------------------

You can freely add more features to the sub setup, by just adding them to the new device class. Similar to scenarios, it
is also allowed to extend the functionality of existing features, by overwriting them. But be careful, you need to make
sure to use the same attribute name and only assign features that are a sub class of the previous feature defined in the
parent setup class.