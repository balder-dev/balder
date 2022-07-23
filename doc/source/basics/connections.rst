Connections
***********

:class:`Connection` objects can be used to define connections between :ref:`Scenario-Devices <Scenario-Device>` and
:ref:`Setup-Devices <Setup-Device>`. This allows to specify the connections you need (Scenario-Devices) or which
connections you have (Setup-Devices). So for example, if you have a scenario, that needs a serial connection between
two devices, it doesn't matter if your setup has both, a serial and an ethernet connection. However, the other way
around it does matter. If your scenario needs both, a serial and an ethernet connection, but your setup only has a
serial connection, it will not work.


Balder is a scenario based testsystem, for which it is necessary to determine if a
:ref:`Scenario <Scenarios>` matches with a :ref:`Setup <Setups>`. For this, in addition to the feature matching,
especially the :class:`Connection` trees between the devices are important.

This section shows the basic functionality of connections and how you can use them in the Balder ecosystem.

Global Connection-Trees
=======================

Internally balder knows exactly how the connections are arranged with each other. For this it refers to the global
connection-tree. For example, this tree defines that a :class:`TcpV4Connection` is based on an :class:`IPV4Connection`.
It also knows that a :class:`HttpConnection` is based on an :class:`TcpV4Connection` or an :class:`TcpV6Connection`.

The global connection tree holds all this relationships.

You can add your own connection object to that tree or also define a complete new tree by your own. You can find more
about this in the section `<Connection-Trees>`_.

Sub-Connection-Trees
====================

Every time you make a connection statement, you create a sub-connection tree. So for example, if you connect two devices
with each other over an :class:`HttpConnection`, this would be a sub-connection tree. A sub-connection-tree is always a
part of the global-connection-tree. This allows to make a short definition, by jumping over some other connections.

For example:

.. code-block:: python

    HttpConnection.based_on(IpV4Connection)

This statement is the same like the following:

.. code-block:: python

    HttpConnection.based_on(TcpV4Connection.based_on(IpV4Connection))

But why are these both statements the same? - the normal Balder global-connection-tree is defined like the following
structure:

.. code-block::

    IPV4Connection             IPV6Connection
          |                          |
       TcpV4Connection    TcpV6Connection
                    |        |
                  HttpConnection

Balder will automatically resolve UNRESOLVED sub-trees according to its current active global-connection-tree.

OR/AND Connection relations
===========================

You can combine connection objects with each other. This makes it possible that a connection is based on a connection or
on another connection (**OR**). So for example, a HTTP connection can be based on TcpV4 **OR** TcpV6:

.. code-block::

    conn = HttpConnection.based_on(TcpV4Connection, TcpV6Connection)

You can specify **OR** dependencies simply by providing a list of :class:`Connection` objects or as seen in our example
above, the most functions provides multiple arguments. These are always **OR** relationships.


It is also possible that a connection requires multiple other connections (**AND**). For example a
:class:`.DnsConnection` requires a :class:`UdpConnection` **AND** a :class:`TcpConnection`, because DNS uses UDP per
default, but it uses TCP for requests that sends data that is to much for UDP.

So we can define an AND connection simply by using tuples:

.. code-block::

    conn = DnsConnection.based_on((UdpConnection, TcpConnection))

Limits of connection-relations
------------------------------

You can define **AND**/**OR** definitions in almost any possible variation, but there is one limit.
It is not allowed to define **AND** connections that on the highest level, so for example:

.. code-block:: python

    # ALLOWED
    conn = SpecialConnection.based_on((AConnection, BConnection), CConnection)
    # NOT ALLOWED
    conn = SpecialConnection.based_on((AConnection, BConnection, (CConnection, DConnection)))

The last definition is not allowed because we use an inner **AND** connection there. We can write the same logic more
easier by refactor the **OR** and **AND** relations:

.. code-block:: python

    # same like the NOT ALLOWED tree from above - BUT NOW IT IS ALLOWED
    conn = SpecialConnection.based_on((AConnection, BConnection, CConnection), (AConnection, BConnection, DConnection)))

This limitation makes it easier to read the logic.

Using the base Connection object
================================

You can use the base Connection object for different use cases.

General Connection
------------------

If you want to specify that you need a connection, but it doesn't matter which connection type, you can use
the :class:`Connection` class.

.. code-block:: python

    conn = Connection()

This is the universal connection that describes a **can-be-everything** connection

**A general connection does never have based-on elements!**

Container Connection
--------------------

Sometimes you want to create a statement AConnection OR BConnection. This can easily defined with an container
connection:

.. code-block:: python

    conn = Connection.based_on(AConnection, BConnection)

**A container connection always has based-on elements**.

Defining your own Connection
============================

Balder allows to define own connections. For that you have to provide a `connections` module somewhere in your project.
Balder automatically looks into all existing modules with this name and loads all custom connections.

If you want to define your own connection class, you have to create a new class that inherits from the general
:class:`Connection` class:

.. code-block:: python

    # file `lib/connections.py`

    import balder
    import balder.connections as conns

    class MyConnection(balder.Connection):
        pass

This sets and enables the connection. But till now, it is inserted without some parent or child dependencies.

Inserting into the tree
-----------------------

You can insert your connection also in the global connection tree. For this you have to insert it with the decorator
``@balder.insert_into_tree(..)``. This decorator allows you to define parents of the connection. These dependencies will
be set globally for the whole Balder session. If you have a connection that is based on a TcpV4 connection, you can
implement this easily:

.. code-block:: python

    # file `lib/connections.py`

    import balder
    import balder.connections as conns

    @balder.insert_into_tree(parents=[conns.TcpConnection])
    class MyConnection(balder.Connection):
        pass

.. note::
    Note that we do not use inheritance to specify children connections. If you want to add a connection and insert it
    into the global connection tree, use the decorator ``@balder.insert_into_tree(..)``.

.. note::
    Note that you have to add the connection into a ``connections.py`` file or make it importable from a ``connections``
    module (directory ``connections`` with ``__init__.py`` file). It is only require that the module has the name
    ``connections``, but it doesn't matter where it is located inside your environment.

You are now able to use this connection. It is integrated in the project global connection tree.

Global-Connection-Tree
======================

In balder all connections are embedded in a so called global-connection-trees. This tree defines how the connections are
arranged to each other.

The global connection tree
--------------------------

Balder provides an global connection tree. This tree is already specified for all integrated connections objects (see
`<Connections API>`_). Per default Balder uses this pre-defined tree.

.. note::
    COMING SOON - We are working on a graphical tool to show this global-connection-tree.

..
    .. todo

Overwrite the default global tree
---------------------------------

Per default, the ``@balder.insert_into_tree(..)`` decorator inserted the connection in the global connection tree. If
you want to use another connection tree, you can specify the ``tree_name=".."`` argument in the
``@balder.insert_into_tree(..)``. This allows to specify an complete own connection tree by your own.

.. note::
    If you want to use your newly defined global tree, you have to set the property ``used_global_connection_tree``
    in the :class:`BalderSettings` object of your testenvironment to the same name!

.. note::
    If you define a global-connection-tree by your own, every pre-defined arrangement is not applicable anymore.

So let's take a look at the following example:

.. code-block:: python

    # file 'balderglob.py'

    import balder

    class Settings(balder.BalderSettings):
        used_global_connection_tree = 'my_project_one'

.. code-block:: python

    # file `lib/connections.py`
    import balder
    from balder import connections as conns

    @balder.insert_into_tree(parents=[conns.TcpConnection], tree_name="my_project_one")
    class MyTcpConnection():
        pass

.. warning::

    Be careful with changing the standard connection tree. With that, there is no connection included in the tree
    anymore, so you have to define every connection by yourself. If you use standard balder connections
    note that some BalderHub projects uses the original balder connections.

    If you want to change the tree dependencies for an existing tree, you can use the class method ``set_parents(..)``.

    .. code-block::

        from balder import connections as conns

        conns.DnsConnection.set_parents(
            parents=[(conns.UdpConnection, conns.TcpConnection)], tree_name="my_project_one")

What means CONTAINED-IN?
========================

.. warning::
    This section is still under development.

..
    .. todo