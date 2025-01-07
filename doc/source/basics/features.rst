Features
********

.. important::

    .. todo complete reworking of this section

    Please note that this part of the documentation is not yet finished. It will still be revised and updated.

Features implement functionality for a :ref:`Device <Devices>` class. For example, if you have a device
that could send messages, this device has to have a :class:`Feature` class that implements the functionality to send
these messages.
A :class:`Device` itself does never implement these functionality. A :class:`Device` is only a container that contains
different :class:`Feature` classes.

The first definition of a feature is normally done in the :class:`Scenario` class in a
:ref:`Scenario-Devices <Scenario-Device>`. If you remember, a scenario describes the interface, that should be
implemented at least in the :ref:`Setup-Devices <Setup-Device>`, where the real implementation is provided.
To understand this more easily, let's take a look at the following example:

.. code-block:: python

    # file `scenario_my/features.py`
    class SenderFeature(balder.Feature):

        def send(msg):
            raise NotImplementedError("this feature has to be implemented by feature class of setup")


.. code-block:: python

    # file `scenario_my/scenario_my.py`

    from .features import SenderFeature

    class MyScenario(balder.Scenario):

        class SenderDevice(balder.Device):

            sender = SenderFeature()

        def test_send_something():
            self.SenderDevice.sender.send("Hello World!")

Till now we have all interfaces we need in our test ``test_send_something``, but we have no real implementation for
that. So, let's take a look to the setup implementation. For this we add a file and implement the feature for our setup
there:

.. code-block:: python

    # file `my_setup/my_setup_features.py`
    from ..my_scenario.features import SenderFeature

    class PipeSenderFeature(SenderFeature):
        ...
        def send(msg):
            self.pipe.send(msg)

This feature class is not abstract anymore. It implements all the abstract methods (in our case the method ``send()``).
We can now use this feature in our setup class now:

.. code-block:: python

    # file `my_setup/setup_my.py`
    from .my_setup_features import PipeSenderFeature

    class SetupMy(balder.Scenario):

        class PipeDevice(balder.Device):
            pipe_sender = PipeSenderFeature()

.. note::
    You should only provide non-abstract features inside an active setup


As you can see you have to implement the feature and instantiate it in the same way, like you have instantiated it in
the scenario class.

.. note::
    Often it is easier to rename these feature files in an way, that the filename says the origin of definition
    and where these features belongs to. This really depends on the project, so feel free to create a nice feature file
    structure.

Inner-Feature-Referencing
=========================

Sometimes it is necessary that you refer another feature from a feature. For example, in the real world, you would need
access to the pipe from the example above. This can easily be done by using inner-feature-referencing.

Imagine, we have another feature ``ManagePipeFeature``, that is also instantiated in the same setup-device where our
``PipeSenderFeature`` has already been instantiated:

.. code-block:: python

    # file `my_setup/setup_my.py`
    from .my_setup_features import PipeSenderFeature

    class SetupMy(balder.Scenario):

        class PipeDevice(balder.Device):
            pipe_manager = ManagePipeFeature()
            pipe_sender = PipeSenderFeature()

The implementation of the ``ManagePipeFeature`` doesn't matter, but we want to use this feature inside our main
``PipeSenderFeature``. For this, we have to inner-referencing it:

.. code-block:: python

    # file `my_setup/my_setup_features.py`
    from ..my_scenario.features import SenderFeature

    class PipeSenderFeature(SenderFeature):

        pipe = ManagePipeFeature()

        def send(msg):
            self.pipe.send(msg)

You simply have to instantiate it as class attribute inside your feature. This will automatically lead to the behavior,
that Balder assumes that your feature only works with a device, that also provides an implementation for the
``ManagePipeFeature``. The reference inside your feature will automatically provided by Balder on variation-level.

Autonomous-Features
===================

Autonomous-Features are a special type of :class:`Feature` classes. These features has no own methods or
properties, they are only used to say:

*This device has the feature* ``IsRedFeature``

So we want to filter them, because we only want a match with a device that has the same feature, but we can't or
don't want to influence or interact with this device over the autonomous :class:`Feature`.

The definition for such a autonomous feature, is really easy:

.. code-block:: python

    # file `scenario_my/scenario_my_features.py`

    class PipeMirrorAutonomousFeature(balder.Feature):
        # an autonomous feature has no implementation
        pass


An Autonomous-Feature has the same behavior than a normal :class:`.Feature`. Since you can't really use it, we highly
recommend that you assign it to a property name with a beginning underscore:

.. code-block:: python

    # file `scenario_my/scenario_my.py`
    from .features import SenderFeature, PipeMirrorAutonomousFeature

    class MyScenario(balder.Scenario):

        class SenderDevice(balder.Device):

            sender = SenderFeature()

        @balder.connect(SenderDevice, over_connection=PipeConnection)
        class ReceiverDevice(balder.Device):
            # the autonomous feature
            _pipe_mirror = PipeMirrorAutonomousFeature()

This example shows a good real world example. Imagine, you want to test if the ``ReceiverDevice`` can mirror a
message you have send with another ``SenderDevice``. Picture that we can only influence the ``SenderDevice``, but have
no possibilities to interact with the ``ReceiverDevice``. We only know, that this device can mirror the messages
we sent. Here we can use a so-called Autonomous-Feature for our ``ReceiverDevice``, because we know that the device
must have it, but you can not influence it.

Your setup can use the same object. You don't have to overwrite it, because you don't want to add functionality
to it, like we have done with the other features before. So we simply reuse this feature from scenario level in our
setup:

.. code-block:: python

    # file `setup_my/setup_my.py`
    from ..scenario_my.features import SenderFeature, PipeMirrorAutonomousFeature
    from . import setup_my_features

    class SetupMy(balder.Scenario):

        class PipeDevice(balder.Device):

            sender = setup_my_features.PipeSenderFeature()

        @balder.connect(PipeDevice, over_connection=PipeConnection)
        class MirrorDevice(balder.Device):
            # autonomous-device
            mirror = setup_my_features.PipeMirrorAutonomousFeature()


Bind features
=============

A big advantage of Balder is that you are able to reuse components. This also applies to features. But mostly you will
not use them under the exact same conditions. So maybe you want to use a ``SendFeature`` with a device that can only
send messages over SMS while you also use this feature with a device that can only send its messages over tcp. So how we
can handle this?

For this, it is time to **bind features**!

Features can be bind to special sub-connection-trees that are allowed to use with matching device for a assigned
:ref:`VDevice <VDevices and method-variations>`. A :class:`VDevice` is used in features to define that you want another
device that has some defined features, that interact with the current device, that implements this feature. If you want
to limit the allowed connections the feature is able to use with this :class:`VDevice` you can bind this feature class.
This is the so called **class-based-binding**.

In addition to that, it is also possible to bind single methods of your feature to a subset of the allowed sub-connection
tree or/and for the usage with one vDevice only. This allows it to define a method multiple times with different
`@for_vdevice` bindings. So for example you can implement a method `send` that will be used if the device (that is
assigned as vDevice) is connected over a TcpConnection. And additionally to that you have another method `send` that is
bind to a `UdpConnection`. Depending on the current scenario/setup, Balder will use the correct method variation of
`send`, after you call it in your testcase. This is the so called **method-based-binding**.

This section describes how this mechanism generally works. You can find a lot of more detailed explanations in the
:ref:`VDevices and method-variations` section.

Class-Based-Binding
-------------------

**Class-Based-Binding** can be defined with a :class:`Feature` class decorator `@for_vdevice()`.

.. code-block:: python

    # file `my_scenario/features.py`
    import balder
    from .connections import PipeConnection

    @balder.for_vdevice("OtherPipeVDevice", with_connections=[PipeConnection])
    class PipeSendReceive(balder.Feature):

        class OtherPipeVDevice(balder.VDevice):
            ...

The example describes that this feature needs a ``PipeConnection`` for every connection with the mapped device of the
inner vDevice ``OtherPipeVDevice``.

But how does you assign which device should be mapped with the vDevice?

You must provide this mapping in the constructor of the feature as a key-value pair. So for our example, you add the
attribute ``OtherPipeVDevice="PipeDevice2"`` to the feature constructor to define that the scenario device
``PipeDevice2`` should be mapped to the ``OtherPipeVDevice`` vDevice.

.. code-block:: python

    # file `my_scenario/my_scenario.py`
    import balder
    from .connections import PipeConnection

    class ScenarioMy(balder.Scenario):

        @balder.connect("PipeDevice2", over_connection=PipeConnection)
        class PipeDevice1(balder.Device):
            pipe = PipeSendReceive(OtherPipeVDevice="PipeDevice2")

        class PipeDevice2(balder.Device):
            ...

        ...


.. note::
    In Python it depends on the definition order if you can reference the device inside the ``@balder.connect(..)``
    decorator. If the device is defined above your decorator, it is possible, otherwise not. For this, Balder always
    allows to provide the device as string too.


You can do this with different devices that could stand for different usages of this feature. So you can also add
the ``PipeSendReceive`` feature of the ``PipeDevice2`` should use a vdevice-device mapping with the ``PipeDevice1`` too:

.. code-block:: python

    # file `my_scenario/my_scenario.py`
    import balder
    from .connections import PipeConnection

    class ScenarioMy(balder.Scenario):

        @balder.connect("PipeDevice2", over_connection=PipeConnection)
        class PipeDevice1(balder.Device):
            pipe = PipeSendReceive(OtherPipeVDevice="PipeDevice2")

        class PipeDevice2(balder.Device):
            pipe = PipeSendReceive(OtherPipeVDevice="PipeDevice1")

        ...

As you can see the ``@balder.connect(PipeDevice2, over_connection=PipeConnection)`` is a required statement, because
otherwise the requirement of our feature is not fulfilled. This scenario defines that the :class:`Feature` requires a
``PipeConnection`` between the two devices ``PipeDevice1`` and ``PipeDevice2``. If we would use our fixture without the
connection between these devices, it would result in an error, because the :class:`Feature` is not applicable in this
way.

.. note::
    Balder checks if the requirement that is given with the **Class-Based-Binding** is available. If the requirement
    doesn't match the class-based statement, it throws an error!

How does that influence the setup? - You are also able to define these vDevice-Device mapping in the setup. This is even
often the case, because your setup normally uses the specific functionality. Your scenario should be as universal as
possible. You can also use this mechanism on scenario level. If you want to find out more about this, take a look at the
:ref:`VDevices and method-variations` section.

Method-Based-Binding
--------------------

Often it is required to provide different implementations for different vDevices or different sub-connection-trees in a
feature. For this you can use **Method-Based-Binding**.

Let's assume, we have a feature that could send a message to another device. For this case, the connection type
does not really matter, because the feature should support this requirement generally for every possible connection.
So it is only important to test that the device can send a message to another device. It does not matter, how the
feature send this message (at least at scenario level).

So in this example, we want to implement the messaging feature for one or more devices that can send messages over TCP
or over Serial. With this, we add one :class:`VDevice` which implements the receiving side by adding the
feature ``RecvMessengerFeature`` to it. Our send feature itself should get two possible methods to send the message. One
method to send the message over TCP and one method to send it over Serial.

Basically our scenario level implementation looks like:

.. code-block:: python

    # file `my_scenario/features.py`
    import balder
    from balder.connections import TcpConnection
    from .connections import SerialConnection

    @balder.for_vdevice('OtherVDevice', with_connections=TcpConnection | SerialConnection)
    class SendMessengerFeature(balder.Feature):

        class OtherVDevice(balder.VDevice):
            msg = RecvMessengerFeature()

        def send(msg) -> None:
            raise NotImplementedError("this method has to be implemented in setup")



As you can see, we have defined the inner vDevice ``OtherVDevice`` here. We want to use the feature
``RecvMessengerFeature`` with this vDevice. For this we instantiate it as class property of the ``OtherVDevice``. This
allows us, to define the requirement the mapped device should implement already in this feature.

.. note::
    The elements given in the inner vDevice class definition is a **MUST HAVE**, which means that the statement has to
    be available in the mapped device later, otherwise it would throw an error.

Till now the scenario-feature doesn't use some **Method-Based-Bindings**. This will change in a few moments, when we
implement the setup-level representation of this feature.

Before we take action for the setup implementation, we want to create a :ref:`Scenario <Scenarios>` using this newly
created feature. For this, we want to implement a example scenario with two devices that communicates with each other.

.. code-block:: python

    # file `my_scenario/scenario_my.py`
    import balder
    from balder.connections import TcpConnection
    from .connections import SerialConnection
    from .features import SendMessengerFeature, RecvMessengerFeature

    class ScenarioMy(balder.Scenario):

        class SendDevice(balder.Device):
            send = SendMessengerFeature(RecvVDevice="RecvDevice")

        @balder.connect(SendDevice, over_connection=TcpConnection)
        class RecvDevice(balder.VDevice):
            recv = RecvMessengerFeature(SendVDevice="SendDevice")

        def test_check_communication(self):
            SEND_DATA = "Hello World"
            self.RecvDevice.recv.start_async_receiving()
            self.SendDevice.send.send(SEND_DATA)
            all_messages = self.RecvDevice.recv.get_msgs()
            assert len(all_messages) == 1, "have not received anything"
            assert all_messages[0] == SEND_DATA, "have not received the sent data

As you can see we have created a mapping for the inner :class:`VDevice` to an real defined scenario :class:`Device`
by using the name of the inner vDevice as key and the name of the real device as value in the constructor. We also
implement a basic test, that should check the communication.

So let's start to implement the setup level. We can implement our earlier defined feature by simply inheriting from it.
In this child class, we want to provide two different implementations for our abstract method ``send``. We want to
provide two different implementation, one for a Serial connection and one for the connection over tcp. For this we can
use the **Method-Based-Binding** decorator:

.. code-block:: python

    # file `my_setup/features.py`
    import balder
    from balder.connections import TcpConnection
    from ..my_scenario.features import MessengerFeature
    from .connections import SerialConnection

    class SetupSendMessengerFeature(MessengerFeature):

        @balder.for_vdevice(MessengerFeature.OtherVDevice, with_connections=SerialConnection)
        def send(msg) -> None:
            serial = MySerial(com=..)
            ...

        @balder.for_vdevice(MessengerFeature.OtherVDevice, with_connections=TcpConnection)
        def send(msg) -> None:
            sock = socket.socket(...)
            ...

As you can see you can provide completely different implementations for the different sub-connection types. Depending on
the really used connection (the relative possible sub-connection the setup devices are connected with each other), the
corresponding method variation will be called.

So take a look at the following :class:`Setup`, that matches our :class:`Scenario` and supports both connections.

.. code-block:: python

    # file `my_setup/setup_my.py`
    import balder
    from balder.connections import TcpConnection
    from .features import SetupSendMessengerFeature, SetupRecvMessengerFeature

    class MySetup(balder.Setup):

        @balder.connect(SlaveDevice, over_connection=SerialConnection | TcpConnection)
        class MainDevice(balder.Device):
            msg = SetupSendMessengerFeature()

        class SlaveDevice(balder.Device):
            recv = SetupRecvMessengerFeature()

This example connects the two relevant devices over a :class:`TcpConnection` with each other, because the scenario
defines, that the devices should be connected over an TcpConnection. If the test
now uses on of our methods ``MyMessengerFeature.send(..)``, the variation with the decorator
``@balder.for_vdevice(..., over_connection=TcpConnection)`` will be used.

If one would exchange the connection with the ``SerialConnection``, Balder would select the method variation with the
decorator ``@balder.for_vdevice(MessengerFeature.OtherVDevice, with_connection=SerialConnection)``.

.. note::
    In the setup example there is no vDevice-Device mapping anymore. This isn't needed, because we have already fixed
    this at scenario level.

Feature inheritance
===================

.. warning::
    This section is still under development.

..
    .. todo