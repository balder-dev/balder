
<div align="center">
  <img style="margin: 20px;max-width: 68%" src="https://docs.balder.dev/en/latest/_static/balder_w_boarder.png" alt="Balder logo">
</div>

Balder is a very powerful, universal and flexible python test system that allows you to reuse a once written testcode as 
efficiently as possible for different but similar platforms/devices/applications. Balder's goal is
being a platform for combining the single steps of defining, developing and documenting the entire test 
process while using test scenarios which can be reused across different projects.

You can share your own testcode by creating a new BalderHub project, or you use an 
[existing BalderHub project](https://hub.balder.dev), by simply installing and using it. This makes the test development 
for your project much faster, since it is often times enough to only provide the user-specific code.

Be part of the progress and share your tests with others, your company or the whole world.

# Installation

You can install the latest release with pip:

```
python -m pip install baldertest
```

# Run Balder

After you've installed it, you can run Balder inside a Balder environment with the following command:

```
balder
```

You can also provide a specific path to the balder environment directory by using this console argument:

```
balder --working-dir /path/to/working/dir
```

# How does it work?

Balder allows you to reuse previously written test code by dividing it into the components that **are needed** for a 
test (`Scenario`) and the components that **we have** (`Setup`).

`Scenario` classes define a test. Only describe the most important aspects **you need** for the execution of the 
corresponding test (method of the scenario class) inside `Scenario` classes. Often it is enough to define abstract 
methods in the scenario-level features.

In contrast, `Setup` classes describe exactly what **you have**. This is where you define all the devices and their 
features. Balder will then automatically search for mappings and run your test with them.

## Define the `Scenario` class

Inside `Scenario` or `Setup` classes, inner `Device` classes describe your environment. For example, if you want to test 
the process of sending a message between two devices, you can create a `Scenario` like shown below:

```python
import balder
from .features import SendMessageFeature, RecvMessageFeature


class ScenarioMessaging(balder.Scenario):
    
    class Sender(balder.Device):
        send = SendMessageFeature()
    
    @balder.connect(Sender, over_connection=balder.Connection())
    class Receiver(balder.Device):
        recv = RecvMessageFeature()
        
    

```

You have now defined, that the `Sender` device must be able to send messages (has `SendMessageFeature()`), while 
the `Receiver` device must be able to receive messages (has `RecvMessageFeature()`). Both devices are connected with 
each other. For this we use the general connection `balder.Connection()`, which allows every type of connection.

You can implement your test, by adding a new method that starts with `test_*()`:

```python
import balder
from .features import SendMessageFeature, RecvMessageFeature


class ScenarioMessaging(balder.Scenario):
    
    class Sender(balder.Device):
        send = SendMessageFeature()
    
    @balder.connect(Sender, over_connection=balder.Connection())
    class Receiver(balder.Device):
        recv = RecvMessageFeature()
        
    def test_send_msg(self):
        MESSAGE_TXT = "Hello World"
        self.Sender.send.send_msg(MESSAGE_TXT)
        received_msg = self.Receiver.recv.get_last_received_msg()
        assert received_msg == MESSAGE_TXT

```

## Define the `Setup` class

The next step is defining a `Setup` class, which describes what we have. For a `Scenario` to match a `Setup`, all of 
your scenario-devices must be able to map to a sub selection of some setup-devices. 

For example, if you want to verify if your DUT is able to receive messages from your computer (both are connected over 
USB), just create a `Setup` class with the both devices `Computer` and `Dut` and add an implementation (subclasses) of 
our previously defined feature classes `SendMessageFeature` and `RecvMessageFeature` to them:

```python
import balder
from balder import connections as cnns
from .setup_features import SendUsbMessageFeature, RecvUsbMessageFeature


class SetupOverUsb(balder.Setup):
    
    class Computer(balder.Device):
        # non-abstract subclass of `SendMessageFeature`
        send = SendUsbMessageFeature()
    
    @balder.connect(Computer, over_connection=cnns.UsbConnection())
    class Dut(balder.Device):
        # non-abstract subclass of `RecvMessageFeature`
        recv = RecvUsbMessageFeature()

```

With the features `SendUsbMessageFeature` and `RecvUsbMessageFeature`, both devices hold an implementation of our 
previous scenario-level features `SendMessageFeature` and `RecvMessageFeature`. They are the child classes of our
scenario-level features and hold the full implementation for sending/receiving data over USB.

As soon as you run Balder, Balder will automatically detect that our scenario `ScenarioMessaging` can be mapped to the 
`SetupOverUsb`. This will cause Balder to run the test `test_send_msg()` with the implemented setup-level version of 
the features.

The big advantage of Balder is the reusability. If you want to test if the communication also works in the other 
direction, just add the features inverted:

```python
import balder
from balder import connections as cnns
from .setup_features import SendUsbMessageFeature, RecvUsbMessageFeature


class SetupOverUsb(balder.Setup):
    
    class Computer(balder.Device):
        # non-abstract subclass of `SendMessageFeature`
        send = SendUsbMessageFeature()
        # non-abstract subclass of `RecvMessageFeature`
        recv = RecvUsbMessageFeature()
    
    @balder.connect(Computer, over_connection=cnns.UsbConnection())
    class Dut(balder.Device):
        # non-abstract subclass of `SendMessageFeature`
        send = SendUsbMessageFeature()
        # non-abstract subclass of `RecvMessageFeature`
        recv = RecvUsbMessageFeature()

```

Balder will now run the test once with the `Computer` being the sender and once with the `Dut` being the Sender, even 
though you didn't implement anything new.

|             | `ScenarioMessaging.Sender` | `ScenarioMessaging.Sender` |
|-------------|----------------------------|----------------------------|
| VARIATION 1 | `SetupOverUsb.Computer`    | `SetupOverUsb.Dut`         |
| VARIATION 2 | `SetupOverUsb.Dut`         | `SetupOverUsb.Computer`    |

Do you have another device, that should be tested too? Just add it to your setup:

```python
import balder
from balder import connections as cnns
from .setup_features import SendUsbMessageFeature, RecvUsbMessageFeature


class SetupOverUsb(balder.Setup):
    
    class Computer(balder.Device):
        # non-abstract subclass of `SendMessageFeature`
        send = SendUsbMessageFeature()
        # non-abstract subclass of `RecvMessageFeature`
        recv = RecvUsbMessageFeature()
    
    @balder.connect(Computer, over_connection=cnns.UsbConnection())
    class Dut(balder.Device):
        # non-abstract subclass of `SendMessageFeature`
        send = SendUsbMessageFeature()
        # non-abstract subclass of `RecvMessageFeature`
        recv = RecvUsbMessageFeature()
        
    @balder.connect(Computer, over_connection=cnns.UsbConnection())
    class AnotherDut(balder.Device):
        # non-abstract subclass of `RecvMessageFeature`
        recv = RecvUsbMessageFeature()

```

Now balder will run our scenario once each with the following mappings:

|             | `ScenarioMessaging.Sender` | `ScenarioMessaging.Sender` |
|-------------|----------------------------|----------------------------|
| VARIATION 1 | `SetupOverUsb.Computer`    | `SetupOverUsb.Dut`         |
| VARIATION 2 | `SetupOverUsb.Dut`         | `SetupOverUsb.Computer`    |
| VARIATION 3 | `SetupOverUsb.Computer`    | `SetupOverUsb.AnotherDut`  |

If you want to test a `Dut` device that does not use USB for communication, you can also add other feature 
implementations of ``SendMessageFeature`` and ``RecvMessageFeature`` in your setup devices. For this we just add a new 
setup:

```python
import balder
from balder import connections as cnns
from .setup_features import SendUsbMessageFeature, RecvUsbMessageFeature, SendBluetoothMessageFeature, RecvBluetoothMessageFeature


class SetupOverUsb(balder.Setup):
    
    ...

class SetupOverBluetooth(balder.Setup):
    class Computer(balder.Device):
        # non-abstract subclass of `SendMessageFeature`
        send = SendBluetoothMessageFeature()
    
    @balder.connect(Computer, over_connection=cnns.BluetoothConnection)
    class Dut(balder.Device):
        # non-abstract subclass of `RecvMessageFeature`
        recv = RecvBluetoothMessageFeature()

```

If you now execute Balder, it will run the scenario with all possible device constellations of the `SetupOverUsb` and 
the `SetupOverBluetooth`. 

|             | `ScenarioMessaging.Sender`      | `ScenarioMessaging.Sender` |
|-------------|---------------------------------|----------------------------|
| VARIATION 1 | `SetupOverUsb.Computer`         | `SetupOverUsb.Dut`         |
| VARIATION 2 | `SetupOverUsb.Dut`              | `SetupOverUsb.Computer`    |
| VARIATION 3 | `SetupOverUsb.Computer`         | `SetupOverUsb.AnotherDut`  |
| VARIATION 4 | `SetupOverBluetooth.Computer`   | `SetupOverBluetooth.Dut`   |

NOTE: *You could also add all of these devices in a shared setup and use one common feature for both protocols, but for this you would need to use VDevices. You can read more about this in [the documentation section about VDevices](https://docs.balder.dev/en/latest/basics/vdevices.html)*


# Example: Use an installable BalderHub package

With Balder you can create custom test environments or install open source available test packages, so called 
[BalderHub packages](https://hub.balder.dev). If you want to test a SNMP client device for example, you can use the 
[package balderhub-snmpagent](https://github.com/balder-dev/balderhub-snmpagent). Just install it with:

```
$ pip install balderhub-snmpagent
```

You only need to provide two things: The configuration of your DUT as subclass of `SnmpSystemConfig` and your 
environment (the `Setup` class):

```python
# file `features.py`
from balderhub.snmpagent.lib import features

class MySnmpSystemConfig(features.SnmpSystemConfig):

    host = "192.168.178.28"
    sys_descr = "my fancy sysDescr"
    sys_object_id = "1.3.6.1.4.1.1234.2.3.9.1"
    read_community = "public"
    write_community = "public"

```

```python
# file `setup_example.py`
import balder
from balderhub.snmpagent.lib.connections import SnmpConnection
from balderhub.snmpagent.lib.features import HasSnmpSystemGroupFeature
from balderhub.snmpagent.lib.setup_features import SendSnmpGetRequestPysnmpFeature, SendSnmpSetRequestPysnmpFeature
from . import features as setup_features


class SetupPrinter(balder.Setup):

    class Printer(balder.Device):
        _snmp_sys = HasSnmpSystemGroupFeature()
        config = setup_features.SnmpSystemConfig()

    @balder.connect(Printer, over_connection=SnmpConnection())
    class HostPc(balder.Device):
        get_request_snmp = SendSnmpGetRequestPysnmpFeature()
        set_request_snmp = SendSnmpSetRequestPysnmpFeature()

```

Call Balder in your project:

```
$ balder
```

And all existing and matching tests in [balderhub-snmpagent](https://github.com/balder-dev/balderhub-snmpagent) will 
then be executed for you:

```
+----------------------------------------------------------------------------------------------------------------------+
| BALDER Testsystem                                                                                                    |
|  python version 3.10.6 (main, Mar 10 2023, 10:55:28) [GCC 11.3.0] | balder version 0.1.0b6                           |
+----------------------------------------------------------------------------------------------------------------------+
Collect 1 Setups and 3 Scenarios
  resolve them to 3 mapping candidates

================================================== START TESTSESSION ===================================================
SETUP SetupPrinter
  SCENARIO ScenarioMibSysDescr
    VARIATION ScenarioMibSysDescr.SnmpAgent:SetupPrinter.Printer | ScenarioMibSysDescr.SnmpManager:SetupPrinter.HostPc
      TEST ScenarioMibSysDescr.test_get_sys_descr [.]
      TEST ScenarioMibSysDescr.test_get_sys_descr_ascii_check [.]
      TEST ScenarioMibSysDescr.test_set_sys_descr [.]
  SCENARIO ScenarioMibSysObjectId
    VARIATION ScenarioMibSysObjectId.SnmpAgent:SetupPrinter.Printer | ScenarioMibSysObjectId.SnmpManager:SetupPrinter.HostPc
      TEST ScenarioMibSysObjectId.test_get_sys_object_id [.]
      TEST ScenarioMibSysObjectId.test_set_sys_object_id [.]
  SCENARIO ScenarioMibSysUpTime
    VARIATION ScenarioMibSysUpTime.SnmpAgent:SetupPrinter.Printer | ScenarioMibSysUpTime.SnmpManager:SetupPrinter.HostPc
      TEST ScenarioMibSysUpTime.test_get_sys_up_time [.]
      TEST ScenarioMibSysUpTime.test_get_sys_up_time_changed_check [.]
      TEST ScenarioMibSysUpTime.test_set_sys_up_time [.]
================================================== FINISH TESTSESSION ==================================================
TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 8 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0
```


# Contribution guidelines

Any help is appreciated. If you want to contribute to balder, take a look into the 
[contribution guidelines](https://github.com/balder-dev/balder/blob/main/CONTRIBUTING.md).

Balder is still in its early steps. Unfortunately, this also means that we don't have a broad variety of 
[BalderHub projects](https://hub.balder.dev) at the moment. 

Are you an expert in your field? Do you enjoy the concept of balder? How about you create your own
BalderHub project? Take a look into our [Balder GitHub Group](https://github.com/balder-dev) and feel free to share 
your ideas. You can contribute to an existing project or create your own. If you are not sure, a project for your idea 
already exists or if you want to discuss your ideas with others, feel free to
[create an issue in the BalderHub main entry project](https://github.com/balder-dev/hub.balder.dev/issues) or
[start a new discussion](https://github.com/balder-dev/hub.balder.dev/discussions).

# License

Balder is free and Open-Source

Copyright (c) 2022 Max Stahlschmidt and others

Distributed under the terms of the MIT license
