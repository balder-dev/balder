from __future__ import annotations

import inspect
from typing import List, Type, Any, Dict, Iterable, TYPE_CHECKING
import types
from graphlib import TopologicalSorter
from collections import OrderedDict

from _balder.executor.basic_executor import BasicExecutor
from _balder.executor.parametrized_testcase_executor import ParametrizedTestcaseExecutor
from _balder.parametrization import Parameter
from _balder.previous_executor_mark import PreviousExecutorMark
from _balder.testresult import BranchBodyResult

if TYPE_CHECKING:
    from _balder.executor.variation_executor import VariationExecutor
    from _balder.scenario import Scenario
    from _balder.setup import Setup


class UnresolvedParametrizedTestcaseExecutor(BasicExecutor):
    """
    This executor class represents a group of dynamically parametrized tests.
    """

    def __init__(
            self,
            testcase: callable,
            parent: VariationExecutor,
            static_parameters: Dict[str, Any] = None,
    ) -> None:
        super().__init__()

        self._base_testcase_callable = testcase
        self._parent_executor = parent

        # holds the specific static parameters for this unresolved group
        self._static_parameters = static_parameters if static_parameters is not None else {}

        # holds the dynamically created testcase executors as soon as this executor is entered
        self._testcase_executors = None

        # contains the result object for the BODY part of this branch
        self.body_result = BranchBodyResult(self)

    @property
    def parent_executor(self) -> VariationExecutor:
        return self._parent_executor

    @property
    def base_testcase_callable(self) -> callable:
        """returns the testcase function"""
        return self._base_testcase_callable

    @property
    def all_child_executors(self) -> List[ParametrizedTestcaseExecutor]:
        return self.get_testcase_executors()

    @property
    def base_testcase_obj(self) -> Scenario:
        """
        return the testcase Scenario this testcase is defined in
        """
        return self.parent_executor.cur_scenario_class

    @property
    def base_instance(self) -> object:
        """
        returns the base class instance to which this executor instance belongs"""
        return self._base_testcase_callable

    @property
    def parametrization_has_been_resolved(self) -> bool:
        """returns true if the parametrization has been resolved"""
        return self._testcase_executors is not None

    def has_runnable_tests(self, consider_discarded_too=False) -> bool:
        """
        This method returns true if this executor element is runnable. The method returns true if this element has
        `prev_mark=RUNNABLE` and minimum one of its children has `prev_mark=RUNNABLE` too.

        :param consider_discarded_too: True if the method allows DISCARDED elements too
        """
        if self.parametrization_has_been_resolved:
            return super().has_runnable_tests(consider_discarded_too=consider_discarded_too)

        allowed_prev_marks = [PreviousExecutorMark.RUNNABLE]

        if consider_discarded_too:
            allowed_prev_marks.append(PreviousExecutorMark.DISCARDED)

        if self.prev_mark not in allowed_prev_marks:
            return False
        return True

    def get_all_base_instances_of_this_branch(
            self, with_type: Type[Setup] | Type[Scenario] | Type[types.FunctionType],
            only_runnable_elements: bool = True) -> List[Setup | Scenario | object]:
        """
        returns itself if the type matches, otherwise an empty list
        """
        # todo
        if isinstance(self.base_instance, with_type):
            return [self.base_instance]
        return []

    def get_covered_by_element(self) -> List[Scenario | callable]:
        """
        This method returns a list of elements where the whole scenario is covered from. This means, that the whole
        test methods in this scenario are already be covered from every single element in the list.
        """
        all_covered_by_data = []
        scenario_executor = self.parent_executor.parent_executor
        scenario_class = scenario_executor.base_scenario_class
        covered_by_dict_resolved = scenario_executor.get_covered_by_dict()
        if self.base_testcase_callable in covered_by_dict_resolved.keys():
            all_covered_by_data += covered_by_dict_resolved[self.base_testcase_callable]
        if scenario_class in covered_by_dict_resolved.keys():
            all_covered_by_data += covered_by_dict_resolved[scenario_class]
        return all_covered_by_data

    def get_testcase_executors(self) -> List[ParametrizedTestcaseExecutor | UnresolvedParametrizedTestcaseExecutor]:
        """returns all sub testcase executors that belongs to this variation-executor"""
        if self._testcase_executors is None:
            return [self]
        return self._testcase_executors

    def resolve_dynamic_parametrization(self):
        """
        resolves the dynamic parametrization - should be called when setup features are active in the scenario
        """
        self._testcase_executors = []

        parametrization = self.get_parametrization()
        if parametrization:
            for cur_parametrization in parametrization:
                self._testcase_executors.append(
                    ParametrizedTestcaseExecutor(
                        self._base_testcase_callable,
                        parent=self.parent_executor,
                        parametrization=cur_parametrization,
                        unresolved_group_obj=self
                    )
                )

    def get_parametrization(self) -> List[OrderedDict[str, Any]] | None:
        """
        returns all parametrization elements that belongs to this group executor
        """
        scenario_controller = self.parent_executor.parent_executor.base_scenario_controller
        dynamic_parametrization = scenario_controller.get_parametrization_for(self._base_testcase_callable,
                                                                              static=False)
        if not dynamic_parametrization:
            raise ValueError('can not determine dynamic parametrization, because there are no dynamic parameters')

        # sort attributes according their Parameter - using TopologicalSorter
        graph = {attr: [param.name for param in config.get_parameters(of_type=Parameter).values()]
                 for attr, config in dynamic_parametrization.items()}
        # also add all elements from static parameters
        graph.update({param: [] for param in self._static_parameters})

        ts = TopologicalSorter(graph)
        resolvable_order_of_attribues = ts.static_order()
        resolvable_dynamic_attribues = [attr for attr in resolvable_order_of_attribues
                                        if attr in dynamic_parametrization.keys()]

        def get_variations_for(
                resolved_parameters: Dict[str, Any],
                remaining_attributes: Iterable[str]
        ) -> List[Dict[str, Any]]:
            result = []
            remaining_attributes = list(remaining_attributes).copy()
            attr = remaining_attributes.pop(0)
            feature_access_selector = dynamic_parametrization[attr]
            # get value for this attribute
            attr_value_list = feature_access_selector.get_value(resolved_parameters)
            if not isinstance(attr_value_list, Iterable):
                raise TypeError(
                    f'feature parametrizing not possible, because `{feature_access_selector.device.__qualname__}'
                    f'.{feature_access_selector.device_property_name}.{feature_access_selector.feature_property_name}` '
                    f'does not return Iterable')

            for cur_value in attr_value_list:
                parameters_with_cur_attr_value = resolved_parameters.copy()
                parameters_with_cur_attr_value[attr] = cur_value
                if len(remaining_attributes) > 0:
                    result.extend(get_variations_for(parameters_with_cur_attr_value, remaining_attributes))
                else:
                    result.append(parameters_with_cur_attr_value)

            return result

        resolved_parameters = self._static_parameters.copy()

        all_full_parametrization = get_variations_for(resolved_parameters, resolvable_dynamic_attribues)

        # get combined parametrization
        result = []
        for cur_full_parametrization in all_full_parametrization:
            cur_parameter_set = OrderedDict()
            for cur_arg in inspect.getfullargspec(self._base_testcase_callable).args:
                # only if this is a parametrization value
                if cur_arg in cur_full_parametrization:
                    cur_parameter_set[cur_arg] = cur_full_parametrization[cur_arg]
            result.append(cur_parameter_set)
        return result

    def cleanup_empty_executor_branches(self, consider_discarded=False):
        pass
