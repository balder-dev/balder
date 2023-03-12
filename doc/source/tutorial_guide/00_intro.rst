Balder Intro Example
********************

In the next sections, we want to test the login functionality for a website. For this, we will create a scenario, that
allows us to test the login procedure. This scenario secures that we are logged-in over the possibility that we can
access the internal webpage.

Our goal is an implementation, that allows executing the scenario with a lot of different environments (``Setup``
classes). For example we want to execute our test scenarios with an UI setup and also with a REST API setup.

The project we are using in this tutorial is the ``balderexample-loginserver``. You can find it
`on GitHub <https://github.com/balder-dev/balderexample-loginserver>`_. It is a
`Django Application <https://www.djangoproject.com/>`_ that has a graphical login interface to login into a
internal backend area. In addition to that, the project also implements a REST interface, which allows to get a JSON
representation of all registered users and permission groups. This REST application supports a
`Basic Authentication <https://datatracker.ietf.org/doc/html/rfc7617>`_ (with username and password).

Do not worry, you don't need experiences with Django or with REST, we will go through this topics and don't have to
implement these functionality by ourselves.

So let's start.

Prepare the loginserver
=======================

Before we can really start testing the loginserver, we have to initialize our environment.

Checkout/Download loginserver
-----------------------------

First of all you have to checkout the loginserver. For this make sure, that you have
`installed git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.

After you have installed git, you can checkout the repository with the command:

.. code-block::

    >>> git clone https://github.com/balder-dev/balderexample-loginserver.git

This command will download the latest environment of the loginserver.

**ALTERNATIVE: Manually download the repository**

Otherwise you can also download the loginserver package
`from github <https://github.com/balder-dev/balderexample-loginserver>`_ and extract it in a directory of your choice.
Make sure that you download/checkout the main branch!

OPTIONAL: Start virtual environment
-----------------------------------

With virtual environments it is possible to separate your system installed packages from the project dependencies. With
this you install project packages only on project level and your system packages will not be changed. More information
about the virtual environment, you can find in
`the official venv documentation <https://docs.python.org/3/library/venv.html>`_.

You can create a new virtual environment simple by executing the build in command. Go to the root directory of the
loginserver project and execute the following command

.. code-block::

    >>> python38 -m venv venv

This will create the virtual environment.

After you have created the venv, you have to activate it. The command to activate the virtual environment is depended
on your OS:

.. list-table:: Activate VirtualEnv
   :widths: 25 25 50
   :header-rows: 1

   * - OS
     - Shell
     - Command
   * - POSIX
     - bash/zsh
     - $ source venv/bin/activate
   * - POSIX
     - fish
     - $ source venv/bin/activate.fish
   * - POSIX
     - csh/tcsh
     - $ source venv/bin/activate.csh
   * - POSIX
     - PowerShell Core
     - $ source venv/bin/Activate.ps1
   * - POSIX
     - csh/tcsh
     - $ source venv/bin/activate.csh
   * - POSIX
     - PowerShell Core
     - $ venv/bin/Activate.ps1
   * - WINDOWS
     - cmd.exe
     - C:\> venv\Scripts\activate.bat
   * - WINDOWS
     - PowerShell
     - PS C:\> venv\Scripts\Activate.ps1

.. note::
    You have to activate the venv (last command) in every new console session before you can use the virtual
    environment.

Install requirements
--------------------

All dependencies that are required by the loginserver project are defined in the ``requirements.txt``. You can install
all of these dependencies by simply executing the following command:

.. code-block::

    >>> pip install -r requirements.txt

This command will install all dependencies for the loginserver.

Start development server
------------------------

If you want to run the ``balderexample-loginserver`` application, just start the django included developer server. For
this, call the following command:

.. code-block::

    >>> python3 manage.py runserver


Now the server is available at url http://localhost:8000

.. image:: ../_static/balderexample-loginserver-login.png

**Use specific port:**

You can also set a specific port with an additional argument. To start the server on port 3000 simply execute the
command:

.. code-block::

    >>> python3 manage.py runserver 3000

.. warning::
    Never use this package in an real environment. It uses the Django developer server that is only for developing and
    not secure to use in a productive environment.

Prepare Balder
==============

Now it's time to prepare our Balder environment. For this, we create a sub folder ``tests`` into our project.

.. note::

    For an easier development we integrate our Balder project inside the main project directory. In the most cases, it
    doesn't make sense to do it this way, because we want to do the test for multiple environments. For an easier
    workflow in this example here, however, we create a directory ``tests`` directly in the project.

First of all, we have to create a new Balder environment in our project. For this we create a new Balder project
in our ``tests`` directory. We will create the following directory structure:

.. code-block:: none

    - balderexample-loginserver/
        |- ...
        |- tests
            |- lib
                |- __init__.py
                |- connections.py
                |- features.py
            |- scenarios
                |- __init__.py

The ``lib`` directory contains important stuff we maybe want to reuse, like :ref:`Feature <Features>` or
:ref:`Connection <Connections>` objects. The scenario module will contain our :ref:`Scenario <Scenarios>` class later.

One submodule is still missing. We also need :ref:`Setup <Setups>` classes. We will add them later.
