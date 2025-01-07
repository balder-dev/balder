VDevices and method-variations
******************************

.. important::

    .. todo complete reworking of this section

    Please note that this part of the documentation is not yet finished. It will still be revised and updated.

In many circumstances, it can be helpful, that you are able to access the :ref:`Features` of other :ref:`Devices`
inside a feature. This allows you to get information from outside the feature and also allows you to definite the
expected outside environment in features too.

For example if you have a ``LoadSiteFeature``, which allows to load a website or a ``SendMessageFeature``, which allows
to send a message *to another device*, you need some information about this other device.

One possibility to get data from one device to another is the providing of data through a method argument, like shown
in the following example:

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

But this could getting really confusing, after you have defined tons of information and provide this on every different
scope. Actually it would be enough if the feature gets access to the other device. For this you can use so called
:class:`VDevice` objects.


vDevices
========

A vDevice is a device-like class that describes a virtual device this feature interacts with. It is defined as an inner
class of a feature which is a subclass of :class:`VDevice`. Balder will ensure that in case you are using this feature
inside an scenario/setup, a real device (which implements at least the features of your VDevice) is mapped to it.

You simply create a vDevice, describe which features it should have (by instantiating them like it is done with normal
devices) and use them. All other things will be automatically managed from Balder.

Let's go back to the example from earlier. Instead of giving the attribute as method parameters, you can create a
vDevice that uses the ``HttpServerFeature``. This allows you to access the properties and methods of the
``HttpServerFeature`` from the ``LoadSiteFeature`` (in which you have defined the vDevice).

To make this a little bit clearer, please take a look for the following scenario (and the feature implementation) which
implements the functionality of the earlier example, but with vDevices:

.. code-block:: python

    # features.py

    class LoadSiteFeature(balder.Feature):
        # inner-feature referencing (more details about this in the `Features` section)
        my_browser = ...

        class WebServerVDevice(balder.VDevice):
            serv = HttpServerFeature()

        @property
        def open_website(self):
            url = self.WebServerVDevice.serv.url
            ret = self.my_browser.open(url)
            ...


.. code-block:: python

    # scenario_load_web.py

    class ScenarioLoadWeb(balder.Scenario):

        class Server(balder.Device):
            serv = HttpServerFeature()
            ...

        class Client(balder.Device):
            # we have to map the vDevice with our real device (use the class name of the vDevice as key and the
            #  device class you want to map as value)
            load = LoadSiteFeature(WebServerVDevice=ScenarioLoadWeb.Server)

        def test_load(self):
            ...
            self.Client.load.open_website()
            ...

As you can see, you don't have to provide the url in the testcase. This is not necessary, because the value is already
available trough the vDevice ``WebServerVDevice``.

.. note::
    By specifying and mapping vDevices you describe that it is only allowed to use this feature with a device that at
    least implements the required features instantiated in the vDevice.

Multiple vDevices
-----------------

Balder allows only to map one vDevice, but it is possible to define more than one vDevice in one feature class. This
will be really powerful while creating a feature class which allows to do the similar process, but in very different
ways. Let's extend the example from above a little bit. Assume we want to create a feature that opens a webpage and
returns the title of the page. Instead of allowing this feature only to work with webpages we can also update the
feature working with apps and other GUI applications, like programs or machine interfaces. With this information,
we can rework our feature class:

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
|                                  |                        | which is often used to interact with machines            |
+----------------------------------+------------------------+----------------------------------------------------------+

For all of these different types, the feature should be able to work with. But how should our method ``get_title()`` be
implemented to work with all these different vDevices?

Use the property ``mapped_device``
----------------------------------

**NOT RECOMMENDED**

One possibility to implement your method to support all available vDevices is the using of the property
:meth:`Feature.active_vdevice`. This method returns the current active **vDevice**.
If you use our feature in a scenario and add the following vDevice mapping:

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

The property ``self.active_vdevice`` (inside the ``LoadSiteFeature``) will return the
``GetTitleFeature.WebserverVDevice`` class and the property ``self.active_mapped_device`` will return the
``ScenarioTitleCheck.Server`` class.

Take a look at the implementation of our ``GetTitleFeature`` if we are using the :meth:`Feature.active_vdevice` property
to determine the currently active mapping:

.. code-block:: python

    # features.py
    import balder
    from balder.exceptions import UnknownVDeviceException

    class GetTitleFeature(balder.Features):

        browser = ..
        emulator = ..
        hmi = ..

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
                self.browser.open_website(url)
                return self.browser.title
            elif self.active_vdevice == self.AppEmulatorVDevice:
                page_id = self.AppEmulatorVDevice.main_page_id
                self.emulator.start(page_id)
                return self.emulator.page_title
            elif self.active_vdevice == self.HumanMachineInterfaceVDevice:
                self.hmi.start(self.HumanMachineInterfaceVDevice.power_on)
                return self.hmi.read_title()
            else:
                raise UnknownVDeviceException('unknown vDevice mapping was given')

Using method variations
=======================

Another possibility to create the functionality above is the using of method variations. This allows you to define a
method multiple times, while you decorate it with the ``@for_vdevice(..)`` decorator, which binds the method to a
specific vDevice. Balder will automatically determine the correct method before the fixture or the testcase will be
executed.

The example from before becomes much clearer if you use method variations:


.. code-block:: python

    # features.py
    import balder
    from balder.exceptions import UnknownVDeviceException

    class GetTitleFeature(balder.Features):

        browser = ..
        emulator = ..
        hmi = ..

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
            self.browser.open_website(url)
            return self.browser.title

        @balder.for_vdevice('AppEmulatorVDevice', with_connections=balder.Connection())
        def get_title(self):
            page_id = self.AppEmulatorVDevice.main_page_id
            self.emulator.start(page_id)
            return self.emulator.page_title

        @balder.for_vdevice('HumanMachineInterfaceVDevice', with_connections=balder.Connection())
        def get_title(self):
            self.hmi.start(self.HumanMachineInterfaceVDevice.power_on)
            return self.hmi.read_title()

.. note::
    Sometimes python does not allow to reference the type variable for vDevices. You can use a string with the name of
    the vDevice here too. Balder will automatically resolve this internally.

Depending on the current mapped vDevice Balder automatically calls the method variation, that fits for the current
active vDevice.

.. note::
    It is important that you only access the vDevices from a method variation that is also decorated with that vDevice.

Nested method variation calls
-----------------------------

Often you want to call other methods from methods itself. You can freely do this. Balder will handle the correct calling
of all methods in the feature, also for nested calls.

Bind vDevice for connection-trees
=================================

You can also narrow the method variations even further by specifying a specific connection tree in the
``@balder.for_vdevice(..)`` decorator. This allows you to implement different method variations for different
connections, depending on the mapped device and its connections to the device, that uses the feature.


Method variations depending on connection-trees
-----------------------------------------------

Let's go back to an easy scenario which only has one single vDevice:

.. code-block:: python

    # scenario_title_check.py

    class ScenarioSendMessage(balder.Scenario):

        class Receiver(balder.Device):
            recv = RecvFeature()

        @balder.connect(with_device=Receiver, over_connection=SmsConnection | EMailConnection)
        class Sender(balder.Device):
            send = SendFeature(receiver=ScenarioSendMessage.Receiver)

        def test_send_msg(self):
            SEND_TEXT = 'Hello World'
            self.Sender.send.send_msg(SEND_TEXT)
            assert self.Receiver.recv.get_last_message() == SEND_TEXT

In this example we ignore the connection establishment, which would be implemented with :ref:`Fixtures`. We assume that
the connection between the two elements is already established.

Our ``SendFeature`` class is implemented in the following way:

.. code-block:: python

    # features.py

    class SendFeature(balder.Feature):

        sms_provider = ...
        email_provider = ...

        class Receiver(balder.VDevice):
            receiver = RecvFeature()

        @balder.for_vdevice('Receiver', SmsConnection)
        def send(self, msg):
            phone_number = self.Receiver.receiver.get_phone_number()
            this.sms_provider.send(phone_number, msg)

        @balder.for_vdevice('Receiver', EMailConnection)
        def send(self, msg):
            mail_addr = self.Receiver.receiver.get_email()
            this.email_provider.login()
            this.email_provider.send(mail_addr, msg)

As you can see it is also possible to define method variations depending on the current active connection tree. Even
it is not clear which variation it will execute in scenario level, till now it does not matter over which connection
the two devices are connected with each other. It is enough if the setup will restrict this later. If we specify that
our setup only supports an ``EMailConnection`` for example, Balder automatically knows which method variation should be
called.

What happens if we have multiple possibilities?
-----------------------------------------------


It is the responsibility of the feature developer that there exists exactly one clear variation for every possible
vDevice and connection-tree constellation. For this Balder will execute an initial check on the beginning of the
execution.

Instead of illegally multiple method variations (multiple variations, with independent OR connections), hierarchically
method variations are allowed. It is possible that you provide different implementations for different sizes of an
connection-tree. If you have one method variation with a connection tree ``Tcp.based_on(Ethernet)`` and one with a
single ``Ethernet``, of course you want to use the method variation with the bigger tree (the
``Tcp.based_on(Ethernet)``). Theoretically, however, the small one would also fit. Here Balder first tries to sort these
trees hierarchically and check if one of them is CONTAINED-IN another. Balder allows the execution and selects the
biggest one if, this hierarchical structure works for all method-variation candidates of a variation.

It will secure that for every possible constellation only one method variation is implemented or that all possibilities
of the method variation connection-tree are CONTAINED-IN each other. Otherwise it will run in an error in the collecting
stage of Balder. It would be not possible to execute the test session with that.

Use multi-vDevice feature multiple times
========================================

.. warning::
    This function has not yet been extensively tested.

..
    .. todo

Maybe you wondered if you can use a feature multiple times. Normally Balder does not support this, because it is
not defined which scenario-feature should be replaced with which setup-feature. But there is one useful
possibility to define features multiple times. Map different vDevices on it.

Let's assume we have two receiver devices and one sender device that wants to send to both receiver. We could implement
all of that with our two features ``SendFeature`` and ``RecvFeature``:

.. code-block:: python

    # scenario_title_check.py

    class ScenarioSendMessage(balder.Scenario):

        class Sender(balder.Device):
            send_to_recv1 = SendFeature(receiver='Receiver1')
            send_to_recv2 = SendFeature(receiver='Receiver2')

        @balder.connect(with_device=Sender, over_connection=SmsConnection | EMailConnection)
        class Receiver1(balder.Device):
            recv = RecvFeature()

        @balder.connect(with_device=Sender, over_connection=SmsConnection | EMailConnection)
        class Receiver2(balder.Device):
            recv = RecvFeature()

        def test_send_msg(self):
            SEND_TEXT = 'Hello Receiver {}'
            self.Sender.send_to_recv1.send_msg(SEND_TEXT.format(1))
            self.Sender.send_to_recv2.send_msg(SEND_TEXT.format(2))
            assert self.Receiver1.recv.get_last_message() == SEND_TEXT.format(1)
            assert self.Receiver2.recv.get_last_message() == SEND_TEXT.format(2)

Of course the related setup has to support this too. In this case you have to provide a vDevice-Device mapping on setup
and on scenario level. The setup implementation could look like the following example:

.. code-block:: python

    class SetupSenderAndReceiver(balder.Setup):

        class SendDevice(balder.Device):
            send_recv1 = SendFeature(receiver='RecvDevice1')
            send_recv2 = SendFeature(receiver='RecvDevice2')

        @balder.connect(with_device=SendDevice, over_connection=SmsConnection)
        class RecvDevice1(balder.Device):
            recv = RecvFeature()

        @balder.connect(with_device=SendDevice, over_connection=SmsConnection)
        class RecvDevice2(balder.Device):
            recv = RecvFeature()

As you can see in the example above, you only have to secure that Balder exactly knows which feature instance it should
use for which device. With this it is possible to instantiate the same features multiple times.

Class based for_vdevice
=======================

It is highly recommended to provide a class based ``@balder.for_vdevice(..)`` too. This makes it much easier for a user
of the feature to figure out what it is suitable for, because this class based decorator describes exactly the usable
interface of the feature. For this you should define a ``@balder.for_vdevice(..)`` class decorator for every vDevice you
have:

.. code-block:: python

    # features.py
    import balder
    import balder.connections as conns
    from balder.exceptions import UnknownVDeviceException

    @balder.for_vdevice(WebserverVDevice, over_connection=conns.HttpConnection)
    @balder.for_vdevice(AppEmulatorVDevice) # allow every connection for this vDevice
    @balder.for_vdevice(HumanMachineInterfaceVDevice) # allow every connection for this vDevice
    class GetTitleFeature(balder.Features):

        browser = ..
        emulator = ..
        hmi = ..

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

The class based decorator always prescribe the possible vDevice connections and the allowed connection-trees between the
corresponding devices later. It always describes the merged data of the method variations.

.. note::
    Balder automatically throws a warning if you have not specified a class based ``@balder.for_vdevice(..)`` for a
    defined vDevice, if there are some method variations for it. This warning contains a proposal for an class based
    decorator.

.. note::
    If you define a class based decorator which is a smaller set than the possibilities defined with method variations,
    balder will reduce the method variation set to the defined class based decoration here! In this case, Balder will
    throw a warning.