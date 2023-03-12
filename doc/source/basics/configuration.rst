Configure Balder
****************

.. important::

    .. todo complete reworking of this section

    Please note that this part of the documentation is not yet finished. It will still be revised and updated.

Console arguments
=================

Balder provides a lot of different console arguments. You can get an overview by calling:

.. code-block:: none

    $ balder --help


BalderSettings object
=====================

You can specify different settings in a :class:`BalderSetting` class in your ``balderglob.py`` file. For this you have
to create a new class inside the ``balderglob.py`` file, that inherits from :class:`BalderSetting`.

.. code-block:: python

    # file `balderglob.py`
    import balder
    ...

    class MySettings(balder.BalderSetting):
        ...
        used_global_connection_tree = "my-own-tree"
        ...

BalderPlugin object
===================

You can also influence the mechanism of Balder by developing Balder plugins. For this Balder has a global plugin object
that allows to interact with different callbacks. This helps you to influence the mechanism of the Balder system.

.. note::
    The plugin section is still under development. We will integrate and add new callbacks soon!

..
    .. todo

If you want to create and use a Balder plugin, simply create a new child object of :class:`BalderPlugin` and include it
in the global ``balderglob.py`` file:

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

If you only want to use a third-party-plugin, you only have to install it and import the plugin class into your
``balderglob.py`` file.

.. code-block:: python

    # file `balderglob.py`
    import balder
    ...
    from my.third.party.plugin import MyPluginClass


The following shows the documentation of the :class:`BalderPlugin` object:

.. autofunction:: balder.BalderPlugin
    :noindex:
