Scenarios
*********

A test scenario describes the environment that a test **needs** in order to be carried out (in contrast to the
:ref:Setups, which describe **what you have**).

A scenario holds the definition of the required test environment and the test logic itself.

Create a scenario
=================

Every scenario class has to be located in a file that matches the naming pattern ``scenario_*.py``. Balder will load
the Python file (matching the pattern ``scenario_*.py``) during its collection process. It then searches for classes
that are subclasses of :class:`Scenario` and whose names start with ``Scenario*``.

.. code-block:: python

        # file `scenarios/scenario_simple_send_msg.py`

        import balder

        class ScenarioSimpleSendMsg(balder.Scenario):
                pass

Recall that **a scenario defines the environment your test needs**. The most obvious aspect is that you want to test
something - typically a device or an object. To support this, Balder provides :class:`Device` classes.

Add one or more devices
=======================

If you need more than one :class:`Device`, you should also think about defining their relationships. This can be done
by connecting them.

Let's assume we want to test the communication between two devices, where they send a message to each other. For this
example, it doesn't matter how these two devices are connected - whether via an Ethernet connection or even a Morse
signal. So, we define our scenario connection (remember, **a scenario defines what we need**) using the most universal
:class:`Connection` class. We can connect two devices using the ``@balder.connect()`` decorator.

Let's expand our example with the two devices and their connection:

.. code-block:: python

        # file `scenarios/scenario_simple_send_msg.py`

        import balder

        class ScenarioSimpleSendMsg(balder.Scenario):

                class SendDevice(balder.Device):
                        pass

                @balder.connect(SendDevice, over_connection=balder.Connection)
                class RecvDevice(balder.Device):
                        pass

Let's recapture it again: :class:`Device` classes are inner classes that define the devices we need for our test scenario. They must always be
subclasses of :class:`Device`. These devices can be related to each other. To establish these relationships, we use the
``@balder.connect(..)`` decorator. You can read more about devices in :ref:`Devices` section.

In this example, we used the universal :class:`Connection` object, but there are many other connection types available.
You can also define your own custom connections. However, by using this universal :class:`Connection`, we specify that
the exact method of connection between the devices doesn't matter, as long as they are connected. Connections provide
a powerful tool, so if you want to read more about them, please refer to the :ref:`Connections` section.


Add new device features
=======================

Now we have two devices, but they can't do anything yet. We can add functionality to them by creating or using
:class:`Feature` classes. We want to define some ourselves. To do this, we add a new file ``messaging_features.py`` in
our common scenario feature directory ``lib/scenario_features``. Within this file, we want to define one feature that
can send messages and another that can receive the sent messages. First, let's define these new features without an
implementation:

.. code-block:: python

        # file `lib/scenario_features/messaging_features.py`

        import balder

        class SendMessageFeature(balder.Feature):
                pass

        class RecvMessageFeature(balder.Feature):
                pass

You can assign a feature to a scenario device such that the device requires this feature for execution. This is done
by instantiating the feature as a class attribute inside the device class:

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

As you can see above, we have to instantiate our new :class:`Feature` classes as class attributes of the device classes.
This defines that the devices require these features.

In this example, we define that we need a ``SendDevice`` with a ``SendMessageFeature`` and a ``RecvDevice`` with a
``RecvMessageFeature``. Both must be connected via a universal :class:`Connection`. These are the elements we need in a
setup later to enable the execution of this scenario. Otherwise, the variation between a non-matching setup and this
scenario would not be applicable. Balder uses this information to determine whether a variation (the matching between
a setup and a scenario) is possible or not.

Add real functionality
----------------------

Up to now, we have defined some :ref:`Features`, but they still have no real implementation. So, we can't really do
anything with them yet.

Now, we want to update our features by adding some methods. Let's expand our ``features.py`` file a bit:

.. code-block:: python

    # file `lib/scenario_features/messaging_features.py`

    import balder

    class SendMessageFeature(balder.Feature):

        @property
        def address(self):
            raise NotImplementedError("has to be implemented in subclass")

        def send_bytes_to(self, other, the_bytes):
            """sends the bytes to the `other` object"""
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

With that, we have added two abstract methods without implementations yet. We will implement them later in the
:class:`Feature` subclasses within our :ref:`Setups`.

.. note::
    In some cases, it can be useful to provide an implementation in the scenario's feature class as well. You can
    find more details about this in the :ref:`Features <Features>` section.

Use the features to write tests
================================

Now, we can write our first test method. We want to send a "Hello World" message and ensure that it was received
successfully. It is important that the name of a test method always starts with ``test_``, otherwise Balder will not
collect it as a test case.


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

        def test_simple(self):
            send_msg = b"Hello World!"
            self.SendDevice.send.send_bytes_to(self.RecvDevice.recv.address, send_msg)
            recv_list = self.RecvDevice.listen_for_incoming_msgs(timeout=1)
            assert (self.SendDevice.send.address, send_msg) in recv_list, "can not find the message in received message list"

Accessing a device inside a test method is straightforward. You can use ``self.SendDevic``e or ``self.RecvDevice`` to
reach the devices you've defined. Through their attributes, you can also access the :ref:`Features` objects. This
allows you to call and execute the newly defined methods and properties.

When executing the scenario with a matching setup, Balder will automatically replace the feature references with the
actual instances provided by the setup. Balder handles all of this for you behind the scenes.

Mark test to SKIP or IGNORE
===========================

Balder provides an integration to mark a test in the way to SKIP or IGNORE it from Balder test system. This can be
done with the class attributes ``IGNORE``, ``SKIP`` and ``RUN``, which are part of every :class:`.Scenario` class. Per
default the ``RUN`` attribute contains a list with all testcases that are mentioned in the :class:`.Scenario` and
inherited tests that are still active in the higher classes.

If we want to add our newly creates test to the ``SKIP`` list, we have to define it like shown in the example below:

Balder provides a way to mark tests as SKIP or IGNORE within the Balder test system. This can be done using the class
attributes ``IGNORE``, ``SKIP``, and ``RUN``, which are available in every :class:`Scenario` class. By default, the
``RUN`` attribute contains a list of all test cases defined in the :class:`Scenario`, along with any inherited tests
that remain active from parent classes.

If we would like to add our newly created test to the ``SKIP`` list, we have to define it as shown in the example below:

.. code-block:: python

    # file `scenarios/scenario_simple_send_msg.py`

    import balder
    from lib.scenario_features.messaging_features import SendMessageFeature, RecvMessageFeature

    class ScenarioSimpleSendMsg(balder.Scenario):

        SKIP = [ScenarioSimpleSendMsg.test_simple]

        class SendDevice(balder.Device):
            send = SendMessageFeature()

        @balder.connect(SendDevice, over_connection=balder.Connection)
        class RecvDevice(balder.Device):
            recv = RecvMessageFeature()

        def test_simple(self):
            ...

In this case, the test case ``test_simple`` will be marked as **SKIP** and will never be executed. This can be useful
during the development process of a test, if you don't want to activate it until the implementation is complete.

Scenario inheritance
====================

Balder supports inheritance for scenario classes, just like in standard Python class inheritance. This allows you to
create a base scenario with common devices and fixtures and extend or modify it in child scenarios. It's particularly
helpful when you have similar tests that share device structures or setup/cleanup code, that can be summarized in
fixtures, which should be reused over different scenarios.


To use inheritance, simply subclass your new scenario from an existing one. Balder will automatically inherit all the
devices, features, connections, and test methods from the parent class. You can add new elements or override existing
ones in the child class.

Overwriting Scenario Devices
----------------------------

You can overwrite devices and **extend** their feature set, but you can never replace an existing feature set from the
parent class. It is also important to use the same device names when a device exists in a parent class.
This ensures that Balder can properly map, connect, and resolve the devices across the inheritance chain without
conflicts. For instance, if the parent has a device named ``SendDevice``, any override in the child must also be called
``SendDevice``.

.. code-block:: python

    class ScenarioInherited(ScenarioSimpleSendMsg):

        class SendDevice(ScenarioSimpleSendMsg.SendDevice): # Balder only allows overwriting and assigning the same name
            # if you do not overwrite features here, the features from `ScenarioSimpleSendMsg.SendDevice` are still active
            pass

        @balder.connect(SendDevice, over_connection=balder.Connection)
        class RecvDevice(ScenarioSimpleSendMsg.RecvDevice):
            # if you do not overwrite features here, the features from `ScenarioSimpleSendMsg.RecvDevice` are still active
            pass

        # the test `InheritedScenario.test_simple` is still active and will be executed for this scenario

Keep in mind that inherited test methods (those starting with ``test_``) will be collected and executed unless you
explicitly skip or ignore them using the SKIP or IGNORE class attributes. This way, you can build modular and reusable
test structures while maintaining clarity and consistency.

Overwriting Features of overwritten Devices
-------------------------------------------

Sometimes it makes sense to overwrite a specific feature in a scenario device's parent class. So for example, if we want
to use a more specific implementation for our ``SendMessageFeature`` within our ``ScenarioInherited``, we can overwrite
it, by using the new feature in the sub class:

.. code-block:: python

    class ScenarioInherited(ScenarioSimpleSendMsg):

        class SendDevice(ScenarioSimpleSendMsg.SendDevice):
            send = MoreSpecificSendMessageFeature()
        ...

This works, but there need to be two conditions, that Balder allows it:

1) you need to use the same attribute name ``send``, that is used in the parent class
2) ``MoreSpecificSendMessageFeature`` needs to be a subclass of ``SendMessageFeature``

These conditions are necessary, because Balder would not be able to execute the test
``ScenarioSimpleSendMsg.test_simple`` from parent scenario class, if the interface defined in ``SendMessageFeature``
would not be available.

Behavior for collected sub and parent classes
---------------------------------------------

Balder has a mechanism that detects duplicated scenarios because of inheritance. If balder collects the same variation
(same setup and same device mapping) with the ``ScenarioSimpleSendMsg`` and the ``ScenarioInherited``, Balder
automatically removes the variation with the parent class ``ScenarioSimpleSendMsg`` because it is fully covered up by
the inherited scenario ``ScenarioInherited``.

If you want to avoid this, just creating a new subclass without any further implementation:

.. code-block:: python

    class ScenarioUnchanged(ScenarioSimpleSendMsg):
        pass

This will collect ``ScenarioUnchanged`` instead of ``ScenarioSimpleSendMsg`` which results in the execution of
the unchanged test code provided in ``ScenarioSimpleSendMsg``.
