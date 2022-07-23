from __future__ import annotations
from typing import TYPE_CHECKING, Type, Tuple, List

if TYPE_CHECKING:
    from .executor.executor_tree import ExecutorTree
    from .balder_session import BalderSession
    from .setup import Setup
    from .scenario import Scenario
    import argparse

import pathlib


class BalderPlugin:
    """
    This is the balder plugin class. You can create your own plugin, by creating a subclass of it. With that you are
    able to overwrite the methods you want to use in your plugin.
    """

    def __init__(self, session: BalderSession):
        self.balder_session = session

    def addoption(self, argument_parser: argparse.ArgumentParser):
        """
        The callback will be executed while the `ArgumentParser` is being created.

        :param argument_parser: the argument parser object
        """
        pass

    def modify_collected_pyfiles(self, pyfiles: List[pathlib.Path]) -> List[pathlib.Path]:
        """
        This callback will be executed after the :class:`Collector` has collected all python files that are inside the
        current working directory.

        .. note::
            Note that these files are not filtered yet. The list will contain every existing python file.

        :param pyfiles: a list with all python filepaths

        :return: the new list of all filepaths
        """
        pass

    def modify_collected_classes(self, scenarios: List[Type[Scenario]], setups: List[Type[Setup]]) \
            -> Tuple[List[Type[Scenario]], List[Type[Setup]]]:
        """
        This callback will be executed after the :class:`Collector` has collected the :class:`Scenario` classes and the
        :class:`Setup` classes.

        :param scenarios: all collected :class:`Scenario` classes that are currently in the collected list

        :param setups: all collected :class:`Setup` classes that are currently in the collected list

        :return: a tuple of lists, where the first list is the new list with all :class:`Scenario` classes, the second
                 element is a list with all :class:`Setup` classes
        """
        pass

    def filter_executor_tree(self, executor_tree: ExecutorTree) -> None:
        """
        This callback will be executed before the ExecutorTree runs. It contains the current representation
        of the :class:`ExecutorTree`, that will be executed in the next step. With this callback it is possible to
        manipulate the :class:`ExecutorTree`. You have not to return something, the given ``executor_tree`` is a
        reference.

        :param executor_tree: the reference to the main :class:`ExecutorTree` object balder uses for this session
        """
        pass
