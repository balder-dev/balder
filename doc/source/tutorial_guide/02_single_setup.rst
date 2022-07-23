Part 2: Implement Browser Setup
*******************************

Before we start to implement our first setup, let's take a look to the login-page. If you
:ref:`start the development server <Start development server>` and open the login page with a browser of your choice
you will see the login page.

.. image:: ../_static/balderexample-loginserver-login.png

We want to create a setup that allows to test this login screen now.

Install mechanize
=================

We need a package that allows us to control a Browser window. For this we use the
`python package mechanize <https://mechanize.readthedocs.io/en/latest/>`_, which is a stateful programmatic web browsing
python package, that allows to fill simple forms and clicking links of a html page.

We can simply install the python package with the command:

.. code-block::

    >>> pip install mechanize

Create the new setup
====================

We want to create a setup for our scenario that allows us to login over the mentioned web interface. First we have to
create a new module `setups`. This can be done, by creating a new directory ``setups`` and add a ``__init__``
file into it. In this directory we also add our new setup file ``setup_web_browser.py``. This results in the following
new directory structure:

.. code-block:: none

    - balderexample-loginserver/
        |- ...
        |- tests
            |- lib
                |- __init__.py
                |- features.py
                |- connections.py
            |- scenarios
                |- __init__.py
                |- scenario_simple_loginout.py
            |- setups
                |- __init__.py
                |- setup_web_browser.py

We can now create the initial setup class in our newly created file:

.. code-block:: python

    # file tests/setups/setup_web_browser.py
    import balder

    class SetupWebBrowser(balder.Setup):

        pass

We want to create a setup, that matches with our scenario, we have created in
:ref:`part 1 <Part 1: Develop a Scenario>`. In our scenario we defined two devices we need for the execution. These two
devices are needed in our setup too.

Think about devices
-------------------

According to our developed scenario we have developed in :ref:`part 1 <Part 1: Develop a Scenario>`, we need two devices
that implements the following features.

``MechanizeClient``:

* ``InsertCredentialsFeature``
* ``ViewInternalPageFeature``


``Loginserver``:

* ``HasLoginSystemFeature`` (autonomous feature)
* ``ValidRegisteredUserFeature``

These features have to be available in our setup so that Balder allows our newly created ``SetupWebBrowser`` as matching
candidate for our scenario. Except for the ``HasLoginSystemFeature`` all other features are abstract features, that has
no implementation yet.

**Balder-Matching-Mechanism:**

In the solving process, balder searches all Setup <=> Scenario Mappings, that can be executed. For this the setup
candidate must have the same devices like in the scenario. This means, that every device candidate in the setup must
implement the features of the scenario device that is mapped to the setup device. Balder will try all combinations and
mark an mapping (further called a VARIATION) as applicable if every scenario device maps to the assigned setup device.
In addition to that, also the defined scenario-device-connections have to BE IN the related connections of the setup
devices.

Autonomous Feature
------------------

The autonomous feature ``HasLoginSystemFeature`` is a feature that doesn't contain some functional code, it simply
stands for a functionality the device has, but we do not interact with it. For example that the device has the
color red or in our case, that the device **has a login feature**. For this we have not to provide a special
implementation, we can simply add it to every device that has this feature.

You can find more about autonomous features :ref:`here <Autonomous-Features>`.

Abstract Features
-----------------

The most of our current feature implementations are abstract and has no implementation or at least have no complete
implementation. This is often the case for scenario features, because it simply can't be provided, because the scenario
simply does not know it. Imagine you want to test the reset functionality of something, how do you should know how the
"something" can be reset. You do not even know what something is.
So like in this example, these features often need an implementation in our setup area. Maybe we want to reuse the
features in a similar matter, so we organize them in a hierarchy structure within the setup directory.

For this we add a new file `features` in the `setups` directory:

.. code-block:: none

    - balderexample-loginserver/
        |- ...
        |- tests
            ...
            |- setups
                |- __init__.py
                |- features.py
                |- setup_web_browser.py

This newly created file ``features.py`` should contain our specific feature implementations for the browser controllable
login.

.. note::
    In :ref:`Part 3: Expand Setup Code` we will expand this and use real hierarchy structured setup-feature code,
    but for now this is quite sufficient.

Add the devices
---------------

In the same way we have developed our scenario in :ref:`part 1 <Part 1: Develop a Scenario>`, we add the features
before we really implement it. For an easier understanding, we use a simple name for the features we will overwrite in
our setup area. These features we will name in the way ``My<scenario-feature-name>``.

We will already add the import statement even if we don't have an implementation yet. Often this helps to get a clearer
imagine about the things we need. We will import these features from the setup feature file ``setups/features.py``, that
we have created recently.

``Loginserver``:

* ``HasLoginSystemFeature`` (autonomous feature, can be imported directly from SCENARIO-LEVEL lib folder)
* ``MyValidRegisteredUserFeature`` (specific setup feature)


``MechanizeClient``:

* ``MyInsertCredentialsFeature`` (specific setup feature)
* ``MyViewInternalPageFeature`` (specific setup feature)

We want to connect the two devices exactly in the same way as in the scenario. So we only use a simply
``HttpConnection``:


.. code-block:: python

    import balder
    # we can directly import the autonomous feature
    from ..lib.features import HasLoginSystemFeature
    # all new features has to be imported from the global setup feature file, where we will define them later
    from .features import MyValidRegisteredUserFeature, MyInsertCredentialsFeature, MyViewInternalPageFeature

    class SetupWebBrowser(balder.Setup):

        class Server(balder.Device):
            _ = HasLoginSystemFeature()
            valid_user = MyValidRegisteredUserFeature()

        @balder.connect(ServerDevice, conn.HttpConnection)
        class Client(balder.Device):
            credentials = MyInsertCredentialsFeature()
            internal = MyViewInternalPageFeature()

It is important that the devices also directly inherit from the basic balder device and not from the scenario device.
Balder manage this automatically. Balder doesn't really care for the device class, because it only exchange the
features of it, but does not change the device itself.

What's about the vDevices?
--------------------------

As you can see in our :ref:`scenario definition <Think about device features>`, we have used vDevices there. To
understand why we use them, let's recall the earlier used scenario code again. Our scenario devices looks like the
following:

.. code-block:: python

    import balder
    import balder.connections as conn

    class ScenarioSimpleLoginOut(balder.Scenario):

        class ServerDevice(balder.Device):
            ...

        @balder.connect(ServerDevice, conn.HttpConnection)
        class ClientDevice(balder.Device):
            login_out = InsertCredentialsFeature(Server=ServerDevice)
            ...

In the ``InsertCredentialsFeature`` constructor, that is used by the ``ClientDevice`` we have a mapping between the
vDevice ``Server`` and our real device ``ServerDevice``. A VDevice definition allows to define on FEATURE level, that
we need a connection to another device (from the device that currently implements the feature) which itself implements
some required features. So specially in our example you can see this feature definition in the feature
`InsertCredentialsFeature`:

.. code-block:: python

    # file tests/lib/features.py

    ...

    class InsertCredentialsFeature(balder.Feature):

        class Server(balder.VDevice):
            _ = HasLoginSystemFeature()

        ...

    ...

You can see that our mapped VDevice ``Server``, needs a connection to a device that minimum implements the
``HasLoginSystemFeature``. This would allow us, to also access this features of the device within our feature method.
However, since we have only an autonomous feature here the mapping will only be used to define that other device. It
simply doesn't make sense to use this feature without another device that provides this interface.


This VDevice-Device mapping also affects our setup, but we don't have to define the mapping again in the setup. It will
automatically secured by the device mapping algorithm.

.. note::
    You can use multiple vDevices with different feature requirements here too. Although we have not use this
    functionality here, it is an easy and powerful way to provide feature implementations for different types of
    applications. By specifying a mapping you definitely set, which vDevice you want to use for your setup/scenario.

.. note::
    It is also possible to assign a vDevice in the setup.

Implement the Setup-Features
============================

Now let us implement the different features we have already imported. Open the file ``setups/features.py`` and add the
basic code. Secure that you inherit from the parent classes of the scenario level. With inheritance balder secures that
a feature belongs to another. We also add the abstract methods, we have defined earlier that are filled with an
``NotImplementedError``. We will provide the full implementation of our methods there later:

.. code-block:: python

    import balder
    from ..lib.features import InsertCredentialsFeature, ViewInternalPageFeature, BrowserSessionManagerFeature, \
        ValidRegisteredUserFeature


    # Server Features
    class MyValidRegisteredUserFeature(ValidRegisteredUserFeature):
        def get_valid_user(self):
            pass

    # Client Features

    class MyInsertCredentialsFeature(InsertCredentialsFeature):

        class Server(InsertCredentialsFeature.Server):
            pass


        def insert_username(self, username):
            pass

        def insert_password(self, password):
            pass

        def execute_login(self):
            pass

        def execute_logout(self):
            pass


    class MyViewInternalPageFeature(ViewInternalPageFeature):

        class Server(ViewInternalPageFeature.Server):
            pass

        def check_internal_page_viewable(self):
            pass

As you can see, we have overwritten the internal empty vDevices here too, because we will add some more features there
later. You can add features to a vDevice by overwriting the inner class with the same name of the vDevice class and
inheriting from the next parent. This is done here for the features ``MyInsertCredentialsFeature`` and
``MyViewInternalPageFeature``.

Client Feature
--------------

We want to start with the method ``MyValidRegisteredUserFeature.get_user()``. This method should return a tuple with the
username and the password. According to the ``README.md`` file of the
`balderexample-loginserver repository <https://github.com/balder-dev/balder>`_,
the server provides static credentials:

Username: ``guest``
Password: ``guest12345``

We simply add a return statement with these values:

.. code-block:: python

    ...

    class MyValidRegisteredUserFeature(ValidRegisteredUserFeature):
        def get_user() -> Tuple[str, str]:
            return "guest", "guest12345"

    ...

That was easy, wasn't it? So lets get a little bit deeper.

Use shared features
-------------------

We have two features to implement, the ``MyInsertCredentialsFeature`` and the ``MyViewInternalPageFeature``. Both of
them will be used to access the loginserver over a browser window. To ensure access via the login area we must allow
cookies to be passed between webpage changes, for this we need one common browser object. The ``mechanize`` package
allows this with a so called browser object. To reuse cookies, of course we need the same ``Browser`` object for the
whole test session, but for us it seems hard to share this object between different feature instances. We also can not
add it to the constructor or something similar. But how can we share this? We can use a shared feature, that is added
as required feature to our both feature classes ``MyInsertCredentialsFeature`` and ``MyViewInternalPageFeature``.

.. note::
    We will add this shared feature only in setup code, which will lead to the fact that we can create other setups
    that do not implement our specific mechanize feature here.

Let's call this feature ``BrowserSessionManagerFeature``. It should completely manage this browser object and also
provide some methods, we can interact with.

We add this feature to our file ``setups/features.py`` too. Because this feature is new, we can directly inherit from
``balder.Feature`` and don't need some inheritance from the SCENARIO LEVEL:

.. code-block:: python

    class BrowserSessionManagerFeature(balder.Feature):
        # our mechanize browser object that simulates the browser
        browser = None

First of all we add a property ``browser``, which should be managed by some methods. Two methods are enough for our
application. We will add a method ``create_browser_if_necessary()`` which should create a browser only if there was no
browser object generated before and a method ``open_page()`` that opens a url. For the implementation we have to add
some simple mechanize code.

.. code-block:: python

    class BrowserSessionManagerFeature(balder.Feature):
        # our mechanize browser object that simulates the browser
        browser = None

        def create_browser_if_necessary(self):
            if self.browser is None:
                self.browser = mechanize.Browser()

        def open_page(self, open_page_url=None):
            return self.browser.open(open_page_url)

That's all. But how can we use this feature in our features ``MyInsertCredentialsFeature`` and
``MyViewInternalPageFeature``, that both needing access to it. That is really easy, simply instantiate it as static
class property in the features that want to use it. For example, this can look like the following code:

.. code-block:: python

    class MyViewInternalPageFeature(ViewInternalPageFeature):

        ...

        browser_manager = BrowserSessionManagerFeature()

This allows you to simply refer it from your methods. It also defines that every device that uses the feature
`MyViewInternalPageFeature` (by defining it as static attribute), has also implement the `BrowserSessionManagerFeature`.

Implement the client Setup-Features
-----------------------------------

As you may remember the setup features ``MyInsertCredentialsFeature`` and ``MyViewInternalPageFeature`` (which we still
have to implement) have a vDevice ``Server`` in our scenario implementation. But on this scenario level implementation,
the vDevice has only the one autonomous feature ``HasLoginSystemFeature``.
We have written it very universal, that allows that the scenario implementation is very flexible. But now on setup
level, we need some more information from our communication partner device that is mapped to the vDevice
``MyInsertCredentialsFeature.Server``.

Balder allows us to access these information by simply specifying the features that provide this info in our vDevice.
As mentioned earlier, we can overwrite a vDevice, by inheriting from the vDevice of the parent feature class **and**
give the same class name to the child vDevice class. We will add a new feature that should return some constant
values about the server, for example the webpage url.

.. code-block:: python

    class MyViewInternalPageFeature(ViewInternalPageFeature):

        class Server(ViewInternalPageFeature.Server):
            internal_webpage = InternalWebpageFeature()

        browser_manager = BrowserSessionManagerFeature()

        def check_internal_page_viewable(self):
            self.browser_manager.create_browser_if_necessary()
            self.browser_manager.open_page(self.Server.internal_webpage.url)
            if self.browser_manager.browser.title() != self.Server.internal_webpage.title:
                # redirect to another webpage -> not able to read the internal webpage
                return False
            return True

Similar to the normal device usage we can now use our vDevice feature property to access the data. Currently we have no
implementation for our feature ``InternalWebpageFeature``. We will implement it in a few moments.

.. note::
    Note that it is really important, that the child vDevice class has the same name that is given in the parent feature
    class! Otherwise the child vDevice will be interpreted as a new device! In this case this will produce an exception
    because balder only allows the redefining of inner devices by overwriting all on one class level.

We will do the same for the other feature:

.. code-block:: python

    class MyInsertCredentialsFeature(InsertCredentialsFeature):

        class Server(InsertCredentialsFeature.Server):
            login_webpage = LoginWebpageFeature()
            internal_webpage = InternalWebpageFeature()

        browser_manager = BrowserSessionManagerFeature()
        setup_done = False

        def do_setup_if_necessary(self):
            if not self.setup_done:
                self.browser_manager.create_browser_if_necessary()
                self.browser_manager.open_page(self.Server.login_webpage.url)
                self.setup_done = True

        def insert_username(self, username):
            self.do_setup_if_necessary()
            # now insert the username
            self.browser_manager.browser.select_form(name=self.Server.login_webpage.dom_name_login_form)
            self.browser_manager.browser[self.Server.login_webpage.dom_name_username_field] = username

        def insert_password(self, password):
            self.do_setup_if_necessary()
            # now insert the password
            self.browser_manager.browser.select_form(name=self.Server.login_webpage.dom_name_login_form)
            self.browser_manager.browser[self.Server.login_webpage.dom_name_password_field] = password

        def execute_login(self):
            response = self.browser_manager.browser.submit()
            return response.wrapped.code == 200

        def execute_logout(self):
            response = self.browser_manager.open_page(self.Server.internal_webpage.url_logout)
            return response.wrapped.code == 200

We will implement the newly created ``LoginWebpageFeature`` in the ``Server`` vDevice in the next stage.

The object has also a new method ``do_setup_if_necessary()``, which was not defined in the scenario version. Of course
you can expand it after the definition in the scenario too.

Implement the vDevice features
------------------------------

We have created some new features that we need specially for this setup, the ``LoginWebpageFeature`` and
``InternalWebpageFeature``. We only use some constants here. Let's define these features.

.. code-block:: python

    class LoginWebpageFeature(balder.Feature):
        @property
        def url(self):
            return "http://localhost:8000/accounts/login"

        @property
        def dom_name_login_form(self):
            return "login"

        @property
        def dom_name_username_field(self):
            return "username"

        @property
        def dom_name_password_field(self):
            return "password"


    class InternalWebpageFeature(balder.Feature):
        @property
        def url(self):
            return "http://localhost:8000"

        @property
        def title(self):
            return "Internal"

        @property
        def url_logout(self):
            return "http://localhost:8000/accounts/logout"


.. note::
    **We instantiate every feature multiple times, why do we think they are synchronized?**

    In the resolving process balder automatically exchange all objects with the original objects that were initialized
    in the setup. Everywhere! In all inner feature references (also feature properties that are other instantiated
    features), scenarios, vDevices and so on.

Update our setup
----------------

Our setup can not be resolved yet, because our server device does not have the vDevice features we have defined. For
this we have to add them.

Our new setup devices should implement the following:

.. code-block:: python

    import balder
    from tests.lib.features import HasLoginSystemFeature
    from tests.setups import features as setup_features

    class SetupWebBrowser(balder.Setup):

        class Server(balder.Device):
            _ = HasLoginSystemFeature()
            login_webpage = setup_features.LoginWebpageFeature()
            internal_webpage = setup_features.InternalWebpageFeature()
            valid_user = setup_features.MyValidRegisteredUserFeature()

        class Client(balder.Device):
            browser_manager = setup_features.BrowserSessionManagerFeature()
            credentials = setup_features.MyInsertCredentialsFeature()
            internal = setup_features.MyViewInternalPageFeature()



The whole setup and setup features
==================================

Done, we have successfully implement our setup. The whole code is shows below, but you can find the code
in the
`single-setup branch on GitHub <https://github.com/balder-dev/balderexample-loginserver/tree/single-setup>`_ too.

.. code-block:: python

    # file tests/setups/features.py
    import balder
    from ..lib.features import InsertCredentialsFeature, ViewInternalPageFeature, BrowserSessionManagerFeature, \
        ValidRegisteredUserFeature


    # Server Features
    class MyValidRegisteredUserFeature(ValidRegisteredUserFeature):
        def get_valid_user(self):
            return "guest", "guest12345"


    class LoginWebpageFeature(balder.Feature):
        @property
        def url(self):
            return "http://localhost:8000/accounts/login"

        @property
        def dom_name_login_form(self):
            return "login"

        @property
        def dom_name_username_field(self):
            return "username"

        @property
        def dom_name_password_field(self):
            return "password"


    class InternalWebpageFeature(balder.Feature):
        @property
        def url(self):
            return "http://localhost:8000"

        @property
        def title(self):
            return "Internal"

        @property
        def url_logout(self):
            return "http://localhost:8000/accounts/logout"


    # Client Features

    class MyInsertCredentialsFeature(InsertCredentialsFeature):
        class Server(InsertCredentialsFeature.Server):
            login_webpage = LoginWebpageFeature()
            internal_webpage = InternalWebpageFeature()

        browser_manager = BrowserSessionManagerFeature()
        setup_done = False

        def do_setup_if_necessary(self):
            if not self.setup_done:
                self.browser_manager.create_browser_if_necessary()
                self.browser_manager.open_page(self.Server.login_webpage.url)
                self.setup_done = True

        def insert_username(self, username):
            self.do_setup_if_necessary()
            # now insert the username
            self.browser_manager.browser.select_form(name=self.Server.login_webpage.dom_name_login_form)
            self.browser_manager.browser[self.Server.login_webpage.dom_name_username_field] = username

        def insert_password(self, password):
            self.do_setup_if_necessary()
            # now insert the password
            self.browser_manager.browser.select_form(name=self.Server.login_webpage.dom_name_login_form)
            self.browser_manager.browser[self.Server.login_webpage.dom_name_password_field] = password

        def execute_login(self):
            response = self.browser_manager.browser.submit()
            return response.wrapped.code == 200

        def execute_logout(self):
            response = self.browser_manager.open_page(self.Server.internal_webpage.url_logout)
            return response.wrapped.code == 200


    class MyViewInternalPageFeature(ViewInternalPageFeature):
        class Server(ViewInternalPageFeature.Server):
            internal_webpage = InternalWebpageFeature()

        browser_manager = BrowserSessionManagerFeature()

        def check_internal_page_viewable(self):
            self.browser_manager.create_browser_if_necessary()
            self.browser_manager.open_page(self.Server.internal_webpage.url)
            if self.browser_manager.browser.title() != self.Server.internal_webpage.title:
                # redirect to another webpage -> not able to read the internal webpage
                return False
            return True


.. code-block:: python

    # file tests/setups/setup_web_browser.py
    import balder
    from tests.lib.features import HasLoginSystemFeature
    from tests.setups import features as setup_features

    class SetupWebBrowser(balder.Setup):

        class Server(balder.Device):
            _ = HasLoginSystemFeature()
            login_webpage = setup_features.LoginWebpageFeature()
            internal_webpage = setup_features.InternalWebpageFeature()
            valid_user = setup_features.MyValidRegisteredUserFeature()

        class Client(balder.Device):
            browser_manager = setup_features.BrowserSessionManagerFeature()
            credentials = setup_features.MyInsertCredentialsFeature()
            internal = setup_features.MyViewInternalPageFeature()

Execute balder
==============

Now it is time to check if balder finds the match by executing balder. We have one setup and one scenario, while
the setup definition should match the scenario definition. We also expect, that balder will find exactly one matching.

Let's take a look how balder will resolve our project. For this you can simply execute the following command:

.. code-block:: none

    $ balder --working-dir tests --resolve-only

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.7 (default, Sep  3 2021, 12:37:55) [Clang 12.0.5 (clang-1205.0.22.9)] | balder version 0.0.1     |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 1 Scenarios
      resolve them to 1 mapping candidates

    RESOLVING OVERVIEW

    Scenario `ScenarioSimpleLoginOut` <-> Setup `SetupWebBrowser`
       ScenarioSimpleLoginOut.ClientDevice = SetupWebBrowser.Client
       ScenarioSimpleLoginOut.ServerDevice = SetupWebBrowser.Server
       -> Testcase<ScenarioSimpleLoginOut.test_valid_login_logout>


You can see how balder finds the mappings between the devices.

Now it is time to really run the balder session.

.. note::
    Do not forget to start the django server before:

    .. code-block:: none

        $ python manage.py runserver

After you have secured that the django server will be executed, you can start balder with the simple command:

.. code-block:: none

    $ balder --working-dir tests

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.5 (default, Nov 23 2021, 15:27:38) [GCC 9.3.0] | balder version 0.0.1                            |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 1 Scenarios
      resolve them to 1 mapping candidates

    ================================================== START TESTSESSION ===================================================
    SETUP SetupWebBrowser
      SCENARIO ScenarioSimpleLoginOut
        VARIATION ScenarioSimpleLoginOut.ClientDevice:SetupWebBrowser.Client | ScenarioSimpleLoginOut.ServerDevice:SetupWebBrowser.Server
          TEST ScenarioSimpleLoginOut.test_valid_login_logout [✓]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 1 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0


Congratulations! You have successfully created a Scenario and a suitable Setup for it.