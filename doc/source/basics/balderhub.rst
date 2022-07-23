BalderHub - the share place of tests
************************************

.. note::
    The main navigation web page for BalderHub projects is currently under development, but will be released shortly.

Balder' grand vision is to create a open-source, share place for testing-projects. We call them ``BalderHub`` packages.
These packages are normal python packages. You can easily install them like normal python package and simply include
them into your specific project. That allows you to reuse scenario and feature implementation by your own. You only have
to provide your custom implementation that really depends on your device, but not the general test logic.


Along the way these ``BalderHub`` packages provide some common implementation too, so you only need to implement your
application specific code, but you can reuse different test devices. The idea is that you can access a wide range of
different tests where a lot of clever minds has already think about. You simply have to inherit from their scenarios,
add the specific setup-device feature code for your device and go for it. Different mock functions, helper devices or
complete testable implementations of remote devices (for example a dhcp server for dhcp-client tests) are already
provided in these balderhub project. This helps you and your team to develop test a lot of faster.

.. note::

    Balder is a very young project. Unfortunately, this also means that we do not have so many BalderHub projects at the
    moment.

    We need your help here. There are a lot of people in this world, that are experts in the thing they are doing and
    exactly these experts we need here.

    Do you know one area really well? Do you like the concept of balder? Think about to initiate an own
    BalderHub project. Take a look into our `Balder GitHub Group <ht>`_ and feel free to contribute to an existing
    project or create your own one. If you are not secure if your subject already exist or if you are searching for some
    colleagues to develop a BalderHub project within a group, fell free to
    `create an issue <ht>`_ or
    `start a new discussion <ht>`_.

    Of course you could develop the project by your own too. But if you want to release it, we would really like to add
    it into our group. Currently, we are working on a specific section in our documentation that should provide a big
    overview about all existing BalderHub projects. We will release this shortly. If you provide your package within the
    `Balder GitHub Group <ht>`_, we can secure to add your package as soon as possible. Of course you will remain
    maintainer of the project.

Where can I search for?
=======================

Our idea is that all public BalderHub packages are contained in our `BalderHub GitHub Group <ht>`_. Of course you
can create a package by your own too, but if you want to share it easily with the community it is the best way to
move your repository to our `BalderHub GitHub Group <ht>`_. With this it is also available on the
`official BalderHub <htp>`_ webpage (will be released shortly) and under ``https://hub.balder.dev/<your project>``.

How can I use them?
===================

You can use a BalderHub project easily by installing it into your python environment. For this you can use ``pip``. The
public BalderHub projects are published on `PyPi <https://pypi.org>`.

Which scenarios are used?
-------------------------

If you want to use a scenario of a BalderHub project, you have to create a new scenario class in your project and
inherit from the installed package. For example, if you want to use the scenario ``ScenarioExample`` of the
project ``balderhub-example``, you have to  create a new scenario file in your project and inherit from it:

.. code-block:: python

    # file tests/scenarios/scenario_for_me.py
    from balderhub.example.scenarios import ScenarioExample

    class ScenarioForMe(ScenarioExample):
        pass

With that the whole scenario will be active and all test methods of the inherited scenario ``ScenarioExample`` will be
used. Of course your setup-devices have to implement the features of the scenario-devices too.

..
    .. todo

..
    Limit test methods
    ------------------
    You can also limit test methods, by using the ``RUN``, ``SKIP`` and/or ``IGNORE`` class attributes. For example, the
    following code only executes the test method ``test_simple_add()``:
    .. code-block:: python
        # file tests/scenarios/scenario_for_me.py
        from balderhub.example.scenarios import ScenarioExample
        class ScenarioForMe(ScenarioExample):
            RUN = ['test_simple_add']
    You find our more about these class attributes at :ref:`Mark test to SKIP or IGNORE`.

How create my own BalderHub project?
====================================

If you want to contribute to a existing BalderHub project or if you want to create a new BalderHub project, feel free
to `create an issue <ht>`_ or `start a new discussion <ht>`_. Your contribution is really appreciated.
