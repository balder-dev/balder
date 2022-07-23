from __future__ import annotations

from typing import List, Dict, Tuple, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.setup import Setup
    from _balder.device import Device
    from _balder.scenario import Scenario
    from _balder.connection import Connection
    from _balder.plugin_manager import PluginManager

import itertools
from .executor.executor_tree import ExecutorTree
from .executor.setup_executor import SetupExecutor
from .executor.scenario_executor import ScenarioExecutor
from .executor.testcase_executor import TestcaseExecutor
from .executor.variation_executor import VariationExecutor
from _balder.previous_executor_mark import PreviousExecutorMark
from _balder.controllers import ScenarioController, SetupController


class Solver:
    """
    The solver class is the class to map corresponding :class:`Scenario` with :class:`Setup` classes. This class
    determines all possibilities in which a scenario can be mapped to a setup constellation.
    """

    def __init__(self, setups: List[Type[Setup]], scenarios: List[Type[Scenario]], connections: List[Type[Connection]]):
        #: contains all available setup classes
        self._all_existing_setups = setups
        #: contains all available scenario classes
        self._all_existing_scenarios = scenarios
        #: contains all available connection classes
        self._all_existing_connections = connections
        #: contains all mappings between :meth:`Scenario`'s and :meth:`Setup`'s
        #: will contain all possibilities and will then be reduced to the really applicable set using the `filter_*()`
        #: methods
        self._mapping: List[Tuple[Type[Setup], Type[Scenario], Dict[Type[Device], Type[Device]]]] = []
        self._resolving_was_executed = False

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS -----------------------------------------------------------------

    def _set_data_for_covered_by_in_tree(self, executor_tree: ExecutorTree):
        """
        This method updates the executor tree and sets all metadata for the `@covered_by()` decorator.

        :param executor_tree: the executor tree object, that should be updated
        """
        # now determine all covered_by items
        all_scenarios = executor_tree.get_all_scenario_executors()
        all_testcases = executor_tree.get_all_testcase_executors()
        all_available_testcase_functions = [
            cur_testcase_executor.base_testcase_callable for cur_testcase_executor in all_testcases]
        all_available_scenario_classes = [
            cur_scenario_executor.base_scenario_class for cur_scenario_executor in all_scenarios]

        covered_by_mapping_of_interest = {}
        for cur_scenario in all_scenarios:
            covered_by_item = cur_scenario.get_covered_by_element()
            if covered_by_item is not None:
                covered_by_mapping_of_interest[cur_scenario] = covered_by_item

        for cur_testcase in all_testcases:
            covered_by_item = cur_testcase.get_covered_by_element()
            if covered_by_item is not None:
                covered_by_mapping_of_interest[cur_testcase] = covered_by_item

        # now go throw all covered_by items and check if the destination is contained in the tree -> set prev_mark
        for cur_elem, covered_from_items in covered_by_mapping_of_interest.items():
            all_matched_covered_from_executors = []
            for cur_covered_from_item in covered_from_items:
                if cur_covered_from_item in all_available_scenario_classes:
                    all_matched_covered_from_executors.append(
                        all_scenarios[all_available_scenario_classes.index(cur_covered_from_item)])

                elif cur_covered_from_item in all_available_testcase_functions:
                    all_matched_covered_from_executors.append(
                        all_testcases[all_available_testcase_functions.index(cur_covered_from_item)])
            if len(all_matched_covered_from_executors) > 0:
                cur_elem.prev_mark = PreviousExecutorMark.COVERED_BY
                cur_elem.covered_by_executors = all_matched_covered_from_executors

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def all_mappings(self) -> List[Tuple[Type[Setup], Type[Scenario], Dict[Type[Device], Type[Device]]]]:
        if self._mapping is None or self._mapping == [] or self._resolving_was_executed is False:
            raise AttributeError("please call the `resolve()` method before omitting this value")
        return self._mapping

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _get_all_unfiltered_mappings(self) -> List[Tuple[Type[Setup], Type[Scenario]]]:
        """
        This method searches for all possible hits for the internal lists `_all_existing_setups` and
        `_all_existing_scenarios`. It returns all combinations of :meth:`Setup`'s and :meth:`Scenario`'s that could
        exist.

        :return: a list with tuple pairs that defines all possible pairs of :meth:`Setup` classes and :meth:`Scenario`
                 classes
        """
        matching_list = []
        for cur_setup in self._all_existing_setups:
            for cur_scenario in self._all_existing_scenarios:
                matching_list.append((cur_setup, cur_scenario))
        return matching_list

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def get_initial_mapping(self) -> List[Tuple[Type[Setup], Type[Scenario], Dict[Device, Device]]]:
        """
        This method creates the initial amount of data for `self._mapping`. Only those elements are returned where the
        :meth:`Setup` class has more or the same amount of :meth:`Device`'s than the :meth:`Scenario` class.
        The method does not reduce the set with other criteria yet. This will be done later with filter methods.
        """
        setup_scenario_matches = self._get_all_unfiltered_mappings()

        mapping = []

        for cur_setup, cur_scenario in setup_scenario_matches:

            setup_devices = SetupController.get_for(cur_setup).get_all_abs_inner_device_classes()
            scenario_devices = ScenarioController.get_for(cur_scenario).get_all_abs_inner_device_classes()
            if len(scenario_devices) <= len(setup_devices):
                # only if there are more or as many devices in the setup as in the scenario

                # go through every possible constellation
                for cur_setup_devices in itertools.permutations(setup_devices, len(scenario_devices)):
                    # get device mapping for this constellation
                    device_mapping = {scenario_devices[idx]: cur_setup_devices[idx] for idx in range(
                        0, len(scenario_devices))}
                    mapping.append((cur_setup, cur_scenario, device_mapping))
        return mapping

    def resolve(self, plugin_manager: PluginManager) -> None:
        """
        This method carries out the entire resolve process and saves the end result in the object property
        `self._mapping`.
        """
        # reset mapping list
        self._mapping = []
        initial_mapping = self.get_initial_mapping()
        self._mapping = initial_mapping
        self._resolving_was_executed = True

    def get_executor_tree(self, plugin_manager: PluginManager) -> ExecutorTree:
        """
        This method builds the ExecutorTree from the resolved data and returns it

        :return: the executor tree is built on the basis of the mapping data
        """

        executor_tree = ExecutorTree()


        # create all setup executor

        for cur_setup, cur_scenario, cur_device_mapping in self._mapping:
            setup_executor = executor_tree.get_executor_for_setup(setup=cur_setup)
            if setup_executor is None:
                # setup is not available -> create new SetupExecutor
                setup_executor = SetupExecutor(cur_setup, parent=executor_tree)
                executor_tree.add_setup_executor(setup_executor)

            scenario_executor = setup_executor.get_executor_for_scenario(scenario=cur_scenario)
            if scenario_executor is None:
                # scenario is not available -> create new ScenarioExecutor
                scenario_executor = ScenarioExecutor(cur_scenario, parent=setup_executor)
                setup_executor.add_scenario_executor(scenario_executor)

            variation_executor = scenario_executor.get_executor_for_device_mapping(device_mapping=cur_device_mapping)
            if variation_executor is None:
                # variation is not available -> create new VariationExecutor
                variation_executor = VariationExecutor(device_mapping=cur_device_mapping, parent=scenario_executor)

                # only add if the features for this device mapping matches
                if variation_executor.can_be_applied():
                    scenario_executor.add_variation_executor(variation_executor)

                    for cur_testcase in ScenarioController.get_for(cur_scenario).get_all_test_methods():
                        cur_testcase_executor = TestcaseExecutor(cur_testcase, parent=variation_executor)
                        variation_executor.add_testcase_executor(cur_testcase_executor)

                        # determine prev_mark IGNORE/SKIP for the testcase
                        if cur_testcase_executor.should_be_skipped():
                            variation_executor.prev_mark = PreviousExecutorMark.SKIP
                        # always overwrite if it should be ignored
                        if cur_testcase_executor.should_be_ignored():
                            variation_executor.prev_mark = PreviousExecutorMark.IGNORE

        # now filter all elements that have no child elements
        #   -> these are items that have no valid matching, because no variation can be applied for it (there are no
        #      required :class:`Feature` matching or there exists no possible routing for the variation)
        executor_tree.cleanup_empty_executor_branches()

        self._set_data_for_covered_by_in_tree(executor_tree=executor_tree)

        return executor_tree
