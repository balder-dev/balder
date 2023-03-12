Installation
************

Before you can start to develop with Balder, you will need to install it.

Install python
==============

For this python in the version ``3.9`` or higher is required. You can get the latest version of python at
`https://www.python.org/downloads/ <https://www.python.org/downloads/>`_ or install it with your packet management
system of your operating system.

Install Balder
==============

You can easily install Balder in different ways, that are described here.

Install the official release
----------------------------

You can install the latest release with pip:

.. code-block::

    python -m pip install baldertest

That's it. The package is installed.

Install the latest developer version
------------------------------------

1. Secure that you have installed the latest version of git (see `Git Installation <https://git-scm.com/>`_).
   You can test this while trying to execute the command ``git help``
2. Check out the main development branch of baldertest by inserting ``git clone https://github.com/balder/balder.git`` -
   this will create a new directory ``balder`` in the current working directory
3. Then run the command ``python -m pip install -e balder``

This will make the code of Balder importable and allows you to develop with the latest state of this branch.

If you want to update your further installed developer version to the latest version, simply pull
the changes with:

.. code-block::

    git pull

This will automatically update your installed environment.
