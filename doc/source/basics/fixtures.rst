Fixtures
********

Fixtures are functions or methods that run code before or after specific stages in a test execution. In Balder,
fixtures can be triggered at various points during the testing process (known as the **execution-level**) and can be
defined in different locations within your code (known as the **definition-scope**). The order in which these fixtures
run can also be affected by chained dependencies between them. You'll learn more about all this in the following
sections.

A simple fixture
================

Defining a fixture is straightforward. Just create a function and decorate it with ``@balder.fixture()``.

.. code-block:: python

    # file balderglob.py

    @balder.fixture(level='session')
    def my_own_fixture():
        print("is executed before the test session")
        yield
        print("will be executed after the test session")

In the example above, we use the decorator ``@balder.fixture(level='session')`` with the argument ``level``. This
defines the **execution-level** of the fixture, which specifies when and how often it will run during the testing
process. We placed this fixture in the global ``balderglob.py`` file to ensure it always gets executed. A fixture
defined here has the broadest scope, meaning it applies to every scenario and setup variation in your tests.

What exactly does this fixture do? The parameter ``level="session"`` means the fixture will run only once for the
entire test session. Specifically, a fixture at the session level gets called right after the test session begins.

But what about the ``yield`` statement? Fixtures typically divide into two parts, separated by the Python ``yield``
keyword. The code before ``yield`` runs before the relevant test branch (like a scenario or variation) starts - this is
the construct phase, where you set things up. The code after ``yield`` runs afterward, once the test branch has
finished - this is the teardown phase, where you clean up resources.

.. note::
    You can also omit the yield statement entirely. In that case, Balder assumes there is no teardown code to execute
    after the test branch finishes.

Execution-Level
---------------

The decorator ``@balder.fixture(level="session")`` defines a fixture function that runs at the execution-level
``session``. This means the fixture's construct part executes right before the entire test session begins, while the
teardown part runs after the session ends. Balder offers many other execution levels for fixtures to suit different
needs. For instance, if you want a fixture to read logs from a device after each test case finishes, you can set its
**execution-level** to ``'testcase'``. In this case, the fixture will run before and after every relevant test case. For
details on all available options, see the section :ref:`Execution-Level possibilities`.

Definition-Scope
----------------

The **definition-scope** describes the validity of a fixture. It depends on where the fixture is defined within the
Balder test system. For example, if you implement a fixture in the global ``balderglob.py`` file, it has the
**definition-scope** GLOBAL. This means it is valid for the entire test session and applies to every test case executed
during that session. If a fixture defined in the ``balderglob.py`` file uses the decorator
``@balder.fixture(level="session")``, it will always be executed - regardless of the specific
:ref:`Scenario <Scenarios>` or which :ref:`Setup <Setups>` or variation is matched. That is similar for all other
**execution-level**, as long as it is defined within the ``balderglob.py`` file.

.. note::
    The ``balderglob.py`` is a global configuration file that can be used to define fixtures too. It always needs to be
    placed in the working-dir root directory.

The situation changes when you define the fixture inside a single :ref:`Scenario <Scenarios>`. Let's say we call this
one ``ScenarioA``, and we also have another called ``ScenarioB``. Suppose we add a decorator with an
**execution-level** ``testcase`` (``@balder.fixture(level="testcase")``) to the fixture method in ``ScenarioA``. If we
run the test environment, the fixture will be called for all testcases that belong to the ``ScenarioA``, but for no
testcases of ``ScenarioB``. The **definition-scope** is limited to the ``ScenarioA`` only.

You can find more detailed information about the definition scope in the section
:ref:`Definition-Scopes <Definition-Scope possibilities>`.

Fixture ordering
----------------

As you saw in the earlier sections, two important characteristics determine when and how a fixture will be executed:
the **execution-level**, which is specified as argument in the fixture decorator, and the **definition-scope**,
which depends on where the fixture is placed in your code. But how does Balder order fixtures that share the same
execution level?

First, Balder establishes an initial ordering based on the **definition-scope**. Global fixtures (defined in the
``balderglob.py`` file) run first. Next come setup-scoped fixtures (defined inside a :class:`Setup <Setup>` class).
Finally, scenario-scoped fixtures (defined within a :class:`Scenario <Scenario>` class) are executed. This gives us a
basic sequence, but the order remains undefined for fixtures that have the same **definition-scope** (and, of course,
the same **execution-level**). To handle this, Balder allows you to chain fixtures together, creating explicit
dependencies.

Take a look at the following example:


.. code-block:: python

    # file `balderglob.py`

    @balder.fixture(level='session')
    def my_own_fixture1():
        print("Fixture1: is executed before the test session")
        yield
        print("Fixture1: will be executed after the test session")

    @balder.fixture(level='session')
    def my_own_fixture2(my_own_fixture1):
        print("Fixture2: is executed before the test session")
        yield
        print("Fixture2: will be executed after the test session")

If you run this test session, the following output will be generated:

.. code-block:: none

    Fixture1: is executed before the test session
    Fixture2: is executed before the test session

    ... further outputs of test run

    Fixture2: will be executed after the test session
    Fixture1: will be executed after the test session


You can reference another fixture by adding a function or method argument with the same name as that fixture's
function or method. As shown in the example, the fixture ``my_own_fixture2`` references ``my_own_fixture1`` by using
the same name for its function argument. With this setup, it's clear that ``my_own_fixture1`` must run before
``my_own_fixture2``. If you don't provide this chaining mechanism, Balder will determine the order itself. That's
perfectly fine, because sometimes the exact sequence simply doesn't matter.

Referencing other fixtures
---------------------------

If you reference another fixture as described above, you'll need access to its return value.

Now, let's revisit the previous example with a small modification:

.. code-block:: python

    # file `balderglob.py`

    @balder.fixture(level='session')
    def my_own_fixture1():
        print("Fixture1: is executed before the test session")
        yield 42
        print("Fixture1: will be executed after the test session")

    @balder.fixture(level='session')
    def my_own_fixture2(my_own_fixture1):
        print("Fixture2: is executed before the test session - value of Fixture 1 is `{}`".format(my_own_fixture1))
        yield
        print("Fixture2: will be executed after the test session")

In this updated example, we calculate a value in the construct part of ``my_own_fixture1`` (the code before the
``yield``) and pass it back using the ``yield`` keyword. This value is then automatically injected into the parameter
``my_own_fixture1`` of the dependent fixture ``my_own_fixture2``, where you can use it directly. Running this example
would produce the following output:

.. code-block:: none

    Fixture1: is executed before the test session
    Fixture2: is executed before the test session - value of Fixture 1 is `42`

    ... further outputs of test run

    Fixture2: will be executed after the test session
    Fixture1: will be executed after the test session


You can also reference fixtures that have a different **execution-level** or **definition-scope**, but you must ensure
that the referenced fixture runs before the one that depends on it. For more information about referencing fixtures
and how it affects their order, see :ref:`reference fixtures`.

Execution-Level possibilities
=============================
Balder supports various **execution-levels** that you can assign to a fixture. Since tests in Balder are organized into
scenarios - and these scenarios can run under specific setups - there are multiple points where you can focus during
test execution.

The following table lists all possible **execution-level** options:

+------------------------+---------------------------------------------------------------------------------------------+
| level                  | description                                                                                 |
+========================+=============================================================================================+
| ``session``            | This is the outermost **execution-level**. The construct part of the fixture runs right     |
|                        | after the collecting and resolving process but before any test code executes. The teardown  |
|                        | part runs after the entire test session has finished.                                       |
+------------------------+---------------------------------------------------------------------------------------------+
| ``setup``              | Depending on the **definition-scope**, this fixture runs before and after every             |
|                        | :ref:`Setup <Setups>` change. It surrounds the activation of each new :ref:`Setup <Setups>` |
|                        | class in the test executor.                                                                 |
+------------------------+---------------------------------------------------------------------------------------------+
| ``scenario``           | Depending on the **definition-scope**, this fixture runs before and after every             |
|                        | :ref:`Scenario <Scenarios>` change. It surrounds the activation of each new                 |
|                        | :ref:`Scenario <Scenarios>` class in the test executor.                                     |
+------------------------+---------------------------------------------------------------------------------------------+
| ``variation``          | A variation in the Balder test system refers to a possible device assignment between        |
|                        | :ref:`Scenario-Devices <Scenario-Device>` and :ref:`Setup-Devices <Setup-Device>`.          |
|                        | Depending on the **definition-scope**, this fixture runs before and after every new device  |
|                        | variation within its scoped :ref:`Setup <Setups>` / :ref:`Scenario <Scenarios>`             |
|                        | combination.                                                                                |
+------------------------+---------------------------------------------------------------------------------------------+
| ``testcase``           | Depending on the **definition-scope**, this fixture runs before and after every test        |
|                        | method. It surrounds each new test case defined in the :ref:`Scenario <Scenarios>` class    |
|                        | within the specified definition scope.                                                      |
+------------------------+---------------------------------------------------------------------------------------------+

Definition-Scope possibilities
==============================

Balder offers three different **definition-scopes**. These scopes determine the validity and applicability of your
fixtures.

The following table outlines these scopes:

+------------------------+------------------------+--------------------------------------------------------------------+
| Definition             | Validity               | description                                                        |
+========================+========================+====================================================================+
| as function in         | everywhere             | This fixture will always be executed, no matter which specific     |
| ``balderglob.py`` file |                        | test setup or scenario is selected. It runs in every test session. |
+------------------------+------------------------+--------------------------------------------------------------------+
| as method in           | only in this setup     | This fixture runs only if the setup where it is defined is         |
| :ref:`Setups`          |                        | executed in the current test run. If the **execution-level** is    |
|                        |                        | ``session``, it acts as a session fixture but only if this setup   |
|                        |                        | appears in the executor tree. If the **execution-level** is        |
|                        |                        | ``setup`` or lower, the fixture is called only when the setup is   |
|                        |                        | active during the test run.                                        |
+------------------------+------------------------+--------------------------------------------------------------------+
| as method in           | only in this scenario  | This fixture runs only if the scenario where it is defined is      |
| :ref:`Scenarios`       |                        | executed in the current test run. If the **execution-level** is    |
|                        |                        | ``session`` or ``setup``, it acts as a session or setup fixture    |
|                        |                        | but only if this scenario appears in the executor tree. If the     |
|                        |                        | **execution-level** is ``scenario`` or lower, the fixture is       |
|                        |                        | called only when the scenario is active during the test run.       |
+------------------------+------------------------+--------------------------------------------------------------------+

Reference fixtures
==================

As mentioned earlier, Balder allows fixtures to reference one another.

Sometimes, you may want to use values from certain fixtures in your test cases or in other fixtures. For example, if
you prepare an object in one fixture, you might need to access that object in another fixture or directly in a test
case. In Balder, this is achieved simply by referencing fixtures through function or method parameters.

.. code-block:: python

    # file `balderglob.py`

    import balder

    class MyWorker:

        def prepare_it(self):
            self.workload = do_something()

        def work(self):
            self.workload.pop(0)

    @balder.fixture(scope="session")
    def prepared_worker():
        obj = MyObject()
        obj.prepare_it()
        yield obj

    @balder.fixture(scope="testcase")
    def do_one_work(prepared_worker):
        workload = prepared_worker.work()


As you can see, fixtures from other **execution-levels** can be referenced simply by adding the fixture's function name
as a parameter in your function or method. This approach works for fixtures that share the same **execution-level** and
**definition-scope**, but also for those with different **execution-levels** and/or **definition-scopes**. The key
requirement is that the referenced fixture must have executed before the one that depends on it.

.. note::

    If you only want to influence the ordering of fixtures within the same **execution level** and **definition scope**,
    you can reference them in a similar way. This always affects the order, because a referenced fixture must run before
    the one that depends on it.

    Of course, this ordering influence only works for fixtures that share the same **execution-level** and
    **definition-scope**. It's not possible to specify that a fixture at the scenario level should run before one at
    the setup level.

In addition to referencing fixtures with one another, you can also access their return values directly from a test
method. Let's take a look at the following example:

.. code-block:: python

    # file `scenarios/scenario_work.py`

    import balder

    class ScenarioWork(balder.Scenario):

        class MyDevice(balder.Device):
            ...
        ...

        def test_worker(self, prepared_worker):
            ...
            new_workload = prepared_worker.work()
            ...

In this example, we're using the previously defined fixture ``prepared_worker``, which is located in the
``balderglob.py`` file. The test method receives the instantiated ``MyObject`` from it.

.. note::
    You can also define a class method or static method as a fixture. Balder automatically detects this and handles
    the ``self`` or ``cls`` parameters correctly.

You can reference fixtures defined in different locations and even access them directly from your test methods. However,
be careful when referencing fixtures that have different **execution-levels** and/or different **definition-scopes**.
It doesn't make sense to reference a fixture with a deeper **execution-level** from one with a higher level. Take a
look at the following NOT WORKING example:

.. code-block:: python

    # file `balderglob.py`

    # BE CAREFUL: THIS EXAMPLE LEADS TO AN ERROR!

    import balder

    static_counter = 1

    @balder.fixture(level="testcase")
    def calc_add():
        static_counter += 1
        yield static_counter + 3

    @balder.fixture(level="session")
    def print_result(calc_add):
        print("the result is {}".format(calc_add))

In the non-working example above, it attempts to reference a fixture with ``level="testcase"`` from a fixture with
``level="session"``. This doesn't make sense, because the session-level fixture runs only once at the start of the test
session, while the testcase-level fixture runs multiple times (once before and after each test case). As a result, the
session fixture can't reliably access values from something that hasn't executed yet or that changes per test case.

A similar issue can arise if you try to reference a fixture from a **definition-scope** that is narrower (more specific)
than the **definition-scope** of the fixture doing the referencing. For example, assume we have the following fixtures
defined:

.. code-block:: python

    # file `scenarios/scenario_specific.py`

    import balder

    class ScenarioSpecific(balder.Scenario):

        scenario_testcase_cnt = 0

        ...

        @balder.fixture(scope="testcase")
        def calc_multiply(self):
            self.scenario_testcase_cnt += 1

Now, suppose we want to reference the calc_multiply() fixture from a broader **definition-scope**, such as in our
setup class:

.. code-block:: python

    # file `setups/setup_base.py`

    # BE CAREFUL: THIS EXAMPLE LEADS TO AN ERROR!

    import balder

    class SetupBase(balder.Setup):

        ...

        @balder.fixture(scope="testcase")
        def prepare_device(self, calc_multiply):
            self.MyDevice.setup(calc_multiply)


In this example, we're trying to access a fixture that's defined in a more specific **definition-scope** than the one
doing the referencing. This won't work, because another :class:`Scenario <Scenario>` could also match with our
``SetupBase`` here. In such a case, we would end up with results from two different ``calc_multiply`` fixtures during
a single setup run, which won't work. Therefore, you need to ensure that the fixtures you reference have already
executed before the one that is doing the referencing.


Name conflicts
--------------

You might wonder what happens if there are fixtures with the same name and you want to reference them. For example,
suppose you define a fixture named ``calc`` in your global ``balderglob.py`` file, and you're using a
:class:`Scenario <Scenario>` that also defines a fixture called ``calc``. Now, if you want to reference ``calc`` within
a test method of that scenario, which value will be provided?

First, Balder will execute every fixture, regardless of whether they share the same name. The name only matters when
you're referencing these fixtures.

It might become clearer if we look at the following example:

.. code-block:: python

    # file `scenarios/scenario_my.py`

    import balder

    class ScenarioMy(balder.Scenario):

        ...

        @balder.fixture(scope="testcase")
        def calc(self):
            yield 3 * 5

Now, suppose we have a fixture with the same name defined in our global ``balderglob.py`` file:

.. code-block:: python

    # file `balderglob.py`

    import balder

    @balder.fixture(scope="testcase")
    def calc():
        yield 3 * 1

Both fixtures have the same name ``calc`` and the same **execution-level**. The **definition-scope** doesn't affect the
execution order of the fixtures as long as they aren't referenced by each other. In that case, Balder can run them in
any sequence it chooses. However, things change when you do reference these fixtures. If you have two fixtures with the
same **execution-level** and the same name but different **definition-scopes**, Balder selects the appropriate one based
on their **definition-scopes**.

For example, if you reference the ``calc`` fixture from another fixture in the ``balderglob.py`` file, Balder will use
the one with the broadest scope (the global one, in this case):

.. code-block:: python

    # file `balderglob.py`

    import balder

    @balder.fixture(scope="testcase")
    def calc():
        yield 3 * 1

    @balder.fixture(scope="testcase")
    def print_my_thing(calc):
        print("print_my_thing from balderglob.py: calculation is {}".format(calc))

This will print the following output:

.. code-block:: none

    print_my_thing from balderglob.py: calculation is 3

But which fixture will be used if we reference ``calc`` from a fixture in our setup class (assuming it matches with our
``ScenarioMy``)?

.. code-block:: python

    # file `setups/setup_main.py`

    import balder

    class SetupMain(balder.Setup):

        ...

        @balder.fixture(scope="testcase")
        def print_it(self, calc):
            print("print_it from setup: calculation is {}".format(calc))


Balder will first search for a fixture named ``calc`` within the ``SetupMain`` class itself. If none exists there, it
moves upward through the **definition-scope** hierarchy until it finds one. In our example, this means it would use the
``calc`` fixture from the ``balderglob.py`` file here as well.

.. code-block:: none

    print_it from setup: calculation is 3

The behavior changes if you reference ``calc`` from another fixture within our ``ScenarioMy`` class:

.. code-block:: python

    # file `scenarios/scenario_my.py`

    import balder

    class ScenarioFromBalderhub(balder.Scenario):

        ...

        @balder.fixture(scope="testcase")
        def calc(self):
            yield 3 * 5

        def print_my_calc(self, calc):
            print("print_it from scenario: calculation is {}".format(calc))

Similar to the process described above, Balder first searches in the scenario's **definition-scope**, then in the
matched setup's **definition-scope** (only the currently active one), and finally in the global scope
(the balderglob.py file) for the referenced fixture. In this case, the closest fixture with the matching name is found
in the same definition scope - the ``ScenarioMy`` class itself.

This produces the following output:

.. code-block:: none

    print_it from scenario: calculation is 15

Special case: Unclear-Setup-Scoped-Fixture-Reference problematic
----------------------------------------------------------------

There's one specific case you should be aware of: attempting to reference a session-level fixture with a
**definition scope** of SETUP from a session-level fixture with a definition scope of SCENARIO. In this situation,
it's unclear which setup Balder should use, since no setup is active yet (we're still at the SESSION level).

This should be avoided. Balder will throw an :class:`UnclearSetupScopedFixtureReference` exception in such cases!

.. note::
    Note that you can freely define fixtures at any of these execution levels, but you need to be careful, when you are
    trying to reference the levels themselves.
