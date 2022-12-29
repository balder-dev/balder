from __future__ import annotations
from typing import TYPE_CHECKING, List, Type, Tuple, Union

import argparse
import pathlib
from _balder.balder_plugin import BalderPlugin
from _balder.exceptions import UnexpectedPluginMethodReturnValue

if TYPE_CHECKING:
    from _balder.balder_session import BalderSession
    from _balder.executor.executor_tree import ExecutorTree
    from _balder.scenario import Scenario
    from _balder.setup import Setup


class PluginManager:
    """
    This class is a helper class that manages all existing plugins.
    """

    def __init__(self):
        self.all_plugins: List[BalderPlugin] = []

    def register(self, plugin_class: Type[BalderPlugin], session: BalderSession):
        """
        This method registers a new plugin class.

        :param plugin_class: the new class that should be registered

        :param session: the balder session, the new plugin belongs to
        """
        if plugin_class in [cur_plugin_instance.__class__ for cur_plugin_instance in self.all_plugins]:
            raise ValueError(f"the given plugin class `{plugin_class.__name__}` can not be added twice")
        plugin_instance = plugin_class(session)
        self.all_plugins.append(plugin_instance)

    def execute_addoption(self, argument_parser: argparse.ArgumentParser) -> None:
        """
        This method executes all plugin callbacks :ref:`BalderPlugin.addoption`.

        The callback will be executed while the `ArgumentParser` is being created.

        :param argument_parser: the argument parser object
        """
        for cur_plugin in self.all_plugins:
            cur_plugin.addoption(argument_parser)

    def execute_modify_collected_pyfiles(self, pyfiles: List[pathlib.Path]) -> List[pathlib.Path]:
        """
        This method executes all plugin callbacks :ref:`BalderPlugin.cb_filter_executor_tree`.

        The callback will be executed to filter the collected pyfiles, that will be analysed later. From these files,
        balder tries to determine and then import relevant :class:`Scenario` and :class:`Setup` classes later.

        :param pyfiles: a list with all collected pyfiles

        :return: the new list that should be used for the pyfiles
        """
        cur_pyfiles = pyfiles
        for cur_plugin in self.all_plugins:
            if cur_plugin.__class__.modify_collected_pyfiles == BalderPlugin.modify_collected_pyfiles:
                # there is no specific implementation
                break
            ret = cur_plugin.modify_collected_pyfiles(pyfiles=cur_pyfiles)
            if ret is None:
                raise UnexpectedPluginMethodReturnValue(
                    f"the method `modify_collected_pyfiles` of balder plugin `{cur_plugin.__class__.__name__}` has not"
                    f"returned something - a list of filepaths was expected")
            if not isinstance(ret, list):
                raise UnexpectedPluginMethodReturnValue(
                    f"the method `modify_collected_pyfiles` of balder plugin `{cur_plugin.__class__.__name__}` has not"
                    f"returned a list (return type is `{type(ret)}`)")
            cur_pyfiles = ret
        return cur_pyfiles

    def execute_collected_classes(self, scenarios: List[Type[Scenario]], setups: List[Type[Setup]]) \
            -> Tuple[List[Type[Scenario]], List[Type[Setup]]]:
        """
        This method executes all plugin callbacks :ref:`BalderPlugin.cb_filter_executor_tree`.

        The callback will be executed to filter the collected :class:`Scenario` and :class:`Setup` classes.

        :param scenarios: a list with all collected :class:`Scenario` classes before the plugin can filter it

        :param setups: a list with all collected :class:`Setup` classes before the plugin can filter it

        :return: a tuple where the first element is the new :class:`Scenario` list and the second is the new
                 :class:`Setup` class list
        """
        cur_scenarios = scenarios
        cur_setups = setups
        for cur_plugin in self.all_plugins:
            if cur_plugin.__class__.modify_collected_classes == BalderPlugin.modify_collected_classes:
                # there is no specific implementation
                break
            ret = cur_plugin.modify_collected_classes(scenarios=cur_scenarios, setups=cur_setups)
            if ret is None:
                raise UnexpectedPluginMethodReturnValue(
                    f"the method `execute_collected_classes` of balder plugin `{cur_plugin.__class__.__name__}` has not"
                    f"returned something - a tuple with two lists for Scenarios and Setups was expected")
            if not isinstance(ret, tuple):
                raise UnexpectedPluginMethodReturnValue(
                    f"the method `execute_collected_classes` of balder plugin `{cur_plugin.__class__.__name__}` has not"
                    f"returned a tuple (return type is `{type(ret)}`)")
            if not len(ret) == 2:
                raise UnexpectedPluginMethodReturnValue(
                    f"the method `execute_collected_classes` of balder plugin `{cur_plugin.__class__.__name__}` has not"
                    f"returned a tuple of length 2")
            if not isinstance(ret[0], list) or not isinstance(ret[1], list):
                raise UnexpectedPluginMethodReturnValue(
                    f"the method `execute_collected_classes` of balder plugin `{cur_plugin.__class__.__name__}` has not"
                    f"returned a tuple with two lists as values")
            cur_scenarios, cur_setups = ret
        return cur_scenarios, cur_setups

    def execute_filter_executor_tree(self, executor_tree: ExecutorTree) -> None:
        """
        This method executes all plugin methods :ref:`BalderPlugin.filter_executor_tree`.

        The callback will be executed to filter the created :class:`ExecutorTree` for this balder session. For this the
        :class:`ExecutorTree` reference (given by ``executor_tree``) can be manipulated.

        :param executor_tree: the reference to the main :class:`ExecutorTree` object that balder uses for this session
        """
        for cur_plugin in self.all_plugins:
            cur_plugin.filter_executor_tree(executor_tree=executor_tree)

    def execute_session_finished(self, executor_tree: Union[ExecutorTree, None]) -> None:
        """
        This method executes all plugin methods :ref:`BalderPlugin.session_finished`.

        This callback will be executed at the end of every session. The callback will run in a `collect-only` and
        `resolve-only` session too. Note, that the `executor_tree` argument is None in a `collect-only` session.

        :param executor_tree: the reference to the main :class:`ExecutorTree` object that balder uses for this session
        """
        for cur_plugin in self.all_plugins:
            cur_plugin.session_finished(executor_tree=executor_tree)
