Features
********

Features implement functionality for a :ref:`Device <Devices>` class. For example, if you have a device that can send
messages, this device needs a :class:`Feature` class that implements the functionality to send those messages.

A :class:`Device` itself never implements this functionality. Instead, a :class:`Device` acts only as a container that
holds various :class:`Feature` classes.

The initial definition of a feature is typically done within the :class:`Scenario` class, specifically in a
:ref:`Scenario-Devices <Scenario-Device>`. As a reminder,
**a scenario describes the interface that must be implemented at minimum in the :ref:`Setup-Devices <Setup-Device>`**,
where the actual implementation is provided.

To make this easier to understand, let's examine the following example:

.. code-block:: python

    # file `lib/scenario_features/sender_feature.py`
    class SenderFeature(balder.Feature):

        def send(msg):
            raise NotImplementedError("this feature has to be implemented by subclass")


.. code-block:: python

    # file `scenarios/scenario_my.py`

    from lib.scenario_features.sender_feature import SenderFeature

    class MyScenario(balder.Scenario):

        class SenderDevice(balder.Device):

            sender = SenderFeature()

        def test_send_something():
            self.SenderDevice.sender.send("Hello World!")

So far, we have defined all the interfaces we need in our test ``test_send_something``, but we still lack the actual
implementation for them. So, let's take a look at the setup implementation. To do this, we'll add a new file and
implement the feature for our setup there:

.. code-block:: python

    # file `lib/setup_features/pipe_sender_feature.py`
    from lib.scenario_features.sender_feature import SenderFeature

    class PipeSenderFeature(SenderFeature):
        ...
        def send(msg):
            self.pipe.send(msg)

This feature class is no longer abstract. It implements all the abstract methods (in our case, the method ``send()``).
We can now use this feature in our setup class:

.. code-block:: python

    # file `setups/setup_my.py`
    from lib.setup_features.pipe_sender_feature import PipeSenderFeature

    class SetupMy(balder.Setup):

        class PipeDevice(balder.Device):
            pipe_sender = PipeSenderFeature()



As you can see you have to implement the feature and instantiate it in the same way, like you have instantiated it in
the scenario class.

Inner-Feature-Referencing
=========================

Sometimes it is necessary to refer to another feature from within a feature. For example, in the real-world example
from above, you might need access to the pipe. This can easily be achieved using inner-feature referencing.

Imagine we have another feature called ``ManagePipeFeature``, which provides some methods to interact with the pipe. We
can use it within ``PipeSenderFeature`` like that:

.. code-block:: python

    # file `lib/setup_features/pipe_sender_feature.py`
    from lib.scenario_features.sender_feature import SenderFeature

    class PipeSenderFeature(SenderFeature):

        pipe = ManagePipeFeature()

        def send(msg):
            self.pipe.send(msg)

You simply have to instantiate it as class attribute inside your feature. This will automatically lead to the behavior,
that Balder assumes that your feature only works with a device, that also provides an implementation for the
``ManagePipeFeature``. The reference inside your feature will automatically provided by Balder on variation-level.

You simply need to instantiate it as a class attribute inside the feature, that wants to use it. This will automatically
result in Balder assuming that your feature only works with a device that also provides an implementation for the
``ManagePipeFeature``.

So this means, that we need to add the ``ManagePipeFeature`` to our setup like that:

.. code-block:: python

    # file `setups/setup_my.py`
    from lib.setup_features.manage_pipe_feature import ManagePipeFeature
    from lib.setup_features.pipe_sender_feature import PipeSenderFeature

    class SetupMy(balder.Scenario):

        class PipeDevice(balder.Device):
            pipe_manager = ManagePipeFeature()
            pipe_sender = PipeSenderFeature()



.. note::
    You don't need to make any changes in the scenario, as the scenario isn't concerned with how you provide the
    implementation. This detail is only relevant to the specific setup implementation - in this case, via the
    ``ManagePipeFeature``.

Autonomous-Features
===================

Autonomous features are a special type of :class:`Feature` class. These features have no methods or properties of
their own; they are only used to indicate that: **This device has the feature IsRedFeature.**

We use them for filtering because we only want to match with a setup device that provides the same feature.

Defining such an autonomous feature is really straightforward:

.. code-block:: python

    # file `lib/scenario_features/pipe_mirror_autonomous_feature.py`

    class PipeMirrorAutonomousFeature(balder.Feature):
        # an autonomous feature has no implementation
        pass


An autonomous feature behaves the same way as a normal :class:`Feature`. Since you can't interact with it directly, we
highly recommend assigning it to a property name that starts with an underscore:

.. code-block:: python

    # file `scenarios/scenario_my.py`
    import balder

    from lib.scenario_features.pipe_mirror_autonomous_feature import PipeMirrorAutonomousFeature
    from lib.scenario_features.sender_feature import SenderFeature

    class MyScenario(balder.Scenario):

        class SenderDevice(balder.Device):
            sender = SenderFeature()

        @balder.connect(SenderDevice, over_connection=balder.Connection)
        class ReceiverDevice(balder.Device):
            _pipe_mirror = PipeMirrorAutonomousFeature()  # the autonomous feature


This is a good real-world example. Imagine you want to test whether the ``ReceiverDevice`` can mirror a message that
you've sent using another ``SenderDevice``. In this case, we can only influence the ``SenderDevice``, but we have no
way to interact with the ``ReceiverDevice``. We only know that this device can mirror the messages we've sent.

As we have done here, we can use an **autonomous feature** for our ``ReceiverDevice``, because we know the device must
have this capability, but we cannot influence it.

Your setup can use the same object. You don't need to override it, since you don't want to add any functionality to it.
So, we simply reuse this feature from the scenario level in our setup:

.. code-block:: python

    # file `setups/setup_my.py`
    import balder

    from lib.scenario_features.pipe_mirror_autonomous_feature import PipeMirrorAutonomousFeature
    from lib.setup_features.manage_pipe_feature import ManagePipeFeature
    from lib.setup_features.pipe_sender_feature import PipeSenderFeature


    class SetupMy(balder.Setup):

        class PipeDevice(balder.Device):
            pipe_manager = ManagePipeFeature()
            pipe_sender = PipeSenderFeature()

        @balder.connect(PipeDevice, over_connection=balder.Connection)
        class MirrorDevice(balder.Device):
            mirror = PipeMirrorAutonomousFeature()  # autonomous-device


Bind features
=============

One of the major advantages of Balder is its ability to reuse components, and this applies to features as well. However,
you often won't use them under exactly the same conditions.

That's where **binding features** comes in!

Features can be bound to peer devices, that needs to provide a specific feature-set. This can be done with
:class:`VDevice` classes, that are used within features to specify that you need another device with certain defined
features - one that interacts with the current device implementing the feature.

If you want to restrict the connections that the feature can use with this :class:`VDevice`, you can bind the feature
class itself. This approach is called **class-based binding**.

Additionally, you can bind individual methods of your feature to a subset of the allowed sub-connection tree, or limit
them to use with a specific ``VDevice`` only. This lets you define the same method multiple times, each with different
``@for_vdevice`` bindings. For example, you could implement a ``send()`` method that applies when the assigned
``VDevice`` is connected via a ``TcpConnection``. You could then add another ``send()`` method bound to a
``UdpConnection``. Depending on the current scenario or setup, Balder will automatically select and use the correct
method variation of ``send()`` when you call it in your test case. This is called **method-based binding**.

This section provides a general overview of how this mechanism works. For more detailed explanations, refer to the
:ref:`VDevices and method-variations` section.

Class-Based-Binding
-------------------

**Class-Based-Binding** can be defined with a :class:`Feature` class decorator ``@for_vdevice()``.

.. code-block:: python

    # file `lib/scenario_features/pipe_send_receive_feature.py`
    import balder
    from lib.connections import PipeConnection

    @balder.for_vdevice("OtherPipeVDevice", with_connections=[PipeConnection])
    class PipeSendReceiveFeature(balder.Feature):

        class OtherPipeVDevice(balder.VDevice):
            ...

The example illustrates that this feature requires a ``PipeConnection`` for every connection with the mapped device of
the inner VDevice ``OtherPipeVDevice``.

But how do you assign which device should be mapped to the VDevice?

You must provide this mapping in the constructor of the feature as a key-value pair. For our example, you add the
attribute ``OtherPipeVDevice="PipeDevice2"`` to the feature constructor to specify that the scenario device
``PipeDevice2`` should be mapped to the ``OtherPipeVDevice`` VDevice.


.. code-block:: python

    # file `scenarios/my_scenario.py`
    import balder
    from lib.connections import PipeConnection
    from lib.scenario_features.pipe_send_receive_feature import PipeSendReceiveFeature

    class ScenarioMy(balder.Scenario):

        @balder.connect("PipeDevice2", over_connection=PipeConnection)
        class PipeDevice1(balder.Device):
            # Scenario-Device `PipeDevice2` will be mapped to VDevice `OtherPipeVDevice`
            pipe = PipeSendReceiveFeature(OtherPipeVDevice="PipeDevice2")

        class PipeDevice2(balder.Device):
            ...

        ...


.. note::
    In Python, whether you can directly reference a device class inside the ``@balder.connect(..)`` decorator or in
    the VDevice mapping in constructor depends on the order of definitions in your code. If the device class is defined
    before the decorator, you can reference it directly; otherwise, you cannot. To handle this, Balder also allows you
    to provide the device reference as a string instead.

You can apply this mapping to different devices, which might represent various usages of the same feature. For instance,
you could also specify that the ``PipeSendReceiveFeature`` feature of ``PipeDevice2`` should use a VDevice-device
mapping with ``PipeDevice1`` as well:

.. code-block:: python

    # file `scenarios/my_scenario.py`
    import balder
    from lib.connections import PipeConnection
    from lib.scenario_features.pipe_send_receive_feature import PipeSendReceiveFeature

    class ScenarioMy(balder.Scenario):

        @balder.connect("PipeDevice2", over_connection=PipeConnection)
        class PipeDevice1(balder.Device):
            pipe = PipeSendReceiveFeature(OtherPipeVDevice="PipeDevice2")

        class PipeDevice2(balder.Device):
            pipe = PipeSendReceiveFeature(OtherPipeVDevice="PipeDevice1")

        ...


The ``@balder.connect(PipeDevice2, over_connection=PipeConnection)`` is necessary here because, when using the
``PipeSendReceiveFeature``, we must fulfill the requirement defined by
``@balder.for_vdevice("OtherPipeVDevice", with_connections=[PipeConnection])``. Since we've specified that we want to
use the other scenario device as our VDevice, we also need to ensure the appropriate ``PipeConnection`` exists between
them.

As you can see, this scenario defines that both devices - ``PipeDevice1`` and ``PipeDevice2`` - are connected via a
``PipeConnection``. If we tried to use our feature without this connection between the devices, it would lead to an
error, since the ``PipeSendReceiveFeature`` simply wouldn't apply in that case.

.. note::
    Balder verifies whether the requirement specified through the **Class-Based-Binding** is met. If the requirement
    does not match the class-based declaration, it raises an error!

You can use this mechanism at the setup level too. If you'd like to learn more about it, check out the
:ref:`VDevices and method-variations` section.

Method-Based-Binding
--------------------

Often, it is necessary to provide different implementations for different VDevices or different sub-connection trees
within a single feature. To achieve this, you can use **Method-Based-Binding**.

Let's assume we have a feature that can send a message to another device. In this case, the connection type doesn't
really matter, because the feature should generally support this requirement over any possible connection. The key point
is simply to test that the device can send a message to another device - it doesn't matter how the
feature sends this message (at least at the scenario level).

This is different, when we want to build universal (setup-level) features. Of course, we could build multiple features,
one for TCP and another for serial, but sometimes it makes sense to summarize the logic within one features. With Balder,
you can implement the same method multiple times and decorate it with a specific requirement, that needs to be fulfilled
so that this method is executed.

This is different when we want to create universal features at the setup level. Of course, we could create multiple
separate features, but sometimes it makes sense to consolidate the logic within a single feature. With Balder, you can
implement the same method multiple times and decorate each variation with a specific requirement that must be met for
that particular implementation to be executed.

In this example, we want to implement the messaging feature for one or more devices that can send messages over TCP or
over a serial connection. To do this, we'll add one :class:`VDevice` that represents the receiving side by including
the feature ``RecvMessengerFeature`` in it. Our sending feature itself will have two possible methods for sending the
message: one for sending over TCP and another for sending over serial.

Basically, our scenario-level implementation looks like:

.. code-block:: python

    # file `lib/scenario_features.py`
    import balder
    from balder.connections import TcpConnection
    from lib.connections import SerialConnection

    ...

    @balder.for_vdevice('OtherVDevice', with_connections=TcpConnection | SerialConnection)
    class SendMessengerFeature(balder.Feature):

        class OtherVDevice(balder.VDevice):
            msg = RecvMessengerFeature()

        def send(msg) -> None:
            raise NotImplementedError("this method has to be implemented in setup")


As you can see, we've defined the inner VDevice ``OtherVDevice`` here. We want to associate the feature
``RecvMessengerFeature`` with this VDevice. To do this, we instantiate it as a class property of the ``OtherVDevice``.
This enables us to specify the requirements that the mapped device must implement directly within this feature.

.. note::
    The elements specified in the inner VDevice class definition are **MUST HAVE**. This means that they must be
    available in the mapped device later on; otherwise, Balder will raise an error.

Up to now, the scenario feature doesn't use any **Method-Based-Bindings**. This will change shortly when we implement
the setup-level representation of this feature.

Before we proceed with the setup implementation, let's create a :ref:`Scenario <Scenarios>` that uses this newly
created feature. To do this, we'll implement an example scenario with two devices that communicate with each other.

.. code-block:: python

    # file `scenarios/scenario_my.py`
    import balder
    import balder.connections as cnn
    from lib import scenario_features
    from lib.connections import SerialConnection

    class ScenarioMy(balder.Scenario):

        class SendDevice(balder.Device):
            send = scenario_features.SendMessengerFeature(RecvVDevice="RecvDevice")

        # on scenario level, we are using a serial OR a TCP connection
        @balder.connect(SendDevice, over_connection=SerialConnection | cnn.TcpConnection)
        class RecvDevice(balder.VDevice):
            recv = scenario_features.RecvMessengerFeature(SendVDevice="SendDevice")

        def test_check_communication(self):
            SEND_DATA = "Hello World"
            self.RecvDevice.recv.start_async_receiving()
            self.SendDevice.send.send(SEND_DATA)
            all_messages = self.RecvDevice.recv.get_msgs()
            assert len(all_messages) == 1, "have not received anything"
            assert all_messages[0] == SEND_DATA, "have not received the sent data

As you can see, we've created a mapping for the inner :class:`VDevice` to a real, defined scenario :class:`Device` by
using the name of the inner VDevice as the key and the name of the real device as the value in the constructor. We've
also implemented a basic test to check the communication.

Now, let's move on to implementing the setup level. We can create our earlier defined feature by simply inheriting
from it. In this child class, we want to provide two different implementations for our abstract method send - one for
a serial connection and another for a TCP connection. To achieve this, we can use the **Method-Based-Binding**
decorator:

.. code-block:: python

    # file `lib/setup_features.py`
    import balder
    from balder.connections import TcpConnection
    from lib import scenario_features
    from .connections import SerialConnection

    class SetupSendMessengerFeature(scenario_features.SendMessengerFeature):

        @balder.for_vdevice(scenario_features.SendMessengerFeature.OtherVDevice, with_connections=SerialConnection)
        def send(self, msg) -> None:
            serial = MySerial(com=..)
            ...

        @balder.for_vdevice(scenario_features.SendMessengerFeature.OtherVDevice, with_connections=TcpConnection)
        def send(self, msg) -> None:
            sock = socket.socket(...)
            ...

As you can see, you can provide completely different implementations for the various sub-connection types. Depending on
the actual connection used (that is, the specific sub-connection over which the setup devices are linked to each other),
Balder will automatically call the corresponding method variation.

Now, let's take a look at the following :class:`Setup` that matches our :class:`Scenario` and supports both connections.

.. code-block:: python

    # file `setups/setup_my.py`
    import balder
    import balder.connections as cnn
    from lib import setup_features

    class MySetup(balder.Setup):

        @balder.connect(SlaveDevice, over_connection=cnn.TcpConnection)
        class MainDevice(balder.Device):
            msg = setup_features.SetupSendMessengerFeature()

        class SlaveDevice(balder.Device):
            recv = setup_features.SetupRecvMessengerFeature()

This example connects the two relevant devices over a :class:`TcpConnection` with each other, because the scenario
defines, that the devices should be connected over an TcpConnection. If the test
now uses on of our methods ``SendMessengerFeature.send(..)``, the variation with the decorator
``@balder.for_vdevice(..., over_connection=TcpConnection)`` will be used.

If one would exchange the connection with the ``SerialConnection``, Balder would select the method variation with the
decorator ``@balder.for_vdevice(..., with_connection=SerialConnection)``.

This example connects the two relevant devices to each other via a :class:`TcpConnection`. When the test calls one of
our methods, such as ``MyMessengerFeature.send(..)``, Balder will use the method variation decorated with
``@balder.for_vdevice(..., over_connection=TcpConnection)``.

If we were to replace that connection with a ``SerialConnection``, Balder would instead select the method variation
decorated with ``@balder.for_vdevice(..., with_connection=SerialConnection)``.

.. note::
    In the setup example, there is no VDevice-device mapping. This isn't necessary, as we've already specified it at
    the scenario level.

Feature inheritance
===================

.. warning::
    This section is still under development.

..
    .. todo