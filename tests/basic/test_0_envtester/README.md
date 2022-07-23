# General EnvTester Environment

This ist the basic EnvTester environment that helps to validate the balder architecture. It provides a
``RuntimeObserver`` object in the ``balderglob.py`` file that allows to record the execution order.

## The basic balder environment

The structure depends on the testcase. This basic example contains two setups and two scenarios. Both of them have two
devices. Every device has one feature and is connected over a self-created connection with the other device.

The ``ScenarioA`` matches with the ``SetupA`` and the ``ScenarioB`` matches with the ``SetupB`` because their devices
implements the correct features (exactly the same, no more and no less) and have the same connection they are connected
with each other.

## The ``RuntimeObserver`` object

The `RuntimeObserver` object provides a static method `add_entry(..)` that can be called to create a log entry. It 
automatically saves the record in the given order, and you are able to request them from your processed test function.

You can use the following code to reference the static object from your processed test function:

```python

import sys
...

# get the class instance from already imported module - balder loads it from given working directory
RuntimeObserver = getattr(sys.modules.get('env.balderglob'), "RuntimeObserver")
runtime_data = RuntimeObserver.data.copy()

```

## The helper validation function ``compare_observed_list_with_expected``

The balder test directory has an own function ``compare_observed_list_with_expected``, that allows the validation of the
``RuntimeObserver`` entries with an own list of expected-values.

You can find this function at ``tests/test_utilities/observer_compare.py``.

The validation should be done after the balder test session was executed. For the most cases the code looks like the 
following:

```python

import pathlib
import sys

from _balder.balder_session import BalderSession

from tests.test_utilities.observer_compare import compare_observed_list_with_expected

...


def processed(env_dir):
    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    session.run()
    print("\n")

    # get the class instance from already imported module - balder loads it from given working directory
    RuntimeObserver = getattr(sys.modules.get('env.balderglob'), "RuntimeObserver")
    runtime_data = RuntimeObserver.data.copy()

    # cleanup the data from `RuntimeObserver` and convert filepath to relative path
    exec_list = []
    for cur_data in runtime_data:
        new_data = cur_data.copy()
        new_data["file"] = pathlib.Path(new_data["file"]).relative_to(env_dir)
        exec_list.append(new_data)

    expected_data = (
        ...
    )

    compare_observed_list_with_expected(exec_list, expected_data)

```

### Entry of ``expected_data`` tuple

You can define single entries in your ``expected_data`` tuple, that describe which next ``add_entry`` call is expected. 
So for example, in this test environment the first ``RuntimeObserver.add_entry(..)`` call will be in the fixture
``balderglob.balderglob_fixture_session``. The code for this fixture looks like the following:

```python

import balder


@balder.fixture(level="session")
def balderglob_fixture_session():
    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_session, "begin execution CONSTRUCTION of fixture",
                              category="fixture", part="construction")
    yield
    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_session, "begin execution TEARDOWN of fixture",
                              category="fixture", part="teardown")

```

Now we can define an entry that describes that we expect this entry as first one to our ``expected_data`` tuple. Such 
an entry is always a dictionary that describes all properties the ``RuntimeObserver.add_entry`` call should have. For 
it to be considered successfully accepted, all the values of the ``expected_data`` dictionary have to be correct. So for 
the validation of our ``balderglob_fixture_session``, we could add the following entry:

```python

expected_data = (
    {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},
    ...
)
```

The execution of the validation function ``compare_observed_list_with_expected`` will check if the first entry of
``RuntimeObserver.add_entry`` was called within the file ``balderglob.py``. In addition to that, it checks that the 
given method is ``balderglob_fixture_session`` and the value given for ``part`` was ``construction``. If these three 
values are given in the ``expected_data`` dictionary, the function ``compare_observed_list_with_expected`` will accept 
this  execution step. Other values like the ``category`` will not be checked here, because they are not mentioned in the
dictionary.

### Structure of ``expected_data`` tuple

You can nest the ``expected_data`` list with lists (describes that the list elements will
follow, but the order of them is undefined) or with another tuples (collection with entries that has to be executed
in the given item order). With these items you can nest your ``expected_data`` tuple as deep as you want.

#### Dictionaries

As described before, dictionaries are single execution steps, that describe a single call of `add_entry`. All keys that
are mentioned in the dictionary, will be validated for the entry. All not given keys will be ignored here.

The dictionary could contain the following keys:

| Dictionary Key | Description                                                            |
|----------------|------------------------------------------------------------------------|
| ``file``       | describes the file in which the ``add_entry`` call was done            |
| ``cls``        | describes the class in which the ``add_entry`` call was done           |
| ``meth``       | describes the method/function in which the ``add_entry`` call was done |
| ``msg``        | describes the message that was given with the ``add_entry`` call       |
| ``category``   | describes the category that was given to ``add_entry``                 |
| ``part``       | describes the part that was given to``add_entry``                      |

#### Lists

With lists, it is possible to define a subset of next items, for which the order is not being fixed. Every direct list 
member has to be executed, but the order of them is not set yet.

For example the following definition allows two possible execution orders:

```python

expected_data = (
    [
        {"cls": "SetupA", "meth": "fixture_session", "part": "construction"},
        {"cls": "SetupB", "meth": "fixture_session", "part": "construction"},
    ]
    ...
)
```

For the ``compare_observed_list_with_expected`` there are two possible real executions:

* CONSTRUCTION part of ``SetupA.fixture_session``
* CONSTRUCTION part of ``SetupB.fixture_session``

OR

* CONSTRUCTION part of ``SetupB.fixture_session``
* CONSTRUCTION part of ``SetupA.fixture_session``

#### Tuples

Tuples are collections of execution steps. A tuple describes an element in which the items have to be executed in the
given order. These tuples will be used specially for list items, which have to be executed in a fixed order.

For example, if we also want to check that the feature-calls are done for every setup-scoped fixture and allow that the
setups can be executed in every possible order, we could use tuples for them.

```python

expected_data = (
    [
        (
            # FIXTURE-CONSTRUCTION: SetupA.fixture_session
            {"cls": "SetupA", "meth": "fixture_session", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
        ),
        (
            # FIXTURE-CONSTRUCTION: SetupB.fixture_session
            {"cls": "SetupB", "meth": "fixture_session", "part": "construction"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
        )
    ],
    ...
)
```

