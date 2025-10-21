Configure Balder
****************

Balder is built to be highly customizable. You can limit the collection for different setups or scenarios, configure
it through the global ``balderglob.py`` file, and even create your own plugins.

Console arguments
=================

Balder offers many different command-line arguments. You can get an overview by running:

.. code-block:: shell

    $ balder --help

Changing the working directory
------------------------------

Normally, Balder assumes that your current directory is the working directory. If you want to change that, you can use
the command-line option ``--working-dir``:

.. code-block:: shell

    $ balder --working-dir <relative/absolute path to working director>

Limit the collected scenarios/setups
------------------------------------

Balder also allows you to limit the collection of scenarios and setups by using the CLI flags ``--only-with-scenario``
or ``--only-with-setup``. You can provide fixed strings for the path, but you can also use ``*`` to match any
characters of a file or directory name or ``**`` to match all directories and / or subdirectories.

The following command will consider all scenario files that have the filename ``scenario_one.py``, regardless of their
location:

.. code-block:: shell

    $ balder --only-with-scenario **/scenario_one.py

The following example will collect all setups located in the relative directory setups or its subdirectories with the
filename ``setup_example.py``:

.. code-block:: shell

    $ balder --only-with-setup setups/**/setup_example.py

Of course you can combine these both options:

.. code-block:: shell

    $ balder --only-with-scenario scenarios/login/** --only-with-setup setups/office1/*


BalderSettings object
=====================

You can specify different settings in a :class:`BalderSetting` class in your ``balderglob.py`` file. For this you have
to create a new class inside the ``balderglob.py`` file, that inherits from :class:`BalderSetting`.

You can specify various settings by defining a class in your ``balderglob.py`` file that inherits from
``BalderSetting``. To do this, simply create a new class inside the ``balderglob.py`` file and have it extend the
``BalderSetting`` base class.

.. code-block:: python

    # file `balderglob.py`
    import balder
    ...

    class MySettings(balder.BalderSetting):
        ...
        used_global_connection_tree = "my-own-tree"
        ...

The following overview lists all the settings available in the ``BalderSetting`` class:

.. autoclass:: balder.BalderSettings
    :noindex:
    :members:

BalderPlugin object
===================

You can also influence Balder's mechanisms by developing your own Balder plugins. To achieve this, Balder provides a
global plugin manager that allows you to register plugins and interact with various callbacks. This enables you to
customize and extend the overall behavior of the Balder system.

.. note::
    The plugin engine is still under development. If you need any additional callbacks, feel free to create a
    `GitHub Feature Request <https://github.com/balder-dev/balder/issues>`_

If you want to create and use a Balder plugin, simply define a new subclass of :class:`BalderPlugin` and include it in
your global ``balderglob.py`` file:

.. code-block:: python

    # file `balderglob.py`
    import balder
    ...

    class MyPlugin(balder.BalderPlugin):

        ...

        def modify_collected_pyfiles(self, pyfiles):
            ..
            return filtered_pyfiles

        ...

If you only want to use a third-party plugin, you simply need to install it and then import the plugin class into your
``balderglob.py`` file:

.. code-block:: python

    # file `balderglob.py`
    import balder
    ...
    from my.third.party.plugin import MyPluginClass


The following section provides documentation for the :class:`BalderPlugin` class:

.. autoclass:: balder.BalderPlugin
    :noindex:
    :members:
