.. balder documentation master file, created by
   sphinx-quickstart on Fri Jan 22 20:19:38 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Balder
******

.. toctree::
   :maxdepth: 2
   :hidden:

   getting_started/index.rst
   tutorial_guide/index.rst
   basics/index.rst
   deeper/index.rst
   api/index.rst

   BalderHub <https://hub.balder.dev>

Balder is a very powerful, universal and flexible python test system that allows you to reuse a once written testcode as
efficiently as possible for different but similar platforms/devices/applications.

In the real world you have a lot of different projects that use the same interfaces, like
the SNMP, SMTP or HTTP protocol. Other processes like *login into backend* are being implemented multiple
times as well. This often works in the similar way for login with the app, over the api or directly over the web
frontend. If you want to test these various possibilities, you have to provide similar tests, which are often times
repetitive.

For example if you have a backend system which you are testing on the login function, you would have three possible
ways to login. You could use the mobile app, the normal web app and the api interface. For all of these possibilities
you follow a similar pattern:

1. open the login area/create the login request
2. insert the username
3. insert the password
4. send the request
5. check if you are successfully logged in

These steps are independent from the method you want to login with. You would still have the same **Scenario** but
different **Setups**:

* **Setup 1:** a smartphone app on iOS
* **Setup 2:** a smartphone app on Android
* **Setup 3:** a webpage which provides the login area
* **Setup 4:** a API endpoint which allows to identify with your username and password

Balder was created especially for that. You can write one **Scenario** and use it for different setups.

You can find out more about Scenario-Based-Testing and how Balder works in this documentation.

If you are completely new, we recommend to start with the :ref:`Getting Started <Getting Started>` section. Since, in
our opinion, the best way is learning-by-doing. We recommend to continue with the :ref:`Tutorial Guide`. If
you want to discover all components of Balder you can continue with the :ref:`Basic Guides<Basic Guides>`. All profound
functions of Balder, like the different internal work processes, you can find in the
:ref:`Reference Guides<Reference Guides>`.

It is recommended to go throw the different subsections of the :ref:`Getting Started <Getting Started>` and the
:ref:`Tutorial Guide` in the provided order to fully understand the basic functionality of **Scenario-based-testing**
and how it works in the Balder framework. The different subsections of :ref:`Basic Guides<Basic Guides>` and
:ref:`Reference Guides<Reference Guides>` are created independently from each other. So feel free to jump to the
subsection you want to learn more about. But we always recommend to start with the complete
:ref:`Getting Started <Getting Started>` section before going deeper into the :ref:`Basic Guides<Basic Guides>` and
:ref:`Reference Guides<Reference Guides>`.