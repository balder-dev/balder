Setups
******

.. important::

    .. todo complete reworking of this section

    Please note that this part of the documentation is not yet finished. It will still be revised and updated.

Setup classes describe your real-world test setup. It describes what you **have** (in contrast to the :ref:`Scenarios`,
that describes what you need). A :class:`Setup` describes the structure of :ref:`Devices` and their relationship to each
other. It also contains the final implementation of all :ref:`Features` the :ref:`Devices` should have.

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

Defining this test process device
---------------------------------

You can create a new :class:`Device` in your setup by simply defining a new inner class and inherit from
:class:`Device`.

.. code-block:: py

    import balder

    class SetupBasic(balder.Setup):

        class ThisDevice(balder.Device):
            ...
        ...


Add other device
----------------

Feel free to create more devices. You should add all devices you want to use in your tests within this setup. Balder
will automatically search for all mappings between these setups and your scenarios.

We want to add a new :class:`Device` ``TestDevice`` to our example before and connect both with a `HttpConnection`:

.. code-block:: py

    import balder
    import balder.connections as conn

    class SetupBasic(balder.Setup):

        class ThisDevice(balder.Device):
            ...

        @balder.connect(ThisDevice, over_connection=conn.HttpConnection)
        class TestDevice(balder.Device):
            ...

        ...

That was it already. We have now defined our devices and their relationship with each other. In the next step, we only
have to add their supported :ref:`Features`.

Add setup-device features
=========================

Last but not least, we have to add some features to our devices. Normally these result from the definitions in the
scenario. A scenario defines which features they need. So that a setup will match with a scenario, the setup have to
provide an implementation for these features.

If we have a scenario like the following:

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

    ...

We need an implementation for these two devices. And this implementation will than be added into our setup:

.. code-block:: py

    import balder
    import balder.connections as conn
    # contains the implementation of the scenario features above (non abstract methods anymore
    from .setup_features import SendMessageFeatureImpl, RecvMessageImplFeature

    class SetupBasic(balder.Setup):

        class ThisDevice(balder.Device):
            send_impl = SendMessageFeatureImpl()

        @balder.connect(ThisDevice, over_connection=conn.HttpConnection)
        class TestDevice(balder.Device):
            recv_impl = RecvMessageImplFeature()

        ...

Setup inheritance
=================


.. warning::
    This section is still under development.

..
    .. todo