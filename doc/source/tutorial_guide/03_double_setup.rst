Part 3: Expand setup code
*************************

In this part we are going to learn one of the key concepts of Balder - reusing tests.

This essential concept allows you to effortlessly utilize existing scenarios for various setups. Many projects require
similar testing in multiple ways, whether it's supporting a user interface on different platforms or managing a device
over several apps. Perhaps you need to test a bus system where every member must function identically. Balder was
designed precisely for this purpose.


There are a lot of different ways to expand our testing environment. If we have a new device, but inside the same
environment, we just need to add this device to the setup. If we just want to add a new feature to an already existing
device, we can just add it inside our setup. And of course, if we have a complete other environment, we can simply
create a complete new setup.

In this section, we'll add a new setup class.

How the all-in-one setup approach works is described in :ref:`Part 5: One common setup`.

So let's go back to our example and restructure our earlier created project a little bit.


Prepare for the new setup
=========================

In :ref:`part 2 <Part 2: Implement browser setup>` we have already implemented a setup for our login server, that uses
the web frontend to login to our internal page. Often we also need an API/REST interface to connect with internal
components. Our loginserver also supports this. We want to add a new setup for this method now.

First of all, think about the features we need for it.

Think about the devices
-----------------------

Similar to :ref:`part 2 <Part 2: Implement browser setup>` we could think about the required features we need for our
new setup class. If we go back to the scenario definition we need the following features:

``Loginserver``:

* ``HasLoginSystemFeature`` (autonomous feature)
* ``ValidRegisteredUserFeature``

``RestClient``

* ``InsertCredentialsFeature``
* ``ViewInternalPageFeature``

As you can see we need the same features like we have used earlier in our first setup. Of course we need the same one,
because we still have the same procedure. Similar to the webpage login, we need the procedure defined in
:ref:`part 1 <Part 1: Develop a scenario>`:

* check that we have no access to the internal page/data
* insert a valid username
* insert a valid password
* press submit/send request
* check that we have access to the internal page/data
* logout (over request)
* check that we have no access to the internal page/data

The procedure is the same, we only must do it a little bit different. With that we don't have to change the scenario and
also we can still use some similar setup features. So with the first step, we want to refactor our setup directory to
reuse some setup feature classes.

Refactor our setup directory
----------------------------

We want to sort our setup classes into individual directories. We create a new directory ``setups/browser`` and move
the ``setup_web_browser.py`` file into it. In addition to that we rename our ``setups/features.py`` file to
``setup_features.py``. For this changes, we have to update our import statements too. Our new refactored directory
should now looks like the following:

.. code-block:: none

    - balderexample-loginserver/
        |- ...
        |- tests
            ...
            |- setups
                |- browser
                    |- __init__.py
                    |- setup_web_browser.py
                |- __init__.py
                |- setup_features.py

Now we want to organize our features of the old setup. All features usable without a browser should be placed
in the ``setup_features.py`` file. All specific features that are implemented to test the login with the
browser should be placed in a separate feature file ``setups/browser/browser_features.py``.

So our new structure looks like the following:

.. code-block:: none

    - balderexample-loginserver/
        |- ...
        |- tests
            ...
            |- setups
                |- browser
                    |- __init__.py
                    |- browser_features.py
                    |- setup_web_browser.py
                |- __init__.py
                |- setup_features.py

.. note::
    As you can see, it could be helpful to organize your feature inside own namespace modules. Of course you can
    organize your project in the structure of your choice. You can also name it in the way you want,
    but it is highly recommended to use a name to easily distinguish the source of an imported setup. If you name every
    file ``features.py`` this can get really hard to understand, specially when you import from different directory
    levels, like it is showed below.

    .. code-block:: python

        from .features import X, Y
        from ..features import P, Z
        ...

    Its easier if you rename the files, like we have done above:

    .. code-block:: python

        from . import browser_features
        from .. import setup_features
        ...

        class SetupExample(balder.Setup):

            class Browser(balder.Device):
                glob = setup_features.GlobFeature()
                browser = browser_features.SpecialBrowserFeature()
                ...

So think about which features are global and which features are special browser features. If you take a look into
our file ``setup_features.py`` you should find the following features:

* ``MyValidRegisteredUserFeature``:  This feature provides the user credentials valid for the whole ``balderexample-loginserver``. The user is valid for all access strategies.
* ``LoginWebpageFeature``: This feature provides all specific data of the login front-end webpage.
* ``InternalWebpageFeature``: This feature provides all specific data of the internal front-end webpage.
* ``MyInsertCredentialsFeature``: This feature allows inserting credentials into a login system.
* ``MyViewInternalPageFeature``: This feature allows the owner device to interact with the internal area provided by the vDevice.

The first feature ``MyValidRegisteredUserFeature`` returns the global valid credentials to access the login area in
every possible way. This feature is not limited to the browser method, so we can left it in the higher file
``setups/setup_features.py``. All the other features, however, are specific, so we move them to the browser specific
file ``setups/browser/setup_web_browser.py``.

Implement the REST setup
========================

Ok so we have redesigned our environment now. It is time to add a new setup. The ``balderexample-loginserver`` package
also provides a REST api, that allows us to request all existing users, but of course only if we are logged in.

We want to create a setup that allows us to request all registered users. For this we can ask the
endpoint ``/api/users``. But this endpoint contains sensitive data, so it is behind an authentication system. Our
server uses a standard authentication system ``Basic Authentication`` that requires the same username and password as
credentials, we also have used in the browser setup before. We can use the python library ``requests``, which
allows us easily to execute a GET request with ``Basic Authentication``.

Install requests
----------------

For testing our API, we use the python package ``requests``. Make sure that you have installed it.

.. code-block::

    >>> pip install requests

Add the new file
----------------

First of all, we want to create the new file. We are adhering to our new structure and add a new module in our
setup directory first. We can name it ``setups/rest``. There we add a new file ``rest_features.py`` for our rest
specific features and a new ``setup_rest_basicauth.py``, which will contain our setup implementation. Our directory
should look like the following:

.. code-block:: none

    - balderexample-loginserver/
        |- ...
        |- tests
            ...
            |- setups
                |- browser
                    |- __init__.py
                    |- browser_features.py
                    |- setup_web_browser.py
                |- rest
                    |- __init__.py
                    |- rest_features.py
                    |- setup_rest_basicauth.py
                |- __init__.py
                |- setup_features.py

Similar to :ref:`part 2 <Part 2: Implement browser setup>` we first define our new setup with the devices and all
imported features. Again we want to create two devices, one server devices that provides the rest api and one rest
client device, that executes the requests with the basic authentication.

Similar to the first setup, we name the features in a format ``My<scenario feature name>``. We will import them all from
our new specific rest file ``setups/rest/rest_features.py``, except for our ``MyValidRegisteredUserFeature``, which we
have already moved in the common setup-feature file ``setups/setup_features.py``.

Our setup file will look like:

.. code-block:: python

    import balder
    from balder.connections import HttpConnection
    from tests.lib.features import HasLoginSystemFeature
    from tests.setups import setup_features
    from tests.setups.rest import rest_features


    class SetupRestBasicAuth(balder.Setup):

        class Server(balder.Device):
            # the autonomous feature can be imported directly
            _ = HasLoginSystemFeature()
            # we have imported it from our common setup-feature file
            valid_user = setup_features.MyValidRegisteredUserFeature()

        @balder.connect(Server, HttpConnection)
        class Client(balder.Device):
            # all of the following files are rest specific files - these are imported from the specific feature file
            credentials = rest_features.MyInsertCredentialsFeature()
            internal = rest_features.MyViewInternalPageFeature()


Add the REST specific features
------------------------------

We have added two features that requires a own REST specific implementation. Let us add these features in the file:

.. code-block:: python

    import balder
    from ...lib.features import InsertCredentialsFeature, ViewInternalPageFeature

    # Client features
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

As you can see, we have also overwritten the vDevice instances, because we will need them in this features too.
Similar to the :ref:`part 2 <Part 2: Implement browser setup>` we need a common feature that provides access to our api
endpoint. Even though we don't really have a login area here, but actually send the access data with each request, we
want to set up the whole thing similarly.

The shared REST feature with basic auth support
-----------------------------------------------

Let us add a common feature ``BasicAuthManager`` to our global ``lib.features`` module. It should provide some helper
methods that allow us to set the credentials and also should provide a method allowing us to request an endpoint.
Depending on whether a username/password is specified, the request is done with basic authentication. The implementation
can look like the following code:

.. code-block:: python

    class BasicAuthManager(balder.Feature):
        username = None
        password = None

        def set_credentials(self, username, password):
            self.username = username
            self.password = password

        def reset_credentials(self):
            self.username = None
            self.password = None

        def request_webpage(self, url):
            if self.username is not None or self.password is not None:
                auth = HTTPBasicAuth(username=self.username, password=self.password)
            else:
                auth = None
            return requests.get(url, auth=auth)

We want to use this manager in our specific REST feature file.

Add the basic auth manager to our REST features
-----------------------------------------------

We want to use this file as required feature in our specific rest features. As you know, this can be done by simply
instantiating it inside the specific rest features that need it:

.. code-block:: python

    import balder
    from ...lib.features import InsertCredentialsFeature, ViewInternalPageFeature

    # Client features
    class MyInsertCredentialsFeature(InsertCredentialsFeature):
        class Server(InsertCredentialsFeature.Server):
            pass

        basic_auth_manager = BasicAuthManager()
        username = None
        password = None

        def insert_username(self, username):
            self.username = username

        def insert_password(self, password):
            self.password = password

        def execute_login(self):
            self.basic_auth_manager.set_credentials(self.username, self.password)
            return True

        def execute_logout(self):
            self.basic_auth_manager.reset_credentials()
            return True


    class MyViewInternalPageFeature(ViewInternalPageFeature):

        class Server(ViewInternalPageFeature.Server):
            pass

        basic_auth_manager = BasicAuthManager()

        def check_internal_page_viewable(self):
            response = self.basic_auth_manager.request_webpage("TODO add the endpoint")
            return response.status_code == 200

Nice, we already have the main implementation. The only thing, we still need is the endpoint url of the server.

Add the server feature
----------------------

For this we have to add a feature to the server vDevice, that provides these information. Let's call this the
``UserApiFeature``. It should only contain a property which returns the url here. In order for us to use it, we only
have to instantiate it in our vDevice class:

.. code-block:: python

    import balder
    from ...lib.features import InsertCredentialsFeature, ViewInternalPageFeature

    # Server features
    class UserApiFeature(balder.Feature):
        @property
        def url_users(self):
            return "http://localhost:8000/api/users"

    # Client features
    class MyInsertCredentialsFeature(InsertCredentialsFeature):
        class Server(InsertCredentialsFeature.Server):
            pass

        basic_auth_manager = BasicAuthManager()
        username = None
        password = None

        def insert_username(self, username):
            self.username = username

        def insert_password(self, password):
            self.password = password

        def execute_login(self):
            self.basic_auth_manager.set_credentials(self.username, self.password)
            return True

        def execute_logout(self):
            self.basic_auth_manager.reset_credentials()
            return True


    class MyViewInternalPageFeature(ViewInternalPageFeature):

        class Server(ViewInternalPageFeature.Server):
            api = UserApiFeature()

        basic_auth_manager = BasicAuthManager()

        def check_internal_page_viewable(self):
            response = self.basic_auth_manager.request_webpage(self.Server.api.url_users)
            return response.status_code == 200

Of course we have to add our new helper features in our REST setup too:

.. code-block:: python

    import balder
    from balder.connections import HttpConnection
    from tests.lib.features import HasLoginSystemFeature
    from tests.setups import setup_features
    from tests.setups.rest import rest_features


    class SetupRestBasicAuth(balder.Setup):

        class Server(balder.Device):
            _ = HasLoginSystemFeature()
            # our new helper feature
            api_route = rest_features.UserApiFeature()
            valid_user = setup_features.MyValidRegisteredUserFeature()

        @balder.connect(Server, HttpConnection)
        class Client(balder.Device):
            # our new helper feature
            basicauth_manager = rest_features.BasicAuthManager()
            credentials = rest_features.MyInsertCredentialsFeature()
            internal = rest_features.MyViewInternalPageFeature()


We have made it! We have implemented both setups and manage the common use of feature classes. So let's start Balder.

Execute Balder with both setups
===============================

We can check if Balder resolves our scenario with the both setups correctly. For this, just call Balder with the
argument ``--resolve-only``:

.. code-block::

    $ balder --working-dir tests --resolve-only

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.7 (default, Sep  3 2021, 12:37:55) [Clang 12.0.5 (clang-1205.0.22.9)] | balder version 0.0.1     |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 2 Setups and 1 Scenarios
      resolve them to 2 mapping candidates

    RESOLVING OVERVIEW

    Scenario `ScenarioSimpleLoginOut` <-> Setup `SetupWebBrowser`
       ScenarioSimpleLoginOut.ClientDevice = SetupWebBrowser.Client
       ScenarioSimpleLoginOut.ServerDevice = SetupWebBrowser.Server
       -> Testcase<ScenarioSimpleLoginOut.test_valid_login_logout>
    Scenario `ScenarioSimpleLoginOut` <-> Setup `SetupRestBasicAuth`
       ScenarioSimpleLoginOut.ClientDevice = SetupRestBasicAuth.Client
       ScenarioSimpleLoginOut.ServerDevice = SetupRestBasicAuth.Server
       -> Testcase<ScenarioSimpleLoginOut.test_valid_login_logout>


Great, it works. Balder can find our two possible variations, one using our ``SetupWebBrowser`` and one using our
``SetupRestBasicAuth``.

Now it is time to really run the Balder session.

.. note::
    Do not forget to start the django server before:

    .. code-block:: none

        $ python manage.py runserver

After you have secured that the django server runs, you can run Balder:

.. code-block::

    $ balder --working-dir tests

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.5 (default, Nov 23 2021, 15:27:38) [GCC 9.3.0] | balder version 0.0.1                            |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 2 Setups and 1 Scenarios
      resolve them to 2 mapping candidates

    ================================================== START TESTSESSION ===================================================
    SETUP SetupRestBasicAuth
      SCENARIO ScenarioSimpleLoginOut
        VARIATION ScenarioSimpleLoginOut.ClientDevice:SetupRestBasicAuth.Client | ScenarioSimpleLoginOut.ServerDevice:SetupRestBasicAuth.Server
          TEST ScenarioSimpleLoginOut.test_valid_login_logout [✓]
    SETUP SetupWebBrowser
      SCENARIO ScenarioSimpleLoginOut
        VARIATION ScenarioSimpleLoginOut.ClientDevice:SetupWebBrowser.Client | ScenarioSimpleLoginOut.ServerDevice:SetupWebBrowser.Server
          TEST ScenarioSimpleLoginOut.test_valid_login_logout [✓]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 2 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0
