# General EnvTester Environment

This ist the special METHOD-VARIATION EnvTester environment that helps to validate the balder architecture. This type
specially check that the method-variation works as expected. Same like the basic envtester environment, it provides a
``RuntimeObserver`` object in the ``balderglob.py`` file that allows to record the execution order.

## The basic balder environment

The structure depends on the testcase. This basic example contains three different setups and one scenario `ScenarioA`. 
All of them have two devices. The first device has all three features and is connected over the general `Connection` 
object with the other device. The VDevice assignable feature is always assigned to the second device of the scenario
and the setups. The scenario `ScenarioA` and every setup class match with each other.

The environment provides three similar setup classes. All of them assign another VDevice:
    
* `SetupI` assigns `VDeviceI` for `SetupI.SetupDevice2`
* `SetupII` assigns `VDeviceII` for `SetupII.SetupDevice2`
* `SetupIII` assigns `VDeviceIII` for `SetupIII.SetupDevice2`

The `SetupX.SetupDevice2` and `ScenarioA.ScenarioDevice2` uses an inherited chain of features on four levels.The parent 
feature `BaseMethVarFeature` is as pre scenario feature. Its child class (the `ScenarioMethVarFeature`) is instantiated 
in the scenario `ScenarioA`. The child class of the `ScenarioMethVarFeature` is the `BetweenMethVarFeature`, which is 
not directly instantiated. The last child class is the `SetupMethVarFeature`, which is instantiated in the `SetupA`.

This basic testcase has three different method variations, that are implemented on all four levels. The
class-based-decorator allows three different VDevices (all have another Feature), while their exists three different
method-variations. The chained features have only one method `do_something_as_var()`, which is implemented with 
different method variations for every vDevice. All other decorator for all vDevices are for the default 
:meth:`Connection` object.

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


## The base test class `Base01EnvtesterMethvarClass`

This is a base test class from which every test should inherit that wants to use this environment. This makes the test 
process much easier. Internally, this class provides an auto test method `test()` which manages the process and 
secures that the queue is available in the balder-process. 

You can simply inherit from this class and only overwrite the necessary methods, like shown below:

```python
from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.base_01_envtester_methvar_class import Base01EnvtesterMethvarClass


class Test01EnvtesterMethvar(Base01EnvtesterMethvarClass):

    @property
    def expected_data(self) -> tuple:
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},

            [
                (
                    # FIXTURE-CONSTRUCTION: SetupI.fixture_session
                    {"cls": "SetupI", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: SetupII.fixture_session
                    {"cls": "SetupII", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: SetupIII.fixture_session
                    {"cls": "SetupIII", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
                )
            ],
            ...,
            # FIXTURE-TEARDOWN: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "teardown"},
        )

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere (have to be SUCCESS everywhere)
        assert session.executor_tree.executor_result == ResultState.SUCCESS, \
            "test session does not terminates with success"

        ...

```

Everything else is automatically managed by the `Base01EnvtesterMethvarClass`

## The helper validation function ``compare_observed_list_with_expected``

The balder test directory has an own function ``compare_observed_list_with_expected``, that allows the validation of the
``RuntimeObserver`` entries with an own list of expected-values.

You can find this function at ``tests/test_utilities/observer_compare.py``.

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

