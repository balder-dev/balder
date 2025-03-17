from __future__ import annotations
from typing import Union, Type, Callable, Generator, TYPE_CHECKING
import dataclasses

from .utils.typings import MethodLiteralType

if TYPE_CHECKING:
    from _balder.scenario import Scenario
    from _balder.setup import Setup


@dataclasses.dataclass
class FixtureMetadata:
    """
    describes meta information for a fixture
    """
    #: the namespace where it is defined (None if it is in a balderglob file)
    namespace: Union[None, Type[Scenario], Type[Setup]]
    #: the type of the fixture function
    function_type: MethodLiteralType
    #: the fixture callable itself
    callable: Callable
    #: the generator object (if the fixture is not a generator, it holds an empty generator)
    generator: Generator
    #: result according to the fixture's construction code (will be cleaned after it leaves a level)
    retval: object
