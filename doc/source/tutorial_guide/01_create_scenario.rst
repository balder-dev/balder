Part 1: Develop a scenario
**************************

First of all we have to think about the test scenarios we want to create for such a login app. There are a lot of
different aspects, that should be tested. For example scenarios for login are required, that expects a valid username
and also an invalid. The same procedure for passwords. We could test the registration process, while checking if all
required fields have to be given to create a valid account and also check if this newly created account works then. What
happens if we try to reset the password. Do we get a mail and does the reset process works as expected? You can see,
that there are a lot of different tests that should be created here.

Let's begin with the typical situation of a client and server. The server offers a login page and an exclusive section
that requires authentication from the client before accessing it. Once authenticated, the client can enter this secure
area and is also able to logs out itself.

Our test should look like the following:

* check that we have no access to the internal page
* insert a valid username
* insert a valid password
* press submit
* check that we have access to the internal page
* logout
* check that we have no access to the internal page

With this test we ensure, that it is possible to login with a valid username and a valid password. Then we can
access the internal page and also check that we can logout again.

Sounds nice, so let's do it.

Create the new scenario
-----------------------

First of all we create a new file in our scenario submodule ``tests/scenarios/scenario_simple_loginout.py``. It is
required, that the file name starts with ``scenario_*``, because Balder only collects this files while it searches for
scenario files.

In this newly created file, we have to create a new :class:`Scenario` class:

.. code-block:: python

    import balder

    class ScenarioSimpleLoginOut(balder.Scenario):
        ...

You can name your class as you like, but it has to begin with ``Scenario*`` and has to inherit from the global Balder
class :class:`balder.Scenario`.

Add a new test method
---------------------

Now we also want to add a test method in our newly created ``ScenarioSimpleLoginOut``. For this we have to add a method,
that starts with ``test_*``.

.. code-block:: python

    import balder

    class ScenarioSimpleLoginOut(balder.Scenario):

        def test_valid_login_logout(self):
            pass

This is all. Now we have a valid scenario with an valid test method, but of course it still doesn't do something.
Before we can start to write our testcode, we have to create our devices.

Add our devices
---------------

Devices are special test scenario members. In our case we will have a device, that represents the server or the
interface to the backend itself and a device that represents the client, which tries to login.

So we add these two devices. We call them ``ServerDevice`` and ``ClientDevice``.

.. code-block:: python

    import balder

    class ScenarioSimpleLoginOut(balder.Scenario):

        class ServerDevice(balder.Device):
            pass

        class ClientDevice(balder.Device):
            pass

        def test_valid_login_logout(self):
            pass

The device classes are always inner-classes of the scenario class, that uses the devices. In addition, they must inherit
from :class:`balder.Device`.

Connect the devices
-------------------

Now we have two devices which has no relationship to each other. But in the real world, we have a relationship here.
Both devices should be connected over a :class:`HttpConnection`.

.. note::
    This is the first stage we can think about to create a more generic scenario, because the two devices can be
    connected in every possible way to do an login process. You can also login over an :class:`SerialConnection` or
    over a :class:`BluetoothConnection`. But for now we can use this :class:`HttpConnection`, we come back to this
    generalization mechanism later.

To connect two devices you can simply use the ``@balder.connect()`` decorator:

.. code-block:: python

    import balder
    import balder.connections as conn

    class ScenarioSimpleLoginOut(balder.Scenario):

        class ServerDevice(balder.Device):
            pass

        @balder.connect(ServerDevice, conn.HttpConnection)
        class ClientDevice(balder.Device):
            pass

        def test_valid_login_logout(self):
            pass

.. note::
    Often it is easier to create the decorator on the second mentioned device, because python knows the reference only
    to the devices that are defined above. As an alternative Balder also supports the mentioning of the other device
    with a string reference. The following code is the same like the statement before:

    .. code-block:: python

        class ScenarioSimpleLoginOut(balder.Scenario):

            @balder.connect("ClientDevice", conn.HttpConnection)
            class ServerDevice(balder.Device):
                pass

            class ClientDevice(balder.Device):
                pass

            def test_valid_login_logout(self):
                pass

.. note::
    Please note, that Balder currently only supports bidirectional connections. The support for non-bidirectional
    connections will be added in a later version of Balder.

Think about device features
---------------------------

With that we have created our scenario environment. We know which devices we need and how they are connected with each
other. But till now, these devices can not do something. They still have no functionality. We have to add some features
to them.

So think about which features we need. Our server has to provide an address, we can connect with and a feature that
provides the backend. On the other side our client needs the functionality to connect with the server and send requests
to it.

So let us introduce some features:

* ``HasLoginSystemFeature``: this feature defines that the owner has a system where it is possible to connect with
* ``ValidRegisteredUserFeature``: this feature describes a user that is already registered in the backend system

In addition to that we also need some features for our client device:

* ``InsertCredentialsFeature``: this feature defines that the owner can login and logout to the backend of another
  device
* ``ViewInternalPageFeature``: this feature defines that the owner can access the internal page of another device


Often it can be easier if we just write down, how we want to structure our scenario. For this just instantiate our
future feature classes inside our ``ScenarioSimpleLoginOut`` devices, even though we have not defined the feature
classes yet. We will add the necessary implementations and imports later.

.. code-block:: python

    import balder
    import balder.connections as conn

    class ScenarioSimpleLoginOut(balder.Scenario):

        class ServerDevice(balder.Device):
            _autonomous = HasLoginSystemFeature()
            user_credential = ValidRegisteredUserFeature()

        @balder.connect(ServerDevice, conn.HttpConnection)
        class ClientDevice(balder.Device):
            login_out = InsertCredentialsFeature(server=ServerDevice)
            internal_page = ViewInternalPageFeature(server=ServerDevice)

        def test_valid_login_logout(self):
            pass

As you can see you can simply add :class:`Feature` classes to devices by instantiating and assigning them as class
attributes.

.. note::
    Note that we have not defined the feature classes itself yet, but we have already instantiate it in the device
    classes. This helps us to think clearer about the required feature methods we need later. If you like it in an other
    order and first want to define the feature classes, of course you can firstly create the features too.

We have added the ``HasLoginSystemFeature`` with the attribute name ``_autonomous``, that describes an
:ref:`Autonomous-Features`. This naming is not mandatory but recommended, because it has no properties or method you can
use. In short term an autonomous feature describes a feature that only identifies its owner with some functionality but
doesn't really provide methods. You can think about it as an property the device has, but you can not interact with it.
You can read more about autonomous features :ref:`here <Autonomous-Features>`.

We are also able to define the imports for now even if we do not have the feature class definition yet. We will
implement all scenario features in our ``lib.features`` submodule that we have created before. So let us add the
imports for all of our features:

.. code-block:: python

    import balder
    import balder.connections as conn
    from ..lib.features import HasLoginSystemFeature, ValidRegisteredUserFeature, InsertCredentialsFeature, ViewInternalPageFeature

    class ScenarioSimpleLoginOut(balder.Scenario):

        class ServerDevice(balder.Device):
            _autonomous = HasLoginSystemFeature()
            user_credential = ValidRegisteredUserFeature()

        @balder.connect(ServerDevice, conn.HttpConnection)
        class ClientDevice(balder.Device):
            login_out = InsertCredentialsFeature(server="ServerDevice")
            internal_page = ViewInternalPageFeature(server="ServerDevice")

        def test_valid_login_logout(self):
            pass

Maybe you recognized the constructor argument ``server=ServerDevice`` for the ``InsertCredentialsFeature`` and the
``ViewInternalPageFeature``. This is a so called :ref:`VDevice mapping <VDevices and method-variations>`. We will need
that for getting some server data without giving it over method arguments. It is quite enough to have the knowledge
that such a thing exists. We will dive a little deeper into this later.

Write the testcase
------------------

Writing tests freestyle is often the most comfortable way to go about it. After the test is written, we can then add
the used feature classes and methods later on. This helps streamline the writing process, making it easier to get the
test down.

So let's do it. Let us go back and read our scenario again:

* check that we have no access to the internal page
* insert a valid username
* insert a valid password
* press submit
* check that we have access to the internal page
* logout
* check that we have no access to the internal page

With this we now create the code for our test method:

**Check that we have no access to the internal page:**

.. code-block:: python

    # secure that we are not logged in
    assert not self.ClientDevice.internal_page.check_internal_page_viewable(), \
        "can access internal data before user is logged in"

**insert a valid username + password and press submit:**

.. code-block:: python

    # get example user with a valid username and password
    username, password = self.ServerDevice.user_credential.get_user()

    # insert the user data and execute the login command
    self.ClientDevice.login_out.insert_username(username)
    self.ClientDevice.login_out.insert_password(password)
    assert self.ClientDevice.login_out.execute_login(), \
        "login does not work"


**check that we have access to the internal page:**

.. code-block:: python

    # check that the internal page is viewable
    assert self.ClientDevice.internal_page.check_internal_page_viewable(), \
        "can not access internal data after login"

**logout:**

.. code-block:: python

    # now log out user
    assert self.ClientDevice.login_out.execute_logout(), \
        "logout does not work"

**check that we have no access to the internal page:**

.. code-block:: python

    # check that we can not access the internal page after user is logged out
    assert not self.ClientDevice.internal_page.check_internal_page_viewable(), \
        "can access internal data after user was logged out"

The final scenario
------------------

Now let's take a look how the full scenario looks like. For this we take a look at the complete code.

.. code-block:: python

    import balder
    import balder.connections as conn
    from ..lib.features import HasLoginSystemFeature, ValidRegisteredUserFeature, InsertCredentialsFeature, ViewInternalPageFeature

    class ScenarioSimpleLoginOut(balder.Scenario):

        class ServerDevice(balder.Device):
            _autonomous = HasLoginSystemFeature()
            user_credential = ValidRegisteredUserFeature()

        @balder.connect(ServerDevice, conn.HttpConnection)
        class ClientDevice(balder.Device):
            login_out = InsertCredentialsFeature(server="ServerDevice")
            internal_page = ViewInternalPageFeature(server="ServerDevice")

        def test_valid_login_logout(self):
            # secure that we are not logged in
            assert not self.ClientDevice.internal_page.check_internal_page_viewable(), \
                "can access internal data before user is logged in"

            # get example user with a valid username and password
            username, password = self.ServerDevice.user_credential.get_user()

            # insert the user data and execute the login command
            self.ClientDevice.login_out.insert_username(username)
            self.ClientDevice.login_out.insert_password(password)
            assert self.ClientDevice.login_out.execute_login(), \
                "login does not work"

            # check that the internal page is viewable
            assert self.ClientDevice.internal_page.check_internal_page_viewable(), \
                "can not access internal data after login"

            # now log out user
            assert self.ClientDevice.login_out.execute_logout(), \
                "logout does not work"

            # check that we can not access the internal page after user is logged out
            assert not self.ClientDevice.internal_page.check_internal_page_viewable(), \
                "can access internal data after user was logged out"

That was it. This is the complete scenario code for testing a general authentication process. But for now
we don't have a real implementation for all the feature methods. So let us go to define them too.


Define the features
-------------------

We have already imported the features from our submodule ``test.lib.features``. Now we want to add them in these module
too:

.. code-block:: python

    # file tests/lib/features.py

    import balder

    class HasLoginSystemFeature(balder.Feature):
        pass

    class ValidRegisteredUserFeature(balder.Feature):
        pass

    class InsertCredentialsFeature(balder.Feature):
        pass

    class ViewInternalPageFeature(balder.Feature):
        pass


We can add our previously used methods here too:


.. code-block:: python

    # file tests/lib/features.py

    import balder


    class HasLoginSystemFeature(balder.Feature):
        pass


    class ValidRegisteredUserFeature(balder.Feature):

        def get_user() -> Tuple[str, str]:
            raise NotImplementedError("this method has to be implemented on setup level")


    class InsertCredentialsFeature(balder.Feature):

        class Server(balder.VDevice):
            # our vDevice we have mapped earlier (we will come back to this later) - it only
            #  instantiates the autonomous feature
            _ = HasLoginSystemFeature()

        def insert_username(self, username: str):
            raise NotImplementedError("this method has to be implemented on setup level")

        def insert_password(self, password: str):
            raise NotImplementedError("this method has to be implemented on setup level")

        def execute_login(self) -> bool:
            raise NotImplementedError("this method has to be implemented on setup level")


        def execute_logout(self) -> bool:
            raise NotImplementedError("this method has to be implemented on setup level")



    class ViewInternalPageFeature(balder.Feature):

        class Server(balder.VDevice):
            # our vDevice we have mapped earlier (we will come back to this later) - it only
            #  instantiates the autonomous feature
            _ = HasLoginSystemFeature()

        def check_internal_page_viewable(self) -> bool:
            raise NotImplementedError("this method has to be implemented on setup level")


When creating scenarios, it is often the case that only the interfaces are provided and not the implementation, as the
implementation depends heavily on the real setup. In these cases, we typically add abstract methods and properties.
However, it is still possible to provide some implementations in certain scenarios. The same applies here, which is why
we make our methods abstract by adding ``NotImplementedError`` everywhere.

.. note::
    If you are writing BalderHub projects or if you are creating common scenarios that are used from other people
    it is highly recommended to add nice comments of all the classes and methods. In addition to that it is highly
    recommended to use type definitions. This makes the code more readable and nice structured. If you take a look in
    the example of this code in the
    `balder github repository <https://github.com/balder-dev/balderexample-loginserver/tree/single-setup>`_
    you find these comments and type definitions, for the sake of clarity, however, we have not done it here in the
    example code.

Now we have successfully implemented the scenario. In the next session we will add a setup and execute Balder the first
time.