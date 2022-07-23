Balder process
**************

This section describes the process how balder executes a test session and which steps it passes during it.

.. warning::
    Please note: This section is currently under development and will be released shortly!

..
    .. todo

First of all, it will collect the test data in the ``Collecting`` process. Afterwards it starts the ``Resolving`` of
all collected data. It tries to find matchings between :ref:`Setups` and :ref:`Scenarios` and their related
:ref:`Devices`. After this step has completed, balder tries to create its most important object, the
:class:`.ExecutorTree`. This object contains the whole session data organized in different specialized executor objects.
