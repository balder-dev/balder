from typing import Union
from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0TreecheckFixtSetupaSessionConstruction(Base0EnvtesterClass):
    """
    This testcase executes the basic envtester and forces an error on a specific given position. The test checks if the
    system behaviour is as expected.

    file: ``setups/setup_a.py``
    class: ``SetupA``
    method/function: ``fixture_session``
    part: ``construction``
    """

    @property
    def cmd_args(self):
        return [
            '--test-error-file', 'setups/setup_a.py',
            '--test-error-cls', 'SetupA',
            '--test-error-meth', 'fixture_session',
            '--test-error-part', 'construction',
        ]

    @property
    def expected_exit_code(self):
        return 1

    @property
    def expected_data(self):
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupB.fixture_session
            {"cls": "SetupB", "meth": "fixture_session", "part": "construction"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_session
            {"cls": "SetupA", "meth": "fixture_session", "part": "construction"},
            # {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            # {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # stops execution here (only valid if the ScenarioB fixture was called first)
            # {"cls": "SetupA", "meth": "fixture_session", "part": "teardown"},

            # FIXTURE-TEARDOWN: SetupA.fixture_session
            {"cls": "SetupB", "meth": "fixture_session", "part": "teardown"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "teardown"}
        )

    @property
    def expected_data_alternative(self) -> Union[tuple, None]:
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_session
            {"cls": "SetupA", "meth": "fixture_session", "part": "construction"},

            # {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            # {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            # stops execution here (only valid if the ScenarioB fixture was called first)
            # {"cls": "SetupA", "meth": "fixture_session", "part": "teardown"},

            # FIXTURE-TEARDOWN: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "teardown"},
        )

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere
        assert session.executor_tree.executor_result == ResultState.ERROR, "test session does not terminates with ERROR"

        assert session.executor_tree.construct_result.result == ResultState.ERROR, \
            "global executor tree construct part does not set ResultState.ERROR"
        assert session.executor_tree.body_result.result == ResultState.NOT_RUN, \
            "global executor tree body part does not set ResultState.NOT_RUN"
        assert session.executor_tree.teardown_result.result == ResultState.SUCCESS, \
            "global executor tree teardown part does not set ResultState.SUCCESS"
        for cur_setup_executor in session.executor_tree.get_setup_executors():
            assert cur_setup_executor.executor_result == ResultState.NOT_RUN, \
                "the setup executor does not have result NOT_RUN"

            assert cur_setup_executor.construct_result.result == ResultState.NOT_RUN
            assert cur_setup_executor.body_result.result == ResultState.NOT_RUN
            assert cur_setup_executor.teardown_result.result == ResultState.NOT_RUN

            for cur_scenario_executor in cur_setup_executor.get_scenario_executors():
                assert cur_scenario_executor.executor_result == ResultState.NOT_RUN, \
                    "the scenario executor does not have result NOT_RUN"

                assert cur_scenario_executor.construct_result.result == ResultState.NOT_RUN
                assert cur_scenario_executor.body_result.result == ResultState.NOT_RUN
                assert cur_scenario_executor.teardown_result.result == ResultState.NOT_RUN

                for cur_variation_executor in cur_scenario_executor.get_variation_executors():
                    assert cur_variation_executor.executor_result == ResultState.NOT_RUN, \
                        "the variation executor does not have result NOT_RUN"

                    assert cur_variation_executor.construct_result.result == ResultState.NOT_RUN
                    assert cur_variation_executor.body_result.result == ResultState.NOT_RUN
                    assert cur_variation_executor.teardown_result.result == ResultState.NOT_RUN

                    for cur_testcase_executor in cur_variation_executor.get_testcase_executors():
                        assert cur_testcase_executor.executor_result == ResultState.NOT_RUN, \
                            "the testcase executor does not have result NOT_RUN"

                        assert cur_testcase_executor.construct_result.result == ResultState.NOT_RUN
                        assert cur_testcase_executor.body_result.result == ResultState.NOT_RUN
                        assert cur_testcase_executor.teardown_result.result == ResultState.NOT_RUN
