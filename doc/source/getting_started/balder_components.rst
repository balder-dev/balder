Main Balder components
**********************

The following section should help getting an overview over the available components in Balder. You will learn the key
facts about :ref:`Scenarios` and :ref:`Setups` and how their :ref:`Devices` work. You will learn what
:ref:`Features` are and how Balder matches these between :ref:`Scenarios` and :ref:`Setups`. You will also learn how to
connect devices with each other over :ref:`Connections` and how :ref:`connection trees` are defined.

By working through this section, you should be able to understand Balder tests and also manage and set up your
own tests with Balder.

Note that this section only provides an overview of the components. You can find a detailed description of each
element in the :ref:`Basic Guide <Basic Guides>`.

Difference setup and scenario
=============================

The key concept in Balder is the separation of test logic within scenarios and the specific implementation within setup
classes. Scenarios define a situation under which individual tests are carried out. Setups, on the other hand, describe
how a test environment currently looks like. So, the most important statements in Balder are:

**Scenario:** Describes what you need

**Setup:** Describes what you have

So what does this mean? Take a closer look into these definitions.

Scenario: Describes what you need
---------------------------------

A :ref:`Scenario <Scenarios>` always defines what **you need**. So for example if you want to test an online login on a
server, you need the server and a client device that tries to connect to the server device. These are the components of
a :ref:`Scenario <Scenarios>`.

Setup: Describes what you have
------------------------------

It is different when we look at the :ref:`Setups`. In a setup you define everything that is available and
relevant in the environment, the particular setup is for. So for example, if you have your computer, the router and the
server of company X in your influenceable spectrum of devices you can add all of them to your setup. Also if the
scenario is written later only for the router and the server, it will work out, because Balder will automatically match
scenario-devices with compatible setup-devices.

What are devices?
=================

A device is a component of a :ref:`Setup <Setups>` or of a :ref:`Scenario <Scenarios>`. In generally it describes
a container object, which represents a test component, an application or a real physically device. Generally, a device
contains functionality, so called :ref:`Features <Features>`. These features can directly be used within your
test scenario or within fixtures of your setup. You can access these properties with ``self.MyDevice.*``.

.. note::
    Note that a device itself never implements something by itself! A device should only have class-attributes which
    hold an instantiated :ref:`Feature <Features>` object. More about this later on.

Functionality = Feature
-----------------------

A device can also be described as a collection of :ref:`Features`. Every feature stands for a functionality the device
has. So for example a **ClientDevice** can have ``OpenAWebpageFeature()``, which describes the functionality to
interact with a website. It does not provide the site itself. The website should be provided by another **ServerDevice**
which uses something like a ``ProvideWebpageFeature()``.

In Balder you have to add features to scenario-devices as class attributes like shown below:

.. code-block:: python

    class ScenarioMyOwn(balder.Scenario):
        ...
        class ClientDevice(balder.Device):
            webpage = OpenAWebpageFeature()

        class ServerDevice(balder.Device):
            provider = ProvideWebpageFeature()
        ...
        # you could use the device in a testcase
        def test_webpage(self):
            addr = self.ServerDevice.provider.get_address()
            ...

.. note::
    Please note, that :class:`Scenario` classes must be defined inside files that start with ``scenario_*.py``. In
    addition their class name has to start with ``Scenario*``. Otherwise the file will not be picked up by Balder.


How to connect devices
======================

In the real world, devices are connected with each other. If you have a **ClientDevice** and a **ServerDevice** like
mentioned before, you could expect that these are connected with each other a HTTP connection. For
this, Balder provides :ref:`Connections`.

Simple connections
------------------

Balder is shipped with a lot of different connections (see :ref:`Connections API`), that are organized in a so called
:ref:`connection-tree <Global connection-trees>`. In addition to that, you can also create your
own ones, by simply inheriting from the master class :class:`Connection`.

.. code-block:: python

    from balder import Connection

    class MyOwnConnection(Connection):
        pass

Connection trees
----------------

The connection-tree is a global hierarchical structure, that describes how connections are arranged with each other. For
example that a ``HttpConnection`` is based on a ``TcpConnection`` which itself is based on ``IpV4Connection`` or
``IpV6Connection``.

The whole thing allows you to define subtrees, that can be used to connect devices. You can read more about this in
the section :ref:`Connections`.

Connections between devices
---------------------------

We have learned a lot about connections and how they are organized, but how do we connect some devices with each other?
This is really simple, because Balder provides a decorator ``@balder.connect(..)`` here. If you want to connect the
``ClientDevice`` with the ``ServerDevice``, you can do the following:

.. code-block:: python

    import balder

    class ScenarioMyOwn(balder.Scenario):
        ...
        class ClientDevice(balder.Device):
            ...

        @balder.connect(ClientDevice, over_connection=HttpConnection.based_on(IpV4Connection))
        class ServerDevice(balder.Device):
            ...

It works the same way in setups.

How setups work?
================

So far we have finished the scenario level (**what we need**). But of course we also have to define the actual
real implementation for what we want to test. For this we use the :class:`Setup` classes.

As mentioned earlier, **Setups always describe what you have**! Similar to :ref:`Scenarios` you define all your devices
and add features to it. But here you can define everything you have or you want to use in the test environment. Balder
will automatically determine (based on the feature set and the connections between the devices) in which constellation
a scenario fits to a setup.

Implement features
------------------

Often scenario-features don't provide the whole implementation. In most cases, these features are abstract
and a user specific implementation has to be provided on setup level (means, the setup device needs to hold the feature
implementations of the scenario devices).

This implementation normally holds your specific code. We want to add them into a new module
``lib/scenario_features.py``, that provides the specific setup level features:

.. code-block:: none

    |- src/
        |- lib/
            |- scenario_features.py
            |- setup_features.py
        |- scenarios/
            |- ...
        |- setups/
            |- setup_my.py
            |- ...

.. note::
    Balder doesn't care where you implement the feature objects, but it is easier to use a common understandable
    structure to make it easier to read your code.

.. note::
    Often its a good idea to use a directory as a python module for managing features. For this you create a directory
    with the name ``scenario_features`` instead of the ``scenario_features.py`` file and add a ``__init__.py`` file in
    it.

    .. code-block:: none

        |- src/
            |- lib/
                |- scenario_features/
                    |- __init__.py
                    |- ...
                |- setup_features/
                    |- __init__.py
                    |- my_example_feature.py
                    |- ...
            |- scenarios/
                |- ...
            |- setups/
                |- setup_my.py
                |- ...

    Here you can implement many files, which allows you to organize your features in a clear way.

How does Balder know, which feature you are implementing?
---------------------------------------------------------

Maybe you ask yourself how Balder knows which scenario-feature you are implementing in your setup. For this Balder
uses **Inheritance**!

A setup level feature always needs to be a subclass of the related scenario-level feature to match.

In most cases the scenario-features implement abstract properties or methods, which are filled with a specific
implementation on setup level. You can implement them easily by overwriting them.

The file ``features_setup.py`` for example could have the following content:

.. code-block:: python

    # file src/lib/setup_features.py

    from lib import scenario_features

    class SeleniumFeature(scenario_features.OpenAWebpageFeature):

        ...

        def open_page(self, url):
            self.selenium.open(url)

        ...

This setup-level feature holds the ready-to-use implementation for the scenario-level feature
``lib.scenario_features.OpenAWebpageFeature`` by using the selenium Framework.

If you want to use this feature, you need to assign it to a setup device. The setup file itself, defines all the
devices you have in your test environment and adds the features to it in the same
way like it is done in the scenario, but with the setup-level implementation of the feature:

.. code-block:: python

    # file src/setups/setup_my.py

    import balder
    from lib import setup_features

    class SetupMy(balder.Setup):
        # also inherits directly from `balder.Device`
        class DeviceDoer(balder.Device):
            selenium = setup_features.SeleniumFeature()
            ...

        class OtherDevice(balder.Device):
            ...

        ...

.. note::
    Please note, that :class:`Setup` classes must be defined inside files that start with ``setup_*.py``. In
    addition their class name has to start with ``Setup*``. Otherwise the file will not be picked up by Balder.

You can implement more devices than in the scenario, Balder doesn't care. It will search for devices that match the
**requirement**, defined within the scenario. If the matching candidates have a matching connection-tree and if all
required features of a scenario-device are also implemented current considered setup-device, Balder will run the
scenario-testcases with this constellation as a new VARIATION!

.. note::
    Note that test methods have to be defined in scenario classes only. Setups don't support own test methods!

How does this work together?
============================

In order to understand Balder, it is really important to be clear about the meaning of scenarios and setups, which is
why we want to remind ourselves of this again:

**Scenario:** Describes what you need

**Setup:** Describes what you have

These are the golden rules, Balder works with.

You have to define a scenario, add some devices to it and instantiate
their feature objects as their class attributes. This describes what your testcase needs.

Then you think about **what you have**. How does your test rack or your test pc/pipeline look like? All this can be
defined in a setup. Add every device you have and implement your features for them. In the same way you have defined the
scenarios, you have to instantiate your implemented features in the setup devices.

Matching process
----------------

When Balder is executed and after it has collected all relevant classes, the matching process takes place. It
determines which device-mappings (between scenarios and setups) match with each other. For
that, Balder is interested in the feature sets your devices have. Based on these feature sets, Balder will automatically
determine the possible mappings between the :ref:`Scenario <Scenarios>`-Devices and the
:ref:`Setup <Setups>`-Devices.

Feature check
-------------

The first filter stage will remove all mapping candidates where one or more setup devices don't provide all features the
related scenario device has.

For example we have the following inheritance structure:

.. code-block:: none

    balder.Feature -> MyAbstractFeature1 -> MyFeature1
    balder.Feature -> MyAbstractFeature2 -> MyFeature2
    balder.Feature -> MyAbstractFeature3 -> MyFeature3

Now we have the follow matching candidates

.. code-block:: none

    ScenarioDevice:                 <=>     SetupDevice:
        MyAbstractFeature1()                    MyFeature1()
        MyAbstractFeature2()                    MyFeature2()

This would work because the ``MyFeature1`` is a subclass of ``MyAbstractFeature1`` and the ``MyFeature2`` is
a subclass of ``MyAbstractFeature2``.

The following example would also work, because the same features are allowed as well

.. code-block:: none

    ScenarioDevice:                 <=>     SetupDevice:
        MyFeature1()                            MyFeature1()
        MyAbstractFeature2()                    MyFeature2()

Now let's also take a look at an example that does not work:


.. code-block:: none

    ScenarioDevice:                 <=>     SetupDevice:
        MyAbstractFeature1()                    MyFeature1()
        MyAbstractFeature2()
                                                MyFeature3()

This wouldn't work because there is no feature in the setup, that implements the  ``MyAbstractFeature2()``!

What about having more features in the ``SetupDevice`` than in the ``ScenarioDevice``?

.. code-block:: none

    ScenarioDevice:                 <=>     SetupDevice:
        MyAbstractFeature1()                    MyFeature1()
                                                MyFeature2()
        MyAbstractFeature3()                    MyFeature3()

This would work, because we have an implementation for all scenario-level features. There is a equivalent subclass
within the ``SetupDevice`` for the ``MyAbstractFeature1`` and the ``MyAbstractFeature3``. Balder doesn't care, that the
scenario device doesn't provide a parent class for the ``MyFeature2``. For this current mapping, we are just not
interested in it. Remember, the scenario describes **what we need**, the setup describes **what we have**. If we have
more features implemented in our setup device, it is
okay and we are not interested in this for the current mapping. Maybe we will need it for another scenario within
another mapping later.

Connection Sub-Tree Check
-------------------------

The feature filter has already filtered the variation candidates for the most important criteria: If they have an
implementation for the required features.

Now Balder will also check how the devices are connected with each other. For this, Balder checks if the
connection-tree, that has been defined in the scenario, is contained in the connection tree, that has been defined
in the setup. This will be done for every connection between the matching devices.

If one of the variation candidates do not pass this check, because the scenario defined connection is not contained
within the setup defined connection between two devices of the current variation, the variation will be discarded and
not considered for execution.

Execution
=========

In the last step Balder will execute the mappings.

Executor Tree
-------------

When Balder determines valid variations during the resolving process, these variations will be added to the executor
tree. As soon as Balder enters the execution stage, this tree will be executed.

The tree runs trough the following levels:

.. code-block:: none

    | Construction SESSION Scope

        | Construction SETUP Scope `SetupMy`

            | Construction SCENARIO Scope `ScenarioMyOwn`

                | Construction VARIATION Scope `ScenarioMyOwn.ClientDevice:SetupMy.Client | ScenarioMyOwn.ServerDevice:SetupMy.Server`

                    | Construction TESTCASE Scope `ScenarioMyOwn.test_webpage`
                        | Run TESTCASE Scope `ScenarioMyOwn.test_webpage`
                    | Teardown TESTCASE Scope `ScenarioMyOwn.test_webpage`
                    ... further test cases of this variation
                | Teardown VARIATION Scope `ScenarioMyOwn.ClientDevice:SetupMy.Client | ScenarioMyOwn.ServerDevice:SetupMy.Server`
                ... further variations

            | Teardown SCENARIO Scope `ScenarioMyOwn`
            ... further scenarios of this setup

        | Teardown SETUP Scope `SetupMy`
        ... further setups

    | Teardown SESSION Scope

Feature Swap before Execution
-----------------------------

The "magic" occurs right before starting the CONSTRUCTION phase of a new variation. At this point, Balder swaps out
each abstract feature from the current scenario with a matching feature from the setup level. This setup feature
contains the actual code needed for the specific variation that's about to run.

In our example, Balder looks at the ``ScenarioMyOwn.ClientDevice`` class. It goes through each feature instance one
by one and replaces the abstract scenario-level feature with its corresponding setup-level version (which is a subclass
of it). For instance, it swaps the ``OpenAWebpageFeature()`` assigned to ``ScenarioMyOwn.ClientDevice.webpage`` with
the equivalent ``SeleniumFeature()`` instance from ``SetupMy.DeviceDoer.selenium``.

.. code-block:: python

    # file src/setups/setup_my.py

    import balder
    from lib import setup_features

    class SetupMy(balder.Setup):
        # also inherits directly from `balder.Device`
        class DeviceDoer(balder.Device):
            selenium = setup_features.SeleniumFeature()
            ...

        class OtherDevice(balder.Device):
            ...

        ...

.. code-block:: python

    import balder
    from lib import scenario_features
    ...

    class ScenarioMyOwn(balder.Scenario):
        ...
        class ClientDevice(balder.Device):
            webpage = scenario_features.OpenAWebpageFeature()

        class ServerDevice(balder.Device):
            provider = scenario_features.ProvideWebpageFeature()

As soon as the Construction-Part of a Variation is entered, every class attribute of a device holds the related
setup-level feature instance. So in our example, the ``ClientDevice.webpage`` holds the selenium implementation
``setup_features.SeleniumFeature`` and we can execute its implemented methods.

This will be done equivalent for all scenario-level feature instances that are assigned to scenario devices.

Of course Balder will rollback this afterwards, as soon as the teardown code of the variation was finished.

Run
---

You can execute Balder, by simply calling it inside the project
directory:

.. code-block:: none

    $ balder

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.5 (default, Nov 23 2021, 15:27:38) [GCC 9.3.0] | balder version 0.1.0b5                          |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 1 Scenarios
      resolve them to 1 mapping candidates

    ================================================== START TESTSESSION ===================================================
    SETUP SetupMy
      SCENARIO ScenarioMyOwn
        VARIATION ScenarioMyOwn.ClientDevice:SetupMy.Client | ScenarioMyOwn.ServerDevice:SetupMy.Server
          TEST ScenarioMyOwn.test_webpage [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 1 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0

Balder automatically detects valid variations between every scenario and the existing setups. For every mapping all
tests of the scenario will be executed.
