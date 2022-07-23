# Balder Testsystem

This directory contains a lot of different tests, that will be used to validate the Balder testsystem. As main test
framework, we use [pytest](http://pytest.org/) here.
But why? - In the most testcases we want to test that the whole balder procedure (COLLECTING-SOLVING-EXECUTING) works 
as expected. With that we execute every test run in an own python subprocess. This makes it possible for us to simulate 
a clean-up python run. In the most cases, we use pytest only to trigger these subprocesses.

## Functionality

In this directory you find a lot of different tests, which all are constructed in a special structure. You can find 
different deeply nested directories that always ends in a directory that starts with ``test_*``, which contains a python 
file with the same name. For example:

```

|- tests/
   |- general/
      |- test_connections/
         |- env/
            |- scenarios.py
            |- setups.py
            |- connections.py
         |- test_connections.py

```

The python file ``test_connections.py`` can contain any number of test functions or test classes. If the testfile wants 
to use a special balder environment, the directory has a subdirectory ``env/``. This directory contains the balder
environment under test. In the example above you only see a basic structure, but you can freely expand it. In background 
the helper fixture function (that will be introduced later) calls balder in the working directory ``env/``. So you can 
provide all scenarios, setups and other objects you want to use in your simulated environment.

## The basic directory

The `tests` directory has a subdirectory `basic`, that provides the basic environments the balder tests use. You find an
example implementation, we expect that it always works with balder. Every different environment has an own id 
(``test_{id}_*``). Every other test that builds on these environments has the same id and a description about the 
changes that were done for the current test in contrast to the standard implementation.

## Call Balder

If you want to run balder in a testcase, it is really recommended doing this in a separate process. This helps to 
separate namespace and import paths. Often the following implementation is used:

```python
from multiprocessing import Process
from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

def test_example(balder_working_dir):
    """
    ...
    """
    proc = Process(target=processed, args=(balder_working_dir, ))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):
    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    session.run()
    print("\n")

    assert session.executor_tree.executor_result == ResultState.SUCCESS, \
        "test session does not terminates with success"

```

In this example code, the `test_example` is the test method. It executes a process function `processed`. With this 
processed function balder will be executed and all results will be evaluated. The pytest function `test_example` only 
evaluates if the processed function was executed successfully.

The ``balder_working_dir`` attribute is a [pytest fixture](https://docs.pytest.org/en/latest/explanation/fixtures.html) 
that returns the current environment path for the current test function.

This structure can be used for the most testcases.