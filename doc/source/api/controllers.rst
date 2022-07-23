Controllers API
***************

Controller are objects, that provides different methods to manage important Balder objects like :class:`Device`,
:class:`Scenario`, :class:`Setup` or :class:`Feature` objects.

Controller objects are only relevant if you want to modify the behavior of Balder or sometimes if you want to work with
the plugin engine. **In the most cases you have not to interact with controllers.**

Basic ``Controller``
====================

.. autoclass:: _balder.controllers.Controller
    :members:

Scenario/Setup Controller
=========================

.. autoclass:: _balder.controllers.NormalScenarioSetupController
    :members:

.. autoclass:: _balder.controllers.ScenarioController
    :members:

.. autoclass:: _balder.controllers.SetupController
    :members:

Device controller
=================

.. autoclass:: _balder.controllers.BaseDeviceController
    :members:

.. autoclass:: _balder.controllers.DeviceController
    :members:

.. autoclass:: _balder.controllers.VDeviceController
    :members:

Feature controller
==================

.. autoclass:: _balder.controllers.FeatureController
    :members:
