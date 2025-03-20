from __future__ import annotations
from typing import Any, TYPE_CHECKING

from collections import OrderedDict
from _balder.utils.functions import get_method_type
from .testcase_executor import TestcaseExecutor

if TYPE_CHECKING:
    from _balder.executor.unresolved_parametrized_testcase_executor import UnresolvedParametrizedTestcaseExecutor
    from _balder.executor.variation_executor import VariationExecutor


class ParametrizedTestcaseExecutor(TestcaseExecutor):
    """
    special testcase executor for parametrized testcases
    """
    def __init__(
            self,
            testcase: callable,
            parent: VariationExecutor,
            parametrization: OrderedDict[str, Any] = None,
            unresolved_group_obj: UnresolvedParametrizedTestcaseExecutor = None
    ) -> None:
        super().__init__(testcase=testcase, parent=parent)
        self._parametrization = parametrization
        # holds a reference to the parent unresolved object (if it has dynamic parametrized components
        self._unresolved_group_obj: UnresolvedParametrizedTestcaseExecutor | None = unresolved_group_obj

    @property
    def full_test_name_str(self) -> str:
        """
        returns the name of the test method, that should be used in output
        """
        # try to get string name for parametrization
        if self._parametrization:
            # todo what if it is not convertable to string?
            parametrization_name = ';'.join([str(e) for e in self._parametrization.values()])
            return f"{super().full_test_name_str}[{parametrization_name}]"
        return super().full_test_name_str

    def get_all_test_method_args(self):
        func_type = get_method_type(self.base_testcase_obj.__class__, self.base_testcase_callable)
        all_kwargs = self.fixture_manager.get_all_attribute_values(
            self,
            self.base_testcase_obj.__class__,
            self.base_testcase_callable,
            func_type,
            ignore_attributes=self._parametrization.keys()
        )
        if self._parametrization:
            all_kwargs.update(self._parametrization)
        return all_kwargs
