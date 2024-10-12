from __future__ import annotations
from typing import Union, List, Tuple, Dict, Type, TYPE_CHECKING

import os
import sys
import inspect
import pathlib
import argparse
import balder
from _balder.balder_plugin import BalderPlugin
from _balder.plugin_manager import PluginManager
from _balder.executor.executor_tree import ExecutorTree
from _balder.collector import Collector
from _balder.solver import Solver
from _balder.exceptions import DuplicateBalderSettingError
from _balder.balder_settings import BalderSettings

if TYPE_CHECKING:
    from _balder.setup import Setup
    from _balder.device import Device
    from _balder.scenario import Scenario
    from _balder.connection import Connection


class BalderSession:
    """
    This is the main balder executable object. It contains all information about the current session and executes the
    different steps.

    This object contains all command line arguments that can be used, while calling `balder ..`. All settings that
    are given in `balderglob.py` will be imported in `self.baldersetting`
    """
    # this is the default value (will be overwritten in this constructor if necessary)
    baldersettings: BalderSettings = BalderSettings()

    def __init__(self, cmd_args: Union[List[str], None] = None, working_dir: Union[pathlib.Path, None] = None):
        """

        :param cmd_args: optional the command line list of strings that should be parsed instead of parsing the real
                         command line arguments (used for testing)

        :param working_dir: the working directory that should be used instead of the given value in `cmd_arg_str` or
                            the current directory (determined by `os.getcwd()`)
        """
        #: contains the alternative command line arguments as a string list (has to be given, if the object should
        #: not use the console params of this call)
        self._alt_cmd_args = cmd_args
        #: contains a reference to the ArgumentParser that parses the command line string
        self.cmd_arg_parser = None
        #: contains the parsed object
        self.parsed_args: argparse.Namespace

        ##
        # all general settings that can be modified by command line arguments
        ##

        #: the working directory for this balder session (default: current directory from `os.getcwd()`)
        self.working_dir: Union[pathlib.Path, None] = pathlib.Path(os.getcwd())
        #: specifies that the tests should only be collected but not be resolved and executed
        self.collect_only: Union[bool, None] = None
        #: specifies that the tests should only be collected and resolved but not executed
        self.resolve_only: Union[bool, None] = None
        #: specifies that all discarded variations should be printed (with information why they were discarded)
        self.show_discarded: Union[bool, None] = None
        #: contains a number of :class:`Setup` class strings that should only be considered for the execution
        self.only_with_setup: Union[List[str], None] = None
        #: contains a number of :class:`Scenario` class strings that should only be considered for the execution
        self.only_with_scenario: Union[List[str], None] = None
        #: if this is true, the test run should include duplicated tests that are declared as covered_by another test
        #: method
        self.force_covered_by_duplicates: Union[bool, None] = None

        self.preparse_args()

        #: overwrite working directory if necessary
        if working_dir:
            self.working_dir = working_dir

        # add the current working variable to sys.path
        sys.path.insert(0, str(self.working_dir.absolute()))

        ##
        # instantiate and initialize all components to completely load the plugins (plugins could access the command
        # line argument parser)
        ##
        #: contains the reference to the used PluginManager
        self.plugin_manager = PluginManager()
        #: contains the reference to the used :class:`Collector` class
        self.collector = Collector(self.working_dir)

        # determine the balder settings
        BalderSession.baldersettings = self.get_baldersettings_from_balderglob()
        BalderSession.baldersettings = BalderSession.baldersettings if BalderSession.baldersettings is not None else \
            BalderSettings()

        if BalderSession.baldersettings.force_covered_by_duplicates:
            # overwrite console argument only if the value in BalderSettings is true (because cmd line can only
            # overwrite the value False)
            self.force_covered_by_duplicates = True

        for cur_plugin_cls in self.get_balderplugins_from_balderglob():
            self.plugin_manager.register(cur_plugin_cls, self)

        ##
        # instantiate all sub objects that are relevant for this test session
        ##
        self.parse_args()

        #: overwrite working directory if necessary
        if working_dir:
            self.working_dir = working_dir

        #: contains the reference to the used :class:`Solver´ class (or none, if there was no solving executed till
        #: now)
        self.solver: Union[Solver, None] = None
        #: contains the reference to the used :class:`ExecutorTree` class (or none, if there was no solving executed
        #: till now)
        self.executor_tree: Union[ExecutorTree, None] = None

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    @staticmethod
    def get_current_active_global_conntree_name():
        """
        This method returns the current active global connection tree name, depending on the current active setting in
        :class:`BalderSettings`, that is active for the current run.
        """
        if BalderSession.baldersettings is None:
            raise ValueError("no baldersettings loaded yet")

        return BalderSession.baldersettings.used_global_connection_tree

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def all_collected_pyfiles(self) -> List[pathlib.Path]:
        """returns all collected pyfiles"""
        try:
            return self.collector.all_pyfiles
        except AttributeError as exc:
            raise RuntimeError("this property is only available after the collecting process was executed") from exc

    @property
    def all_collected_setups(self) -> List[Type[Setup]]:
        """returns all collected :class:`Setup` classes"""
        try:
            return self.collector.all_setups
        except AttributeError as exc:
            raise RuntimeError("this property is only available after the collecting process was executed") from exc

    @property
    def all_collected_scenarios(self) -> List[Type[Scenario]]:
        """returns all collected :class:`Scenario` classes"""
        try:
            return self.collector.all_scenarios
        except AttributeError as exc:
            raise RuntimeError("this property is only available after the collecting process was executed") from exc

    @property
    def all_collected_connections(self) -> List[Type[Connection]]:
        """returns all collected :class:`Connection` classes"""
        try:
            return self.collector.all_connections
        except AttributeError as exc:
            raise RuntimeError("this property is only available after the collecting process was executed") from exc

    @property
    def all_resolved_mappings(self) -> List[Tuple[Type[Setup], Type[Scenario], Dict[Type[Device], Type[Device]]]]:
        """returns all resolved mappings for the :class:`Device` mappings between :class:`Scenario` and
        :class:`Setup`"""
        try:
            return self.solver.all_mappings
        except AttributeError as exc:
            raise RuntimeError("this property is only available after the resolving process was executed") from exc

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_baldersettings_from_balderglob(self) -> Union[BalderSettings, None]:
        """
        Helper method that checks if there is a valid :class:`BalderSettings` class in the given module
        """
        module = self.collector.load_balderglob_py_file()
        class_members = inspect.getmembers(module, inspect.isclass)
        all_classes = []
        for _, cur_class in class_members:
            if issubclass(cur_class, BalderSettings):
                all_classes.append(cur_class)
        if len(all_classes) == 0:
            return None
        if len(all_classes) > 1:
            raise DuplicateBalderSettingError(f"found more than one object that could be a BalderSettings object - "
                                              f"found {','.join([cur_class.__name__ for cur_class in all_classes])}")
        return all_classes[0]()

    def get_balderplugins_from_balderglob(self) -> List[Type[BalderPlugin]]:
        """
        Helper method that loads all valid :class:`BalderPlugin` classes and returns them
        """
        module = self.collector.load_balderglob_py_file()
        class_members = inspect.getmembers(module, inspect.isclass)
        all_classes = []
        for _, cur_class in class_members:
            if issubclass(cur_class, BalderPlugin):
                all_classes.append(cur_class)
        return all_classes

    def preparse_args(self):
        """
        This method pre-parses the console arguments and checks if one or more of the most important (for example
        `--working-dir`) attributes are given as CLI argument. This will be automatically pre-set. With that balder
        secures that it can read the correct `balderglob.py` file, to initialize the plugins correctly.
        """
        argv_working_dir_key = "--working-dir"
        if argv_working_dir_key in sys.argv:
            found_idx = sys.argv.index(argv_working_dir_key)
            if found_idx != -1:
                if len(sys.argv) <= found_idx + 1:
                    raise AttributeError(f"no path given for `{argv_working_dir_key}`")

                self.working_dir = pathlib.Path(sys.argv[found_idx + 1]).absolute()
                if not self.working_dir.is_dir():
                    raise NotADirectoryError(
                        f'can not parse the given working directory `{self.working_dir}` correctly or the given '
                        f'path is no directory..')

    def parse_args(self):
        """
        This method can be used to parse the `arg` object and fill all data from that object into the properties of this
        :class:`BalderSession` object.
        """
        self.cmd_arg_parser = argparse.ArgumentParser(
            description='Balder is a simple scenario-based test system that allows you to run your tests on various '
                        'devices without rewriting them')

        self.cmd_arg_parser.add_argument(
            '--working-dir', nargs="?", default=os.getcwd(),
            help="a explicit working directory on which the testsystem is to be executed with")

        self.cmd_arg_parser.add_argument(
            '--collect-only', action='store_true',
            help="specifies that the tests are only collected but not resolved and executed")

        self.cmd_arg_parser.add_argument(
            '--resolve-only', action='store_true',
            help="specifies that the tests are only collected and resolved but not executed")

        self.cmd_arg_parser.add_argument(
            '--show-discarded', action='store_true',
            help="specifies that all discarded variations should be printed (with information why they were discarded)")

        self.cmd_arg_parser.add_argument(
            '--only-with-setup', nargs="*",
            help="defines a number of Setup classes which should only be considered for the execution")

        self.cmd_arg_parser.add_argument(
            '--only-with-scenario', nargs="*",
            help="defines a number of Scenario classes which should only be considered for the execution")
        self.cmd_arg_parser.add_argument(
            '--force-covered-by-duplicates', action='store_true',
            help="specifies that the test run should include duplicated tests that are declared as covered_by another "
                 "test method (also true if it was already set in baldersetting object)")

        self.plugin_manager.execute_addoption(self.cmd_arg_parser)

        self.parsed_args = self.cmd_arg_parser.parse_args(self._alt_cmd_args)

        self.working_dir = self.parsed_args.working_dir
        self.collect_only = self.parsed_args.collect_only
        self.resolve_only = self.parsed_args.resolve_only
        self.show_discarded = self.parsed_args.show_discarded
        self.only_with_setup = self.parsed_args.only_with_setup
        self.only_with_scenario = self.parsed_args.only_with_scenario
        self.force_covered_by_duplicates = self.parsed_args.force_covered_by_duplicates

    def collect(self):
        """
        This method collects all data.
        """
        self.collector.collect(
            plugin_manager=self.plugin_manager,
            scenario_filter_patterns=self.only_with_scenario,
            setup_filter_patterns=self.only_with_setup)

    def solve(self):
        """
        This method resolves all classes and executes different checks, that can be done before the test session starts.
        """
        self.solver = Solver(setups=self.all_collected_setups,
                             scenarios=self.all_collected_scenarios,
                             connections=self.all_collected_connections,
                             fixture_manager=self.collector.get_fixture_manager())
        self.solver.resolve(plugin_manager=self.plugin_manager)

    def create_executor_tree(self):
        """
        This method creates the executor tree object.

        .. note::
            Note that the method creates an :class:`ExecutorTree`, that hasn't to be completely resolved yet.
        """
        self.executor_tree = self.solver.get_executor_tree(plugin_manager=self.plugin_manager,
                                                           add_discarded=self.show_discarded)
        self.plugin_manager.execute_filter_executor_tree(executor_tree=self.executor_tree)

    def run(self):
        """
        This method executes the whole session
        """
        line_length = 120

        self.collect()

        def print_rect_row(text):
            line = "| " + text
            line = line + " " * (line_length - len(line) - 1) + "|"
            print(line)

        print("+" + "-" * (line_length - 2) + "+")
        print_rect_row("BALDER Testsystem")
        sys_version = sys.version.replace('\n', '')
        print_rect_row(f" python version {sys_version} | balder version {balder.__version__}")
        print("+" + "-" * (line_length - 2) + "+")
        print(f"Collect {len(self.all_collected_setups)} Setups and {len(self.all_collected_scenarios)} Scenarios")
        if not self.collect_only:
            self.solve()
            self.create_executor_tree()
            count_valid = len(self.executor_tree.get_all_variation_executors())
            count_discarded = len(self.executor_tree.get_all_variation_executors(return_discarded=True)) - count_valid
            addon_text = f" ({count_discarded} discarded)" if self.show_discarded else ""
            print(f"  resolve them to {count_valid} valid variations{addon_text}")
            print("")
            if not self.resolve_only:
                self.executor_tree.execute(show_discarded=self.show_discarded)
            else:
                self.executor_tree.print_tree(show_discarded=self.show_discarded)

        self.plugin_manager.execute_session_finished(self.executor_tree)
