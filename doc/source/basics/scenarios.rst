Scenarios
*********

.. important::

    .. todo complete reworking of this section

    Please note that this part of the documentation is not yet finished. It will still be revised and updated.

A (test) scenario describes the environment that a test **needs** to be able to be carried out (in contrast to the
:ref:`Setups` that describes what you **have**). A scenario allows to define a test environment first, after the
individual test cases will be implemented.

Create a scenario
=================

Every scenario class have to be located in a file that fulfils the naming ``scenario_*.py``. To keep it clear, it
is often useful to create a own directory for the scenario which has the same name like the scenario python file. So you
can define your related objects, you only use for your single scenario inside this directory.
However Balder will load the python file (with naming ``scenario_*.py``) in its collecting process and searches for
classes that are a subclass of :class:`Scenario` and starts with the name `Scenario`.

.. code-block:: py

        # file `scenario_simple_send_msg.py`

        import balder

        class ScenarioSimpleSendMsg(balder.Scenario):
                pass

Get it back in your mind, **a scenario defines the things your test needs**. The most obvious is that you want to test
something, usually a device or an object. For this Balder provides :class:`Device` classes.

Add one or more devices
=======================

If you need more than one :class:`Device` classes, you should also define their relationship. This can be done by
connecting them. Let's assume, we want to test the connection between two devices. The devices should send a msg between
each other. For this example, it doesn't matter over which connection these two devices are connected, because we can
send a message over an EthernetConnection as well as a morse signal. So we define our scenario connection (remember,
**defines what we need**) with the highest universal :class:`Connection`. We can connect two devices over the
``@balder.connect()`` decorator.

Let's expand our example with the two devices and there connection:

.. code-block:: py

        # file `scenario_simple_send_msg/scenario_simple_send_msg.py`

        import balder

        class ScenarioSimpleSendMsg(balder.Scenario):

                class SendDevice(balder.Device):
                        pass

                @balder.connect(SendDevice, over_connection=balder.Connection)
                class RecvDevice(balder.Device):
                        pass

Let's just capture the whole thing again. :class:`Device` classes are inner classes that defines the devices we need
for our test scenario. They always have to be subclasses of :class:`Device`. These devices can be in a relationship with
each other. For this relationship, we use the ``@balder.connect(..)`` decorator. You can read more about devices at
:ref:`Devices`.

In this example, we have used the universal :class:`Connection` object, but there are a lot of other connections too.
You can also define some by your own.

.. note::
    These connection objects are already in a relationship before you use them. They are included in a global
    connection-tree. This tree defines a hierarchical structure of the connections (for example, that Ethernet can be
    transmitted over a ``CoaxialCableConnection`` or a ``OpticalFiberConnection``.

    It is also possible to expand this tree by your own or if necessary to use a complete custom tree.

    You can read more about this :ref:`here <connection trees>`.

In addition to define single connections, you can also select a part of the global connection tree or combine some
connections with an OR or an AND relationship. So for example you could connect our devices and allow an Ethernet as
well as a Serial connection, by defining
``@balder.connect(SendDevice, over_connection=MyEthernet | MySerial)``. Of course you could also
define, that you need both, the Serial and the Ethernet connection. This can be done with:
``@balder.connect(SendDevice, over_connection=MyEthernet & MySerial``

In our example we only define that we want a universal :class:`Connection` between our devices ``SendDevice`` and
``RecvDevice``. With this the connection type doesn't matter and every connection works here.

Add new device features
=======================

Now we have two devices, but they can't do anything yet. We can add functionality to them by creating or using
so called :class:`Feature` classes. We want to define some by ourselves. For this we add a new file
``features.py`` inside our scenario directory, we've created before. For this example we need one feature that
can send messages and one that can receive the sent messages. First let us define these new features without an
implementation:

.. code-block:: py

        # file `scenario_simple_send_msg/features.py`

        import balder

        class SendMessageFeature(balder.Feature):
                pass

        class RecvMessageFeature(balder.Feature):
                pass

You can assign a feature to a scenario-device in a way that this scenario device now needs this feature for an
execution by instantiating it as class attribute inside the device:

.. code-block:: py

        # file `scenario_simple_send_msg/scenario_simple_send_msg.py`

        import balder
        from .features import SendMessageFeature, RecvMessageFeature

        class ScenarioSimpleSendMsg(balder.Scenario):

                class SendDevice(balder.Device):
                        send = SendMessageFeature()

                @balder.connect(SendDevice, over_connection=balder.Connection)
                class RecvDevice(balder.Device):
                        recv = RecvMessageFeature()

As you can see above, we have to instantiate our new :class:`.Feature` classes as class attribute of the
device classes. With this we want to define that they implement it.

In this example we define that we need a ``SendDevice`` which has a ``SendMessageFeature`` and a ``RecvDevice`` which
has the ``RecvMessageFeature``. Both have to be connected over a universal :class:`Connection`. These are the things, we
need in a setup later, to allow the execution of this scenario. Otherwise the variation between the not-working setup
and this scenario is not applicable. Balder uses this information to check if a variation (matching between a setup and
a scenario) is possible or not.

Add real functionality
----------------------

Up to now we have defined some  :ref:`Features`, but they still have no real implementation. So we can't really do
something with them.

Now we want to update our features to add some methods. We expand our ``features.py`` file a little bit:

.. code-block:: py

    # file `scenario_simple_send_msg/features.py`

    import balder

    class SendMessageFeature(balder.Feature):

        @property
        def address(self):
            raise NotImplementedError("has to be implemented in subclass")

        def send_bytes_to(self, other, the_bytes):
            """sends the bytes to the object"""
            raise NotImplementedError("has to be implemented in subclass")

    class RecvMessageFeature(balder.Feature):

        @property
        def address(self):
            raise NotImplementedError("has to be implemented in subclass")

        def listen_for_incoming_msgs(timeout):
            """returns list with tuples (sender_object, the_bytes)"""
            raise NotImplementedError("has to be implemented in subclass")

With that, we added two abstract methods without an implementation yet. We are going to implemented them in the
:class:`Feature` subclass of our :ref:`Setups` later.

.. note::
    In some cases it can be useful to provide a implementation in the scenario-feature implementation too.
    You can find more details about that in the :ref:`Features section <Features>`.

Use the features and write tests
================================

Now we can write our first test method. We want to send a Hello-World message and want to make sure that it was
received successfully. It is important that the name of a test method always starts with ``test_*()``, otherwise Balder
will not collect it as a testcase.


.. code-block:: py

    # file `scenario_simple_send_msg/scenario_simple_send_msg.py`

    import balder
    from .features import SendMessageFeature, RecvMessageFeature

    class ScenarioSimpleSendMsg(balder.Scenario):

        class SendDevice(balder.Device):
            send = SendMessageFeature()

        @balder.connect(SendDevice, over_connection=balder.Connection)
        class RecvDevice(balder.Device):
            recv = RecvMessageFeature()

        def test_simple(self):
            send_msg = b"Hello World!"
            self.SendDevice.send.send_bytes_to(self.RecvDevice.recv.address, send_msg)
            recv_list = self.RecvDevice.listen_for_incoming_msgs(timeout=1)
            assert (self.SendDevice.send.address, send_msg) in recv_list, "can not find the message in received message list"

It is very easy to access a device inside a test method. With ``self.SendDevice`` or ``self.RecvDevice`` we can access
our created devices and over their class attributes we can access the :ref:`Features` objects too. This allows us to
execute our newly created properties and methods.

..
    this is currently not official supported todo
    Mark test to SKIP or IGNORE
    ===========================

    Balder provides an easy integration to mark a test in the way to SKIP or IGNORE it from Balder test system. This can be
    done with the class attributes ``IGNORE``, ``SKIP`` and ``RUN``, which are part of every :class:`.Scenario` class. Per
    default the ``RUN`` attribute contains a list with all testcases that are mentioned in the :class:`.Scenario` and
    inherited tests that are still active in the higher classes.

    If we want to add our newly creates test to the ``SKIP`` list, we have to define it like shown in the example below:

    .. code-block:: py

        # file `scenario_simple_send_msg/scenario_simple_send_msg.py`

        import balder
        from .features import SendMessageFeature, RecvMessageFeature

        class ScenarioSimpleSendMsg(balder.Scenario):

            SKIP = [ScenarioSimpleSendMsg.test_simple]

            class SendDevice(balder.Device):
                send = SendMessageFeature()

            @balder.connect(SendDevice, over_connection=balder.Connection)
            class RecvDevice(balder.Device):
                recv = RecvMessageFeature()

            def test_simple(self):
                send_msg = b"Hello World!"
                self.SendDevice.send.send_bytes_to(self.RecvDevice.recv.address, send_msg)
                recv_list = self.RecvDevice.listen_for_incoming_msgs(timeout=1)
                assert (self.SendDevice.send.address, send_msg) in recv_list, "can not find the message in received message list"

    In this case the testcase ``test_simple`` will be marked as **SKIP** and will never be called. This can be used, if
    you are in the developing process of a test and you don't want to activate it before the development is completed.

Scenario inheritance
====================

.. warning::
    This section is still under development.

..
    .. todo