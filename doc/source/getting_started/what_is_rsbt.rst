What is reusable-scenario-based testing?
****************************************


The most common way of writing tests is to create single test cases. You have a requirement that your device or
application must be able to fulfill. For this you need to write a test case. If it fails, this requirement does not
work, otherwise everything is fine.

The general testcase
====================

Imagine we are developers of coffee machines and want to test whether they function properly. We came up with a test
case to check whether the "Make me a coffee" process is started when the button is pressed. The test should also secure,
that the coffee tastes well.

The basic test
--------------

The test case could look like this, for example:

.. code-block:: py

    def test_execute_coffee_process():
        tiered_developer = TieredDeveloper()
        coffee_machine = CoffeeMachine()
        tiered_developer.start_coffee_machine(coffee_machine)
        tiered_developer.place_cup()
        tiered_developer.wait_until_machine_is_ready(coffee_machine)
        tiered_developer.press_coffee_button(coffee_machine)
        assert coffee_machine.has_started(), "The coffee machine did not start the process"

        tiered_developer.wait_for_coffee_machine(coffee_machine)

        assert not tiered_developer.cup_is_empty(), "The cup is still empty and the coffee machine did not fill the cup"
        assert tiered_developer.the_coffee_tastes_good(), "The coffee doesn't taste good. That is not acceptable!"

So far so good. Well, we don't just manufacture one coffee machine, but many different ones. We have a lot of products
that do similar the same thing, but often not in the same way. Some machines have other features, some working in
another way or like in our case, the coffee machine ``CoffeeMachine`` can also be managed over a wlan smartphone app.

One more test
-------------

So we want to test the coffee machine with the mentioned app too. For this, we create a new testcase:

.. code-block:: py

    def test_execute_coffee_process():
        tiered_developer = TieredDeveloperWithSmartphone()
        coffee_machine = CoffeeMachine()
        tiered_developer.open_app()
        tiered_developer.start_coffee_machine_with_app()
        tiered_developer.do_some_coding_till_machine_is_ready()
        tiered_developer.place_cup()
        tiered_developer.press_coffee_button(coffee_machine)
        assert coffee_machine.has_started(), "The coffee machine did not start the process"

        tiered_developer.wait_for_coffee_machine(coffee_machine)

        assert not tiered_developer.cup_is_empty(), "The cup is still empty and the coffee machine did not fill the cup"
        assert tiered_developer.the_coffee_tastes_good(), "The coffee doesn't taste good. That is not acceptable!"

So if you take a look at these two tests you can see, that both do basically the same, but in different approaches. You
will find this problem in most companies or projects. You have similar products, that do a lot of tasks in a similar way
and/or you have one product that can do things in a lot of different but similar approaches.

Generalize
==========

Similar to the normal developing process, we can now think about generalization. Of course the DRY (don't repeat
yourself) standard does not really count in testing, but think about what happens if we forget something in our test
concept (for example to try if the coffee tastes well) and have various different testcases where we have to add this.
If we don't have an orderly test management system it can get hard to find all relevant testcases we have to fix here.
So what about creating a little default structure how such a test should look like? **We start to generalize tests.**

So back to our example test. How can we generalize it? What is the common process here?

* two components interact with each other - the **developer** and the **coffee machine**
* the developer is able to interact with the coffee machine
* the coffee machine is able to create coffees
* the developer is able to taste a coffee

With these information we can create a ``Scenario`` later, but first let's think about the components of our scenario.
Let us organize the information above a little bit:

.. mermaid::
    :align: center

    classDiagram
        class Developer
        Developer : ManageACoffeeMachineFeature()
        Developer : ManageACupFeature()
        Developer : TasteAndDrinkCoffeesFeature()

        class CoffeeMachine
        CoffeeMachine : CreateCoffeeFeature()

We uses the keyword ``*Feature`` in the functionality classes, the devices are using. This helps us to categorize the
functionality a little bit.

We have two components the ``Developer`` and the ``CoffeeMachine`` which interact with each other. We will call such
components **Devices**. Both of these **Devices** have different features. As mentioned above, these features are
**objects of functionality**, that could save information and can execute something over their methods.

But how can we use these elements now in a generalized way?

Separation of test code and application specific code
-----------------------------------------------------

This allows us to separate the test code from the application code. With these elements we can now implement a test
``Scenario``, that tests our coffee-machine process above without exactly the knowledge over which interface a
``Developer`` interacts with the ``CoffeeMachine``. We only want that the ``Developer`` starts the ``CoffeeMachine``
without the knowledge how this is executed. Real specific code doesn't need to be implemented.

How could such a scenario look like? The following code shows how this test scenario would be implemented with Balder:

.. code-block:: python

    import balder
    ...

    class ScenarioCoffeeMachine(balder.Scenario):

        class Developer(balder.Device):
            cm_manager = ManageACoffeeMachineFeature()
            cup_manager = ManageACupFeature()
            trink = TasteAndDrinkCoffeesFeature()

        class CoffeeMachine(balder.Device):
            creation = CreateCoffeeFeature()

        def test_create_coffee(self):
            self.Developer.cm_manager.start_coffee_machine()
            self.Developer.cm_manager.wait_until_machine_is_ready()
            self.Developer.cup_manager.place_cup()
            self.CoffeeMachine.creation.fill_cup()

            assert self.CoffeeMachine.cm_manager.creation.has_started(), "The coffee machine did not start the process"

            self.Developer.cm_manager.wait_for_coffee_machine(coffee_machine)

            assert not self.Developer.cup_manager.cup_is_empty(), "The cup is still empty and the coffee machine did not fill the cup"
            assert self.Developer.trink.the_coffee_tastes_good(), "The coffee doesn't taste good. That is not acceptable!"


.. note::
    In a real implementation we would assign a mapping between some vDevices and the given devices here. But for now
    we ignore that. You can read more about vDevices at :ref:`VDevices and method-variations`.

Here you can't see exactly how the machine was started. It could have been started from an app or by pressing the
button on the coffee machine. This information is not necessary here, because at scenario level we only define
**what we need**. And we only need that the coffee machine is started, but it does not matter how. We will add this
specific implementation to our setup-features later.

Setups: the holder of the application specific code
---------------------------------------------------

The setup modules of a Balder test environment hold all the implementations that are application specific. So in our
case we could create two setups, which hold the code for a coffee creation over the button and one setup which
implements the features to use the app.

The setup code holds subclasses of the features we have used above. It mostly also contains the whole implementation.
So for example, the implementation of the ``ManageACupFeature`` could looks like the following:

.. code-block:: python

    from ..scenario_features import ManageACupFeature

    class GeneralManageACupFeature(ManageACupFeature):

        developer_brain = DeveloperBrainFeature()

        def place_cup(self):
            cup = self.developer_brain.get_cup_from_cupboard()
            self.developer_brain.place_cup(...)

        def cup_is_empty(self):
            cup = self.developer_brain.get_cup()
            self.developer_brain.turn_around(cup)
            return self.developer_brain.floor_still_clean()

We can now replace the developer with every other person. We could replace the methods with code to control a robot or
something like this. All this depends on the setup implementation. The scenario code doesn't change.

**Why is this so helpful?** - You can reuse tests for similar devices, by changing only the code that is different. This
makes it really easy to share tests with other similar project company-wide or world-wide. You can publish your scenario
code and make testing easier for others or use scenarios from other community members. You can find about this in the
:ref:`BalderHub - the share place of tests`.

Learn more about
================

This documentation shows you an insight how this concept is implemented in Balder. Feel free to do the
:ref:`tutorial <Tutorial Guide>` to learn the key concepts of Balder.