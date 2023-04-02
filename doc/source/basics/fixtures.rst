Fixtures
********

.. important::

    .. todo complete reworking of this section

    Please note that this part of the documentation is not yet finished. It will still be revised and updated.

Fixtures are functions or methods that ensure that code is executed before or after specific times of a test run.
Fixtures can be executed at different times in the Balder process (**execution-level**) and can be defined on different
positions (**definition-scope**). The order, in which these fixtures will be executed, can be influenced by chained
dependencies too. You can learn more about this in this section.

A simple fixture
================

It is very easy to define a fixture. Simply create a function and add the ``@balder.fixture()`` decorator to it.

.. code-block:: py

    # file balderglob.py

    @balder.fixture(level='session')
    def my_own_fixture():
        print("is executed before the test session")
        yield
        print("will be executed after the test session")

In the example above, we use the decorator ``@balder.fixture(level='session')`` with the argument ``level``. This
defines the **execution-level** of the fixture. It describes on which position the fixture will be executed. We placed
this fixture in the global ``balderglob.py`` file, which secures that the fixture will always be executed. A fixture
has the most extensive validity if it is in the global ``balderglob.py`` file. With this, it will be used in every
scenario/setup variation.

What does this fixture do now? The passed parameter ``level="session"`` specifies that the fixture will finally be
executed only once for the session. A fixture with ``level="session"`` will be called once directly after the test
session starts.

But what does the ``yield`` command do? A fixture usually has two code sections that are separated with the python
command ``yield``. The code before the ``yield`` will be executed before the test-branch runs. It's the **construct**
part of the fixture. The code behind will be executed after the branch ran itself. This is the so called **teardown**.

.. note::

    You can also omit the ``yield`` command. But with this, Balder assumes that no teardown code is available.

Execution-Level
---------------

The decorator ``@balder.fixture(level="session")`` defines a fixture function that will be executed on the
``session`` level, which means that the fixture will run before the test session starts (construct-part) and after
it ends (teardown-part). There are a lot of different other levels you can use with your fixture. For example, if you
need a fixture that reads some logs from a device after every testcase was executed, you can define one with the
**execution-level** ``'testcase'``. This will be executed before and after every relevant testcase. You can find more
information about the **execution-level** in the section :ref:`Execution-Level possibilities`.

Definition-Scope
----------------

The **definition-scope** describes the validity of the fixture. It depends on the definition position, the fixture is
located in the Balder testsystem. For example, if you implement a fixture in the global ``balderglob.py`` file, it has
the **definition-scope** GLOBAL. This means, that it is valid for the whole test session. It is valid for every testcase
that is executed within a test session. If a fixture (that is defined in the ``balderglob.py`` file) has the decorator
``@balder.fixture(level="session")`` it will always be executed, independent of the :ref:`Scenario <Scenarios>` and
independent which :ref:`Setup <Setups>` or variation matches. If the fixture has
the decorator ``@balder.fixture(level="scenario")``, but is still defined in the ``balderglob.py`` file, it has a
different **execution-level** but it keeps the power to be executed in any available :ref:`Scenario <Scenarios>`.

The situation differs when you define the fixture in a single :ref:`Scenario <Scenarios>`. Let's just call this
scenario ``ScenarioA``. In addition, we have another scenario ``ScenarioB``. We add a decorator with a ``session``
**execution-level** (decorator `@balder.fixture(level="session")`) to the fixture method in our ``ScenarioA``. Now we
call our test environment without any scenario filter. Our fixture will be called at session level. If we now add a
scenario filter and only activate our ``ScenarioA``, we have the same situation. But if we trigger a run, that only
uses the ``ScenarioB`` this behavior will change. In this case our fixture won't be called, because our
**definition-scope** is not active (fixture is defined in the not executed ``ScenarioA``).

You can find more detailed information about the **definition-scope** at the
:ref:`Definition-Scopes <Definition-Scope possibilities>`.

Fixture ordering
----------------

Like you saw in the earlier sections, it is due to two important characteristics, when and how a fixture will be
executed - the **execution-level**, which is defined at the fixture decorator and the **definition-scope**, which is
defined over the location the fixture is placed in. But how does Balder order the fixtures that are within the same
**execution-level**?

First of all, Balder creates a outer ordering by its **definition-scope**. Before the scenario-scoped-fixtures (defined
within a :class:`Scenario <Scenario>` class) will be executed, the setup-scoped-fixtures (defined in the
:class:`Setup <Setup>` class) will run. Global-fixtures (defined in the global ``balderglob.py`` file) will be executed
before them both. With this mechanism we have a basic ordering, but the order for fixture with the same
**definition-scope** (and of course the same **execution-level**) is still undefined. For this Balder provides the
ability of chaining fixtures with each other.

Take a look at the following example:


.. code-block:: py

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

.. code-block::

    Fixture1: is executed before the test session
    Fixture2: is executed before the test session

    ... further outputs of test run

    Fixture2: will be executed after the test session
    Fixture1: will be executed after the test session

The fixture ``my_own_fixture2`` references the ``my_own_fixture1``, by using the same name as function argument name.
With this definition it is clear, that the ``my_own_fixture1`` has to run before ``my_own_fixture2``. If you
wouldn't provide this chaining attribute Balder will select the ordering by itself. This is also ok, because sometimes
it simply doesn't matter which fixture runs first.

Referencing other fixtures
---------------------------

If you reference another fixture like mentioned above you need access to its return value.

Now let's look at the previous example again with a small change:

.. code-block:: py

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

We now calculate some value within the ``my_own_fixture1`` construct part and return it with the ``yield`` keyword. The
value will be given to the parameter ``my_own_fixture1`` of the fixture ``my_own_fixture2(my_own_fixture1)`` and can
directly be used there. This example would produce the following output:

.. code-block: cmd

    Fixture1: is executed before the test session
    Fixture2: is executed before the test session - value of Fixture 1 is `42`

    ... further outputs of test run

    Fixture2: will be executed after the test session
    Fixture1: will be executed after the test session

You can also refer fixtures from another **execution-level** or **definition-scope**, but you have to secure that your
referred fixture runs before the fixture that references it. For more information about the referencing of fixtures and
the related ordering, see :ref:`reference fixtures`.

Execution-Level possibilities
=============================

Balder supports different levels that can be assigned to a fixture. Because Balder is a scenario-based test system and
these scenarios can be run under certain setups, there are several levels where you can zoom in during a test
execution. The following table shows all possible **execution-level** attributes:

+------------------------+---------------------------------------------------------------------------------------------+
| level                  | description                                                                                 |
+========================+=============================================================================================+
| ``session``            | This is the furthest out execution-level. The construct part of the fixture will be         |
|                        | executed directly after the collecting and solving process, but before some user code runs. |
|                        | The teardown code will be executed after the whole test session was executed.               |
+------------------------+---------------------------------------------------------------------------------------------+
| ``setup``              | Depending on the **definition-scope** this fixture runs after every or specific             |
|                        | :ref:`Setup <Setups>` change. It embraces every new :ref:`Setup <Setups>` class that will   |
|                        | be get active in the test executor.                                                         |
+------------------------+---------------------------------------------------------------------------------------------+
| ``scenario``           | Depending on the **definition-scope** this fixture runs after every or specific             |
|                        | :ref:`Scenario <Scenarios>` changes. It embraces every new :class:`Setup <Setups>` class    |
|                        | that will be get active in the test executor.                                               |
+------------------------+---------------------------------------------------------------------------------------------+
| ``variation``          | The **variation** in the Balder test system is a new possible device assignment between the |
|                        | :ref:`Scenario-Devices <Scenario-Device>` and the :ref:`Setup-Devices <Setup-Device>`.      |
|                        | Depending on the **definition-scope** this fixture runs before and after every new device   |
|                        | variation of its scoped :ref:`Setup <Setups>` / :ref:`Scenario <Scenarios>` constellation.  |
+------------------------+---------------------------------------------------------------------------------------------+
| ``testcase``           | Depending on the **definition-scope** this fixture runs after every or specific testmethod. |
|                        | It embraces every new testcase which is defined in the :ref:`Scenario <Scenarios>` class    |
|                        | that is in the defined **definition-scope**.                                                |
+------------------------+---------------------------------------------------------------------------------------------+

Definition-Scope possibilities
==============================

Balder has three different **definition-scopes**. These scopes define the validity of the fixtures.

The following table shows these scopes:

+------------------------+------------------------+--------------------------------------------------------------------+
| Definition             | Validity               | description                                                        |
+========================+========================+====================================================================+
| as function in         | everywhere             | This fixture will always be executed. It doesn't matter which      |
| ``balderglob.py`` file |                        | specific testset is called. This fixture will be executed in       |
|                        |                        | every test run.                                                    |
+------------------------+------------------------+--------------------------------------------------------------------+
| as method in           | only in this setup     | This fixture runs only if the setup (the fixture is defined in)    |
|                        |                        | will be executed in the current testrun. If the                    |
| :ref:`Setups`          |                        | **execution-level** is ``session`` it will be executed as          |
|                        |                        | session-fixture only if this setup is in the executor tree. If the |
|                        |                        | **execution-level** is ``setup`` or lower, this fixture will only  |
|                        |                        | be called if the setup is currently active in the test run.        |
+------------------------+------------------------+--------------------------------------------------------------------+
| as method in           | only in this scenario  | This fixture runs only if the scenario (the fixture is defined in) |
| :ref:`Scenarios`       |                        | will be executed in the current testrun. If the                    |
|                        |                        | **execution-level** is ``session`` or `setup` it will be executed  |
|                        |                        | as session-/ or setup-fixture only if this scenario is in the      |
|                        |                        | executor tree. If the  **execution-level** is ``scenario`` or      |
|                        |                        | lower, this fixture will only be called if the scenario is         |
|                        |                        | currently active in the test run.                                  |
+------------------------+------------------------+--------------------------------------------------------------------+

Reference fixtures
==================

As mentioned above, Balder can reference fixtures among each other.

Sometimes you want to use the values of some fixtures in testcases or other fixtures. For example if you prepare an
object in a fixture you maybe want to use this object in another fixture or in your testcase too. This can be
realized in Balder by simply referencing fixtures through method/function attributes.

.. code-block:: py

    # file `balderglob.py`

    import balder

    class MyWorker:
        def prepare_it(self): self.workload = do_something()
        def work(): self.workload.pop(0)

    @balder.fixture(scope="session")
    def prepared_worker():
        obj = MyObject()
        obj.prepare_it()
        yield obj

    @balder.fixture(scope="testcase")
    def do_one_work(prepared_worker):
        workload = prepared_worker.work()

As you can see other fixtures can be referenced from another **execution-level** by simply add the fixture function name
as parameter at the function/method. This works for fixtures within the same **execution-level** and
**definition-scope**, but also for fixtures that have different **execution-levels** and/or **definition-scopes**. It is
only important, that the fixture you reference, was executed before.

.. note::

    If you only want to influence the fixture ordering with-in the same **execution-level** and **definition-scope**
    you can also reference them in the similar way. It always influence the ordering, because a referenced fixture has
    to run before the fixture that references it.

    Of course the order influence only works for fixtures with the same **execution-level** and **definition-scope**.
    It is not possible to define that a fixture with SCENARIO LEVEL should run before a fixture with SETUP LEVEL.

In addition to referencing fixtures with each other, you can also access the return value from a test method. Let's take
a look at the next scenario:

.. code-block:: py

    # file `scenario_work/scenario_work.py`

    import balder

    class ScenarioWork(balder.Scenario):

        class MyDevice(balder.Device):
            ...
        ...

        def test_worker(self, prepared_worker):
            ...
            new_workload = prepared_worker.work()
            ...

This example now uses the previous defined fixture ``prepared_worker``, that is defined in the ``balderglob.py`` file.
The test gets the instantiated ``NewObject`` here.

.. note::
    You can also define a class- or a staticmethod as fixture. Balder automatically detects that, and will manage the
    ``self`` or ``cls`` attributes correctly.

You can reference fixtures from different places and also reference them from your test method. But be careful while
referencing fixtures from different **execution-levels** or/and **definition-scopes**. It doesn't make sense to
reference a fixture with an deeper **execution-level** from a fixture with a higher one. Take a look at the following
example:

.. code-block:: py

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

In the NOT WORKING example above, it is tried to reference a fixture with ``level="testcase"`` from a fixture with
``level="session"``. This doesn't make sense, because the fixture ``print_result`` will only be executed once in the
beginning of the test session.

The same problem can occur if you try to refer a fixture from an **definition-scope** that is more specific than the
**definition-scope** of the fixture that references it. For example, assume we have the following fixtures defined:

.. code-block:: py

    # file `scenario_specific/scenario_specific.py`

    # BE CAREFUL: THIS EXAMPLE LEADS TO AN ERROR!

    import balder

    class ScenarioSpecific(balder.Scenario):

        scenario_testcase_cnt = 0

        ...

        @balder.fixture(scope="testcase")
        def calc_multiply(self):
            self.scenario_testcase_cnt += 1

Now we want to reference the ``calc_multiply()`` fixture from a higher  **definition-scope** like our setup class:

.. code-block:: py

    # file `setup_base/setup_base.py`

    # BE CAREFUL: THIS EXAMPLE LEADS TO AN ERROR!

    import balder

    class SetupBase(balder.Setup):

        ...

        @balder.fixture(scope="testcase")
        def prepare_device(self, calc_multiply):
            self.MyDevice.setup(calc_multiply)

We try to access a fixture that is defined in a more specific **definition-scope** than the referencing fixture. This
can not work, because it would be possible that another :class:`Scenario` matches with our ``SetupBase`` here too. This
other :class:`Scenario` maybe has no ``calc_multiply`` fixture.


Name conflicts
--------------

Maybe you wonder what should we do if there are some fixtures with the same name and we want to
reference them? For example if you define a fixture ``calc`` in your global ``balderglob.py`` file, while you use a
:class:`Scenario` which has a fixture ``calc`` defined too. Now you want to reference `calc` within the test method of
this scenario. Which value will be provided?

First of all, every fixture will be called by Balder. It won't matter if they have the same name. The name will only
matter if you want to referencing these fixtures. Maybe it will be getting clearer if we take a look at the following
example:

.. code-block:: py

    # file `scenario_my/scenario_my.py`

    import balder

    class ScenarioMy(balder.Scenario):

        ...

        @balder.fixture(scope="testcase")
        def calc(self):
            yield 3 * 5

Now we have a fixture with the same name in our global ``balderglob.py`` file:

.. code-block:: py

    # file `balderglob.py`

    import balder

    @balder.fixture(scope="testcase")
    def calc():
        yield 3 * 1

Both fixtures have the same name ``calc`` and the same **execution-level**. First of all the **definition-scope**
doesn't matter for the executed ordering of the fixtures as long as they are not referenced among each other. If you
reference them, Balder will be forced to adjust the order of them. However, the situation is different if you reference
these fixtures. If you have two fixtures with the same **execution-level** and with the same name, but different
**definition-scopes**, Balder will select them according their **definition-scope**.

For example, if you referencing the ``calc`` fixture from another fixture in the ``balderglob.py`` file, it
will call the next higher one (related to the **definition-scope**):

.. code-block::

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

But which fixture will be used if we reference it from our setup (matches with our ``ScenarioMy``):

.. code-block:: py

    # file `setup_main/setup_main.py`

    import balder

    class SetupMain(balder.Setup):

        ...

        @balder.fixture(scope="testcase")
        def print_it(self, calc):
            print("print_it from setup: calculation is {}".format(calc))

It will search for a fixture in the ``SetupMain`` first. There is no one, so it goes the **definition-scope**
upwards, till it finds some. In our example it would call the ``calc`` of ``balderglob.py`` here too:

.. code-block:: none

    print_it from setup: calculation is 3

The behavior differs if you reference ``calc`` from another fixture in our ``ScenarioMy``:

.. code-block:: py

    # file `scenario_my/scenario_my.py`

    import balder

    class ScenarioFromBalderhub(balder.Scenario):

        ...

        @balder.fixture(scope="testcase")
        def calc(self):
            yield 3 * 5

        def print_my_calc(self, calc):
            print("print_it from scenario: calculation is {}".format(calc))

Similar to the procedure described above, it would first search in the SCENARIO definition scope, then in the matched
SETUP definition scope (only the current matched one is possible) and last but not least it searches in the BALDERGLOB
for the referenced fixture. In this case here, the next fixture with the referenced name is in the same
**definition-scope**, the ``ScenarioMy`` itself. This results in the following output:

.. code-block:: none

    print_it from scenario: calculation is 15

Special case: Unclear-Setup-Scoped-Fixture-Reference problematic
----------------------------------------------------------------

There is one single case, you should be aware with. If you want to reference a session-fixture
with the **definition-scope** SETUP from a session-fixture with the **definition-level** SCENARIO. For this case it is
not clear which setup Balder should use, because no setup is active yet (we are still on SESSION level).

This should be avoided and not use. Balder will throw an exception :class:`UnclearSetupScopedFixtureReference` here!

.. note::
    Note that you can freely implement these fixture levels, but you could not reference them.