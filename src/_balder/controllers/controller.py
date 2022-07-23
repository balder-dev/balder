from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__file__)


class Controller(ABC):
    """
    This is the base controller class. It serves as a base class for all other specialized controllers.

    A controller is used to manage the behavior internally.
    """

    @staticmethod
    @abstractmethod
    def get_for(related_cls):
        """
        This class returns the current existing controller instance for the given item. If the instance does not exist
        yet, it will automatically create it and saves the instance in an internal dictionary.
        """

    @property
    @abstractmethod
    def related_cls(self):
        """
        This method returns the related class that belongs to that controller.
        """
