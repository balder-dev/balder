from __future__ import annotations

import itertools
from typing import List, Tuple, Generator, Dict, Union, Type, Callable, Iterable, TYPE_CHECKING

import inspect
from graphlib import TopologicalSorter
from _balder.executor.testcase_executor import TestcaseExecutor
from _balder.scenario import Scenario
from _balder.setup import Setup
from _balder.fixture_definition_scope import FixtureDefinitionScope
from _balder.fixture_execution_level import FixtureExecutionLevel
from _balder.fixture_metadata import FixtureMetadata
from _balder.executor.basic_executor import BasicExecutor
from _balder.executor.setup_executor import SetupExecutor
from _balder.executor.scenario_executor import ScenarioExecutor
from _balder.executor.variation_executor import VariationExecutor
from _balder.exceptions import LostInExecutorTreeException, FixtureReferenceError, UnclearSetupScopedFixtureReference, \
    UnclearUniqueClassReference

if TYPE_CHECKING:
    from _balder.utils.functions import MethodLiteralType
    from _balder.executor.executor_tree import ExecutorTree


class FixtureManager:
    """
    This class is the global fixture manager. It provides various methods to manage fixtures in the balder system.
    """

    def __init__(
            self,
            fixtures: Dict[FixtureExecutionLevel,
                           Dict[Union[None, Type[Scenario], Type[Setup]], List[Tuple[MethodLiteralType, Callable]]]]):

        # The first key is the fixture level, the second key is the namespace in which the fixture is defined. As value
        # a list with tuples is returned. The first element is the type of the method/function and the second is the
        # callable itself.
        self.fixtures: Dict[FixtureExecutionLevel,
                            Dict[Union[None, Type[Scenario], Type[Setup]], List[Tuple[MethodLiteralType, Callable]]]] \
            = fixtures

        # contains all active fixtures with their namespace, their func_type, their callable, the generator object and
        # the result according to the fixture's construction code (will be cleaned after it leaves a level)
        self.current_tree_fixtures: Dict[FixtureExecutionLevel, List[FixtureMetadata]] = {}

    # ---------------------------------- STATIC METHODS ----------------------------------------------------------------

    # ---------------------------------- CLASS METHODS ----------------------------------------------------------------

    # ---------------------------------- PROPERTIES --------------------------------------------------------------------

    @property
    def all_already_run_fixtures(self) -> List[Callable]:
        """
        returns a list of all fixtures that have already been run
        """
        complete_list_in_order = []
        for cur_level in FixtureExecutionLevel:
            if cur_level in self.current_tree_fixtures.keys():
                complete_list_in_order += [
                    cur_fixture_metadata.callable for cur_fixture_metadata in self.current_tree_fixtures[cur_level]]
        return complete_list_in_order

    # ---------------------------------- PROTECTED METHODS -------------------------------------------------------------

    def _validate_for_unclear_setup_scoped_fixture_reference(
            self, fixture_callable_namespace: Union[None, Type[Scenario], Type[Setup]],
            fixture_callable: Callable, arguments: List[str], cur_execution_level: FixtureExecutionLevel):
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

        :param fixture_callable_namespace: the namespace of the current fixture or None if it is a `balderglob.py` file

        :param fixture_callable: the callable with the arguments

        :param arguments: the execution level of the fixture

        :param cur_execution_level: the current execution level that is currently active
        """
        # this method is only interested in fixtures with execution level SESSION!

        if (fixture_callable_namespace is not None and isinstance(fixture_callable_namespace, Scenario)
                and cur_execution_level == FixtureExecutionLevel.SESSION):
            all_setup_scoped_fixtures = []

            for cur_namespace_type, fixtures in self.fixtures.get(FixtureExecutionLevel.SESSION, {}).items():
                if cur_namespace_type is not None and issubclass(cur_namespace_type, Setup):
                    all_setup_scoped_fixtures += [cur_fixt.__name__ for _, cur_fixt in fixtures]
            for cur_arg in arguments:
                if cur_arg in all_setup_scoped_fixtures:
                    raise UnclearSetupScopedFixtureReference(
                        f"your fixture `{fixture_callable.__name__}` has the definition scope SCENARIO and tries to "
                        f"access a fixture name `{cur_arg}` - the environment has one or more SESSION "
                        f"fixtures with the definition scope that have the same name - please rename them!")

    def _sort_fixture_list_of_same_definition_scope(
            self, fixture_namespace_dict: Dict[Union[None, Type[Scenario], Type[Setup]], List[object]],
            outer_scope_fixtures: List[object]) \
            -> List[Tuple[Union[None, Type[Scenario], Type[Setup]], str, Callable]]:
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
        for _, cur_fixture_list in fixture_namespace_dict.items():
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

    def _determine_setup_and_scenario_type(
            self,
            from_branch: Union[ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor, TestcaseExecutor],
            callable_func_namespace: Union[None, Type[Scenario], Type[Setup]]) \
            -> Tuple[Union[None, Type[Setup]], Union[None, Type[Scenario]]]:
        """
        determines the setup and scenario type for a specific fixture based on the branch the system is in

        :param from_branch: the branch for which the types should be determined
        :param callable_func_namespace: the namespace of the current fixture or `None` if it is defined in balderglob
                                        file
        """
        # determine namespaces (in the correct order)
        setup_type = None
        scenario_type = None
        if isinstance(from_branch, SetupExecutor):
            setup_type = from_branch.base_setup_class.__class__
            # normally the scenario is None - only if the current namespace is a scenario we can use it
            if callable_func_namespace is not None and issubclass(callable_func_namespace, Scenario):
                scenario_type = callable_func_namespace
            else:
                scenario_type = None
        elif isinstance(from_branch, ScenarioExecutor):
            setup_type = from_branch.parent_executor.base_setup_class.__class__
            scenario_type = from_branch.base_scenario_class.__class__
        elif isinstance(from_branch, VariationExecutor):
            setup_type = from_branch.cur_setup_class.__class__
            scenario_type = from_branch.cur_scenario_class.__class__
        elif isinstance(from_branch, TestcaseExecutor):
            setup_type = from_branch.parent_executor.cur_setup_class.__class__
            scenario_type = from_branch.parent_executor.cur_scenario_class.__class__
        return setup_type, scenario_type

    # ---------------------------------- METHODS -----------------------------------------------------------------------

    def is_allowed_to_enter(
            self, branch: Union[BasicExecutor, ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor,
                                TestcaseExecutor]) -> bool:
        """
        This method return true if the given branch can be entered, otherwise false
        """
        return branch.fixture_execution_level not in self.current_tree_fixtures.keys()

    def is_allowed_to_leave(
            self, branch: Union[BasicExecutor, ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor,
                                TestcaseExecutor]) \
            -> bool:
        """
        This method returns true if the given branch can be left now (there exist entries from earlier run enter()
        for this branch), otherwise false
        """
        return branch.fixture_execution_level in self.current_tree_fixtures.keys()

    def enter(self, branch: Union[BasicExecutor, ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor,
                                  TestcaseExecutor]):
        """
        With this method you enter a branch for the fixture manager in order to execute the fixtures contained in it

        :param branch: specifies the element of the ExecutorTree that should be entered (note that the current position
                       is very important here)

        :raise BalderFixtureException: is thrown if an error occurs while executing a user fixture
        """

        if not self.is_allowed_to_enter(branch):
            raise LostInExecutorTreeException(
                "the current branch that should be entered is not allowed, because other branches weren't left yet")

        def empty():
            yield None
        # now iterate over all fixtures that should be executed in this enter() call
        #  -> collect them with all different DEFINITION-SCOPES
        for cur_definition_scope in FixtureDefinitionScope:
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
                    if branch.fixture_execution_level not in self.current_tree_fixtures.keys():
                        self.current_tree_fixtures[branch.fixture_execution_level] = []
                    self.current_tree_fixtures[branch.fixture_execution_level].append(
                        FixtureMetadata(namespace=cur_scope_namespace_type, function_type=cur_fixture_func_type,
                                        callable=cur_fixture, generator=cur_generator, retval=cur_retvalue))
                except StopIteration:
                    pass
                # every other exception that is thrown, will be recognized and rethrown

    def leave(self, branch: Union[BasicExecutor, ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor,
                                  TestcaseExecutor]):
        """
        With this method you leave a previously entered branch and execute the teardown code of the fixtures. Note that
        you can only leave the branch that you entered before!

        :param branch: specifies the element of the ExecutorTree that should be left (note that the current position
                       is very important here)
        """
        if branch.fixture_execution_level not in self.current_tree_fixtures.keys():
            raise LostInExecutorTreeException("can not leave the current branch, because it was not entered before")

        current_tree_fixtures_reversed = self.current_tree_fixtures[branch.fixture_execution_level]
        current_tree_fixtures_reversed.reverse()
        exception = None
        for cur_fixture_metadata in current_tree_fixtures_reversed:
            try:
                next(cur_fixture_metadata.generator)
            except StopIteration:
                pass
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if not exception:
                    # only save the first exception
                    exception = exc

        # reset the left location
        del self.current_tree_fixtures[branch.fixture_execution_level]

        if exception:
            raise exception

    def get_all_attribute_values(
            self, branch: Union[ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor, TestcaseExecutor],
            callable_func_namespace: Union[None, Type[Scenario], Type[Setup]], callable_func: Callable,
            func_type: str, ignore_attributes: Iterable[str] = None) -> Dict[str, object]:
        """
        This method tries to fill the unresolved function/method arguments of the given fixture callable. For this it
        searches the return values of all already executed fixtures and supplies the argument values of the
        given ``fixture`` callable in a dictionary.

        It automatically manages `self` / `cls` references for func_type `instancemethod` or `classmethod`. It
        only returns the fixture references and ignores `self` / `cls`

        First the method tries to find the arguments in all fixtures that are in the same namespace. If it does not find
        any references, it will look in the next higher scope. It only uses fixture that has run before!

        :param branch: the current active branch
        :param callable_func_namespace: the namespace of the current fixture or `None` if it is defined in balderglob
                                        file
        :param callable_func: the callable with the arguments
        :param func_type: returns the func_type of the fixture - depending on this value the first argument will be
                          ignored, because it has to be `cls` for `classmethod` and `self` for `instancemethod`
        :param ignore_attributes: holds a list of attributes in the test method that should be ignored
        :return: the method returns a dictionary with the attribute name as key and the return value as value

        """
        arguments = inspect.getfullargspec(callable_func).args
        result_dict = {}

        if func_type in ["classmethod", "instancemethod"]:
            arguments = arguments[1:]
        if ignore_attributes is None:
            ignore_attributes = []

        self._validate_for_unclear_setup_scoped_fixture_reference(
            callable_func_namespace, callable_func, arguments, cur_execution_level=branch.fixture_execution_level)
        all_possible_namespaces = [None]
        setup_type, scenario_type = self._determine_setup_and_scenario_type(
            from_branch=branch, callable_func_namespace=callable_func_namespace)

        # add to possible namespaces only if the namespace of the current fixture allows this
        if callable_func_namespace is not None:
            if (issubclass(callable_func_namespace, Setup) or issubclass(callable_func_namespace, Scenario)) \
                    and setup_type is not None:
                all_possible_namespaces.append(setup_type)
            if issubclass(callable_func_namespace, Scenario) and scenario_type is not None:
                all_possible_namespaces.append(scenario_type)

        for cur_arg in arguments:
            if cur_arg in ignore_attributes:
                continue
            # go to the most specific fixture, because more specific ones overwrite the more global ones
            for cur_possible_namespace, cur_level in itertools.product(all_possible_namespaces, FixtureExecutionLevel):
                if cur_level not in self.current_tree_fixtures.keys():
                    continue
                # filter only these fixtures that have the same namespace
                for cur_fixture_metadata in self.current_tree_fixtures[cur_level]:
                    if (cur_fixture_metadata.namespace == cur_possible_namespace
                            and cur_fixture_metadata.callable.__name__ == cur_arg):
                        result_dict[cur_arg] = cur_fixture_metadata.retval
            if cur_arg not in result_dict.keys():
                raise FixtureReferenceError(
                        f"the argument `{cur_arg}` in fixture `{callable_func.__qualname__}` could not be resolved")
        return result_dict

    def get_fixture_for_class(self, execution_level: FixtureExecutionLevel,
                              setup_or_scenario_class: Union[None, Type[Setup], Type[Scenario]],
                              parent_classes: bool = True) -> List[Tuple[MethodLiteralType, Callable]]:
        """
        This method returns all classes of a specific Setup/Scenario class for a specific execution-level.

        :param execution_level: the execution level the fixture should be returned for
        :param setup_or_scenario_class: the scenario or setup class, the fixtures should be returned for
        :param parent_classes: true if the method should look for fixtures in parent classes too
        :return: list with all fixtures that are matching search criteria
        """
        # get all fixtures of the current relevant level (only `execution_level` is relevant - all other levels are
        # not relevant for this call)
        fixtures_of_exec_level = self.fixtures.get(execution_level, {})
        if setup_or_scenario_class is not None and parent_classes:
            all_fixtures = []
            for cur_parent_class in inspect.getmro(setup_or_scenario_class):
                if issubclass(cur_parent_class, (Scenario, Setup)):
                    all_fixtures += self.get_fixture_for_class(execution_level, cur_parent_class, False)
            # go through list and remove all overwritten fixtures
            _added_fixtures = []
            remaining_fixtures = []
            for cur_fixture_tuple in all_fixtures:
                if cur_fixture_tuple[1].__name__ not in _added_fixtures:
                    _added_fixtures.append(cur_fixture_tuple[1].__name__)
                    remaining_fixtures.append(cur_fixture_tuple)
            return remaining_fixtures
        return fixtures_of_exec_level.get(setup_or_scenario_class, [])

    def get_all_fixtures_for_current_level(
            self, branch: Union[ExecutorTree, SetupExecutor, ScenarioExecutor, VariationExecutor, TestcaseExecutor]) \
            -> Dict[FixtureDefinitionScope, List[Tuple[Union[None, Type[Scenario], Type[Setup]], str, object]]]:
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
        all_fixtures = {}
        # get all relevant fixtures of `balderglob.py` (None is key for balderglob fixtures)
        glob_fixtures = self.get_fixture_for_class(branch.fixture_execution_level, None)
        all_fixtures[FixtureDefinitionScope.GLOB] = {}
        all_fixtures[FixtureDefinitionScope.GLOB][None] = glob_fixtures
        # get all relevant fixtures with definition scope "setup"
        all_fixtures[FixtureDefinitionScope.SETUP] = {}
        for cur_setup in branch.get_all_base_instances_of_this_branch(Setup, only_runnable_elements=True):
            # check if there exists fixtures for the current setup
            cur_setup_fixtures = self.get_fixture_for_class(branch.fixture_execution_level, cur_setup.__class__)
            if cur_setup_fixtures:
                all_fixtures[FixtureDefinitionScope.SETUP][cur_setup.__class__] = cur_setup_fixtures

        # get all relevant fixtures with definition scope "scenario"
        all_fixtures[FixtureDefinitionScope.SCENARIO] = {}
        for cur_scenario in branch.get_all_base_instances_of_this_branch(Scenario, only_runnable_elements=True):
            cur_scenario_fixtures = self.get_fixture_for_class(branch.fixture_execution_level, cur_scenario.__class__)
            if cur_scenario_fixtures:
                all_fixtures[FixtureDefinitionScope.SCENARIO][cur_scenario.__class__] = cur_scenario_fixtures

        ordered_fixtures = {}
        # Now the basic order is: [All of ExecutorTree] -> [All of Setup] -> [All of Scenario]
        #  but the order within these DEFINITION SCOPES has to be determined now!
        outer_scope_fixtures = self.all_already_run_fixtures
        ordered_fixtures[FixtureDefinitionScope.GLOB] = self._sort_fixture_list_of_same_definition_scope(
            fixture_namespace_dict=all_fixtures[FixtureDefinitionScope.GLOB], outer_scope_fixtures=outer_scope_fixtures)

        outer_scope_fixtures = \
            self.all_already_run_fixtures + \
            [cur_fixture for _, _, cur_fixture in ordered_fixtures[FixtureDefinitionScope.GLOB]]
        ordered_fixtures[FixtureDefinitionScope.SETUP] = self._sort_fixture_list_of_same_definition_scope(
            fixture_namespace_dict=all_fixtures[FixtureDefinitionScope.SETUP],
            outer_scope_fixtures=outer_scope_fixtures)

        outer_scope_fixtures = \
            self.all_already_run_fixtures + \
            [cur_fixture for _, _, cur_fixture in ordered_fixtures[FixtureDefinitionScope.GLOB]] + \
            [cur_fixture for _, _, cur_fixture in ordered_fixtures[FixtureDefinitionScope.SETUP]]
        ordered_fixtures[FixtureDefinitionScope.SCENARIO] = self._sort_fixture_list_of_same_definition_scope(
            fixture_namespace_dict=all_fixtures[FixtureDefinitionScope.SCENARIO],
            outer_scope_fixtures=outer_scope_fixtures)

        return ordered_fixtures
