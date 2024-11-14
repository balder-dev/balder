Parametrization
***************

Balder allows to parametrize tests. For this it supports static and dynamic test case parametrization. Static
parametrization allows to feed a test method with static values. A dynamic parametrization will be resolved on
variation level, because it uses values from specified feature methods, that are not clear at collecting or resolving.
You can find out more about parametrization with Balder in this documentation section.

Static Parametrization
======================

If you want to parametrize a test with static values, you can use the static parametrization decorator
``@balder.parameterize()``. Simply decorate your test method with it and add an argument with the specified name:

.. code-block:: py

    import balder

    class ScenarioSenderAndReceiver(balder.Scenario):

        ...

        @balder.parametrize("msg_content", [b"Hello World!", b"Hello Mar3!", b"H3ll0 @"])
        def test_send_a_message(self, msg_content):
            self.SendDevice.send.send_bytes_to(self.RecvDevice.recv.address, msg_content)
            recv_list = self.RecvDevice.listen_for_incoming_msgs(timeout=1)
            ...

That's all. As soon as you execute Balder, the test will be executed three times with the different parametrization:

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.6 (default, Oct  4 2024, 08:01:31) [Clang 16.0.0 (clang-1600.0.26.4)] | balder version           |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 1 Scenarios
      resolve them to 1 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupVarAliceToBob
      SCENARIO ScenarioSenderAndReceiver
        VARIATION ScenarioSenderAndReceiver.ReceiverDevice:SetupVarAliceToBob.Bob | ScenarioSenderAndReceiver.SenderDevice:SetupVarAliceToBob.Alice
          TEST ScenarioSenderAndReceiver.test_send_a_message[b'Hello World!'] [.]
          TEST ScenarioSenderAndReceiver.test_send_a_message[b'Hello Mar3!'] [.]
          TEST ScenarioSenderAndReceiver.test_send_a_message[b'H3ll0 @'] [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 3 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0

Because the parametrization decorator specifies ``msg_content`` as argument, the test method argument ``msg_content``
will be equipped with the currently parameterised value. The first run will be with ``msg_content=b'Hello World!'``,
the second run with ``msg_content=b'Hello Mar3!'`` and the last run with ``msg_content=b'H3ll0 @'``

Add more parametrization arguments
----------------------------------

Of course it is also possible to add multiple parametrization decorator and create a combined parametrization:

.. code-block:: py

    import balder

    class ScenarioSenderAndReceiver(balder.Scenario):

        ...

        @balder.parametrize("first_word", [b"Hello", b"Bye"])
        @balder.parametrize("second_word", [b"World", b"Mars"])
        def test_send_a_message(self, first_word, second_word):
            msg_content = first_word + b" " + second_word
            self.SendDevice.send.send_bytes_to(self.RecvDevice.recv.address, msg_content)
            time.sleep(read_delay)
            recv_list = self.RecvDevice.listen_for_incoming_msgs(timeout=1)
            ...

This test method will be executed four times in total:

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.6 (default, Oct  4 2024, 08:01:31) [Clang 16.0.0 (clang-1600.0.26.4)] | balder version           |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 1 Scenarios
      resolve them to 1 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupVarAliceToBob
      SCENARIO ScenarioSenderAndReceiver
        VARIATION ScenarioSenderAndReceiver.ReceiverDevice:SetupVarAliceToBob.Bob | ScenarioSenderAndReceiver.SenderDevice:SetupVarAliceToBob.Alice
          TEST ScenarioSenderAndReceiver.test_send_a_message[b'Hello';b'World'] [.]
          TEST ScenarioSenderAndReceiver.test_send_a_message[b'Hello';b'Mars'] [.]
          TEST ScenarioSenderAndReceiver.test_send_a_message[b'Bye';b'World'] [.]
          TEST ScenarioSenderAndReceiver.test_send_a_message[b'Bye';b'Mars'] [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 4 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0

Dynamic Parametrization
=======================

Dynamic parametrization is particularly useful when the values are subject to change based on the current state or
configuration of the setup. Unlike static parametrization, where all parameters are known and defined at the start,
dynamic parametrization allows for the test values to be defined at runtime by setup feature methods/properties.

For example, let's checkout a scenario, that validates the availability of websites:

.. code-block:: py

    import balder

    class ScenarioCheckAvailability(balder.Scenario):

        class Website(balder.Device):
            sitemap = SitemapFeature()

        @balder.parametrize_by_feature('url_path', (Website, 'sitemap', 'get_all_url_paths'))
        def test_check_availability(self, url_path):
            full_url = f"https://{self.Website.sitemap.hostname}/{url_path}"
            ...

The **setup** feature implementation of ``SitemapFeature`` could look like the following snippet:

.. code-block::

    import balder
    from .scenario_features import SitemapFeature

    class BalderDocumentationSitemapFeature(SitemapFeature):

        def get_all_url_paths(self):
            return ['en/latest/index.html', 'en/latest/getting_started/installation.html']

The ``@balder.parametrize_by_feature('url_path', (Website, 'sitemap', 'get_all_url_paths'))`` decorator makes clear,
that the parametrization values are provided by the method ``get_all_url_paths()`` of the ``SitemapFeature``. This
mechanism involves parameterizing tests by leveraging the return value from a designated feature. At the scenario
level, it's possible that the method ``SitemapFeature.get_all_url_paths()`` might not have an implementation. However,
since dynamic parameterization occurs at the variation level, this poses no issue. The values for parameterization
are only requested after the setup is chosen and the setup feature is operational (which is at variation level).

If you execute Balder with that Scenario, it will ask the Setup feature for the parametrization values and executes the
test once with every single parameterization:

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.6 (default, Oct  4 2024, 08:01:31) [Clang 16.0.0 (clang-1600.0.26.4)] | balder version           |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 2 Setups and 1 Scenarios
      resolve them to 1 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupBalderDoc
      SCENARIO ScenarioCheckAvailability
        VARIATION ScenarioCheckAvailability.Website:SetupBalderDoc.Website
          TEST ScenarioCheckAvailability.test_check_availability[en/latest/index.html] [.]
          TEST ScenarioCheckAvailability.test_check_availability[en/latest/getting_started/installation.html] [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 2 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0


If we add another setup which has a different implementation of ``SitemapFeature`` feature, this variation will be
executed according this other implementation. So for example, we add another **setup** feature, that has the following
implementation:

.. code-block:: py

    import balder
    from .scenario_features import SitemapFeature

    class GitHubBalderSitemapFeature(SitemapFeature):

        def get_all_url_paths(self):
            return ['balder-dev/balder', 'balder-dev/balder/issues', 'balder-dev/balder/pulls']

We assign this feature to another setup called ``SetupBalderGithub``. Let's execute Balder and see what's happening:

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.6 (default, Oct  4 2024, 08:01:31) [Clang 16.0.0 (clang-1600.0.26.4)] | balder version           |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 2 Setups and 1 Scenarios
      resolve them to 2 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupBalderDoc
      SCENARIO ScenarioCheckAvailability
        VARIATION ScenarioCheckAvailability.Website:SetupBalderDoc.Website
          TEST ScenarioCheckAvailability.test_check_availability[en/latest/index.html] [.]
          TEST ScenarioCheckAvailability.test_check_availability[en/latest/getting_started/installation.html] [.]
    SETUP SetupBalderGithub
      SCENARIO ScenarioCheckAvailability
        VARIATION ScenarioCheckAvailability.Website:SetupBalderGithub.Website
          TEST ScenarioCheckAvailability.test_check_availability[balder-dev/balder] [.]
          TEST ScenarioCheckAvailability.test_check_availability[balder-dev/balder/issues] [.]
          TEST ScenarioCheckAvailability.test_check_availability[balder-dev/balder/pulls] [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 5 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0



As you can see, the same test with the same scenario is executed with two different setup. Both setups return different
parametrization values.

Mix Parametrization Styles
--------------------------

You can of course also mix these two different parametrization styles for your test. Let's add another parametrization
value, that adds a additional slash at the end of the URL, when its value is ``True``:

.. code-block:: py

    import balder

    class ScenarioCheckAvailability(balder.Scenario):

        class Website(balder.Device):
            sitemap = SitemapFeature()

        @balder.parametrize('add_trailing_slash', [True, False])
        @balder.parametrize_by_feature('url_path', (Website, 'sitemap', 'get_all_url_paths'))
        def test_check_availability(self, url_path, add_trailing_slash):
            full_url = f"https://{self.Website.hostname}/{url_path}" + "/" if add_trailing_slash else ""
            ...

If we execute Balder with this scenario, it will run the test for every url twice. Once with trailing slash and another
time without:

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.9.6 (default, Oct  4 2024, 08:01:31) [Clang 16.0.0 (clang-1600.0.26.4)] | balder version           |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 2 Setups and 1 Scenarios
      resolve them to 2 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupBalderDoc
      SCENARIO ScenarioCheckAvailability
        VARIATION ScenarioCheckAvailability.Website:SetupBalderDoc.Website
          TEST ScenarioCheckAvailability.test_check_availability[en/latest/index.html;True] [.]
          TEST ScenarioCheckAvailability.test_check_availability[en/latest/getting_started/installation.html;True] [.]
          TEST ScenarioCheckAvailability.test_check_availability[en/latest/index.html;False] [.]
          TEST ScenarioCheckAvailability.test_check_availability[en/latest/getting_started/installation.html;False] [.]
    SETUP SetupBalderGithub
      SCENARIO ScenarioCheckAvailability
        VARIATION ScenarioCheckAvailability.Website:SetupBalderGithub.Website
          TEST ScenarioCheckAvailability.test_check_availability[balder-dev/balder;True] [.]
          TEST ScenarioCheckAvailability.test_check_availability[balder-dev/balder/issues;True] [.]
          TEST ScenarioCheckAvailability.test_check_availability[balder-dev/balder/pulls;True] [.]
          TEST ScenarioCheckAvailability.test_check_availability[balder-dev/balder;False] [.]
          TEST ScenarioCheckAvailability.test_check_availability[balder-dev/balder/issues;False] [.]
          TEST ScenarioCheckAvailability.test_check_availability[balder-dev/balder/pulls;False] [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 10 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0

Provide Arguments in Feature-Method
-----------------------------------

Sometimes it is necessary to parametrize the method, you are using in your ``@balder.parametrize_by_feature`` decorator
too. Balder supports this, while you can use three different approaches to do so.

**Value:**

If you want to provide a fix value as parameter you can use the :class:`Value` object:

.. code-block:: py

    class ScenarioCheckAvailability(balder.Scenario):

        ...

        @balder.parametrize_by_feature('url_path', (Website, 'sitemap', 'get_all_url_paths'),
                                       parameter={'ignore_redirects': Value(True)})
        def test_check_availability(self, url_path):
            full_url = f"https://{self.Website.sitemap.hostname}/{url_path}"
            ...

In this example, the method ``get_all_url_paths`` has a argument ``ignore_redirects``, which will be fed with the
static value ``True``.

**Parameter:**

You can also use another parameterized value instead of a static value. For that you can use the :class:`Parameter`
object:

.. code-block:: py

    class ScenarioCheckAvailability(balder.Scenario):

        ...

        @balder.parametrize('add_trailing_slash', [True, False])
        @balder.parametrize_by_feature('url_path', (Website, 'sitemap', 'get_all_url_paths'),
                                       parameter={'auto_add_urls_with_trailing_slashes': Parameter('add_trailing_slash')})
        def test_check_availability(self, add_trailing_slash, url_path):
            full_url = f"https://{self.Website.sitemap.hostname}/{url_path}"
            ...

In this case, Balder will provide the current parametrized value of ``add_trailing_slash`` (which is a parametrization
value too).

**FeatureAccessSelector:**

You can even parametrize your feature method by requesting the value of another feature method or property. For that use
the :class:`FeatureAccessSelector` object:

.. code-block:: py

    class ScenarioCheckAvailability(balder.Scenario):

        ...

        @balder.parametrize_by_feature('url_path', (Website, 'sitemap', 'get_all_url_paths'),
                                       parameter={'hostname': FeatureAccessSelector(Website, 'sitemap', 'hostname')})
        def test_check_availability(self, url_path):
            full_url = f"https://{self.Website.sitemap.hostname}/{url_path}"
            ...

You are totally free here. You can use methods/properties from the same feature or from other features or even from
other features of other devices.
