VDevices and method-variations
******************************

In many circumstances, it can be helpful to access the :ref:`Features` of other :ref:`Devices` from within a feature.
This allows you to retrieve information from outside the feature itself and also enables you to define the expected
external environment directly within features.

For example, if you have a ``LoadSiteFeature`` that lets you load a website, or a ``SendMessageFeature`` that lets you
send a message to another device, you often need details about that other device.

One way to pass data from one device to another is by providing it through a method argument, as shown in the following
example:

.. code-block:: python

    class ScenarioLoadWeb(balder.Scenario):

        class Server(balder.Device):
            serv = HttpServerFeature()
            ...

        class Client(balder.Device):
            load = LoadSiteFeature()

        def test_load(self):
            ...
            url = self.Server.serv.url
            self.Client.load.open_website(url)
            ...

However, this approach can become really confusing once you start defining large amounts of information and providing
it across every different scope. In fact, it would be sufficient for the feature to simply gain access to the other
device. To achieve this, you can use so-called :class:`VDevice` objects.

vDevices
========

A VDevice is a device-like class that describes a virtual device with which this feature interacts. It is defined as an
inner class within a feature and must be a subclass of :class:`VDevice`. Balder ensures that when you use this feature
inside a scenario or setup, a real device (which implements at least the features of your VDevice) need to be
mapped to it in the scenario or the setup class.

You simply create a VDevice, specify which features it should have (by instantiating them in the same way as with
normal devices), and then use them. Balder handles all other aspects automatically.

Let's return to the earlier example. Instead of passing attributes as method parameters, you can create a VDevice that
incorporates the ``HttpServerFeature``. This allows you to access the properties and methods of the
``HttpServerFeature`` directly from the ``LoadSiteFeature`` (where you defined the VDevice).

To make this clearer, please take a look at the following scenario (and its feature implementation), which achieves the
same functionality as the earlier example but uses VDevices:

.. code-block:: python

    # features.py

    class LoadSiteFeature(balder.Feature):
        # inner-feature referencing (more details about this in the `Features` section)
        my_browser = ...

        # describes that there needs to be a peer device that has a `HttpServerFeature`
        class WebServerVDevice(balder.VDevice):
            serv = HttpServerFeature()

        @property
        def open_website(self):
            url = self.WebServerVDevice.serv.url
            ret = self.my_browser.open(url)
            ...


.. code-block:: python

    # scenarios/scenario_load_web.py

    class ScenarioLoadWeb(balder.Scenario):

        class Server(balder.Device):
            serv = HttpServerFeature()
            ...

        class Client(balder.Device):
            # we have to map the vDevice with the real device (use the class name of the vDevice as key and the
            #  device class you want to map as value)
            load = LoadSiteFeature(WebServerVDevice=ScenarioLoadWeb.Server)

        def test_load(self):
            ...
            self.Client.load.open_website()
            ...

As you can see, you don't have to provide the URL in the scenario. This is not necessary because the value is already
available through the VDevice ``WebServerVDevice``.

.. note::
    By specifying and mapping VDevices, you indicate that this feature can only be used with a real device that
    implements at least the required features defined within the VDevice.

Multiple vDevices
-----------------

At the moment, Balder allows only to map one vDevice, but it is possible to define more than one vDevice in one feature class. This
will be really powerful while creating a feature class which allows to do the similar process, but in very different
ways. Let's extend the example from above a little bit. Assume we want to create a feature that opens a webpage and
returns the title of the page. Instead of allowing this feature only to work with webpages we can also update the
feature working with apps and other GUI applications, like programs or machine interfaces. With this information,
we can rework our feature class:

Currently, Balder only allows mapping one VDevice at a time. However, you can define more than one VDevice within a
single feature class. This approach becomes particularly powerful when creating a feature class that performs similar
processes but in very different ways, for example for GUI or for CLI.

Let's extend the example from above a bit. Suppose we want to create a feature that opens a webpage and returns the
title of the page. Instead of limiting this feature to webpages only, we can update it to also work with apps and other
GUI applications, such as desktop programs or machine interfaces. With this in mind, we can rework our feature class:

.. code-block:: python

    # features.py

    class GetTitleFeature(balder.Features):

        class WebserverVDevice(balder.VDevice):
            serv = HttpServerFeature()
            ...

        class AppEmulatorVDevice(balder.VDevice):
            app = AppProviderFeature()
            ...

        class HumanMachineInterfaceVDevice(balder.VDevice):
            reader = HMIReaderFeature()
            ...

        def get_title(self):
            # ???
            ...

As you can see, we have three different vDevices in our feature implementation. Every vDevice works in another way:

+----------------------------------+------------------------+----------------------------------------------------------+
| Feature-VDevice                  | needs the features     | Description                                              |
+==================================+========================+==========================================================+
| ``WebserverVDevice``             | ``HttpServerFeature``  | provides a webpage and allows to get the url of the page |
+----------------------------------+------------------------+----------------------------------------------------------+
| ``AppEmulatorVDevice``           | ``AppProviderFeature`` | device that emulates a smartphone app and allows to get  |
|                                  |                        | app information about the current shown page             |
+----------------------------------+------------------------+----------------------------------------------------------+
| ``HumanMachineInterfaceVDevice`` | ``HMIReaderFeature``   | allows to read the data of a human-machine-interface,    |
|                                  |                        | which is often used to interact with physical machines   |
+----------------------------------+------------------------+----------------------------------------------------------+

For all of these different types, the feature should be able to work with. But how should our method ``get_title()`` be
implemented to work with all these different vDevices?

Use the property ``mapped_device`` (NOT RECOMMENDED)
----------------------------------------------------

**NOT RECOMMENDED**

One way to implement your method so that it supports all available VDevices is by using the property
:meth:`Feature.active_vdevice`. This property returns the currently active VDevice. For example, if you use our feature
in a scenario and add the following VDevice mapping:

.. code-block:: python

    # scenario_title_check.py

    class ScenarioTitleCheck(balder.Scenario):

        class Server(balder.Device):
            serv = HttpServerFeature()
            ...

        class Client(balder.Device):
            # we have to map the vDevice with our real device (for this use the class name of the vDevice and the
            #  device class we want to map)
            load = LoadSiteFeature(WebServerVDevice=ScenarioLoadWeb.Server)

        def test_check_title(self):
            ...

The property ``self.active_vdevice`` (inside the GetTitleFeature) will return the ``GetTitleFeature.WebserverVDevice``
class, while the property ``self.active_mapped_device`` will return the ``ScenarioTitleCheck.Server`` class.

Take a look at the implementation of our GetTitleFeature, where we use the :meth:`Feature.active_vdevice` property
to determine the currently active mapping:

.. code-block:: python

    # features.py
    import balder
    from balder.exceptions import UnknownVDeviceException

    class GetTitleFeature(balder.Features):

        guicontrol = ...

        class WebserverVDevice(balder.VDevice):
            serv = HttpServerFeature()
            ...

        class AppEmulatorVDevice(balder.VDevice):
            app = AppProviderFeature()
            ...

        class HumanMachineInterfaceVDevice(balder.VDevice):
            reader = HMIReaderFeature()
            ...

        def get_title(self):

            if self.active_vdevice == self.WebserverVDevice:
                # do the stuff for the `WebserverVDevice`
                url = self.WebserverVDevice.serv.url
                self.guicontrol.open(url)
                return self.guicontrol.session.title
            elif self.active_vdevice == self.AppEmulatorVDevice:
                page_id = self.AppEmulatorVDevice.main_page_id
                self.guicontrol.open(page_id)
                return self.guicontrol.get_property('emulator::page_title')
            elif self.active_vdevice == self.HumanMachineInterfaceVDevice:
                self.guicontrol.start(self.HumanMachineInterfaceVDevice.power_on)
                return self.guicontrol.get_property('hmi::title')
            else:
                raise UnknownVDeviceException('unknown vDevice mapping was given')

Using method variations (RECOMMENDED)
=====================================

Another way to achieve the functionality described above is by using method variations. This allows you to define a
method multiple times, decorating each version with the ``@for_vdevice(..)`` decorator to bind it to a specific VDevice.
Balder will automatically select the correct method variation before executing the fixture or the test case.

The example from before becomes much clearer when using method variations:

.. code-block:: python

    # features.py
    import balder
    from balder.exceptions import UnknownVDeviceException

    class GetTitleFeature(balder.Features):

        guicontrol = ...

        class WebserverVDevice(balder.VDevice):
            serv = HttpServerFeature()
            ...

        class AppEmulatorVDevice(balder.VDevice):
            app = AppProviderFeature()
            ...

        class HumanMachineInterfaceVDevice(balder.VDevice):
            reader = HMIReaderFeature()
            ...

        @balder.for_vdevice('WebserverVDevice', with_connections=balder.Connection())
        def get_title(self):
            # do the stuff for the `WebserverVDevice`
            url = self.WebserverVDevice.serv.url
            self.guicontrol.open(url)
            return self.guicontrol.session.title

        @balder.for_vdevice('AppEmulatorVDevice', with_connections=balder.Connection())
        def get_title(self):
            page_id = self.AppEmulatorVDevice.main_page_id
            self.guicontrol.open(page_id)
            return self.guicontrol.get_property('emulator::page_title')

        @balder.for_vdevice('HumanMachineInterfaceVDevice', with_connections=balder.Connection())
        def get_title(self):
            self.guicontrol.start(self.HumanMachineInterfaceVDevice.power_on)
            return self.guicontrol.get_property('hmi::title')

.. note::
    Sometimes, Python does not allow you to reference the type variable for VDevices directly. In such cases, you can
    use a string containing the name of the VDevice instead. Balder will automatically resolve this internally.

Depending on the currently mapped VDevice, Balder automatically calls the method variation that fits the current active
VDevice.

.. note::
    It is important that you only access the VDevices from within a method variation that is also decorated with the
    corresponding VDevice (using the ``@for_vdevice`` decorator). Otherwise Balder will raise an error.

Nested method variation calls
-----------------------------

Often, you may want to call other methods from within a method itself. You can do this freely. Balder will handle the
correct invocation of all methods in the feature, including nested calls.

Bind vDevice for connection-trees
=================================

You can further refine method variations by specifying a particular connection tree in the ``@balder.for_vdevice(..)``
decorator. This enables you to implement different method variations for specific connections, depending on the mapped
device and its connections to the device that owns the feature.

Method variations depending on connection-trees
-----------------------------------------------


Let's return to a simple scenario that involves only a single VDevice. The following scenario is defined to use a
connection with either a ``ConfirmableConnection`` or a ``NonConfirmableConnection``. A ConfirmableConnection means
that every message must be confirmed by the receiver, while a ``NonConfirmableConnection`` means that no such
confirmation is required. This scenario would look like the following snippet:

.. code-block:: python

    # scenario_title_check.py
    from lib.connections import ConfirmableConnection, NonConfirmableConnection
    from lib.scenario_features import SendFeature, RecvFeature

    class ScenarioSendMessage(balder.Scenario):

        class Receiver(balder.Device):
            recv = RecvFeature()

        @balder.connect(with_device=Receiver, over_connection=ConfirmableConnection | NonConfirmableConnection)
        class Sender(balder.Device):
            send = SendFeature(receiver=Receiver)

        def test_send_msg(self):
            SEND_TEXT = 'Hello World'
            self.Sender.send.send_msg(SEND_TEXT)
            assert self.Receiver.recv.get_last_message() == SEND_TEXT

Our ``SendFeature`` also supports both of these connection types. But we will need two different implementations for
``send()``. This would be implemented like shown below:

.. code-block:: python

    # features.py

    @balder.for_vdevice('Receiver', over_connection=ConfirmableConnection | NonConfirmableConnection)
    class SendFeature(balder.Feature):

        session = ...

        class Receiver(balder.VDevice):
            receiver = RecvFeature()

        @balder.for_vdevice('Receiver', ConfirmableConnection)
        def send(self, msg):
            session = self.session.start_new_session()
            session.establish(self.Receiver.address)
            session.write(msg)
            session.wait_for_confirmation()
            session.close()

        @balder.for_vdevice('Receiver', NonConfirmableConnection)
        def send(self, msg):
            session.send_message(self.Receiver.address, msg)

As you can see, you can define methods multiple times for different VDevices and / or different sub connection types.
Even though it is not clear which variation will be executed at the scenario level, so far it does not matter through
which connection the two devices are connected to each other. It is sufficient if the setup restricts this later.

For example, if we specify that our setup only supports an ``ConfirmableConnection``, Balder automatically knows which
method variation should be called.


What happens if we have multiple possibilities?
-----------------------------------------------

It is the responsibility of the feature developer to ensure that exactly one clear variation exists for every possible
VDevice and connection-tree constellation. To this end, Balder performs an initial check at the beginning of the
execution.

Instead of allowing illegal multiple method variations (such as multiple variations with independent OR connections),
Balder supports hierarchical method variations. This means you can provide different implementations for connection
trees of varying sizes. For example, if you have one method variation with a connection tree ``Tcp.based_on(Ethernet)``
and another with a single Ethernet, you naturally want to use the variation with the larger tree
(``Tcp.based_on(Ethernet)``). Theoretically, however, the smaller one could also match. In such cases, Balder first
sorts these trees hierarchically and checks if one is CONTAINED-IN another. If this hierarchical structure applies to
all method-variation candidates for a given variation, Balder allows execution and automatically selects the largest
one.

This approach ensures that, for every possible constellation, either only one method variation is implemented or all
connection-tree possibilities in the method variations are CONTAINED-IN each other. Otherwise, Balder will raise an
error during the collecting stage, making it impossible to execute the test session.

Class based for_vdevice
=======================

It is highly recommended to also provide a class-based ``@balder.for_vdevice(..)`` decorator. This makes it much easier
for users of the feature to understand what it is suitable for, since the **class-based decorator** precisely describes
the usable interface of the feature. To achieve this, you should define a ``@balder.for_vdevice(..)`` class decorator
for every VDevice you have:

.. code-block:: python

    # features.py
    import balder
    import balder.connections as conns
    from balder.exceptions import UnknownVDeviceException

    @balder.for_vdevice(WebserverVDevice, over_connection=conns.HttpConnection)
    @balder.for_vdevice(AppEmulatorVDevice) # allow every connection for this vDevice
    @balder.for_vdevice(HumanMachineInterfaceVDevice) # allow every connection for this vDevice
    class GetTitleFeature(balder.Features):

        guicontrol = ..

        class WebserverVDevice(balder.VDevice):
            serv = HttpServerFeature()
            ...

        class AppEmulatorVDevice(balder.VDevice):
            app = AppProviderFeature()
            ...

        class HumanMachineInterfaceVDevice(balder.VDevice):
            reader = HMIReaderFeature()
            ...

        ...

The **class-based decorator** always defines the possible VDevice mappings and the allowed connection trees between the
corresponding devices. Put simply, the class-based decorator describes the combined interface and constraints from all
the method variation decorators.

.. note::
    Balder automatically issues a warning if you have not specified a class-based ``@balder.for_vdevice(..)`` decorator
    for a defined VDevice, especially when there are method variations associated with it. This warning includes a
    suggestion for the appropriate class-based decorator.

.. warning::
    If you define a class-based decorator that specifies a smaller set of possibilities than those provided by the
    method variations, Balder will automatically restrict the method variations to align with the class-based decorator.
    In this case, Balder will issue a warning to inform you of the adjustment.