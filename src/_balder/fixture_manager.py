from __future__ import annotations
from typing import List, Tuple, Generator, Dict, Union, Type, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from _balder.executor.executor_tree import ExecutorTree
    from _balder.executor.setup_executor import SetupExecutor
    from _balder.executor.scenario_executor import ScenarioExecutor
    from _balder.executor.variation_executor import VariationExecutor

import sys
import inspect
import traceback
from graphlib import TopologicalSorter
from _balder.executor.testcase_executor import TestcaseExecutor
from _balder.scenario import Scenario
from _balder.setup import Setup
from _balder.testresult import ResultState
from _balder.exceptions import LostInExecutorTreeException, FixtureReferenceError, UnclearSetupScopedFixtureReference, \
    UnclearUniqueClassReference


class FixtureManager:
    """
    This class is the global fixture manager. It provides various methods to manage fixtures in the balder system.
    """
    #: the ordering for the execution levels
    EXECUTION_LEVEL_ORDER = ['session', 'setup', 'scenario', 'variation', 'testcase']

    def __init__(self, executor_tree):
        from .executor.executor_tree import ExecutorTree
        self._executor_tree: ExecutorTree = executor_tree

        # contains all active fixtures with their namespace, their func_type, their callable, the generator object
        # (otherwise an empty generator, if the fixture is not a generator) and the result according to the fixture's
        # construction code (will be cleaned after it leaves a level)
        self.current_tree_fixtures: \
            Dict[str, List[
                Tuple[Union[Type[ExecutorTree], Type[Setup], Type[Scenario]], str, Callable, Generator, object]]] = {}

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def RESOLVE_TYPE_LEVEL(self):
        from .executor.executor_tree import ExecutorTree
        from .executor.setup_executor import SetupExecutor
        from .executor.scenario_executor import ScenarioExecutor
        from .executor.variation_executor import VariationExecutor
        from .executor.testcase_executor import TestcaseExecutor

        return {
            ExecutorTree: 'session',
            SetupExecutor: 'setup',
            ScenarioExecutor: 'scenario',
            VariationExecutor: 'variation',
            TestcaseExecutor: 'testcase'
        }

    @property
    def DEFINITION_SCOPE_ORDER(self):
        """
        returns a list with the definition scope objects in the priority order (ExecutorTree stands for global fixtures)
        """
        from .executor.executor_tree import ExecutorTree
        return [ExecutorTree, Setup, Scenario]

    @property
    def all_already_run_fixtures(self) -> List[Callable]:
        """
        returns a list of all fixtures that have already been run
        """
        complete_list_in_order = []
        for cur_level in self.EXECUTION_LEVEL_ORDER:
            if cur_level in self.current_tree_fixtures.keys():
                complete_list_in_order += [
                    cur_fixture for _, _, cur_fixture, _, _ in self.current_tree_fixtures[cur_level]]
        return complete_list_in_order

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def get_all_attribute_values(
            self, branch: Union[ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor, TestcaseExecutor],
            callable_func_namespace: Union[Type[ExecutorTree], Type[Scenario], Type[Setup]], callable_func: Callable,
            func_type: str) -> Dict[str, object]:
        """
        This method tries to fill the unresolved function/method arguments of the given fixture callable. For this it
        searches the return values of all already executed fixtures and supplies the argument values of the
        given ``fixture`` callable in a dictionary.

        It automatically manages `self` / `cls` references for func_type `instancemethod` or `classmethod`. It
        only returns the fixture references and ignores `self` / `cls`

        First the method tries to find the arguments in all fixtures that are in the same namespace. If it does not find
        any references, it will look in the next higher scope. It only uses fixture that has run before!

        :param branch: the current active branch

        :param callable_func_namespace: the namespace of the current fixture

        :param callable_func: the callable with the arguments

        :param func_type: returns the func_type of the fixture - depending on this value the first argument will be
                          ignored, because it has to be `cls` for `classmethod` and `self` for `instancemethod`

        :return: the method returns a dictionary with the attribute name as key and the return value as value
        """
        from .executor.executor_tree import ExecutorTree
        from .executor.setup_executor import SetupExecutor
        from .executor.scenario_executor import ScenarioExecutor
        from .executor.variation_executor import VariationExecutor
        from .executor.testcase_executor import TestcaseExecutor

        arguments = inspect.getfullargspec(callable_func).args
        result_dict = {}

        if func_type in ["classmethod", "instancemethod"]:
            arguments = arguments[1:]

        self._validate_for_unclear_setup_scoped_fixture_reference(
            callable_func_namespace, callable_func, arguments,
            cur_execution_level=self.RESOLVE_TYPE_LEVEL[branch.__class__])
        all_possible_namespaces = [ExecutorTree]
        # determine namespaces (in the correct order)
        setup_type = None
        scenario_type = None
        if isinstance(branch, SetupExecutor):
            setup_type = branch.base_setup_class.__class__
            # normally the scenario is None - only if the current namespace is a scenario we can use it
            if issubclass(callable_func_namespace, Scenario):
                scenario_type = callable_func_namespace
            else:
                scenario_type = None
        elif isinstance(branch, ScenarioExecutor):
            setup_type = branch.parent_executor.base_setup_class.__class__
            scenario_type = branch.base_scenario_class.__class__
        elif isinstance(branch, VariationExecutor):
            setup_type = branch.cur_setup_class.__class__
            scenario_type = branch.cur_scenario_class.__class__
        elif isinstance(branch, TestcaseExecutor):
            setup_type = branch.parent_executor.cur_setup_class.__class__
            scenario_type = branch.parent_executor.cur_scenario_class.__class__

        # add to possible namespaces only if the namespace of the current fixture allows this
        if (issubclass(callable_func_namespace, Setup) or issubclass(callable_func_namespace, Scenario)) \
                and setup_type is not None:
            all_possible_namespaces.append(setup_type)
        if issubclass(callable_func_namespace, Scenario) and scenario_type is not None:
            all_possible_namespaces.append(scenario_type)

        for cur_arg in arguments:
            # go to the most specific fixture, because more specific ones overwrite the more global ones
            for cur_possible_namespace in all_possible_namespaces:
                for cur_level in self.EXECUTION_LEVEL_ORDER:
                    if cur_level in self.current_tree_fixtures.keys():
                        # filter only these fixtures that have the same namespace
                        for cur_fixt_namespace, _, cur_fixt, _, cur_fixt_retval in \
                                self.current_tree_fixtures[cur_level]:
                            if cur_fixt_namespace == cur_possible_namespace:
                                if cur_fixt.__name__ == cur_arg:
                                    result_dict[cur_arg] = cur_fixt_retval
            if cur_arg not in result_dict.keys():
                raise FixtureReferenceError(
                        f"the argument `{cur_arg}` in fixture `{callable_func.__qualname__}` could not be resolved")
        return result_dict

    def _validate_for_unclear_setup_scoped_fixture_reference(
            self, fixture_callable_namespace: Union[Type[ExecutorTree], Type[Scenario], Type[Setup]],
            fixture_callable: Callable, arguments: List[str], cur_execution_level: str):
        """
        This helper method validates a given fixture reference for the unclear setup scoped fixture reference.

        The problem:
        A scenario scoped fixture (defined in a scenario) with the execution level SESSION references a fixture (over
        an argument) with a name that is also used for one or more setup scoped fixtures with execution level SESSION.

        For this constellation it is unclear which referenced setup scoped fixture is the correct one.

        .. note::
            Note that the error will also be thrown if only one setup fixture with the referenced name exists. (This
            would work, but it becomes difficult to understand it. Balder prohibits it.

        .. note::
            The error will be thrown if a scenario scoped fixture with the execution level SESSION references a fixture
            name that exists in one or more setup scoped fixtures with the execution level SESSION.

        :param fixture_callable_namespace: the namespace of the current fixture

        :param fixture_callable: the callable with the arguments

        :param arguments: the execution level of the fixture

        :param cur_execution_level: the current execution level that is currently active
        """
        from _balder.executor.executor_tree import ExecutorTree
        # this method is only interested in fixtures with execution level SESSION!

        if isinstance(fixture_callable_namespace, Scenario) and cur_execution_level == "session":
            all_setup_scoped_fixtures = []

            for cur_namespace_type, fixtures in ExecutorTree.fixtures.get('session', {}).items():
                if cur_namespace_type is not None and issubclass(cur_namespace_type, Setup):
                    all_setup_scoped_fixtures += [cur_fixt.__name__ for _, cur_fixt in fixtures]
            for cur_arg in arguments:
                if cur_arg in all_setup_scoped_fixtures:
                    raise UnclearSetupScopedFixtureReference(
                        f"your fixture `{fixture_callable.__name__}` has the definition scope SCENARIO and tries to "
                        f"access a fixture name `{cur_arg}` - the environment has one or more SESSION "
                        f"fixtures with the definition scope that have the same name - please rename them!")

    def _sort_fixture_list_of_same_definition_scope(
            self, fixture_namespace_dict: Dict[Tuple[str, Union[Type[ExecutorTree], Type[Scenario], Type[Setup]]],
                                               List[object]], outer_scope_fixtures: List[object]) \
            -> List[Tuple[Union[Type[ExecutorTree], Type[Scenario], Type[Setup]], str, Callable]]:
        """
        This is a helper method that allows to sort the fixtures given in `fixture_namespace_dict`, depending on their
        arguments.
        It also checks that every fixture that is mentioned in the arguments is available and an item of
        ``fixture_namespace_dict`` or ``outer_scope_fixtures``. If the method detects a loop between some fixtures, the
        method throws an exception.

        :param fixture_namespace_dict: the unordered dictionary, where the definition scope namespace object is the key
                                       and a list with the fixture tuple is the value

        :param outer_scope_fixtures: the list of fixtures that have already been ordered as elements before the given
                                     one in ``fixture_list`` (for example the item from another **definition-scope** or
                                     from another **execution-level**)

        :return: the list of tuples where the first element is the definition scope object, the second element is the
                 func_type of the fixture and the third is the fixture callable itself
        """
        if len(fixture_namespace_dict) == 0:
            return []

        # returns the func_type for the given fixture
        fixture_func_types = {}
        for cur_namespace_type, cur_fixture_list in fixture_namespace_dict.items():
            for cur_func_type, cur_fixture in cur_fixture_list:
                fixture_func_types[cur_fixture] = cur_func_type

        # - if we want to access a fixture (over name) from another fixture we have to be careful!
        #   -> if we try to access a fixture with a fixture which is not part of the same namespace scope -> ERROR
        #   -> if we try to access a fixture with a fixture which is part of the same namespace scope -> this fixture
        #      has to run before the other (and return the value to the referencing one)

        # now resolve dependencies, by returning them as single items and add them to the TopologicalSorter
        sorter = TopologicalSorter()

        for cur_namespace_type, cur_fixture_list in fixture_namespace_dict.items():
            for _, cur_fixture in cur_fixture_list:
                # add the item to the sorter, because it should always be executed (also if it is not referenced from
                # another one)
                sorter.add((cur_namespace_type, cur_fixture))
                # determine all function/method arguments that has to be resolved for this fixture
                cur_fixture_args = inspect.getfullargspec(cur_fixture).args
                if fixture_func_types[cur_fixture] in ["instancemethod", "classmethod"]:
                    # this is a class method (remove `cls`) or an instance method (remove `self`)
                    cur_fixture_args = cur_fixture_args[1:]
                # now try to find a possible fixture for every argument
                for cur_arg in cur_fixture_args:
                    # search the fixture in current namespace
                    cur_fixture_list_as_names = [search_fixture.__name__ for _, search_fixture in cur_fixture_list]
                    found = False
                    # found referenced fixture in current namespace and definition scope
                    if cur_arg in cur_fixture_list_as_names:
                        _, cur_arg_fixture = cur_fixture_list[cur_fixture_list_as_names.index(cur_arg)]
                        # only add fixture if the referenced one is not the same as the current fixture
                        if cur_fixture != cur_arg_fixture:
                            sorter.add((cur_namespace_type, cur_fixture), (cur_namespace_type, cur_arg_fixture))
                            found = True
                    # did not find referenced fixture in current namespace and definition scope -> search for it in
                    #  outer scopes
                    if not found:
                        # search it in outer fixture list to secure that they exist
                        if cur_arg not in \
                                [cur_outer_fixture.__name__ for cur_outer_fixture in outer_scope_fixtures]:
                            raise FixtureReferenceError(
                                f"can not find a previous fixture with the name `{cur_arg}`")

        return [(cur_definition_scope, fixture_func_types[cur_func], cur_func)
                for cur_definition_scope, cur_func in sorter.static_order()]

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def is_allowed_to_enter(
            self, branch: Union[ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor, TestcaseExecutor]) \
            -> bool:
        """
        This method return true if the given branch can be entered, otherwise false
        """
        execution_level = self.RESOLVE_TYPE_LEVEL[branch.__class__]
        return execution_level not in self.current_tree_fixtures.keys()

    def is_allowed_to_leave(
            self, branch: Union[ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor, TestcaseExecutor]) \
            -> bool:
        """
        This method returns true if the given branch can be left now (there exist entries from earlier run enter()
        for this branch), otherwise false
        """
        execution_level = self.RESOLVE_TYPE_LEVEL[branch.__class__]
        return execution_level in self.current_tree_fixtures.keys()

    def enter(self, branch: Union[ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor, TestcaseExecutor]):
        """
        With this method you enter a branch for the fixture manager in order to execute the fixtures contained in it

        :param branch: specifies the element of the ExecutorTree that should be entered (note that the current position
                       is very important here)

        :raise BalderFixtureException: is thrown if an error occurs while executing a user fixture
        """
        execution_level = self.RESOLVE_TYPE_LEVEL[branch.__class__]

        if not self.is_allowed_to_enter(branch):
            raise LostInExecutorTreeException(
                "the current branch that should be entered is not allowed, because other branches weren't left yet")

        def empty():
            yield None
        # now iterate over all fixtures that should be executed in this enter() call
        #  -> collect them with all different DEFINITION-SCOPES
        for cur_definition_scope in self.DEFINITION_SCOPE_ORDER:
            cur_fixture_list = self.get_all_fixtures_for_current_level(branch=branch).get(cur_definition_scope)
            for cur_scope_namespace_type, cur_fixture_func_type, cur_fixture in cur_fixture_list:
                try:
                    if cur_fixture_func_type in ["function", "staticmethod"]:
                        # fixture is a function or a staticmethod - no first special attribute
                        kwargs = self.get_all_attribute_values(branch, cur_scope_namespace_type, cur_fixture,
                                                               cur_fixture_func_type)
                        cur_generator = cur_fixture(**kwargs)
                    elif cur_fixture_func_type == "classmethod":
                        kwargs = self.get_all_attribute_values(branch, cur_scope_namespace_type, cur_fixture,
                                                               cur_fixture_func_type)
                        cur_generator = cur_fixture(cur_scope_namespace_type, **kwargs)
                    elif cur_fixture_func_type == "instancemethod":
                        self_reference = branch.get_all_base_instances_of_this_branch(
                            with_type=cur_scope_namespace_type, only_runnable_elements=True)
                        if len(self_reference) != 1:
                            raise UnclearUniqueClassReference(
                                f"can not find exactly one reference of the class "
                                f"`{cur_scope_namespace_type.__name__}` in current tree branch")
                        kwargs = self.get_all_attribute_values(branch, cur_scope_namespace_type, cur_fixture,
                                                               cur_fixture_func_type)
                        cur_generator = cur_fixture(self_reference[0], **kwargs)
                    else:
                        raise ValueError(f"found illegal value for func_type `{cur_fixture_func_type}` for fixture "
                                         f"`{cur_fixture.__name__}`")
                    if isinstance(cur_generator, Generator):
                        cur_retvalue = next(cur_generator)
                    else:
                        cur_retvalue = cur_generator
                        cur_generator = empty()
                        next(cur_generator)
                    # add the executed fixtures to global reference
                    if execution_level not in self.current_tree_fixtures.keys():
                        self.current_tree_fixtures[execution_level] = []
                    self.current_tree_fixtures[execution_level].append(
                        (cur_scope_namespace_type, cur_fixture_func_type, cur_fixture, cur_generator, cur_retvalue))
                except StopIteration:
                    pass
                except Exception as exc:
                    # every other exception that is thrown, will be recognized and rethrown
                    branch.construct_result.set_result(ResultState.ERROR, exc)
                    raise exc
        # set fixture construct part to SUCCESS if no error occurs
        branch.construct_result.set_result(ResultState.SUCCESS)

    def leave(self, branch: Union[ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor, TestcaseExecutor]):
        """
        With this method you leave a previously entered branch and execute the teardown code of the fixtures. Note that
        you can only leave the branch that you entered before!

        :param branch: specifies the element of the ExecutorTree that should be left (note that the current position
                       is very important here)
        """
        execution_level = self.RESOLVE_TYPE_LEVEL[branch.__class__]
        if execution_level not in self.current_tree_fixtures.keys():
            raise LostInExecutorTreeException("can not leave the current branch, because it was not entered before")

        current_tree_fixtures_reversed = self.current_tree_fixtures[execution_level]
        current_tree_fixtures_reversed.reverse()
        exception = None
        for _, _, cur_fixture, cur_generator, _ in current_tree_fixtures_reversed:
            try:
                next(cur_generator)
            except StopIteration:
                pass
            except Exception as exc:
                # print traceback of the current exception
                traceback.print_exception(*sys.exc_info())
                # every other exception that is thrown, will be recognized and rethrown
                branch.teardown_result.set_result(ResultState.ERROR, exc)
                if not exception:
                    # only save the first exception
                    exception = exc

        # reset the left location
        del self.current_tree_fixtures[execution_level]

        if exception:
            raise exception

        # set fixture construct part to SUCCESS if no error occurs
        branch.teardown_result.set_result(ResultState.SUCCESS)

    def get_all_fixtures_for_current_level(
            self, branch: Union[ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor, TestcaseExecutor]) \
            -> Dict[Union[Type[ExecutorTree], Type[Scenario], Type[Setup]],
                    List[Tuple[Union[Type[ExecutorTree], Type[Scenario], Type[Setup]], str, object]]]:
        """
        This method delivers all fixtures which should be executed for the given branch of the executor tree.

        The method collects the following fixtures from all three possible DEFINITION-SCOPES:
        1. collect them from balderglob.py (see ``FixtureManager._glob_fixtures``)
        2. collect them from current used Setup OR if no specific one is set (because we are in a higher branch):
           collect them from all that are part of the current branch
        3. collect them from current used Scenario OR if no specific one is set (because we are in a higher branch):
           collect them from all that are part of the current branch

        :param branch: the branch which is currently active

        :return: a dictionary where the definition object (DEFINITION SCOPE) is the key and a list is the
                 value - this value list has tuple elements as children, where the namespace class (:class:`Scenario`
                 or :class:`Setup`) as first argument, the fixture func_type as second and the fixture callable as third
                 argument (this list is ordered after the call hierarchy)
        """
        from _balder.executor.executor_tree import ExecutorTree
        # current relevant EXECUTION LEVEL - all other levels are not relevant for this call
        cur_execution_level = self.RESOLVE_TYPE_LEVEL[branch.__class__]
        # get all fixtures of the current relevant level
        fixtures_of_exec_level = ExecutorTree.fixtures.get(cur_execution_level, {})

        all_fixtures = {}
        # get all relevant fixtures of `balderglob.py` (None is key for balderglob fixtures)
        glob_fixtures = fixtures_of_exec_level.get(None, [])
        all_fixtures[ExecutorTree] = {}
        all_fixtures[ExecutorTree][ExecutorTree] = glob_fixtures
        # get all relevant fixtures with definition scope "setup"
        all_fixtures[Setup] = {}
        for cur_setup in branch.get_all_base_instances_of_this_branch(Setup, only_runnable_elements=True):
            # check if there exists fixtures for the current setup
            cur_setup_fixtures = fixtures_of_exec_level.get(cur_setup.__class__, [])
            if cur_setup_fixtures:
                all_fixtures[Setup][cur_setup.__class__] = cur_setup_fixtures

        # get all relevant fixtures with definition scope "scenario"
        all_fixtures[Scenario] = {}
        for cur_scenario in branch.get_all_base_instances_of_this_branch(Scenario, only_runnable_elements=True):
            cur_scenario_fixtures = fixtures_of_exec_level.get(cur_scenario.__class__, [])
            if cur_scenario_fixtures:
                all_fixtures[Scenario][cur_scenario.__class__] = cur_scenario_fixtures

        ordered_fixtures = {}
        # Now the basic order is: [All of ExecutorTree] -> [All of Setup] -> [All of Scenario]
        #  but the order within these DEFINITION SCOPES has to be determined now!
        outer_scope_fixtures = self.all_already_run_fixtures
        ordered_fixtures[ExecutorTree] = self._sort_fixture_list_of_same_definition_scope(
            fixture_namespace_dict=all_fixtures[ExecutorTree], outer_scope_fixtures=outer_scope_fixtures)

        outer_scope_fixtures = \
            self.all_already_run_fixtures + \
            [cur_fixture for _, _, cur_fixture in ordered_fixtures[ExecutorTree]]
        ordered_fixtures[Setup] = self._sort_fixture_list_of_same_definition_scope(
            fixture_namespace_dict=all_fixtures[Setup], outer_scope_fixtures=outer_scope_fixtures)

        outer_scope_fixtures = \
            self.all_already_run_fixtures + \
            [cur_fixture for _, _, cur_fixture in ordered_fixtures[ExecutorTree]] + \
            [cur_fixture for _, _, cur_fixture in ordered_fixtures[Setup]]
        ordered_fixtures[Scenario] = self._sort_fixture_list_of_same_definition_scope(
            fixture_namespace_dict=all_fixtures[Scenario], outer_scope_fixtures=outer_scope_fixtures)

        return ordered_fixtures
