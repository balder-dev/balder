Part 2: Install Tests for NextCloud Web
***************************************

In this part of the documentation, we will implement our first tests. One of the main modules within the Nextcloud app
that we want to continue testing here is the Files module. With it, you can manage your files, while Nextcloud
synchronizes them across your devices and stores a version history. You can also share them with other users and
synchronize your desktop computer's file system with the app.

Now we want to write tests that validate file operations such as COPY, MOVE, CREATE, DELETE, or RENAME for both files
and directories within Nextcloud. We will start by testing the Nextcloud web app, since we already set it up
(see `Balder Intro Example <Balder Intro Example>`_.).

Let's install Tests
===================

Before we start, we'll install ``balderhub-nextcloud``. This is a BalderHub project created specifically for testing
Nextcloud apps. It contains various HTML objects (using ``balderhub-html``) to interact with the Nextcloud web app, as
well as other objects for interacting with the Nextcloud CLI or the Nextcloud mobile app (COMING SOON).

Packages like this are usually maintained by the developers themselves or a dedicated team, since they define the
connections to the devices under test and make writing tests much easier (as tester you don't need to take care for
selectors and stuff like that). One extra benefit is that every BalderHub project includes its own testing environment.
This lets you validate everything before using it in a real test setup. It's like testing your tests - a great way to
cut down on unreliable results and ensure your tests are solid before you rely on them.

However, let's start by installing this package:

.. code-block:: shell

    $ pip install balderhub-nextcloud

Installing our tests
--------------------

In this tutorial, we want to test file operations such as CREATE, COPY, MOVE, RENAME, and DELETE for both files and
directories. We could start by developing our own tests from scratch, or we can check out
`BalderHub <https://hub.balder.dev>`_ and search for existing ones. And yes, there is already a package available.
Let's use it:

.. code-block:: shell

    $ pip install balderhub-fileops

According to `the documentation of that package <https://hub.balder.dev/projects/fileops>`_, it provides multiple
scenarios that validate the creation, moving, copying, renaming, and deleting of files - regardless of how these
operations are performed.

Perfect, that's exactly what we need.

Let's implement
===============

Let's start with a copy test - a test that copies a directory. For that, take a look at
`the documentation of balderhub-fileops <https://hub.balder.dev/projects/fileops>`_. We want to use the
standalone versions (``ScenarioDirStandalone``), which also handles the creation of a test directory and the
cleanup of all affected ones.

In the documentation, we can see that we need to provide an implementation for the following features:

* ``balderhub.fileops.lib.scenario_features.CreateDirectoryFeature``: creates a directory
* ``balderhub.fileops.lib.scenario_features.CopyDirectoryFeature``: copies a directory
* ``balderhub.fileops.lib.scenario_features.DeleteDirectoryFeature``: deletes a directory
* ``balderhub.fileops.lib.scenario_features.NavigateFeature``: allows to receive and navigate within the directory tree

Defining our setup
------------------

Before we start implementing these features, let's add them to our setup. We'll create a new setup class that looks
similar to the one from `Part 1: Develop a Login Test from Scratch <Part 1: Develop a Login Test from Scratch>`_:

.. code-block:: python

    # file `setups/setup_docker2.py`

    from selenium import webdriver
    from balderhub.selenium.lib.setup_features import SeleniumRemoteWebdriverFeature
    from lib.setup_features import CreateDirectoryFeature, CopyDirectoryFeature, DeleteDirectoryFeature, NavigateFeature

    class SeleniumManagerFeature(SeleniumRemoteWebdriverFeature):
        # use this feature if you are using selenium grid as docker container
        selenium_options = webdriver.FirefoxOptions()

    class SetupDocker2(balder.Setup):

        class NextCloud(balder.Device):
            serv = IsNextcloudServer()

        @balder.connect(NextCloud, over_connection=balder.Connection())
        class SeleniumBrowser(balder.Device):
            selenium = SeleniumManagerFeature()
            dir_create = CreateDirectoryFeature()
            dir_copy = CopyDirectoryFeature()
            dir_delete = DeleteDirectoryFeature()
            navigate = NavigateFeature()

To make this setup compatible with our ``balderhub.fileops.lib.scenario_features.ScenarioDirCopyStandalone``, we need
to add the required features (as described in the ``balderhub-fileops`` documentation). Since we're implementing these
for the Nextcloud web app, we can also directly include the HTML page object
``balderhub.nextcloud.libs.pages.web.PageFiles`` and ``balderhub.nextcloud.libs.pages.web.PageMarkdownEditor``, because
both of them are necessary for creating and working with directories within the NextCloud web app:


.. code-block:: python

    import balder
    from selenium import webdriver
    import balderhub.nextcloud.lib.scenario_features
    from balderhub.selenium.lib.setup_features import SeleniumRemoteWebdriverFeature
    from lib.setup_features import DirectoryCreatorFeature, DirectoryCopyerFeature, DirectoryDeleterFeature, FileSystemNavigatorFeature

    class SeleniumManagerFeature(SeleniumRemoteWebdriverFeature):
        # use this feature if you are using selenium grid as docker container
        selenium_options = webdriver.FirefoxOptions()

    class SetupDocker2(balder.Setup):

        class NextCloud(balder.Device):
            pass

        @balder.connect(NextCloud, over_connection=balder.Connection())
        class SeleniumBrowser(balder.Device):
            selenium = SeleniumManagerFeature()
            file_page = balderhub.nextcloud.lib.pages.web.PageFiles()
            file_editor = balderhub.nextcloud.lib.pages.web.PageMarkdownEditor()
            dir_create = DirectoryCreatorFeature()
            dir_copy = DirectoryCopyerFeature()
            dir_delete = DirectoryDeleterFeature()
            navigate = FileSystemNavigatorFeature()


.. note::
    Note that we've also added the ``IsNextcloudServer`` feature, which is necessary because it holds the hostname and
    related information. This allows Balder to know where to connect.

We also need to set up selenium. We can copy the fixture from part 1:

.. code-block:: python

    import balder
    ...

    class SetupDocker2(balder.Setup):

        ...

        # register this fixture as a session fixture - meaning it will be executed once before/after the whole test session
        @balder.fixture('session')
        def selenium_manager(self):
            # creates a new selenium connection before the test run
            self.SeleniumBrowser.selenium.create()
            yield # can be used to separate construction code (before session) and teardown code (after session)
            # shuts down selenium after the test run
            self.SeleniumBrowser.selenium.quit()

Before a test can be executed, we need to log in. For that, we want to define another fixture in our setup. We can use
the predefined page objects for that too, so lets add the two pages ``PageLogin`` and ``PageDashboard`` and implement a
new fixture ``login``:

.. code-block:: python

    import balder
    from selenium import webdriver
    import balderhub.nextcloud.lib.scenario_features
    from balderhub.nextcloud.lib.utils import dismiss_welcome_modal
    from balderhub.selenium.lib.setup_features import SeleniumRemoteWebdriverFeature
    from lib.setup_features import DirectoryCreatorFeature, DirectoryCopyerFeature, DirectoryDeleterFeature, FileSystemNavigatorFeature

    class SeleniumManagerFeature(SeleniumRemoteWebdriverFeature):
        # use this feature if you are using selenium grid as docker container
        selenium_options = webdriver.FirefoxOptions()

    class SetupDocker2(balder.Setup):

        class NextCloud(balder.Device):
            pass

        @balder.connect(NextCloud, over_connection=balder.Connection())
        class SeleniumBrowser(balder.Device):
            selenium = SeleniumManagerFeature()

            # add the vdevice mapping for the vdevice `Server`
            dashboard_page = balderhub.nextcloud.lib.pages.web.PageDashboard()
            login_page = balderhub.nextcloud.lib.pages.web.PageLogin()
            file_page = balderhub.nextcloud.lib.pages.web.PageFiles()
            editor_page = balderhub.nextcloud.lib.pages.web.PageMarkdownEditor()

            dir_create = DirectoryCreatorFeature()
            dir_copy = DirectoryCopyerFeature()
            dir_delete = DirectoryDeleterFeature()
            navigate = FileSystemNavigatorFeature()

        @balder.fixture('testcase')
        def login(self):
            login_page = self.SeleniumBrowser.login_page

            login_page.open()
            if login_page.is_applicable():
                # we are not logged in yet
                login_page.input_username.wait_to_be_clickable_for(3).type_text("admin", clean_before=True)
                login_page.input_password.wait_to_be_clickable_for(3).type_text("Admin12345", clean_before=True)
                login_page.btn_login.wait_to_be_clickable_for(3).click()
                self.SeleniumBrowser.dashboard_page.wait_for_page()
                dismiss_welcome_modal(self.SeleniumBrowser.file_page)


Finally, we need to complete one last step. As described in
`the balderhub-nextcloud documentation <https://hub.balder.dev/projects/nextcloud>`_, we must define a so-called
`VDevice mapping <VDevices and method-variations>`_ between the pages and the Nextcloud server device. Additionally, we
need to override the implementation of ``balderhub.nextcloud.lib.scenario_features.IsNextcloudServer`` (which is
required by the vDevice) and specify the correct hostname. This will provide the pages with all the necessary
information about the Nextcloud server to establish a connection.

.. code-block:: python

    import balder
    from selenium import webdriver
    import balderhub.nextcloud.lib.scenario_features
    from balderhub.selenium.lib.setup_features import SeleniumRemoteWebdriverFeature
    from lib.setup_features import DirectoryCreatorFeature, DirectoryCopyerFeature, DirectoryDeleterFeature, FileSystemNavigatorFeature

    class SeleniumManagerFeature(SeleniumRemoteWebdriverFeature):
        # use this feature if you are using selenium grid as docker container
        selenium_options = webdriver.FirefoxOptions()

    class IsNextcloudServer(balderhub.nextcloud.lib.scenario_features.IsNextcloudServer):
        # overwrite the hostname
        hostname = 'nextcloud'

    class SetupDocker2(balder.Setup):

        class NextCloud(balder.Device):
            # and add the feature to the server device
            serv = IsNextcloudServer()

        @balder.connect(NextCloud, over_connection=balder.Connection())
        class SeleniumBrowser(balder.Device):
            selenium = SeleniumManagerFeature()

            # add the vdevice mapping for the vdevice `Server`
            dashboard_page = balderhub.nextcloud.lib.pages.web.PageDashboard(Server="NextCloud")
            login_page = balderhub.nextcloud.lib.pages.web.PageLogin(Server="NextCloud")
            file_page = balderhub.nextcloud.lib.pages.web.PageFiles(Server="NextCloud")
            editor_page = balderhub.nextcloud.lib.pages.web.PageMarkdownEditor(Server="NextCloud")

            dir_create = DirectoryCreatorFeature()
            dir_copy = DirectoryCopyerFeature()
            dir_delete = DirectoryDeleterFeature()
            navigate = FileSystemNavigatorFeature()

        ...

Perfect! Our setup should now match our scenario ``ScenarioDirCopyStandalone`` from ``balderhub-fileops``.
However, we still need to implement the features in our ``lib/setup_features.py`` module.

Start implementing the features
-------------------------------

By reading the documentation of `balderhub-fileops <https://hub.balder.dev/projects/fileops>`_, you'll notice that
these features each require only one or two methods to implement. So, let's define them:

.. code-block:: python

    # file `lib/setup_features.py`

    from typing import Union
    import pathlib
    import time

    import balderhub.fileops.lib.scenario_features
    from balderhub.nextcloud.lib.pages.web import PageFiles, PageMarkdownEditor
    from balderhub.fileops.lib.utils import DirectoryItem, FileItem, FileSystemItemList


    class DirectoryCopyerFeature(balderhub.fileops.lib.scenario_features.DirectoryCopyerFeature):

        page_files = PageFiles()
        page_markdown_editor = PageMarkdownEditor()

        def copy_directory(self, source: Union[str, DirectoryItem]) -> str:
            cur_list_item = self.page_files.focus_visible_list_element(source.name)

            context_menu = cur_list_item.open_context_menu()

            modal_copyormove = context_menu.click_on_moveorcopy()
            modal_copyormove.btn_copy.wait_to_be_clickable_for(3).click()
            return f"{source.name} (copy)"

    class DirectoryCreatorFeature(balderhub.fileops.lib.scenario_features.DirectoryCreatorFeature):

        page_files = PageFiles()

        def create_new_directory(self, name: str) -> None:
            self.page_files.open()
            self.page_files.wait_for_page()

            menu = self.page_files.open_plus_menu()

            modal_create_dir = menu.click_on_new_directory()

            modal_create_dir.input_filename.wait_to_be_clickable_for(3)
            modal_create_dir.input_filename.type_text(name, clean_before=True)
            modal_create_dir.btn_create.click()


    class DirectoryDeleterFeature(balderhub.fileops.lib.scenario_features.DirectoryDeleterFeature):

        page_files = PageFiles()

        def delete_directory(self, directory: DirectoryItem) -> None:
            cur_list_item = self.page_files.focus_visible_list_element(directory.name)

            context_menu = cur_list_item.open_context_menu()
            context_menu.click_on_delete()


    class FileSystemNavigatorFeature(balderhub.fileops.lib.scenario_features.FileSystemNavigatorFeature):

        page_files = PageFiles()

        def navigate_to(self, path: pathlib.Path):
            # TODO this implementation is incomplete, but it is good enough for this tutorial

            if path.is_absolute() and path == pathlib.Path('/'):
                self.page_files.open()
                self.page_files.wait_for_page(3)
            else:
                # TODO
                raise NotImplementedError

        def get_all_list_items(self) -> FileSystemItemList:
            self.page_files.wait_for_page(3)

            shown_items = self.page_files.get_all_visible_list_elements()
            result = []
            for elem in shown_items:
                result.append(FileItem(elem.full_name) if elem.is_file else DirectoryItem(elem.full_name))
            return FileSystemItemList(result)

Because all of our features interact with the Nextcloud Files page, we've added them as an
`inner feature reference <Inner-Feature-Referencing>`_. This allows us to use everything that this page-feature provides
within our feature. According to the documentation of
`balderhub-nextcloud <https://hub.balder.dev/projects/nextcloud>`_, this is the page object that lets us interact with
the Files page of the NextCloud web app.

Let's run
---------

Before we can run something, we need to activate the scenario. We don't need to implement it, but we need to import it.
Create a file ``scenario_balderhub.py`` and add a simple import statement:

.. code-block:: python

    # file `scenarios/scenario_balderhub.py`

    from balderhub.fileops.scenarios import ScenarioDirCopyStandalone


Now we're ready - we haven't specified any tests ourselves. We've only implemented the bindings to our specific app by
defining the features from ``balderhub.fileops.lib.scenario_features``.

Let's run Balder and see what happens:

.. code-block:: shell

    balder --working-dir src --only-with-scenario scenarios/scenario_balderhub.py --only-with-setup setups/setup_docker2.py

We used the CLI arguments ``--only-for-scenario`` and ``--only-for-setup`` here. This lets us limit the collection of
scenarios and setups.

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0] | balder version 0.1.0b14                          |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 1 Scenarios
      resolve them to 1 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupDocker2
      SCENARIO ScenarioDirCopyStandalone
        VARIATION ScenarioDirCopyStandalone.Filesystem:SetupDocker2.SeleniumBrowser
          TEST ScenarioDirCopyStandalone.test_copy_directory [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 1 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0


Adding more tests
=================

Add CREATE and DELETE tests
---------------------------

Okay we also want to test the directory creation and the deletion each within a test. So let's add
``ScenarioDirCreateStandalone`` and ``ScenarioDirDeleteStandalone``. We only need to import it, because all features
that are required by this scenario are already implemented.

So let's add it to our ``scenarios/scenario_balderhub.py``:

.. code-block:: python

    # file `scenarios/scenario_balderhub.py`
    from balderhub.fileops.scenarios import ScenarioDirCopyStandalone
    from balderhub.fileops.scenarios import ScenarioDirCreateStandalone, ScenarioDirDeleteStandalone


So let's run Balder:

.. code-block::

    balder --working-dir src --only-with-setup setups/setup_docker2.py --only-with-scenarios scenarios/scenario_balderhub.py

And we see, that the other test is executed too:

.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0] | balder version 0.1.0b14                          |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 3 Scenarios
      resolve them to 3 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupDocker2
      SCENARIO ScenarioDirCopyStandalone
        VARIATION ScenarioDirCopyStandalone.Filesystem:SetupDocker2.SeleniumBrowser
          TEST ScenarioDirCopyStandalone.test_copy_directory [.]
      SCENARIO ScenarioDirCreateStandalone
        VARIATION ScenarioDirCreateStandalone.Filesystem:SetupDocker2.SeleniumBrowser
          TEST ScenarioDirCreateStandalone.test_create_new_valid_dir [.]
      SCENARIO ScenarioDirDeleteStandalone
        VARIATION ScenarioDirDeleteStandalone.Filesystem:SetupDocker2.SeleniumBrowser
          TEST ScenarioDirDeleteStandalone.test_delete_empty_directory [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 3 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0


Adding RENAME test
------------------

The ``balderhub-fileops`` package also provides scenarios for moving and renaming a directory - we want to add the
``ScenarioDirRenameStandalone`` too. This scenario needs another feature:

* ``balderhub.fileops.lib.scenario_features.RenameDirectoryFeature``: renames a directory

Let's implement them too:

.. code-block:: python

    # file `lib/setup_features.py`
    ...

    class DirectoryRenamerFeature(balderhub.fileops.lib.scenario_features.DirectoryRenamerFeature):

        page_files = PageFiles()

        def rename_directory(self, source: Union[str, DirectoryItem], rename_to: str) -> None:
            cur_list_item = self.page_files.focus_visible_list_element(source.name)

            context_menu = cur_list_item.open_context_menu()
            context_menu.click_on_rename()

            cur_list_item.input_item_name.wait_to_be_clickable_for(3)
            cur_list_item.input_item_name.type_text(rename_to, clean_before=True)
            cur_list_item.td_modified.click()


And add it into our setup:

.. code-block:: python

    # file `setups/setup_docker.py`
    ...

    from lib.setup_features import DirectoryRenamerFeature

    ...

    class SetupDocker(balder.Setup):

        class NextCloud(balder.Device):
            pass


        class SeleniumBrowser(balder.Device):
            ...
            dir_rename = DirectoryRenamerFeature()

And of course activate the scenario:

.. code-block:: python

    # file `scenarios/scenario_balderhub.py`
    ...
    from balderhub.fileops.scenarios import ScenarioDirRenameStandalone


When we run balder, these tests are executed too:


.. code-block:: none

    +----------------------------------------------------------------------------------------------------------------------+
    | BALDER Testsystem                                                                                                    |
    |  python version 3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0] | balder version 0.1.0b14                          |
    +----------------------------------------------------------------------------------------------------------------------+
    Collect 1 Setups and 4 Scenarios
      resolve them to 4 valid variations

    ================================================== START TESTSESSION ===================================================
    SETUP SetupDocker2
      SCENARIO ScenarioDirCopyStandalone
        VARIATION ScenarioDirCopyStandalone.Filesystem:SetupDocker2.SeleniumBrowser
          TEST ScenarioDirCopyStandalone.test_copy_directory [.]
      SCENARIO ScenarioDirCreateStandalone
        VARIATION ScenarioDirCreateStandalone.Filesystem:SetupDocker2.SeleniumBrowser
          TEST ScenarioDirCreateStandalone.test_create_new_valid_dir [.]
      SCENARIO ScenarioDirDeleteStandalone
        VARIATION ScenarioDirDeleteStandalone.Filesystem:SetupDocker2.SeleniumBrowser
          TEST ScenarioDirDeleteStandalone.test_delete_empty_directory [.]
      SCENARIO ScenarioDirRenameStandalone
        VARIATION ScenarioDirRenameStandalone.Filesystem:SetupDocker2.SeleniumBrowser
          TEST ScenarioDirRenameStandalone.test_rename_directory [.]
    ================================================== FINISH TESTSESSION ==================================================
    TOTAL NOT_RUN: 0 | TOTAL FAILURE: 0 | TOTAL ERROR: 0 | TOTAL SUCCESS: 4 | TOTAL SKIP: 0 | TOTAL COVERED_BY: 0


.. note::
    The balderhub-fileops package also provides scenarios for performing the same operations with files. Since this is
    similar to what we've done before, it's not covered in this tutorial. Feel free to try it on your own.

With this BalderHub package, we were able to create file operation tests in just a few minutes - without writing the
tests ourselves, but by using ones developed by an open-source community.

In the next part of this tutorial series, we'll extend these tests to include CLI tests. This is remarkable because
we've just created tests for the web app, and now we want to reuse the same tests for a CLI app?