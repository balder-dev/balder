Part 1: Develop a Login Test from Scratch
*****************************************

As described in the `Balder Intro Example <Balder Intro Example>`_, we want to test the official Nextcloud app. For this, we set up Docker to
be able to test the application locally.

.. note::
    Make sure you have completed the preparation steps and installed Docker, Docker Compose, and Balder. You can find
    an explanation about that in `Balder Intro Example <Balder Intro Example>`_.

In this first part of this tutorial, we'll test the login process of the Nextcloud app. Normally, we would use the
``ScenarioSimpleLogin`` from the ``balderhub-auth`` package, since the test is already implemented there. However, for
this tutorial, we'll implement the test from scratch to help you understand the process better.

Prepare Environment
===================

Before we start, we need to make sure that our test environment is ready.

Start Docker container
----------------------

Let's verify that the docker containers are running:

.. code-block:: shell

    $ docker compose up -d

Open the browser and go to http://localhost:8000. You should see the NextCloud login page, we want to test now.

Create initial filestructure
----------------------------

Let's start by creating some files in an easy-to-use file structure:

.. code-block:: none

    - <your project name>
        | - src
            | - lib
                | - scenario_features.py
                | - setup_features.py
            | - scenarios/
                | - scenario_login.py
            | - setups/
                | - setup_docker.py

This design adheres to the design that is frequently used in Balderhub projects and also by the
`template generator for BalderHub projects <https://github.com/balder-dev/template-balderhub>`_.

Install ``balderhub-html``
--------------------------

We want to develop a test from scratch, but we want to develop a web test. Our live will get much simpler, when we are
using the package ``balderhub-html``. This project provides html components, we can directly use in our tests, which
provides different methods to make sure that it reduces flaky tests, which is often the case for asynchron web apps.

We want to develop a test from scratch, specifically a web test. Our lives will become much simpler if we use the
package ``balderhub-html`` for that. This package provides HTML components that we can directly use in our tests. These
components offer various methods to reduce flaky tests, which are common in web apps.

.. note::
    When using ``balderhub-html``, you can write web tests without worrying about how to control them. This package
    requires a control feature that implements the ``balderhub-guicontrol`` interface, but as an end user, this detail
    is completely irrelevant. Simply install the GUI control package of your choice (we're using ``balderhub-selenium``
    in this tutorial, but you can also use ``balderhub-appium`` (coming soon), ``balderhub-playwright`` (coming soon),
    or any other package that supports the ``balderhub-guicontrol`` interface).


You can install this package with:

.. code-block:: shell

    $ pip install balderhub-html

Developing the Test Scenario
============================

So let's start by developing a test scenario. For this, we need to define **what is needed** to execute the contained
test.

We want to write a test that opens the login page, enters a username and password, and presses the login button. After
that, we also want to check if the user is really logged in.

So let's start defining such a scenario. Often, it helps to just write down what you want to have. In Balder, everything
is organized around devices, and these devices have features. For example, we could have a ``LoginFeature`` feature, and
we can think about having two different devices: a Browser and a WebServer. So let's start with that:

.. code-block:: python

    # file `scenarios/scenario_login.py`

    import balder

    from lib.scenario_features import LoginFeature

    class ScenarioLogin(balder.Scenario):

        class WebServer(balder.Device):
            pass

        @balder.connect('WebServer', over_connection=balder.Connection())
        class Browser(balder.Device):
            login = LoginFeature()

        def test_login(self):
            username = "admin"  # TODO
            password = "Admin12345"  # TODO

            assert not self.Browser.login.user_is_logged_in(), "some user is already logged in"

            self.Browser.login.type_username(username)
            self.Browser.login.type_password(password)
            self.Browser.login.submit_login()

            assert self.Browser.login.user_is_logged_in(), "user was not logged in"

Note that we've set hardcoded values for the username and password for now. These will be replaced later, as we're going
to develop a scenario that can be used for all kinds of logins - not just our specific case with NextCloud and with the
specific username and password. For the time being, we'll leave them as they are.

We've added an import for our future feature ``LoginFeature``, which isn't implemented yet. Since we're working on the
scenario, this feature should be placed in ``lib/scenario_features.py``. Now, let's define it. Before doing that, take
a look at our test method itself: Which methods do we need in our future feature?

We are using the methods ``user_is_logged_in()``, ``type_username()``, ``type_password()``, and ``submit_login()``.
Okay, that's it - these will be the methods for our future feature ``LoginFeature``. Let's define it now.

Define our Scenario-Level-Feature
---------------------------------

On the scenario level, we define **what is needed** without necessarily providing an exact implementation of how it is
realized.

With that in mind, we'll define this feature using abstract methods only:

.. code-block:: python

    # file `lib/scenario_features.py`

    import balder

    class LoginFeature(balder.Feature):

        def user_is_logged_in(self):
            raise NotImplementedError

        def type_username(self, username: str):
            raise NotImplementedError

        def type_password(self, password: str):
            raise NotImplementedError

        def submit_login(self):
            raise NotImplementedError


That's it. Everything on the scenario level is now defined.

That concludes the first part. We've created a login test that can be reused for various purposes. It doesn't matter
whether you want to test the login of a website (as we're doing here) or something entirely different, like the login on
an electric door gate, for example.

Provide the implementation with a Setup
=======================================

When we run Balder later, it will try to find matches between the scenario and our defined setup classes. To do this,
Balder checks if there is at least one device in the setup that provides an implementation for every feature in our
scenario device. An implementation is provided by a feature that is a subclass of the corresponding scenario feature.

If we use more than one feature in the scenario class, Balder will also check for other devices that fulfill the same
feature implementation conditions. Additionally, it validates that these devices are connected using the exact
connections specified.

You can read more about the mechanism of how Balder works in `this guide <Balder execution mechanism>`__. For details on
how connections can be used to select specific variations, see `this guide <Connections>`__.

Define the Setup
----------------

But for now, let's start by defining a setup that can be used for our specific case:

.. code-block:: python

    import balder
    from lib.setup_features import LoginFeature

    class SetupDocker(balder.Setup):

        class NextCloud(balder.Device):
            pass

        @balder.connect("NextCloud", over_connection=balder.Connection())
        class SeleniumBrowser(balder.Device):
            login_func = LoginFeature()


We directly imported a non-existent feature called ``LoginFeature`` from ``lib.setup_features``. This feature doesn't
exist yet, but we'll define it shortly to provide the implementation for our scenario feature
``lib.scenario_features.LoginFeature``.

Define the Setup-Based ``LoginFeature``
---------------------------------------

Now, let's define this feature by creating a new class in ``lib/setup_features.py``. This class should inherit directly
from ``lib.scenario_features.LoginFeature`` and provide implementations for all the abstract methods:

.. code-block:: python

    # file `lib/setup_features.py`

    import balder
    import lib.scenario_features

    class LoginFeature(lib.scenario_features.LoginFeature):

        def user_is_logged_in(self):
            # todo provide an implementation
            pass

        def type_username(self, username: str):
            # todo provide an implementation
            pass

        def type_password(self, password: str):
            # todo provide an implementation
            pass

        def submit_login(self):
            # todo provide an implementation
            pass

Here, we'll add our implementation soon. But for now, this is enough to run Balder:

.. code-block:: shell

    $ balder --working-dir src

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0] | balder version 0.1.0b14                          |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 1 Scenarios
      resolve them to 1 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupDocker
      SCENARIO ScenarioLogin
        VARIATION ScenarioLogin.Browser:SetupDocker.SeleniumBrowser | ScenarioLogin.WebServer:SetupDocker.NextCloud
          TEST ScenarioLogin.test_login [X]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 1 | TOTAL ERROR: 0 | TOTAL SUCCESS: 0 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0

    Traceback (most recent call last):
      File "/home/user/temp_balder_tutorial/.venv/lib/python3.12/site-packages/_balder/executor/testcase_executor.py", line 132, in _body_execution
        self.base_testcase_callable(self=self.base_testcase_obj, **all_args)
      File "/home/user/temp_balder_tutorial/src/scenarios/scenario_login.py", line 25, in test_login
        assert self.Browser.login.user_is_logged_in(), "user was not logged in"
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError: user was not logged in

Of course, we get an error, because we haven't provided any implementation and the test does not really do something (the
methods are still empty), but everything gets collected and Balder can find the match.

Of course, we get an error because we haven't provided any implementation yet, and the test doesn't really do anything
(the methods are still empty). However, everything gets collected, and Balder can find the match.

Provide an Implementation for the Scenario-Based ``LoginFeature``
-----------------------------------------------------------------

When we want to provide an implementation for the ``lib.setup_features.LoginFeature``, we can either write it from
scratch - importing Selenium, setting it up, handling waiting functions, and so on - or we can simply use
``balderhub-html`` and ``balderhub-selenium``.

So let's make sure, that we have installed them:

.. code-block:: shell

    $ pip install balderhub-html balderhub-selenium

Before we add the html elements, let's add the selenium feature. We need a feature that supports the
guicontrol interface (see `balderhub-guicontrol <https://hub.balder.dev/projects/guicontrol>`_). The
balderhub-guicontrol packages handle all the required management for you, so you do not need to do something, except
using one of the features that implements its interfaces.

Before we add the HTML elements, let's incorporate the Selenium feature. We need a feature that supports the guicontrol
interface (see `balderhub-guicontrol <https://hub.balder.dev/projects/guicontrol>`_). The ``balderhub-guicontrol``
packages handle all the required management for you, so you don't need to do anything special - except to use one of
the features that implements this interface.

.. code-block:: python

    # file `lib/setup_features.py`

    import balder
    import lib.scenario_features
    from balderhub.selenium.lib.scenario_features import SeleniumFeature

    class LoginFeature(lib.scenario_features.LoginFeature):

        selenium = SeleniumFeature()

        ...

As you can see, we've added a ``SeleniumFeature`` from ``balderhub-selenium``. But wait - this is a feature within a
feature. What does that mean? It means Balder will ensure that whenever this feature is used, the instantiating device
must also have a ``SeleniumFeature`` (or a subclass of it). Balder will then automatically assign that instance to the
selenium class attribute of our ``LoginFeature``. You don't need to do anything special for this; Balder handles it all
behind the scenes. However, you can certainly make use of it in your code.

So, let's take advantage of it and provide the implementation:


.. code-block:: python

    # file `lib/setup_features.py`

    import balder
    import lib.scenario_features
    from balderhub.html.lib.utils import Selector
    import balderhub.html.lib.utils.components as html
    from balderhub.selenium.lib.scenario_feature import SeleniumFeature

    class LoginFeature(lib.scenario_features.LoginFeature):

        selenium = SeleniumFeature()

        # the url to navigate to be able to login
        login_url = "http://nextcloud/login"

        @property
        def input_username(self):
            # html <input> element where we can type in the username
            return html.inputs.HtmlTextInput.by_selector(self.selenium.driver, Selector.by_name('user'))

        @property
        def input_password(self):
            # html <input> element where we can type in the password
            return html.inputs.HtmlPasswordInput.by_selector(self.selenium.driver, Selector.by_name('password'))

        @property
        def btn_login(self):
            # html <button> element that needs to be clicked to submit the login
            return html.HtmlButtonElement.by_selector(self.selenium.driver, Selector.by_xpath('.//button[@type="submit"]'))

        def user_is_logged_in(self):
            self.selenium.driver.navigate_to(self.login_url)
            return self.selenium.driver.current_url != self.login_url

        def type_username(self, username: str):
            self.input_username.wait_to_be_clickable_for(3).type_text(username, clean_before=True)

        def type_password(self, password: str):
            self.input_password.wait_to_be_clickable_for(3).type_text(password, clean_before=True)

        def submit_login(self):
            self.btn_login.wait_to_be_clickable_for(3).click()

That's it. The test is now ready.

.. note::

    For larger projects, it is recommended to use the
    `balderhub.html.lib.scenario_features.HtmlPage <https://hub.balder.dev/projects/html/en/latest/features.html#balderhub.html.lib.scenario_features.HtmlPage>`__.
    class. This class follows the page-object model, where you directly describe your webpage, including all its HTML
    elements, and interact with them in a straightforward way. Everything is organized within its own dedicated feature.

    Using this approach, the implementation would look like the example shown below:

    .. code-block:: python

            class LoginFeature(lib.scenario_features.LoginFeature):

                # instead of adding all the html elements within this feature, we define them in the html page
                # `NextcloudLoginPage` and using them here
                login_page = NextcloudLoginPage()

                def user_is_logged_in(self):
                    self.login_page.open()
                    return not self.login_page.is_applicable()

                def type_username(self, username: str):
                    self.login_page.input_username.wait_to_be_clickable_for(3).type_text(username, clean_before=True)

                def type_password(self, password: str):
                    self.login_page.input_password.wait_to_be_clickable_for(3).type_text(password, clean_before=True)

                def submit_login(self):
                    self.login_page.btn_login.wait_to_be_clickable_for(3).click()

Set up Selenium in the Setup
----------------------------

Before we finally run Balder, we need to add our Selenium feature. This is required because, with the class attribute
``selenium = SeleniumFeature()``, we've specified that Balder should ensure our setup provides a Selenium feature as
well.

As we are using selenium-grid within a own docker container, we need to use the
``balderhub.selenium.lib.setup_features.SeleniumRemoteWebdriverFeature``. As we are using firefox, we also need to
specify the correct ``selenium_options``. You can read more about that
`in the balderhub-selenium documentation <https://hub.balder.dev/projects/selenium>`_

So, let's do this:

.. code-block:: python

    import balder
    from lib.setup_features import LoginFeature
    from selenium import webdriver
    from balderhub.selenium.lib.setup_features import SeleniumRemoteWebdriverFeature

    class SeleniumManagerFeature(SeleniumRemoteWebdriverFeature):
        # use this feature if you are using selenium grid as docker container
        selenium_options = webdriver.FirefoxOptions()

    class SetupDocker(balder.Setup):

        class NextCloud(balder.Device):
            pass

        @balder.connect("NextCloud", over_connection=balder.Connection())
        class SeleniumBrowser(balder.Device):
            selenium = SeleniumManagerFeature()
            login_func = LoginFeature()

.. note::
    In our example, we're using the ``SeleniumRemoteWebdriverFeature``, which allows us to connect to a Selenium Grid
    container. If you prefer to use Selenium with a browser on your host machine instead, you'll need to select the
    appropriate driver for that browser. You can find more details about this in the
    `balderhub-selenium documentation <https://hub.balder.dev/projects/selenium>`_.

Last but not least, we need to make sure that Selenium is set up before the test is executed. For that, let's use
fixtures (see `Fixtures <Fixtures>`_):

.. code-block:: python

    import balder
    from lib.setup_features import LoginFeature
    from selenium import webdriver
    from balderhub.selenium.lib.setup_features import SeleniumRemoteWebdriverFeature

    ...

    class SetupDocker(balder.Setup):

        ...

        # register this fixture as a session fixture - meaning it will be executed once before/after the whole test session
        @balder.fixture('session')
        def selenium_manager(self):
            # creates a new selenium connection before the test run
            self.SeleniumBrowser.selenium.create()
            yield # can be used to separate construction code (before session) and teardown code (after session)
            # shuts down selenium after the test run
            self.SeleniumBrowser.selenium.quit()


Let's run Balder and verify if it executes successfully. You can observe the test run directly in your browser or
through the Selenium Grid website at http://localhost:4444 (if you've added the container to Docker Compose).

.. code-block:: shell

    $ balder --working-dir src

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0] | balder version 0.1.0b14                          |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 1 Scenarios
      resolve them to 1 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupDocker
      SCENARIO ScenarioLogin
        VARIATION ScenarioLogin.Browser:SetupDocker.SeleniumBrowser | ScenarioLogin.WebServer:SetupDocker.NextCloud
          TEST ScenarioLogin.test_login [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 1 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0


.. todo
    User Roles
    ----------

Okay, but now it's time to install tests. This significantly speeds up the test development process. So, let's jump to
`Part 2 <Part 2: Install Tests for Nextcloud Web>`_ of this tutorial and install tests for validating file operations
within the Nextcloud web app.