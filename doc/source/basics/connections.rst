Connections
***********

:class:`Connection` objects can be used to define connections between :ref:`Scenario-Devices <Scenario-Device>` and
:ref:`Setup-Devices <Setup-Device>`. To do this, Balder provides many different connection objects, which are
organized within a so-called :ref:`Global-Connection-Tree <Global connection tree>`.

You can define sub-connection-trees from it to specify particular connections for scenario-devices or setup-devices. As
before, the connections defined for scenario-devices describe what is required, while the connections for setup-devices
describe what is available.

To run tests effectively, Balder must determine whether a :ref:`Scenario <Scenarios>` matches a :ref:`Setup <Setups>`,
also by validating these connections. In addition to feature matching, these connection trees between the devices are
particularly important for this process.

This section explains the basic functionality of connections and how you can use them in the Balder ecosystem.

Global connection-trees
=======================

Internally, Balder knows exactly how the connections are arranged relative to each other. To achieve this, it refers to
the global connection tree. For example, this tree defines that a :class:`TcpV4Connection` is based on an
:class:`IPv4Connection`. It also knows that a :class:`HttpConnection` is based on a :class:`TcpV4Connection` or a
:class:`TcpV6Connection`.

The global connection tree holds all these relationships.

You can add your own connection objects to this tree or define a completely new tree of your own. You can find more
about this in the section :ref:`Connection Trees <Global connection tree>`.

Sub-Connection-Trees
====================

Every time you define a connection between devices, you create a sub-connection tree. For example, if you connect two
devices using an :class:`HttpConnection`, this forms a sub-connection tree. A sub-connection tree is always a subset of
the global connection tree.

This approach lets you create concise definitions by skipping intermediate connections when they're not needed, for
example:

.. code-block:: python

    HttpConnection.based_on(IpV4Connection)

This statement is the same as the following:

.. code-block:: python

    HttpConnection.based_on(TcpV4Connection.based_on(IpV4Connection))

But why are these two statements the same? The standard Balder global connection tree is defined as shown in the
following structure:

.. code-block::

    IPV4Connection             IPV6Connection
          |                          |
       TcpV4Connection    TcpV6Connection
                    |        |
                  HttpConnection

Balder automatically resolves unresolved sub-connection trees based on the currently active global connection tree.

OR/AND connection relations
===========================

You can combine connection objects with each other. This allows a connection to be based on one connection or another
(**OR**). For example, an :class:`HttpConnection` can be based on either a :class:`TcpV4Connection` **OR** a
:class:`TcpV6Connection`:

.. code-block:: python

    conn = HttpConnection.based_on(TcpV4Connection | TcpV6Connection)

You can specify **OR** dependencies simply by chaining them with ``|``, as seen in our example above. Alternatively,
most functions accept multiple arguments, which are always treated as OR relationships.

It is also possible for a connection to require multiple other connections (**AND**). For example, a
:class:`DnsConnection` requires a :class:`UdpConnection` AND a :class:`TcpConnection`, because DNS uses UDP by default,
but it switches to TCP for requests that send data exceeding UDP's limits.

You can define an **AND** connection simply with:

.. code-block:: python

    conn = DnsConnection.based_on(UdpConnection & TcpConnection)

Using the base connection object
================================

You can use the base :class:`Connection` object for various use cases.

General connection
------------------

If you want to specify that a connection is required but the exact type doesn't matter, you can use the base
:class:`Connection` class.

.. code-block:: python

    conn = Connection()

This base class serves as a universal connection, representing any possible type of connection - it
**can-be-everything**.

**A general connection never has any based-on elements!**

Container connection
--------------------

If you use it with ``based_on()``, you are using it as a container connection.

.. code-block:: python

    conn = Connection.based_on(AConnection | BConnection)

**A container connection always has based-on elements**.

Defining your own connection
============================

Balder allows you to define custom connections. To do this, you need to provide a connections module somewhere in your
project. Balder automatically searches all existing modules with this name and loads any custom connections it finds.

If you want to define your own connection class, you need to create a new class that inherits from the base
:class:`Connection` class:

.. code-block:: python

    # file `lib/connections.py`

    import balder
    import balder.connections as conns

    class MyConnection(balder.Connection):
        pass

This defines and registers the connection. However, up to this point, it is added without any parent or child
dependencies.

Inserting into the tree
-----------------------

You can also insert your custom connection into the global connection tree. To do this, use the decorator
``@balder.insert_into_tree(..)``. This decorator allows you to define the parent connections - that is, the connections
on which your new one is based. These dependencies will be set globally for the entire Balder session.

For example, if your connection is based on a :class:`TcpV4Connection`, you can implement it easily like this:

.. code-block:: python

    # file `lib/connections.py`

    import balder
    import balder.connections as conns

    @balder.insert_into_tree(parents=[conns.TcpConnection])
    class MyConnection(balder.Connection):
        pass

.. note::
    Note that we do not use inheritance to define child connections. Instead, if you want to add a new connection and
    insert it into the global connection tree, use the decorator ``@balder.insert_into_tree(..)``.

.. note::
    Note that you need to add your custom connection class to a file named ``connections.py``, or make it importable
    from a module named connections (for example, a directory called connections that contains an ``__init__.py`` file).
    The location of the ``connections.py`` file within your project doesn't matter.

You can now use this connection, as it is integrated into the project's global connection tree.


Global connection tree
======================

In Balder all connections are embedded in a so called global connection trees. This tree defines how the connections are
arranged to each other.

The global connection tree
--------------------------

In Balder, all connections are embedded in a so-called global connection tree. This tree defines how the connections are
arranged relative to each other.

.. note::
    COMING SOON - We are working on a tool to show this global connection tree graphically.

..
    .. todo

Overwrite the default global tree
---------------------------------

By default, the ``@balder.insert_into_tree(..)`` decorator inserts the connection into the global connection tree. If
you want to insert it into a different connection tree instead, you can specify the ``tree_name=".."`` argument in the
``@balder.insert_into_tree(..)`` decorator. This lets you define a completely custom connection tree of your own.

.. note::
    If you define your own global connection tree, Balder's pre-defined arrangements will no longer apply.

If you want to use your newly defined global connection tree, you need to set the ``used_global_connection_tree``
property in the :class:`BalderSettings` object of your test environment to your custom tree name.

Let's examine the following example:

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

    Be careful when changing the standard connection tree. Doing so means that no connections are included in the tree
    by default anymore, so you will have to define every connection yourself. If you plan to use standard Balder
    connections, keep in mind that some BalderHub projects rely on the original Balder connections.

    If you want to modify the dependencies in an existing tree, you can use the class method ``set_parents(..)``.

    .. code-block:: python

        from balder import connections as conns

        conns.DnsConnection.set_parents(
            parents=[(conns.UdpConnection, conns.TcpConnection)], tree_name="my_project_one")

When does a Connection match?
=============================

To understand when one connection matches another, you should look at the "contained-in" mechanism for connections.

The "contained-in" mechanism checks whether one connection tree is nested within another. This means that smaller, more
general trees can be fully contained within larger, more specific ones.

You can think of it as a two-dimensional, inheritance-like tree. To determine if a connection is "contained-in" this
tree, Balder looks for a subtree within it where the other connection fits. If Balder finds such a subtree, then the
connection is considered "contained-in" the tree.

For more details on how Balder's connection mechanism works, check out :ref:`Deeper look into connections`.
