Balder execution mechanism
**************************

.. important::

    .. todo complete reworking of this section

    Please note that this part of the documentation is not yet finished. It will still be revised and updated.

After you start the execution in a Balder project with the command line `balder ..`, Balder will go through a procedure
of tree steps. First Balder collects all relevant items that can be found in the project directory (the current working
directory) and imports their Balder related classes and functions. For this purpose Balder keeps an internal overview
of all :ref:`Setup <Setups>`, :ref:`Scenario <Scenarios>` and :ref:`Connection <Connections>` classes. With that
information, Balder will start to create possible matching between the collected setups and scenario instances. In this
step, Balder creates the whole execution tree that contains all existing matches with its device-mappings organized in
an execution-tree. In the last step Balder executes this tree with the inclusion of all :ref:`Features` and test cases.

To make it easier to understand the functionality of Balder, we will start to consider the differences between
:ref:`Setup <Setups>` classes and :ref:`Scenario <Scenarios>` classes a little bit more in detail.

Difference between setup and scenario
=====================================

Balder is based on individual :ref:`Scenario <Scenarios>` and :ref:`Setup <Setups>` classes.
Scenarios define a situation in which individual tests can be carried out. Setups, on the other hand, describes how a
test environment currently looks like. In other words, the following definition is important to understand:

**Scenario:** Describes what you need

**Setup:** Describes what you have

So what does this mean? Take a look deeper in these definitions.

Describes what you need: Scenarios
----------------------------------

A :ref:`Scenario <Scenarios>` always defines what **you need**. So for example, if you want to test a online login of a
server, you need the server device and a client device that tries to connect with the server. This describes what you
need, and these are the components of a :ref:`Scenario <Scenarios>`. In this case all other devices that are connected
with the network (for example another client) doesn't matter, because we only need these two devices. If we want to test
if the server can handle two clients to the same time in another scenario, we have to define a scenario that needs these
three devices. So we only define what we need.

Describes what you have: Setups
-------------------------------

It is different when we look at the :ref:`Setup <Setups>`. In a setup you define everything that is available and
relevant in this setup. So for example, if you have your computer, the router, the server of company X and the server of
company Y in your influenceable spectrum of devices you can add these to your setup.

Balder will manage the determination of all available matching between the :ref:`Scenario <Scenarios>` devices
and the :ref:`Setup <Setups>` devices automatically. If it finds matchings, it will execute these possible variations
in the execution step. You can read more about this in the further subsections of this guide (see
:ref:`Matching process of setups and scenarios (SOLVING)`).

Collecting process
==================

The collection process is the first stage of the Balder execution mechanism, directly after executing the ``balder ...``
command. In this stage all available relevant Balder classes within the working directory are collected.

Collect setups and scenarios
----------------------------

First the collector begins to find all setup and scenario classes that are located directly in the Python files
collected in the earlier step.

Balder searches for scenarios exclusively in files with the name ``scenario_*.py``. In these files it searches for
classes, which are subclasses of the master :class:`Scenario` class and if their name starts with ``Scenario*``.
Only for classes that meet all these criteria, Balder will acknowledge these classes as valid scenarios and add
them to the internal collection of executable scenarios.

In the same way, Balder searches for scenarios, it will do that for setups. These setups have to be in files that have
the name ``setup_*.py`` and whose classes have the name ``Setup*`` and are child classes of :class:`Setup`.

.. note::
    Note that every ``.py`` file will be loaded that starts with ``scenario_*`` or ``setup_*``.

Collect tests
-------------

With the previous step, Balder has automatically loaded all defined testcase methods too, because in Balder all
testcases have to be defined as a method in a :ref:`Scenario <Scenarios>` class. The name of these test methods always
has to start with ``test_ *``. A scenario could define as much test methods as you like.

Collect connections
-------------------

:ref:`Connections` are objects that connects devices with each other. These objects will be included in a global
connection tree, which is the general representation of usable Balder connections. In every project you can define your
own connections within python modules/files with the name ``connections``. These files will be read by Balder
automatically during the collecting process. They will be inserted into the
:ref:`global connection-tree <The global connection tree>`.

Matching process of setups and scenarios (SOLVING)
==================================================

After the collecting process, Balder knows all existing setup and scenario classes. Now it is time to determine
the matchings between them. For this Balder checks if the definition of the :ref:`Scenario <Scenarios>` (defines what
we need) matches in one possible constellation of one or more :ref:`Setup(s) <Setups>` (defines what we have).

What are variations?
--------------------

In the SOLVING stage, Balder determines so called variations. This describes the device mappings between all required
:ref:`Scenario-Devices <Scenario-Device>` and their mapped :ref:`Setup-Device`. First all variations will be
added, regardless of whether they are executable. In the first part of the SOLVING stage, Balder will create a
variation for every possible device mapping first. If a mapping really fits (same feature and containing connection
trees between all device mappings - later more) will be determined
:ref:`in the second part of the SOLVING stage <SOLVING Part 2: Filtering Variations>`.

To make this clearer, lets take a look to the following example. Imagine, we have the following scenario:

.. mermaid::
    :align: center
    :caption: ScenarioLogin

    classDiagram
        direction RL
        class ClientDevice
        class ServerDevice

        ClientDevice <--> ServerDevice: HttpConnection



In Balder this could be described like the following:

.. code-block:: python

    import balder
    from balder import connections

    class ScenarioLogin(balder.Scenario):

        class ClientDevice(balder.Device):
            pass

        @balder.connect(ClientDevice, over_connection=connections.HttpConnection)
        class ServerDevice(balder.Device):
            pass


In addition to that, we create a setup in our project too. This setup looks like the following:

.. mermaid::
    :align: center
    :caption: SetupBasic

    classDiagram
        direction RL
        class This
        class MyServerDevice1
        class MyServerDevice2

        This <--> MyServerDevice1: HttpConnection
        This <--> MyServerDevice2: HttpConnection


In code, this will looks like the following:

.. code-block:: python

    import balder
    from balder import connections

    class SetupBasic(balder.Setup):

        class This(balder.Device):
            pass

        @balder.connect(This, over_connection=connections.HttpConnection)
        class MyServerDevice1(balder.Device):
            pass

        @balder.connect(This, over_connection=connections.HttpConnection)
        class MyServerDevice2(balder.Device):
            pass


With this both definitions, the single scenario ``ScenarioLogin`` and the single setup ``SetupBasic``, Balder will
totally create 6 possible variations:

.. code-block:: none

    Variation1:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice1`
    Variation2:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice2`
    Variation3:
        Scenario `ClientDevice` <=> Setup `MyServerDevice1`
        Scenario `ServerDevice` <=> Setup `This`
    Variation4:
        Scenario `ClientDevice` <=> Setup `MyServerDevice1`
        Scenario `ServerDevice` <=> Setup `MyServerDevice2`
    Variation5:
        Scenario `ClientDevice` <=> Setup `MyServerDevice2`
        Scenario `ServerDevice` <=> Setup `This`
    Variation6:
        Scenario `ClientDevice` <=> Setup `MyServerDevice2`
        Scenario `ServerDevice` <=> Setup `MyServerDevice1`


As you can see, every assignment possibility between the scenario devices to every possible setup device will be
created as match here. Till now, no variation was filtered, also no obviously false.

SOLVING Part 2: Filtering Variations
------------------------------------

Balder has created all possible variations now, but it has not check if all of them can be executed. In our example
the scenario device ``ClientDevice`` and the ``ServerDevice`` are connected over a ``HttpConnection``, but the mapped
setup devices in ``Variation4`` or ``Variation6`` aren't connected with each other - they have only a ``HttpConnection``
to the ``This`` device, but not between each other. These variations simply doesn't make sense, because the devices
have a complete different connection with each other.

In view of this fact the ``Variation4`` or the ``Variation6`` can not be executed and will be filtered by Balder. Balder
now has 4 active variations that could be executed from the current point of view:

.. code-block:: none

    Variation1:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice1`
    Variation2:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice2`
    Variation3:
        Scenario `ClientDevice` <=> Setup `MyServerDevice1`
        Scenario `ServerDevice` <=> Setup `This`
    Variation5:
        Scenario `ClientDevice` <=> Setup `MyServerDevice2`
        Scenario `ServerDevice` <=> Setup `This`

As you can see there are still some variations, we do not want to be executed. For example in the ``Variation3``
our scenario device ``ClientDevice`` is mapped to the server device ``MyServerDevice1``, but this doesn't make
sense, we want a client device here. But wait - how should Balder know this? Only the name is an indication that these
two elements do not go together..

They need some :ref:`Features`!

Devices with features
=====================

In the previous step all our devices doesn't have a real functionality, they only exist. For this Balder provides
:ref:`Features`. Features are classes that can be used by devices and offers functionality for these. If you have gone
through the :ref:`Balder Intro Example` you have learned the basic functionality of features. For a full introduction
to features, you can also discover the basic documentation section :ref:`Features`.

Add feature functionality
-------------------------

So let us add some functionality to our scenario definition. For this we have to add some features. Get the rule back
in your mind for what a scenario is for - **A scenario defines what we need**.

What does this mean in terms of our features? - We only have to provide the features, we really need in our scenario.
We will not add features, that we do not need here!

So let us add some features to our example before:

.. mermaid::
    :align: center
    :caption: ScenarioLogin

    classDiagram
        direction RL
        class ClientDevice
        ClientDevice: SendGetRequestFeature()
        class ServerDevice
        ServerDevice: WebServerFeature()

        ClientDevice <--> ServerDevice: HttpConnection

This scenario can be described like the following:

.. code-block:: python

    import balder
    from balder import connections

    class ScenarioLogin(balder.Scenario):

        class ClientDevice(balder.Device):
            req = SendGetRequestFeature(to_device="ServerDevice")

        @balder.connect(ClientDevice, over_connection=connections.HttpConnection)
        class ServerDevice(balder.Device):
            webserver = WebServerFeature()


.. note::
    Normally we can not provide parameters in the :class:`Feature` constructor, except for one use case - to set the
    active vDevice mapping. For now it is enough to understand that the feature ``SendGetRequestFeature`` can access
    the required information of the mapped ``ServerDevice``, while making some GET or POST requests.
    If you want to find out more about vDevices, take a look at :ref:`VDevices <VDevices and method-variations>`.

With this we have defined our required feature classes. We define that our ``ServerDevice`` needs an implementation of
the ``WebServerFeature`` and our ``ClientDevice`` needs an implementation of the ``SendGetRequestFeature``, otherwise
the scenario can not be executed.

Implement features in setup
---------------------------

Of course we also need a feature implementation in our setups too. As you will see later, features in
:ref:`Scenario-Devices <Scenario-Device>` often only define the interface that is needed by the scenario-device, but we
often do not provide a direct implementation of it there. Mostly the direct implementation is done on setup level.

To understand the Balder execution mechanism it doesn't matter where the implementation is done. First of all, it is
sufficient to know, that every ``*ImplFeature`` feature in our setup is a subclass of the defined feature classes in
our ``ScenarioLogin``.
Every of these setup features contains the implementation of all interface methods and properties that are defined in
the related scenario feature.

For this, we expand our setup in the following way:

.. mermaid::
    :align: center
    :caption: SetupBasic

    classDiagram
        direction RL
        class This
        This: WebServerImplFeature()
        This: ...()
        class MyServerDevice1
        MyServerDevice1: SendGetRequestImplFeature()
        MyServerDevice1: ...()
        class MyServerDevice2
        MyServerDevice2: SendGetRequestImplFeature()
        MyServerDevice2: ...()

        This <--> MyServerDevice1: HttpConnection
        This <--> MyServerDevice2: HttpConnection

In Balder, his looks like the following:

.. code-block:: python

    import balder
    from balder import connections

    class SetupBasic(balder.Setup):

        class This(balder.Device):
            server = SendGetRequestImplFeature()  # implements the `SendGetRequestFeature`
            ...

        @balder.connect(This, over_connection=connections.HttpConnection)
        class MyServerDevice1(balder.Device):
            request = WebServerImplFeature()  # implements the `WebServerFeature`
            ...

        @balder.connect(This, over_connection=connections.HttpConnection)
        class MyServerDevice2(balder.Device):
            req = WebServerImplFeature()  # implements the `WebServerFeature`
            ...

.. note::
    The names of the class properties, the feature instances are assigned to, doesn't matter for Balder. They are
    only relevant, if you want to access the feature instance in the setup class itself (you will see later in
    :ref:`Using Fixtures`).

.. note::
    It doesn't matter if one or more of the devices has more features. Balder will scan them to determine if
    the variation can be executed, by securing that every mapped setup device has a valid feature implementation of the
    defined features in the corresponding scenario-device. It doesn't matter if the setup has features, the scenario
    does not have.
    Also here: **Scenarios define what you need** - **Setups define what you have**

What happens with our Variations?
---------------------------------

Get back in mind, that we had four of our six variations left:

.. code-block:: none

    Variation1:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice1`
    Variation2:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice2`
    Variation3:
        Scenario `ClientDevice` <=> Setup `MyServerDevice1`
        Scenario `ServerDevice` <=> Setup `This`
    Variation5:
        Scenario `ClientDevice` <=> Setup `MyServerDevice2`
        Scenario `ServerDevice` <=> Setup `This`

These are already filtered after their connections, but Balder hasn't check their feature implementation.
For this Balder will go through every possible variation and check it the mapped devices on the setup side uses child
classes of the feature that are defined in the corresponding scenario device. Only if every feature of every mapped
scenario device has a relevant child implementation in the corresponding setup device, the variation is still
applicable.

In ``Variation1`` Balder will start looking for the ``ClientDevice``. It will notices that it **needs** the
``SendGetRequestFeature``. The ``This`` device on the other side is the mapped setup device for the ``ClientDevice``.
For this variation matches, Balder has to secure, that this setup device implements all existing features (as child
subclasses). With that, it iterates over the features of the setup device ``This``, and recognize the feature
``SendGetRequestImplFeature``. This feature is a valid subclass of the ``SendGetRequestFeature``, which result in a GO
for this device mapping.

If there would be only one scenario feature that is not a child of one of the setup features this results into an not
applicable mapping and makes these variation non-applicable! In our case this works, so we can go further and execute
the checking process for our last mapping ``ServerDevice`` <-> ``MyServerDevice1`` in our ``Variation1`` too.

We iterate over the features in our scenario-based ``ServerDevice``. Within that, we can only find the
``WebServerFeature``. For that, we have to check that it is available as subclass in our mapped setup-based
``MyServerDevice1`` too. We will find the ``WebServerImplFeature`` which is a child of the scenario-based
``WebServerFeature``.

The ``Variation1`` completely supports our features. ``Variation1`` is an executable mapping.

Balder will continue with this check for every other variation too. ``Variation2`` will also pass, because it is
similar the same. But it is different with ``Variation3`` and ``Variation4``, because both has the mapping
``ClientDevice`` <-> ``MyServerDeviceX`` and also ``ServerDevice`` <-> ``This``. In both mappings, the features are
not supported from each other and so there is no applicable mapping here! ``Variation3`` and ``Variation4`` will be
filtered.

This results in our two of six mappings, that can be really executed:

.. code-block:: none

    Variation1:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice1`
    Variation2:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice2`

Balder will add them to the execution-tree and run these in the last stage, the EXECUTION stage.

Using Fixtures
==============

Balder also supports the concept of fixtures. Fixtures are functions (or methods) that will be executed to prepare or
clean-up devices or other things before or after a testcase or a scenario/setup will be executed.

Fixtures have two main properties that determine the behaviour and validity of a fixture. First they have a
**definition-scope**, that describes where the fixture is defined. In addition to that, they have a **execution-level**,
that defines at which point the fixture should be executed.

The execution-level
-------------------

If you define a fixture, you have to set the **execution-level** with the attribute ``level`` in the fixture
decorator ``@balder.fixture(level="..")``. For this the following execution levels can be used:

+------------------------+---------------------------------------------------------------------------------------------+
| level                  | description                                                                                 |
+========================+=============================================================================================+
| ``session``            | This is the furthest out execution-level. The construct part of the fixture will be         |
|                        | executed directly after the collecting and solving process and before some user code will   |
|                        | run. The teardown code will be executed after the whole test session was executed.          |
+------------------------+---------------------------------------------------------------------------------------------+
| ``setup``              | This fixture runs before and after an underlying :class:`Setup` has changed. It embraces    |
|                        | every new :class:`Setup` class that will get active in the test session.                    |
+------------------------+---------------------------------------------------------------------------------------------+
| ``scenario``           | This fixture runs before and after an underlying :class:`Scenario` has changed. It          |
|                        | embraces every new :class:`Scenario` class that will get active in the test session.        |
+------------------------+---------------------------------------------------------------------------------------------+
| ``variation``          | This fixture runs before and after every new device variation of its scoped                 |
|                        | :class:`Setup` / :class:`Scenario` constellation. It embraces every new variation that      |
|                        | will be get active in the test session.                                                     |
+------------------------+---------------------------------------------------------------------------------------------+
| ``testcase``           | This fixture runs before and after every testmethod. It embraces every new testcase which   |
|                        | is defined in the :class:`Scenario` class.                                                  |
+------------------------+---------------------------------------------------------------------------------------------+

These execution-levels defines on which position the fixture should be executed, but if a fixture will be really
executed or not also depends on the **definition-scope**.

The definition-scope
--------------------

In Balder there exists a lot of different **definition-scopes**. These scopes define to a certain extent the validity
of them. The following table shows them with the scope, they are valid.

+------------------------+------------------------+--------------------------------------------------------------------+
| Definition             | Validity               | description                                                        |
+========================+========================+====================================================================+
| as function in         | everywhere             | This fixture will be executed always. It doesn't matter which      |
| ``balderglob.py`` file |                        | specific testset you are calling. This fixture will be executed in |
|                        |                        | every test run.                                                    |
+------------------------+------------------------+--------------------------------------------------------------------+
| as method in           | only in this setup     | This fixture runs only if this setup will be executed in the       |
| :class:`Setup`         |                        | current testrun. If the **execution-level** is ``session`` it will |
|                        |                        | be executed as session-fixture only if this setup is in the        |
|                        |                        | executor tree. If the  **execution-level** is ``setup`` or lower,  |
|                        |                        | this fixture will only be called if the setup is currently active  |
|                        |                        | in the test run.                                                   |
+------------------------+------------------------+--------------------------------------------------------------------+
| as method in           | only in this scenario  | This fixture runs only if this scenario will be executed in the    |
| :class:`Scenario`      |                        | current testrun. If the **execution-level** is ``session`` or      |
|                        |                        | `setup` it will be executed as session-/ or setup-fixture only if  |
|                        |                        | this Scenario is in the executor tree. If the  **execution-level** |
|                        |                        | is ``scenario`` or lower, this fixture will only be called if the  |
|                        |                        | scenario is currently active in the test run.                      |
+------------------------+------------------------+--------------------------------------------------------------------+

As you can see, it depends on the **execution-level** and on the **definition-scope** whether and when a fixture will be
executed.

Define fixture
--------------

If you want to use a fixture globally you can simply add it to the ``balderglob.py`` file, that has to be located in
the root directory. You can define the startup code that will be executed before and also the teardown code that will be
executed after the embracing object in one function/method. For this you have to separate the code with the ``yield``
command.

This fixture can look like the following:

.. code-block:: python

    # file balderglob.py

    @balder.fixture(level="session")
    def signal_balder_is_running():
        # sets the information that Balder is running now
        notification.send("balder is running")
        yield
        notification.send("balder terminated")

.. note::
    Note that Balder will collect only the ``balderglob.py`` file that is located directly in the working directory. If
    you want to separate your global elements, you can distribute your code but you have to import it in the global
    ``balderglob.py`` file.


Add setup fixture
-----------------

If you want to interact with a special setup, you can define a fixture also in that setup. The big advantage here is,
that you can interact with the setup-devices on this stage too.

.. code-block:: python

    import balder
    from balder import connections

    class SetupBasic(balder.Setup):

        class This(balder.Device):
            request = SendGetRequestImplFeature()
            ...

        @balder.connect(This, over_connection=connections.HttpConnection)
        class MyServerDevice1(balder.Device):
            server = WebServerImplFeature()
            ...

        @balder.connect(This, over_connection=connections.HttpConnection)
        class MyServerDevice2(balder.Device):
            server = WebServerImplFeature()
            ...

        @balder.fixture(level="testcase")
        def start_webservers(self):
            self.MyServerDevice1.server.start()
            self.MyServerDevice2.server.start()
            yield
            self.MyServerDevice1.server.shutdown()
            self.MyServerDevice2.server.shutdown()

.. note::
    In a real-world example, we would have a separate setup-only feature that allows to start and shutdown the
    webserver, because we want to develop these scenarios as universal as possible. Our feature ``WebServerFeature``
    would only define that we have a webserver, but not that we can start and stop it. If we want to test the login of
    pypi for example, we have not the possibility to start and stop the server, but we can assume that the server is
    running.
    With this, we can apply the scenario also for a webserver we can start and stop as we can for the webserver we
    can't start and stop.

    Remember, that we define **what we need** in our scenario and we would not need the possibility to start and stop
    the server for this. This work should be done in setup code only.

Add scenario fixture
--------------------

The same shown within :ref:`Setups` is also possible on :ref:`Scenario <Scenarios>` level. Similar to the setup, you
provide a method here too:

.. code-block:: python

    import balder
    from balder import connections

    class ScenarioLogin(balder.Scenario):

        class ClientDevice(balder.Device):
            req = SendGetRequestFeature(to_device="ServerDevice")

        @balder.connect(ClientDevice, over_connection=connections.HttpConnection)
        class ServerDevice(balder.Device):
            webserver = WebServerFeature()

        @balder.fixture(level="testcase")
        def secure_that_logout(self):
            yield
            self.ClientDevice.req.logout()

For more about fixtures, take a look :ref:`here <Fixtures>`.
