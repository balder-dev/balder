Balder execution mechanism
**************************

Balder execution mechanism runs in three primary phases after invoking the balder command: collection, solving, and
execution. These phases ensure that tests are gathered, matched to available setups, and run efficiently in compatible
configurations. The process revolves around key concepts like :ref:`Scenarios` (describing what is needed for a test),
:ref:`Setups` (describing what is available in the environment), :ref:`Devices` (components within scenarios and
setups), :ref:`Connections` (links between devices), and :ref`Features` (functionalities added to devices).

In the first stage, the collecting phase, Balder collects all relevant items from the project
directory (the current working directory) and imports their Balder-related classes and functions. This builds an
internal registry of components like :ref:`Setup <Setups>`, :ref:`Scenario <Scenarios>`, :ref:`Feature <Features>` and
:ref:`Connection <Connections>` classes that will be used in later phases.

The solving phase, also known as the matching process, is where Balder determines valid combinations (called
variations) between scenarios and setups. It generates potential mappings of scenario devices to setup devices, filters
them based on connections and features, and organizes the valid ones into an execution tree. This tree represents a
hierarchical structure of all executable matches, including device mappings and sub-variations.

In the final execution phase, Balder traverses the execution tree built in the solving phase and runs all valid
variations. This involves instantiating devices, applying features, executing test methods, and handling fixtures
(setup/cleanup functions).

Before we going into the process in more detail, we want to have a look for the exact difference between :ref:`Setups`
and :ref:`Scenarios`.

Difference between setup and scenario
=====================================

Balder is based on individual :ref:`Scenario <Scenarios>` and :ref:`Setup <Setups>` classes. These both classes are
fundamental concepts that enable reusable, environment-agnostic testing. While they work together to facilitate
scenario-based testing, they serve distinct purposes: scenarios define the situation in which individual tests can be
carried out, while setups provide concrete implementations for specific environments.

The following definition is important to understand:

**Scenario:** Describes what you need

**Setup:** Describes what you have

So what does this mean? Let's take a deeper look at it.

Describes what you need: Scenarios
----------------------------------

A scenario represents the required structure and behavior for a test. It describes **what is needed** to perform the
test in an abstract way, without the need to tying it to a specific implementation. Scenarios focus on the reusable
test pattern or logic, such as the steps involved in a process (e.g., logging into a system: opening a login interface,
entering credentials, submitting, and verifying success). In a scenario only the devices are defined, that are relevant
for this specific test scenario.

* Defined in Python files named ``scenario_*.py``.
* Classes must subclass ``balder.Scenario`` and typically start with ``Scenario*``.
* Contain test methods (starting with test_*) that execute the actual assertions.
* Define required devices (components needed for the test) and features (interfaces or capabilities those devices must support).

**Purpose:** To create a shared, platform-independent blueprint for tests that can be applied across multiple setups.


Describes what you have: Setups
-------------------------------

A setup describes the available environment or configuration where the test can run. Or in simpler words: It describes,
**what we have**. Here you define everything that is available and relevant in this setup. It provides the concrete
details of how the devices are implemented in a particular context, such as specific hardware, software, or protocols.
For example, if you have your computer, a smartphone, the router, the server of company X, and the server of company Y
in your controllable spectrum of devices, you can add these devices with all its features to your setup. If you are
planing that your login scenario can be executed with this setup later on for example, Balder could find matches within
these devices to log in via a web browser of the computer, via a web browser of the smartphone, via a mobile app or
even via an API. All this depends on the provided device features and if they match with the feature-requirement of the
applicable scenario devices.

In short, a setup is:

* Defined in Python files named ``setup_*.py``.
* Classes must subclass ``balder.Setup`` and typically start with ``Setup*``.
* Provide actual device instances that match the devices required by scenarios.
* Implement features as subclasses that fulfill the interfaces defined in scenarios.

**Purpose:** To represent real-world variations or environments, allowing the same scenario to be tested in different
contexts without rewriting the test code.

Balder will automatically manage the determination of all available matches between the :ref:`Scenario <Scenarios>`
devices and the :ref:`Setup <Setups>` devices. If it finds any matches, it will execute these possible variations
in the execution step. You can read more about this in the following subsections of this guide (see
:ref:`Matching process of setups and scenarios (SOLVING)`).

Loading Balder Objects (COLLECTING)
===================================

The collection process is the first stage of the Balder execution mechanism, directly after executing the ``balder ...``
command. In this stage, all available relevant Balder classes within the working directory are collected.

Collect setups and scenarios
----------------------------

First, the collector begins to find all Setup and Scenario classes that are located directly in the Python files
collected in the earlier step.

Balder searches for scenarios exclusively in files with the name ``scenario_*.py``. In these files, it searches for
classes that are subclasses of the master :class:`Scenario` class and whose names start with ``Scenario*``.
Only classes that meet all these criteria will be acknowledged by Balder as valid scenarios and added to the internal
collection of executable scenarios.

In the same way that Balder searches for scenarios, it will do so for setups. These setups have to be in files with the
name ``setup_*.py``, and their classes must have names starting with ``Setup*`` and be subclasses of :class:`Setup`.

Collect tests
-------------

With the previous step, Balder has automatically loaded all defined test case methods too, because in Balder, all test
cases have to be defined as a method in a :ref:`Scenario <Scenarios>` class. The names of these test methods always
have to start with ``test_*``. A scenario can define as many test methods as you like.

Collect connections
-------------------

:ref:`Connections` are objects that connect devices to each other. These objects will be included in a global
connection tree, which is the general representation of usable Balder connections. In every project, you can define
your own connections within Python modules or files with the name ``connections``. These files will be read by Balder
automatically during the collecting process. They will be inserted into the
:ref:`global connection tree <The global connection tree>`.

.. note::
    Balder is shipped with a default global connection tree. In many cases, this is sufficient.

Matching process of setups and scenarios (SOLVING)
==================================================

After the collection process, Balder has identified all existing Setup and Scenario classes. Next, it determines the
matches between them. To do this, Balder checks whether the definition of a :ref:`Scenario <Scenarios>` (which
specifies what is required) can be fulfilled by one possible configuration of one or more :ref:`Setups <Setups>`
(which define what is available).

To accomplish this, Balder creates variations between the devices specified in the Scenario and Setup by generating all
possible ways these devices can match.

What are variations?
--------------------

In the SOLVING stage, Balder determines so-called variations. These represent the device mappings between all required
:ref:`Scenario-Devices <Scenario-Device>` and their corresponding :ref:`Setup-Devices <Setup-Device>`. Initially,
Balder adds all possible variations, regardless of whether they are executable. In the first part of the SOLVING stage,
it creates a variation for every conceivable device mapping. Whether a mapping truly fits - meaning it shares the same
features and includes matching connection trees between all device mappings (more on this later) - is checked
:ref:`in the second part of the SOLVING stage <SOLVING Part 2: Filtering Variations>`.

To make this clearer, let's take a look at the following example.
Imagine, we have the following scenario:

.. mermaid::
    :align: center
    :caption: ScenarioLogin

    classDiagram
        direction RL
        class ClientDevice
        class ServerDevice

        ClientDevice <--> ServerDevice: HttpConnection



In Balder this could be described like shown in the following snippet:

.. code-block:: python

    import balder
    from balder import connections

    class ScenarioLogin(balder.Scenario):

        class ClientDevice(balder.Device):
            pass

        @balder.connect(ClientDevice, over_connection=connections.HttpConnection)
        class ServerDevice(balder.Device):
            pass


We also want to create a setup in our project. This setup should look like:

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


In code:

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


With these both definitions, Balder will create six variations:

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


As you can see, every possible assignment between the Scenario devices and the available Setup devices is created as a
potential match at this stage. Up to this point, no variations have been filtered out - not even the ones that are
obviously invalid.

SOLVING Part 2: Filtering Variations
------------------------------------

Balder has now created all possible variations, but it has not yet checked whether all of them can be executed. In our
example, the Scenario devices ``ClientDevice`` and ``ServerDevice`` are connected via an ``HttpConnection``. However,
the mapped Setup devices in ``Variation4`` or ``Variation6`` aren't connected to each other - they only have an
``HttpConnection`` to the ``This`` device, but not between themselves. These variations simply don't make sense, because
the devices have completely different connections to each other.

In light of this fact, ``Variation4`` and ``Variation6`` cannot be executed and will be filtered out by Balder. Balder
now has four active variations that could be executed from the current point of view:

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

As you can see, there are still some variations that we do not want to execute. For example, in ``Variation3``, the
Scenario device ``ClientDevice`` is mapped to the Setup device ``MyServerDevice1``. However, this doesn't make sense
because we need a client device here, not a server. But wait - how should Balder know this?

They need some :ref:`Features`!

Devices with features
=====================

In the previous steps, our devices didn't have any real functionality; they simply existed. To address this, Balder
provides :ref:`Features`. Features are classes that devices can use to add specific functionalities. If you've gone
through the :ref:`Balder Intro Example`, you've already learned the basics of how features work.

Add feature functionality
-------------------------

So let's add some functionality to our Scenario definition. To do this, we need to incorporate some Features. Remember
the key rule for what a Scenario represents: **A Scenario defines what we need**.

What does this mean in terms of our Features? It means we should only include the Features that are truly required for
the Scenario. We won't add any Features that aren't necessary here!

With that in mind, let's enhance our previous example by adding a couple of relevant Features:

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
    Normally, we cannot provide parameters in the :class:`Feature` constructor, except in one specific case: to set the
    active vDevice mapping. For now, it's enough to understand that the ``SendGetRequestFeature`` can access the
    necessary information from the mapped ServerDevice when performing GET or POST requests. If you'd like to learn
    more about vDevices, check out the :ref:`VDevices <VDevices and method-variations>` section.

With this, we have defined our required Feature classes. This means that our ``ServerDevice`` needs an implementation
of the ``WebServerFeature``, while our ``ClientDevice`` requires an implementation of the ``SendGetRequestFeature``.
Otherwise, the Scenario cannot be executed.

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

With that, we have defined the Features required by the Scenario. Of course, we also need to implement these Features
in our Setups. Most of the time, this is where we add the actual code. As you'll see later, Features in
:ref:`Scenario-Devices <Scenario-Device>` often only define the interface needed by the Scenario device, without
providing a direct implementation there. Instead, the actual implementation is usually handled at the Setup level.

To understand Balder's execution mechanism, it doesn't matter where the implementation takes place. For now, it's
enough to know that every ``*ImplFeature`` in our Setup is a subclass of the Feature classes defined in our
``ScenarioLogin``.

For Balder to find a match between our Scenario and the Setup(s), the Setup devices must provide implementations for
all the Features defined in the corresponding Scenario devices.

For this, we expand our setup like that:

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

In Balder, his looks like:

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
    Note that the names of the class properties to which the Feature instances are assigned do not matter to Balder.
    These names are only relevant if you need to access the Feature instances within the Setup class itself (as you'll
    see later in the :ref:`Using Fixtures` section).

.. note::
    It doesn't matter if one or more of the devices has more features. Balder will scan them to determine if
    the variation can be executed, by securing that every mapped setup device has a valid feature implementation of the
    defined features in the corresponding scenario-device. It doesn't matter if the setup has features, the scenario
    does not have.
    Also here: **Scenarios define what you need** - **Setups define what you have**

.. note::
    It doesn't matter if one or more of the devices have additional Features. Balder will scan them to determine
    whether the variation can be executed, by verifying that every mapped Setup device provides a valid implementation
    of the Features defined in the corresponding Scenario device. It also doesn't matter if the Setup includes Features
    that the Scenario does not require.

    Remember: **Scenarios define what you need** - **Setups define what you have**.

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

These variations have already been filtered based on their connections, but Balder hasn't checked their feature
implementations yet. To do this, Balder goes through every remaining variation and verifies whether the mapped devices
on the Setup side provide subclasses of the Features defined in the corresponding Scenario devices. A variation remains
applicable only if every Feature from every mapped Scenario device has a matching subclass implementation in the
corresponding Setup device.

Take ``Variation1`` as an example. Balder starts by examining the ``ClientDevice``. It notices that this device
**needs** the ``SendGetRequestFeature``. The ``This`` device is the mapped Setup device for the ``ClientDevice``. For
the variation to match, Balder must ensure that this Setup device implements all required Features (as subclasses). It
iterates over the Features of the Setup device ``This`` and recognizes the ``SendGetRequestImplFeature``. Since this is
a valid subclass of ``SendGetRequestFeature``, it gives a green light for this device mapping.

If even one Scenario Feature lacks a matching subclass in the Setup Features, the mapping would be invalid, making the
entire variation non-applicable. In our case, everything checks out, so Balder moves on to the final mapping in
``Variation1``: ``ServerDevice`` <-> ``MyServerDevice1``.

Next, Balder iterates over the Features in the scenario-based ``ServerDevice``. It finds only the ``WebServerFeature``.
Now, it checks if this is available as a subclass in the mapped setup-based ``MyServerDevice1``. Sure enough, it finds
the ``WebServerImplFeature``, which is a subclass of the scenario-based ``WebServerFeature``.

As a result, ``Variation1`` fully supports the required Features, making it an executable mapping.

Balder continues this check for all other variations. ``Variation2`` passes as well, since it's essentially the same
setup. However, things are different for ``Variation3`` and ``Variation4``. Both have swapped mappings:
``ClientDevice`` <-> ``MyServerDeviceX`` and ``ServerDevice`` <-> ``This`` (where ``MyServerDeviceX`` refers to
``MyServerDevice1`` or ``MyServerDevice2``, depending on the variation). In these cases, the Features do not match
between the devices, so there is no valid mapping. Therefore, ``Variation3`` and ``Variation4`` get filtered out.

This results in two of previously six mappings, that can be really executed:

.. code-block:: none

    Variation1:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice1`
    Variation2:
        Scenario `ClientDevice` <=> Setup `This`
        Scenario `ServerDevice` <=> Setup `MyServerDevice2`

Balder will add them to the execution-tree and run these variations in the last stage, the EXECUTION stage.

Using Fixtures
==============

Balder also supports the concept of fixtures. Fixtures are functions (or methods) that are executed to prepare or clean
up devices or other resources before or after a test case, scenario, or setup runs.

Structure of a Fixture
----------------------

As mentioned, fixtures are functions or methods that execute setup (construct) and cleanup (teardown) code at specific
points during the test process. They use the ``yield`` statement to separate the construct code (which runs before the
``yield``) from the teardown code (which runs after the ``yield``). Fixtures can also return values through the
``yield``, allowing these values to be passed to dependent fixtures or test cases.

.. code-block:: python

    @balder.fixture(level="scenario")  # the level describes when the fixture should be executed
    def resource():
        # Construction Code: Will be executed before the tests
        my_resource = MyResource()
        my_resource.start()
        yield my_resource  # returns the resource object to make it available in other fixtures or even in test methods

        # Cleanup Code: Will be executed after the tests
        my_resource.quit()


Fixtures have two main properties that determine their behavior and validity. First, they have an **execution-level**,
which defines at which point the fixture should be executed. In addition, they have a **definition-scope**, which is
determined by the position in which the fixture is defined.


The execution-level
-------------------

When defining a fixture, you must specify its **execution-level** using the level attribute in the fixture decorator,
like this: ``@balder.fixture(level="..")``. This determines when the fixture's setup and teardown code will run during
the test process.

The following execution levels are available:


+------------------------+---------------------------------------------------------------------------------------------+
| level                  | Description                                                                                 |
+========================+=============================================================================================+
| ``session``            | This is the outermost level. The fixture's setup code runs right after the collecting and   |
|                        | solving phases, before any test code executes. The teardown code runs after the entire test |
|                        | session completes.                                                                          |
+------------------------+---------------------------------------------------------------------------------------------+
| ``setup``              | This level runs the fixture before and after each change to an underlying Setup. It wraps   |
|                        | around every new Setup class that becomes active in the test session.                       |
+------------------------+---------------------------------------------------------------------------------------------+
| ``scenario``           | This level runs the fixture before and after each change to an underlying Scenario. It      |
|                        | wraps around every new Scenario class that becomes active in the test session.              |
+------------------------+---------------------------------------------------------------------------------------------+
| ``variation``          | This level runs the fixture before and after each new device variation within the current   |
|                        | Setup/Scenario combination. It wraps around every new variation that activates in the test  |
|                        | session.                                                                                    |
+------------------------+---------------------------------------------------------------------------------------------+
| ``testcase``           | This is the innermost level. The fixture runs before and after each individual test method, |
|                        | wrapping around every test case defined in the Scenario class.                              |
+------------------------+---------------------------------------------------------------------------------------------+

These levels help you control the granularity of your fixtures, ensuring resources are prepared and cleaned up at the
right points in Balder's execution flow.

These execution levels define at which point the fixture should be executed. However, whether a fixture is actually
executed or not also depends on its **definition-scope**.

The definition-scope
--------------------

Balder supports several different definition scopes for fixtures. These scopes determine, to a certain extent, when and
where a fixture is valid and can be executed. The following table lists the available definition-scopes, along with
their validity and a brief description.

+------------------------+------------------------+--------------------------------------------------------------------+
| Definition             | Validity               | Description                                                        |
+========================+========================+====================================================================+
| As a function in the   | Everywhere             | This fixture will always be executed, no matter which specific     |
| balderglob.py file     |                        | test set you are running. It will be called in every test run.     |
+------------------------+------------------------+--------------------------------------------------------------------+
| As a method in a       | Only in this Setup     | This fixture runs only if the related Setup is executed in the     |
| :class:Setup class     |                        | current test run. If the execution level is ``session``, it        |
|                        |                        | will be executed as a session fixture only if this Setup appears   |
|                        |                        | in the executor tree. If the execution level is ``setup`` or       |
|                        |                        | lower, the fixture will only be called when the Setup is currently |
|                        |                        | active in the test run.                                            |
+------------------------+------------------------+--------------------------------------------------------------------+
| As a method in a       | Only in this Scenario  | This fixture runs only if the related Scenario is executed in the  |
| :class:Scenario class  |                        | current test run. If the execution level is ``session`` or         |
|                        |                        | ``setup```, it will be executed as a session or setup fixture only |
|                        |                        | if this Scenario appears in the executor tree. If the execution    |
|                        |                        | level is ``scenario`` or lower, the fixture will only be called    |
|                        |                        | when the Scenario is currently active in the test run.             |
+------------------------+------------------------+--------------------------------------------------------------------+

As you can see, whether and when a fixture gets executed depends on both its **execution-level** and its
**definition-scope**.

Define fixture
--------------

If you want to define a global fixture that applies everywhere, you can simply add it as a function in the
``balderglob.py`` file, which must be located in the root directory of your project. In this function, you can include
both the setup code that runs before the wrapped object and the teardown code that runs after it. To separate these two
parts, use the ``yield`` statement.

For example, this fixture can look like:

.. code-block:: python

    # file balderglob.py

    @balder.fixture(level="session")
    def signal_balder_is_running():
        # sets the information that Balder is running now
        notification.send("balder is running")
        yield
        notification.send("balder terminated")

.. note::
    Note that Balder will only load the ``balderglob.py`` file located directly in the working directory. If you want
    to organize your global elements across multiple files, you can split your code accordingly, but be sure to import
    everything into this main ``balderglob.py`` file.


Add setup fixture
-----------------

If you want to interact with a specific Setup, you can define a fixture directly within that Setup class. The major
advantage here is that you can access and interact with the Setup's devices at this stage as well.

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

Add scenario fixture
--------------------

The same approach shown previously for Setups can also be applied at the Scenario level. Just like in Setups, you can
define fixtures as methods within the Scenario class.

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

If you want to learn more about fixtures, feel free to jump straight to the :ref:`Fixtures` section. Otherwise, let's
continue with a more detailed explanation of scenarios.
