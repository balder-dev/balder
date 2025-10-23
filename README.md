
<div align="center">
  <img style="margin: 20px;max-width: 68%" src="https://docs.balder.dev/en/latest/_static/balder_w_boarder.png" alt="Balder logo">
</div>

Balder is a flexible Python test system that allows you to reuse test code written once for different but similar 
platforms, devices, or applications. It enables you to install ready-to-use test cases and provides various test 
development features that help you test your software or devices much faster.

You can use shared test code by installing an [existing BalderHub project](https://hub.balder.dev), or you can create 
your own. This makes test development for your project much faster, since it is oftentimes enough to install a BalderHub
project and only provide the user-specific code.

Be part of the progress and share your tests with others, your company, or the whole world.

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
test (`Scenario`) and the components that **you have** (`Setup`).

You can define a test within a method of a `Scenario` class. This is often an abstract layer, where you only describe 
the general business logic without providing any specific implementation details.

These specific implementation details are provided in the `Setup` classes. They describe exactly **what you have**. In 
these classes, you provide an implementation for the abstract elements that were defined earlier in the `Scenario`. 

Balder then automatically searches for matching mappings and runs your tests using them.

## Define the `Scenario` class

Inside `Scenario` or `Setup` classes, you can describe the environment using inner `Device` classes. For example, let's 
write a test that validates the functionality of a lamp. For that, keep in mind that we want to make this test as 
flexible as possible. It should be able to run with all kind of things that have a lamp:

```python
import balder
from lib.scenario_features import BaseLightFeature


class ScenarioLight(balder.Scenario):
    
    # The device with its features that are required for this test
    class LightSpendingDevice(balder.Device):
        light = BaseLightFeature()
    
    def test_check_light(self):
        self.LightSpendingDevice.light.switch_on()
        assert self.LightSpendingDevice.light.light_is_on()
        self.LightSpendingDevice.light.switch_off()
        assert not self.LightSpendingDevice.light.light_is_on()
        
    

```

Here, we have defined that a `LightSpendingDevice` **needs to have** a feature called `BaseLightFeature` so that this 
scenario can be executed.

We have also added a test case (named with a `test_*()` prefix) called `test_check_light`, which executes the validation
of a lamp, by switching it on and off and checking its state.

**Note:** The `BaseLightFeature` is an abstract Feature class that defines the abstract methods `switch_on()`, 
`switch_off()`, and `light_is_on()`.


## Define the `Setup` class

The next step is defining a `Setup` class, which describes what we have. For a `Scenario` to match a `Setup`, the 
features of all scenario devices must be implemented by the mapped setup devices.

For example, if we want to test a car that includes a lamp, we could have a setup like the one shown below:

```python
import balder
from lib.setup_features import CarEngineFeature, CarLightFeature


class SetupGarage(balder.Setup):
    
    class Car(balder.Device):
        car_engine = CarEngineFeature()
        car_light = CarLightFeature() # subclass of `lib.scenario_feature.BaseLightFeature`
        ...
    

```

When you run Balder in this environment, it will collect the `ScenarioLight` and the `SetupMyCar` classes and try to 
find mappings between them. Based on the `ScenarioLight`, Balder looks for a device that provides an implementation of 
the single `BaseLightFeature`. To do this, it scans all available setups. Since the `SetupMyCar.Car` device provides an 
implementation through the `CarLightFeature`, this device will match.

```shell
+----------------------------------------------------------------------------------------------------------------------+
| BALDER Testsystem                                                                                                    |
|  python version 3.10.12 (main, Aug 15 2025, 14:32:43) [GCC 11.4.0] | balder version 0.1.0b14                         |
+----------------------------------------------------------------------------------------------------------------------+
Collect 1 Setups and 1 Scenarios
  resolve them to 1 valid variations

================================================== START TESTSESSION ===================================================
SETUP SetupGarage
  SCENARIO ScenarioLight
    VARIATION ScenarioLight.LightSpendingDevice:SetupGarage.Car
      TEST ScenarioLight.test_check_light [.]
================================================== FINISH TESTSESSION ==================================================
TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 1 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0
```

## Add another Device to the `Setup` class

Now the big advantage of Balder comes into play. We can run our test with all devices that can implement the 
`BaseLightFeature`, independent of how this will be implemented in detail. **You do not need to rewrite the test**.

So, We have more devices in our garage. So let's add them:

```python
import balder
from lib.setup_features import CarEngineFeature, CarLightFeature, PedalFeature, BicycleLightFeature, GateOpenerFeature


class SetupGarage(balder.Setup):
    
    class Car(balder.Device):
        car_engine = CarEngineFeature()
        car_light = CarLightFeature() # subclass of `lib.scenario_feature.BaseLightFeature`
        ...
    
    class Bicycle(balder.Device):
        pedals = PedalFeature()
        light = BicycleLightFeature() # another subclass of `lib.scenario_feature.BaseLightFeature`
        
    class GarageGate(balder.Device):
        opener = GateOpenerFeature()

```

If we run Balder now, it will find more mappings because the `Bicycle` device also provides an implementation for the 
`BaseLightFeature` we are looking for.

```shell
+----------------------------------------------------------------------------------------------------------------------+
| BALDER Testsystem                                                                                                    |
|  python version 3.10.12 (main, Aug 15 2025, 14:32:43) [GCC 11.4.0] | balder version 0.1.0b14                         |
+----------------------------------------------------------------------------------------------------------------------+
Collect 1 Setups and 1 Scenarios
  resolve them to 2 valid variations

================================================== START TESTSESSION ===================================================
SETUP SetupGarage
  SCENARIO ScenarioLight
    VARIATION ScenarioLight.LightSpendingDevice:SetupGarage.Bicycle
      TEST ScenarioLight.test_check_light [.]
    VARIATION ScenarioLight.LightSpendingDevice:SetupGarage.Car
      TEST ScenarioLight.test_check_light [.]
================================================== FINISH TESTSESSION ==================================================
TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 2 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0
```

Balder handles all of this for you. You only need to describe your environment by defining `Scenario` and `Setup` 
classes, then provide the specific implementations by creating the features. Balder will automatically search for and 
apply the mappings between them.

**NOTE:** Balder offers many more elements to design complete device structures, including connections between multiple 
devices.

You can learn more about that in the 
[Tutorial Section of the Documentation](https://docs.balder.dev/en/latest/tutorial_guide/index.html).


# Example: Use an installable BalderHub package

With Balder, you can create custom test environments or install open-source-available test packages, known as 
[BalderHub packages](https://hub.balder.dev). For example, if you want to test the login functionality of a website, simply use the 
ready-to-use scenario `ScenarioSimpleLogin` from the [`balderhub-auth` package](https://hub.balder.dev/projects/auth/en/latest/examples.html), 


We want to use [Selenium](https://www.selenium.dev/) to control the browser and of course use html elements, so let's install 
`balderhub-selenium` and `balderhub-html` right away.

```
$ pip install balderhub-auth balderhub-selenium balderhub-html
```

So as mentioned, you don't need to define a scenario and a test yourself; you can simply import it:

```python
# file `scenario_balderhub.py`

from balderhub.auth.scenarios import ScenarioSimpleLogin

```

According to the [documentation of this BalderHub project](https://hub.balder.dev/projects/auth/en/latest/examples.html), 
we only need to define the login page by overwriting the ``LoginPage`` feature:

```python

# file `lib/pages.py`

import balderhub.auth.contrib.html.pages
from balderhub.html.lib.utils import Selector
from balderhub.url.lib.utils import Url
import balderhub.html.lib.utils.components as html


class LoginPage(balderhub.auth.contrib.html.pages.LoginPage):

    url = Url('https://example.com')

    # Overwrite abstract property
    @property
    def input_username(self):
            return html.inputs.HtmlTextInput.by_selector(self.driver, Selector.by_name('user'))

    # Overwrite abstract property
    @property
    def input_password(self):
        return html.inputs.HtmlPasswordInput.by_selector(self.driver, Selector.by_name('user'))

    # Overwrite abstract property
    @property
    def btn_login(self):
        return html.HtmlButtonElement.by_selector(self.driver, Selector.by_id('submit-button'))

```

And use it in our setup:

```python


# file `setups/setup_office.py`

import balder
import balderhub.auth.lib.scenario_features.role
from balderhub.selenium.lib.setup_features import SeleniumChromeWebdriverFeature

from lib.pages import LoginPage

class UserConfig(balderhub.auth.lib.scenario_features.role.UserRoleFeature):
    # provide the credentials for the log in
        username = 'admin'
        password = 'secret'

class SetupOffice(balder.Setup):

    class Server(balder.Device):
        user = UserConfig()

    class Browser(balder.Device):
        selenium = SeleniumChromeWebdriverFeature()
        page_login = LoginPage()

    # fixture to prepare selenium - will be executed before the test session runs
    @balder.fixture('session')
    def selenium(self):
        self.Browser.selenium.create()
        yield
        self.Browser.selenium.quit()
```

When you run Balder now, it will execute a complete login test that you didn't write yourself - 
**it was created by the open-source community**.

```shell
+----------------------------------------------------------------------------------------------------------------------+
| BALDER Testsystem                                                                                                    |
|  python version 3.10.12 (main, Aug 15 2025, 14:32:43) [GCC 11.4.0] | balder version 0.1.0b14                         |
+----------------------------------------------------------------------------------------------------------------------+
Collect 1 Setups and 1 Scenarios
  resolve them to 1 valid variations

================================================== START TESTSESSION ===================================================
SETUP SetupOffice
  SCENARIO ScenarioSimpleLogin
    VARIATION ScenarioSimpleLogin.Client:SetupOffice.Browser | ScenarioSimpleLogin.System:SetupOffice.Server
      TEST ScenarioSimpleLogin.test_login [.]
================================================== FINISH TESTSESSION ==================================================
TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 1 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0
```

If you'd like to learn more about it, feel free to dive [into the documentation](https://balder.dev).

# Contribution guidelines

Any help is appreciated. If you want to contribute to balder, take a look into the 
[contribution guidelines](https://github.com/balder-dev/balder/blob/main/CONTRIBUTING.md).

Are you an expert in your field? Do you enjoy the concept of balder? How about creating your own
BalderHub project? You can contribute to an existing project or create your own. If you are not sure, a project for 
your idea already exists or if you want to discuss your ideas with others, feel free to
[create an issue in the BalderHub main entry project](https://github.com/balder-dev/hub.balder.dev/issues) or
[start a new discussion](https://github.com/balder-dev/hub.balder.dev/discussions).

# License

Balder is free and Open-Source

Copyright (c) 2022-2025 Max Stahlschmidt and others

Distributed under the terms of the MIT license
