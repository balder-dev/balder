Main Balder components
**********************

The following section should help getting an overview over the available components in balder. You will learn the key
facts about :ref:`Scenarios` and :ref:`Setups` and how their :ref:`Devices` work. You will learn what
:ref:`Features` are and how balder matches these between :ref:`Scenarios` and :ref:`Setups`. You will also learn how to
connect devices with each other over :ref:`Connections` and how :ref:`Connection-Trees` are defined.

Note that this section only provides an overview of the components. You can find a detailed description of each
element in the :ref:`Basic Guide <Basic Guides>`.

Difference Setup and Scenario
=============================

The basis of Balder is based on individual scenarios and setups that are in a fixed relationship to each other.
Scenarios define a situation under which individual tests are carried out. Setups, on the other hand, describe how a
test environment currently looks like. It is important that the following definition is understood:

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
scenario is written later only for the router and the server, it will work out, because balder will automatically match
these components.

What are devices?
=================

A device can be a component of a :ref:`Setup <Setups>` or of a :ref:`Scenario <Scenarios>`. In generally it describes
a container object, which represents a test component, for example a browser or a server.

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


How to connect devices
======================

In the real world, devices are connected with each other. If you have a **BrowserDevice** and a **ServerDevice** like
mentioned before, you could expect that these are connected with each other over something like a HTTP connection. For
this, Balder provides :ref:`Connections`.

Connection-Trees
----------------

Connections are represented as so called Connection-Trees. These trees describe a hierarchical structure, the connection
object types are arranged with each other.

You can define such a connection tree with the static method ``based_on(..)``:

.. code-block:: python

    HttpConnection.based_on(IpV4Connection)

This would determine the sub-tree of the global connection tree. In the standard balder configuration this is not the
complete resolved tree because there is a TcpConnection between it. Balder always determines the resolved version, which
would look like the following statement:

.. code-block:: python

    HttpConnection.based_on(TcpV4Connection.based_on(IpV4Connection))

But how does balder know this? Balder holds a inner representation of the whole connection tree. This tree describes
exactly how these connections are arranged among themselves. Balder always holds a default representation of this
global-connection-tree, but you can also define one by your own. For more information, take a look into the
:ref:`Connection-Trees` section.

The objects ``TcpV4Connection`` and ``IpV4Connection`` describes only IPv4 based connections. You can also create a
statement that supports IPv6, too. For this you can use the logical **OR**, balder uses for connections:

.. code-block:: python

    HttpConnection.based_on(
            TcpV4Connection.based_on(IpV4Connection),
            TcpV6Connection.based_on(IpV6Connection)
        )

In balder a logical **OR** is represented by a simple list or by multiple arguments. You can also provide **AND**
connections. For this you have to use tuples. Take a look at the following example, which describes that a
``DnsConnection`` needs a UDP and a TCP connection here:

.. code-block:: python

    DnsConnection.based_on(
            (UdpConnection, TcpConnection)
        )

If you want to use the definition for IpV4 and IpV6 here, you can also add an additional **OR** there too:

.. code-block:: python

    DnsConnection.based_on(
            (UdpV4Connection, TcpV4Connection),
            (UdpV6Connection, TcpV6Connection)
        )

This statement describes that the ``DnsConnection`` has to be based on ``UdpV4Connection`` and ``TcpV4Connection`` or on
``UdpV6Connection`` and ``TcpV6Connection``

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

As mentioned earlier, **Setups always describe what you have**! Similar to :ref:`Scenarios` you define all your devices
and add features to it. But here you can define everything you have or you want to use in the testenvironment. Balder
will automatically determine (based on the feature set and the connections between the features) in which constellation
a scenario will fit to a setup.

Implement features
------------------

Often features are provided that don't have the whole implementation. In most cases, these features are abstract and
a user specific implementation have to be provided for the setup devices. For this, you often add a new module
`features_setup.py` into the `setups` directory, so you can implement your specific features there:

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

How does balder know, which feature you are implementing?
---------------------------------------------------------

Maybe you ask yourself how balder knows which scenario-feature you are implementing in your setup. For this balder
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

You can implement more devices than in the scenario, balder doesn't care. It will search for devices that match the
**requirement**, defined in scenario. If the matching candidates have a matching connection-tree and if all required
features of a scenario-device are also implemented in the setup-device, balder will run the scenario-testcases with this
constellation!

.. note::
    Note that a setup can not provide own testcases!

How does this work together?
============================

It is really important to know the difference, so we want to repeat it again. The most important differences
between scenarios and setups are:

**Scenario:** Describes what you need

**Setup:** Describes what you have

These are the golden rules, balder works with. After you have defined a scenario, add some devices to it and instantiate
their feature objects as their class attributes. This describes what your testcase needs.

Then you think about **what you have**. How does your test rack or your test pc/pipeline look like? All this can be
defined in a setup. Add every device you have and implement your features for them. In the same way you have defined the
scenarios, you have to instantiate your implemented features in the setup devices.

After you have defined that, balder will create matchings.

Matching process
----------------

The matching process will determine which device-mappings (between scenarios and setups) match with each other. For
that, Balder is interested in the feature sets your devices have. Based on these feature sets, balder will automatically
determine the possible mappings between the :ref:`Scenario <Scenarios>`-Devices and the
:ref:`Setup <Setups>`-Devices.

Generally, Balder will create matching candidates by searching possible mappings of a scenario device with one of
the available setup devices. In this stage balder does not care if the devices are compatible.

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

What means contained in?
------------------------

Imagine, you have the following connection tree between two devices in the setup:

.. code-block:: python

    TcpConnection.based_on(WifiConnection)

Balder will first resolve the connection and fill all connection items that are defined between the connections.
The example will be resolved in the following resolved-tree:

.. code-block:: python

    # RESOLVED VERSION
    TcpConnection.based_on(IpConnection.based_on(WifiConnection))

To check if a matching candidate really works out, every scenario-device connection has to be **CONTAINED IN** the
related setup-device connection. Balder checks this by searching the expected smaller tree (so the scenario-device
connection) in the expected bigger tree (the related setup device connection). So the connection
``TcpConnection.based_on(IpConnection)`` for example is **CONTAINED IN** the setup connection
``TcpConnection.based_on(IpConnection.based_on(WifiConnection))`` from above. To check this, the connection always has
to be converted into the resolved version!

This whole concept supports complex sub-trees that are connected over **OR**  (multiple attributes) and **AND** (tuples)
connections. If you want to learn more about this, take a look at the :ref:`Basic: Connection <Connections>` section.

Execution
=========

In the last step balder will execute the mappings. For every mapping all tests of their related scenarios will be
executed.