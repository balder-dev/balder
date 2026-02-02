import re

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession
from ...test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0ResolveOnly(Base0EnvtesterClass):
    """
    This testcase executes the basic ENV example with a specific command line argument ``--resolve-only``.

    The test checks that no tests are executed and the printed information is like expected.
    """

    @property
    def cmd_args(self):
        return ['--resolve-only']

    @property
    def expected_data(self) -> tuple:
        return tuple()

    def validate_printed_output(self, stdout: str) -> bool:
        assert self._check_header_of_stdout(stdout, 2, 2, 2), f"problems within header output"
        remaining_lines = stdout.splitlines()
        assert remaining_lines[7] == "RESOLVING OVERVIEW"
        split_blocks = "\n".join(remaining_lines[8:]).strip().split('\n\n')
        assert len(split_blocks) == 2

        expected_blocks = [
"""++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ [APPLICABLE] Scenario `ScenarioB` <-> Setup `SetupB`
+    ScenarioB.ScenarioDevice3 = SetupB.SetupDevice3
+    ScenarioB.ScenarioDevice4 = SetupB.SetupDevice4
+    -> Testcase<ScenarioB.test_b_1>
+    -> Testcase<ScenarioB.test_b_2>
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++""",
"""++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ [APPLICABLE] Scenario `ScenarioA` <-> Setup `SetupA`
+    ScenarioA.ScenarioDevice1 = SetupA.SetupDevice1
+    ScenarioA.ScenarioDevice2 = SetupA.SetupDevice2
+    -> Testcase<ScenarioA.test_a_1>
+    -> Testcase<ScenarioA.test_a_2>
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
        ]

        assert sorted(split_blocks) == sorted(expected_blocks), f"detect issues in blocks"
        return True

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere (have to be SUCCESS everywhere
        assert session.executor_tree.executor_result == ResultState.NOT_RUN, \
            "test session does not terminates with NOT_RUN"
