Main Balder components
**********************

The following section should help getting an overview over the available components in Balder. You will learn the key
facts about :ref:`Scenarios` and :ref:`Setups` and how their :ref:`Devices` work. You will learn what
:ref:`Features` are and how Balder matches these between :ref:`Scenarios` and :ref:`Setups`. You will also learn how to
connect devices with each other over :ref:`Connections` and how :ref:`connection trees` are defined.

Note that this section only provides an overview of the components. You can find a detailed description of each
element in the :ref:`Basic Guide <Basic Guides>`.

Difference setup and scenario
=============================

The basis of Balder is based on individual scenarios and setups that are in a fixed relationship to each other.
Scenarios define a situation under which individual tests are carried out. Setups, on the other hand, describe how a
test environment currently looks like. Two of the most important statements in Balder are:

**Scenario:** Describes what you need

**Setup:** Describes what you have

So what does this mean? Take a closer look into these definitions.

Scenario: Describes what you need
---------------------------------

A :ref:`Scenario <Scenarios>` always defines what **you need**. So for example if you want to test an online login on a
server, you need the server and a client device that tries to connect to the server device. These are the components of
a :ref:`Scenario <Scenarios>`. It describes what you need. In this case all other devices that are connected with the
network don't matter.

Setup: Describes what you have
------------------------------

It is different when we look at the :ref:`Setups`. In a setup you define everything that is available and
relevant in the environment, the particular setup is for. So for example, if you have your computer, the router and the
server of company X in your influenceable spectrum of devices you can add all of them to your setup. Also if the
scenario is written later only for the router and the server, it will work out, because Balder will automatically match
scenario-devices with compatible setup-devices.

What are devices?
=================

A device can be a component of a :ref:`Setup <Setups>` or of a :ref:`Scenario <Scenarios>`. In generally it describes
a container object, which represents a test component, an application or a real physically device. Generally, a device
can be everything which has functionality.

In Balder, devices are inner-classes of :ref:`Setups` or :ref:`Scenarios`. These classes have class properties that
describe instantiated feature classes (later more). This easily allows you to use these features
by referencing the :ref:`Setup <Setups>` or :ref:`Scenario <Scenarios>` devices in your test. You can access the
properties with ``self.MyDevice.*``.

.. note::
    Note that a device itself never implements something by itself! A device should only have class-attributes which
    hold an instantiated :ref:`Feature <Features>` object. More about this later on.

Functionality = Feature
-----------------------

A device is a collection of so called :ref:`Features`. Every feature stands for a functionality the device has. So for
example a **BrowserDevice** can have ``OpenAWebpageFeature()``, which describes the functionality to interact with a
website. It does not provide the site itself. The website should be provided over another **ServerDevice**
which uses something like a ``ProvideWebpageFeature()``.

In Balder you have to define scenario-devices similar to the following example code:

.. code-block:: python

    class ScenarioMyOwn(balder.Scenario):
        ...
        class BrowserDevice(balder.Device):
            webpage = OpenAWebpageFeature()

        class ServerDevice(balder.Device):
            provider = ProvideWebpageFeature()
        ...
        # you could use the device in a testcase
        def test_webpage(self):
            addr = self.ServerDevice.provider.get_address()
            ...

.. note::
    Please note, that :class:`Scenario` classes must be defined inside files that start with `scenario_*.py`. In
    addition their class name has to start with `Scenario*`. Otherwise the file will not be picked up by Balder.


How to connect devices
======================

In the real world, devices are connected with each other. If you have a **BrowserDevice** and a **ServerDevice** like
mentioned before, you could expect that these are connected with each other over something like a HTTP connection. For
this, Balder provides :ref:`Connections`.

Simple connections
------------------

Balder is shipped with a lot of different connections (see :ref:`Connections API`). In addition, you can create your
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
This is really simple, because Balder provides a decorator ``connect(..)`` here. If you want to connect the two devices
``BrowserDevice`` and ``ServerDevice`` with each other, you can do the following:

.. code-block:: python

    import balder

    class ScenarioMyOwn(balder.Scenario):
        ...
        class BrowserDevice(balder.Device):
            ...

        @balder.connect(BrowserDevice, over_connection=HttpConnection.based_on(IpV4Connection))
        class ServerDevice(balder.Device):
            ...

It works the same way in setups.

How setups work?
================

So far we have defined the so-called scenario level (**what we need**). But of course we also have to define the actual
real environment that we have. For this we use the :class:`Setup` classes.

As mentioned earlier, **Setups always describe what you have**! Similar to :ref:`Scenarios` you define all your devices
and add features to it. But here you can define everything you have or you want to use in the testenvironment. Balder
will automatically determine (based on the feature set and the connections between the devices) in which constellation
a scenario will fit to a setup.

Implement features
------------------

Often scenario-features don't provide the whole implementation. In most cases, these features are abstract
and a user specific implementation has to be provided on setup level (means, in a child feature that is instantiated
inside a setup devices). For this, you can add a new module `features_setup.py` into the `setups` directory, that
provides the specific setup level features:

.. code-block:: none

    |- tests/
        |- scenarios/
            |- ...
        |- setups/
            |- features_setup.py
            |- setup_my.py
            |- ...

.. note::
    Balder is not interested in where you implement the feature objects. Feel free to use your own structure, but be
    careful, where you save your files you want to reuse. Without a clear structure this can be a little bit confusing.

.. note::
    If you have many features you can also use a python module. For this you create a directory with the name
    ``features_setup`` and add a ``__init__.py`` file in it.

    .. code-block:: none

        |- tests/
            |- scenarios/
                |- ...
            |- setups/
                |- features_setup/
                    |- __init__.py
                    |- my_example_feature.py
                    |- ..
                |- setup_my.py
                |- ...

    Here you can implement many files in it, which allows you to separate the features a little bit.

How does Balder know, which feature you are implementing?
---------------------------------------------------------

Maybe you ask yourself how Balder knows which scenario-feature you are implementing in your setup. For this Balder
uses **Inheritance**!

The scenario-features often implement abstract properties or methods. You can implement them easily by overwriting them.

The file ``features_setup.py`` for example could have the following content:

.. code-block:: python

    # file tests/setups/features_setups.py

    # import from global lib - has the abstract feature that is directly used in scenario-device
    from ..lib import MyAbstractExampleFeature

    class MyExampleFeature(MyAbstractExampleFeature):

        def do_it(self):
            print("I do it")

The setup file itself, defines all the devices you have in your testsystem and adds the features to it in the same way
like it is done in the scenario, but of course with the subclass, that really provides the implementation:

.. code-block:: python

    # file tests/setups/setup_my.py

    # import from setup feature file
    import balder
    from .features_setup import MyExampleFeature

    class SetupMy(balder.Setup):
        # also inherits directly from `balder.Device`
        class DeviceDoer(balder.Device):
            example = MyExampleFeature()
            ...

        class OtherDevice(balder.Device):
            ...

        ...

.. note::
    Please note, that :class:`Setup` classes must be defined inside files that start with `setup_*.py`. In
    addition their class name has to start with `Setup*`. Otherwise the file will not be picked up by Balder.

You can implement more devices than in the scenario, Balder doesn't care. It will search for devices that match the
**requirement**, defined in scenario. If the matching candidates have a matching connection-tree and if all required
features of a scenario-device are also implemented in the setup-device, Balder will run the scenario-testcases with this
constellation!

.. note::
    Note that test methods have to be defined in scenario classes only. Setups don't support own test methods!

How does this work together?
============================

It is really important to know the difference, so we want to repeat it again. The most important differences
between scenarios and setups are:

**Scenario:** Describes what you need

**Setup:** Describes what you have

These are the golden rules, Balder works with. After you have defined a scenario, add some devices to it and instantiate
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

Generally, Balder will create matching candidates by searching possible mappings of a scenario device with one of
the available setup devices. In this stage Balder does not care if the devices are compatible.

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
        MyAbstractFeature2()                    MyFeature3()

This would not work because there is no feature in the setup, that implements the  ``MyAbstractFeature2()``!

What about having more features in the ``SetupDevice`` than in the ``ScenarioDevice``?

.. code-block:: none

    ScenarioDevice:                 <=>     SetupDevice:
        MyAbstractFeature1()                    MyFeature1()
                                                MyFeature2()
        MyAbstractFeature3()                    MyFeature3()

This would work, because we have an implementation for ``MyAbstractFeature1`` and for ``MyAbstractFeature3`` in the
``SetupDevice``. It is not important that the scenario device doesn't provide a parent class for the ``MyFeature2`` of
the ``SetupDevice``. For this current mapping, we are not interested in it. Remember, the scenario describes
**what we need**, the setup describes **what we have**. If we have more features implemented in our setup device, it is
ok and we are not interested in this for the current mapping. Maybe we will need it in another mapping with another
scenario later.

Connection Sub-Tree Check
-------------------------

With the feature filter we have already filtered a lot of candidates. Now we are interested how the devices are
connected with each other. For this, we check if the connection-tree, that has been defined in the scenario, is
contained in the connection tree, that has been defined in the setup. This will be done for every connection between
the matching devices. Every matching with one or more device-connection that does not pass this, will be filtered.

Execution
=========

In the last step Balder will execute the mappings. You can execute Balder, by simply calling it inside the project
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
