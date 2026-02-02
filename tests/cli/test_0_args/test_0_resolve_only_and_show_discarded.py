import re

from _balder.testresult import ResultState
from _balder.balder_session import BalderSession
from ...test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0ResolveOnlyAndShowDiscarded(Base0EnvtesterClass):
    """
    This testcase executes the basic ENV example with a specific command line argument
    ``--resolve-only --show-discarded``.

    The test checks that no tests are executed and the printed information is like expected. Additionally, it ensures
    that all discarded tests are printed too and the reason why they were discarded is printed too.
    """

    @property
    def cmd_args(self):
        return ['--resolve-only', '--show-discarded']

    @property
    def expected_data(self) -> tuple:
        return tuple()

    def validate_printed_output(self, stdout: str) -> bool:
        assert self._check_header_of_stdout(stdout, 2, 2, 2, expected_discarded=6), \
            f"problems within header output"
        remaining_lines = stdout.splitlines()
        assert remaining_lines[7] == "RESOLVING OVERVIEW"
        split_blocks = "\n".join(remaining_lines[8:]).strip().split('\n\n')
        assert len(split_blocks) == 8

        expected_blocks = [
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X [DISCARDED]  Scenario `ScenarioA` <-> Setup `SetupB`
X    ScenarioA.ScenarioDevice1 = SetupB.SetupDevice3
X    ScenarioA.ScenarioDevice2 = SetupB.SetupDevice4
X    -> Testcase<ScenarioA.test_a_1>
X    -> Testcase<ScenarioA.test_a_2>
X
X    DISCARDED BECAUSE `this variation can not be applicable because there was no setup feature implementation of `FeatureI` (used by scenario device `ScenarioDevice1`) in setup device `SetupDevice3``
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX""",
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X [DISCARDED]  Scenario `ScenarioA` <-> Setup `SetupB`
X    ScenarioA.ScenarioDevice1 = SetupB.SetupDevice4
X    ScenarioA.ScenarioDevice2 = SetupB.SetupDevice3
X    -> Testcase<ScenarioA.test_a_1>
X    -> Testcase<ScenarioA.test_a_2>
X
X    DISCARDED BECAUSE `this variation can not be applicable because there was no setup feature implementation of `FeatureI` (used by scenario device `ScenarioDevice1`) in setup device `SetupDevice4``
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX""",
"""++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ [APPLICABLE] Scenario `ScenarioB` <-> Setup `SetupB`
+    ScenarioB.ScenarioDevice3 = SetupB.SetupDevice3
+    ScenarioB.ScenarioDevice4 = SetupB.SetupDevice4
+    -> Testcase<ScenarioB.test_b_1>
+    -> Testcase<ScenarioB.test_b_2>
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++""",
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X [DISCARDED]  Scenario `ScenarioB` <-> Setup `SetupB`
X    ScenarioB.ScenarioDevice3 = SetupB.SetupDevice4
X    ScenarioB.ScenarioDevice4 = SetupB.SetupDevice3
X    -> Testcase<ScenarioB.test_b_1>
X    -> Testcase<ScenarioB.test_b_2>
X
X    DISCARDED BECAUSE `this variation can not be applicable because there was no setup feature implementation of `FeatureIII` (used by scenario device `ScenarioDevice3`) in setup device `SetupDevice4``
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX""",
"""++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ [APPLICABLE] Scenario `ScenarioA` <-> Setup `SetupA`
+    ScenarioA.ScenarioDevice1 = SetupA.SetupDevice1
+    ScenarioA.ScenarioDevice2 = SetupA.SetupDevice2
+    -> Testcase<ScenarioA.test_a_1>
+    -> Testcase<ScenarioA.test_a_2>
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++""",
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X [DISCARDED]  Scenario `ScenarioA` <-> Setup `SetupA`
X    ScenarioA.ScenarioDevice1 = SetupA.SetupDevice2
X    ScenarioA.ScenarioDevice2 = SetupA.SetupDevice1
X    -> Testcase<ScenarioA.test_a_1>
X    -> Testcase<ScenarioA.test_a_2>
X
X    DISCARDED BECAUSE `this variation can not be applicable because there was no setup feature implementation of `FeatureI` (used by scenario device `ScenarioDevice1`) in setup device `SetupDevice2``
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX""",
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X [DISCARDED]  Scenario `ScenarioB` <-> Setup `SetupA`
X    ScenarioB.ScenarioDevice3 = SetupA.SetupDevice1
X    ScenarioB.ScenarioDevice4 = SetupA.SetupDevice2
X    -> Testcase<ScenarioB.test_b_1>
X    -> Testcase<ScenarioB.test_b_2>
X
X    DISCARDED BECAUSE `this variation can not be applicable because there was no setup feature implementation of `FeatureIII` (used by scenario device `ScenarioDevice3`) in setup device `SetupDevice1``
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX""",
"""XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X [DISCARDED]  Scenario `ScenarioB` <-> Setup `SetupA`
X    ScenarioB.ScenarioDevice3 = SetupA.SetupDevice2
X    ScenarioB.ScenarioDevice4 = SetupA.SetupDevice1
X    -> Testcase<ScenarioB.test_b_1>
X    -> Testcase<ScenarioB.test_b_2>
X
X    DISCARDED BECAUSE `this variation can not be applicable because there was no setup feature implementation of `FeatureIII` (used by scenario device `ScenarioDevice3`) in setup device `SetupDevice2``
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""
        ]

        assert sorted(split_blocks) == sorted(expected_blocks), f"detect issues in blocks"
        return True

    @staticmethod
    def validate_finished_session(session: BalderSession):
        assert session.executor_tree.executor_result == ResultState.NOT_RUN, \
            "test session does not terminates with NOT_RUN"
