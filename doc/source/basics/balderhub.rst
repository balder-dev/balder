BalderHub - the share place of tests
************************************

Balder's grand vision is to create a shared space for open-source testing projects. We call them **BalderHub** packages.
These packages are standard Python packages that you can install as usual and easily integrate into your specific
project. This allows you to reuse existing scenario (mostly with ready-to-use test cases) and feature implementations
on your own. You only need to provide custom implementations for the parts that truly depend on your specific device /
application, without recreating the general test logic.

Along the way, these ``balderhub-*`` packages also provide common implementations, so you only need to write your
application-specific code while reusing various test devices. The idea is that you can access a wide range of
different tests that clever minds have already thought through. You simply inherit from their scenarios, add the
specific setup-device feature code for your device, and get started.

Have a look at our `BalderHub Entry Page <https://hub.balder.dev>`_, we already have packages packages for web tests
or even embedded device tests. Check it out.

Contribute
==========

Imagine unlocking a treasure trove of ready-made tests that supercharge your development pipeline - welcome to the
power of **BalderHub projects**. These open-source marvels, crafted by a passionate community, deliver reusable
scenarios and setups for everything from URL handling and web interactions to remote protocols like RFB and SNMP,
all installable like any Python package. By harnessing BalderHub, you not only slash development time and boost
test consistency across platforms but also become part of a collaborative cosmos where ideas evolve, innovations
thrive, and testing transforms from a chore into a shared adventure.

Ready to contribute your own project or explore what's out there? Dive in and help shape the future of open-source
testing!

.. note::

    We are just at the beginning.

    Do you know one area really well? Do you like the concept of Balder? Think about initiating your own BalderHub
    project. Take a look at our `Balder GitHub Group <https://github.com/balder-dev>`_ and feel free to contribute to
    an existing project or create your own. If you're not sure whether your topic already exists or if you're looking
    for colleagues to develop a BalderHub project together as a group, feel free to
    `create an issue <https://github.com/balder-dev/hub.balder.dev/issues>`_ or
    `start a new discussion <https://github.com/balder-dev/hub.balder.dev/discussions>`_.

    If you want to add your package to `the BalderHub projects <https://hub.balder.dev>`_, just ask for help by
    creating an issue in `the main hub project <https://github.com/balder-dev/hub.balder.dev/issues>`_.

Where can I search for?
=======================

All official BalderHub projects are part of the `BalderHub GitHub Group <https://github.com/balder-dev>`_ and are
displayed on the `BalderHub Entry Page <https://hub.balder.dev>`_ as well as under
``https://hub.balder.dev/projects/<your-project>``.

How can I use them?
===================

You can easily use a BalderHub project by installing it in your Python environment. To do this, simply use ``pip`` or
any other manager of your choice. Public BalderHub projects are published on `PyPI <https://pypi.org>`_.

Using BalderHub Scenarios
-------------------------

If you want to use a scenario from a BalderHub project, simply import it in any ``scenario_*.py`` file in your project,
as shown below:


.. code-block:: python

    # file tests/scenarios/scenario_for_me.py
    from balderhub.example.scenarios import ScenarioExample

By doing this, the entire scenario becomes active, and all the test methods from the ``ScenarioExample`` scenario will
be executed. Don't forget to provide an implementation for the features within your setup.


How create my own BalderHub project?
====================================

If you want to contribute to a existing BalderHub project or if you want to create a new BalderHub project, but still
have some questions, feel free to `create an issue <https://github.com/balder-dev/hub.balder.dev/issues>`_ or
`start a new discussion <https://github.com/balder-dev/hub.balder.dev/discussions>`_. Your contribution is really
appreciated.

If you want to contribute to an existing BalderHub project or create a new one but still have some questions, feel free
to `create an issue <https://github.com/balder-dev/hub.balder.dev/issues>`_ or
`start a new discussion <https://github.com/balder-dev/hub.balder.dev/discussions>`_. Any contribution is very much
appreciated.
