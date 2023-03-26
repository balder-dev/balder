from _balder.testresult import ResultState
from _balder.balder_session import BalderSession

from tests.test_utilities.base_01_envtester_methvar_class import Base01EnvtesterMethvarClass


class Test01MethvarParamCheck(Base01EnvtesterMethvarClass):
    """
    This testcase is based on the 01 method-variation envtester environment.

    It checks on different positions (fixtures of setups and scenarios; testcase) if the method-variation parameters
    are provided as expected as done as in normal methods.
    """

    @property
    def expected_data(self) -> tuple:
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},

            [
                (
                    # FIXTURE-CONSTRUCTION: SetupI.fixture_session
                    {"cls": "SetupI", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: SetupII.fixture_session
                    {"cls": "SetupII", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: SetupIII.fixture_session
                    {"cls": "SetupIII", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
                )
            ],

            # FIXTURE-CONSTRUCTION: ScenarioA.fixture_session
            {"cls": "ScenarioA", "meth": "fixture_session", "part": "construction"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something", "category": "feature"},

            [
                self._generate_expected_data_from_setup_on(
                    "SetupI", "VDeviceI", "VDeviceI", "VDeviceI", "VDeviceI", 10),
                self._generate_expected_data_from_setup_on(
                    "SetupII", "VDeviceII", "VDeviceII", "VDeviceII", "VDeviceII", 20),
                self._generate_expected_data_from_setup_on(
                    "SetupIII", "VDeviceIII", "VDeviceIII", "VDeviceIII", "VDeviceIII", 30),
            ],

            # FIXTURE-TEARDOWN: ScenarioA.fixture_session
            {"cls": "ScenarioA", "meth": "fixture_session", "part": "teardown"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something", "category": "feature"},

            [
                (
                    # FIXTURE-TEARDOWN: SetupI.fixture_session
                    {"cls": "SetupI", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-TEARDOWN: SetupII.fixture_session
                    {"cls": "SetupII", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-TEARDOWN: SetupIII.fixture_session
                    {"cls": "SetupIII", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
                )
            ],

            # FIXTURE-TEARDOWN: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "teardown"},
        )

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere (have to be SUCCESS everywhere)
        assert session.executor_tree.executor_result == ResultState.SUCCESS, \
            "test session does not terminates with success"

        assert session.executor_tree.construct_result.result == ResultState.SUCCESS, \
            "global executor tree construct part does not set ResultState.SUCCESS"
        assert session.executor_tree.body_result.result == ResultState.SUCCESS, \
            "global executor tree body part does not set ResultState.SUCCESS"
        assert session.executor_tree.teardown_result.result == ResultState.SUCCESS, \
            "global executor tree teardown part does not set ResultState.SUCCESS"
        for cur_setup_executor in session.executor_tree.get_setup_executors():
            assert cur_setup_executor.executor_result == ResultState.SUCCESS, \
                "the setup executor does not have result SUCCESS"

            assert cur_setup_executor.construct_result.result == ResultState.SUCCESS
            assert cur_setup_executor.body_result.result == ResultState.SUCCESS
            assert cur_setup_executor.teardown_result.result == ResultState.SUCCESS

            for cur_scenario_executor in cur_setup_executor.get_scenario_executors():
                assert cur_scenario_executor.executor_result == ResultState.SUCCESS, \
                    "the scenario executor does not have result SUCCESS"

                assert cur_scenario_executor.construct_result.result == ResultState.SUCCESS
                assert cur_scenario_executor.body_result.result == ResultState.SUCCESS
                assert cur_scenario_executor.teardown_result.result == ResultState.SUCCESS

                for cur_variation_executor in cur_scenario_executor.get_variation_executors():
                    assert cur_variation_executor.executor_result == ResultState.SUCCESS, \
                        "the variation executor does not have result SUCCESS"

                    assert cur_variation_executor.construct_result.result == ResultState.SUCCESS
                    assert cur_variation_executor.body_result.result == ResultState.SUCCESS
                    assert cur_variation_executor.teardown_result.result == ResultState.SUCCESS

                    for cur_testcase_executor in cur_variation_executor.get_testcase_executors():
                        assert cur_testcase_executor.executor_result == ResultState.SUCCESS, \
                            "the testcase executor does not have result SUCCESS"

                        assert cur_testcase_executor.construct_result.result == ResultState.SUCCESS
                        assert cur_testcase_executor.body_result.result == ResultState.SUCCESS
                        assert cur_testcase_executor.teardown_result.result == ResultState.SUCCESS

    def _generate_expected_data_from_setup_on(
            self, setup_class_name, base_feature_identifier, scenario_feature_identifier,
            between_feature_identifier, setup_feature_identifier, vdevice_multip):
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_setup
            {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "construction"},

            # FIXTURE-CONSTRUCTION: SetupI.fixture_setup
            {"cls": setup_class_name, "meth": "fixture_setup", "part": "construction"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},

            # FIXTURE-CONSTRUCTION: ScenarioA.fixture_setup
            {"cls": "ScenarioA", "meth": "fixture_setup", "part": "construction"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something", "category": "feature"},

            # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},

            # FIXTURE-CONSTRUCTION: SetupI.fixture_scenario
            {"cls": setup_class_name, "meth": "fixture_scenario", "part": "construction"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},

            # FIXTURE-CONSTRUCTION: ScenarioA.fixture_scenario
            {"cls": "ScenarioA", "meth": "fixture_scenario", "part": "construction"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something", "category": "feature"},

            # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},

            # FIXTURE-CONSTRUCTION: SetupI.fixture_variation
            {"cls": setup_class_name, "meth": "fixture_variation", "part": "construction"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
            {"cls": "BaseMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{base_feature_identifier}><BaseMethVarFeature.do_something_as_var>"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{scenario_feature_identifier}><ScenarioMethVarFeature.do_something_as_var>"},
            {"cls": "BetweenMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{between_feature_identifier}><BetweenMethVarFeature.do_something_as_var>"},
            {"cls": "SetupMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{setup_feature_identifier}><SetupMethVarFeature.do_something_as_var> "
                    f"a_int_val={vdevice_multip + 1} a_str_val=hello-from-var-fixt-const"},

            # FIXTURE-CONSTRUCTION: ScenarioA.fixture_variation
            {"cls": "ScenarioA", "meth": "fixture_variation", "part": "construction"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
            {"cls": "BaseMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{base_feature_identifier}><BaseMethVarFeature.do_something_as_var>"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{scenario_feature_identifier}><ScenarioMethVarFeature.do_something_as_var>"},
            {"cls": "BetweenMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{between_feature_identifier}><BetweenMethVarFeature.do_something_as_var>"},
            {"cls": "SetupMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{setup_feature_identifier}><SetupMethVarFeature.do_something_as_var> "
                    f"a_int_val={1000} a_str_val=scenario-var-fixt-const"},

            # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
            {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "construction"},

            # FIXTURE-CONSTRUCTION: SetupI.fixture_testcase
            {"cls": setup_class_name, "meth": "fixture_testcase", "part": "construction"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
            {"cls": "BaseMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{base_feature_identifier}><BaseMethVarFeature.do_something_as_var>"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{scenario_feature_identifier}><ScenarioMethVarFeature.do_something_as_var>"},
            {"cls": "BetweenMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{between_feature_identifier}><BetweenMethVarFeature.do_something_as_var>"},
            {"cls": "SetupMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{setup_feature_identifier}><SetupMethVarFeature.do_something_as_var> "
                    f"a_int_val={vdevice_multip + 2} a_str_val=hello-from-test-fixt-const"},

            # FIXTURE-CONSTRUCTION: ScenarioA.fixture_testcase
            {"cls": "ScenarioA", "meth": "fixture_testcase", "part": "construction"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
            {"cls": "BaseMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{base_feature_identifier}><BaseMethVarFeature.do_something_as_var>"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{scenario_feature_identifier}><ScenarioMethVarFeature.do_something_as_var>"},
            {"cls": "BetweenMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{between_feature_identifier}><BetweenMethVarFeature.do_something_as_var>"},
            {"cls": "SetupMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{setup_feature_identifier}><SetupMethVarFeature.do_something_as_var> "
                    f"a_int_val={2000} a_str_val=scenario-test-fixt-const"},

            # TESTCASE: ScenarioA.test_a_1
            {"cls": "ScenarioA", "meth": "test_a_1"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
            {"cls": "BaseMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{base_feature_identifier}><BaseMethVarFeature.do_something_as_var>"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{scenario_feature_identifier}><ScenarioMethVarFeature.do_something_as_var>"},
            {"cls": "BetweenMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{between_feature_identifier}><BetweenMethVarFeature.do_something_as_var>"},
            {"cls": "SetupMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{setup_feature_identifier}><SetupMethVarFeature.do_something_as_var> "
                    f"a_int_val={100} a_str_val=in-test-a1"},

            # FIXTURE-TEARDOWN: ScenarioA.fixture_testcase
            {"cls": "ScenarioA", "meth": "fixture_testcase", "part": "teardown"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
            {"cls": "BaseMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{base_feature_identifier}><BaseMethVarFeature.do_something_as_var>"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{scenario_feature_identifier}><ScenarioMethVarFeature.do_something_as_var>"},
            {"cls": "BetweenMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{between_feature_identifier}><BetweenMethVarFeature.do_something_as_var>"},
            {"cls": "SetupMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{setup_feature_identifier}><SetupMethVarFeature.do_something_as_var> "
                    f"a_int_val={3000} a_str_val=scenario-test-fixt-teardown"},

            # FIXTURE-TEARDOWN: SetupI.fixture_testcase
            {"cls": setup_class_name, "meth": "fixture_testcase", "part": "teardown"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
            {"cls": "BaseMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{base_feature_identifier}><BaseMethVarFeature.do_something_as_var>"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{scenario_feature_identifier}><ScenarioMethVarFeature.do_something_as_var>"},
            {"cls": "BetweenMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{between_feature_identifier}><BetweenMethVarFeature.do_something_as_var>"},
            {"cls": "SetupMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{setup_feature_identifier}><SetupMethVarFeature.do_something_as_var> "
                    f"a_int_val={vdevice_multip + 3} a_str_val=hello-from-test-fixt-teardown"},

            # FIXTURE-TEARDOWN: balderglob_fixture_testcase
            {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "teardown"},

            # FIXTURE-TEARDOWN: ScenarioA.fixture_variation
            {"cls": "ScenarioA", "meth": "fixture_variation", "part": "teardown"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
            {"cls": "BaseMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{base_feature_identifier}><BaseMethVarFeature.do_something_as_var>"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{scenario_feature_identifier}><ScenarioMethVarFeature.do_something_as_var>"},
            {"cls": "BetweenMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{between_feature_identifier}><BetweenMethVarFeature.do_something_as_var>"},
            {"cls": "SetupMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{setup_feature_identifier}><SetupMethVarFeature.do_something_as_var> "
                    f"a_int_val={4000} a_str_val=scenario-var-fixt-teardown"},

            # FIXTURE-TEARDOWN: SetupI.fixture_variation
            {"cls": setup_class_name, "meth": "fixture_variation", "part": "teardown"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},
            {"cls": "BaseMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{base_feature_identifier}><BaseMethVarFeature.do_something_as_var>"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{scenario_feature_identifier}><ScenarioMethVarFeature.do_something_as_var>"},
            {"cls": "BetweenMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{between_feature_identifier}><BetweenMethVarFeature.do_something_as_var>"},
            {"cls": "SetupMethVarFeature", "meth": "do_something_as_var", "category": "feature",
             "msg": f"MethodVariation<{setup_feature_identifier}><SetupMethVarFeature.do_something_as_var> "
                    f"a_int_val={vdevice_multip + 4} a_str_val=hello-from-var-fixt-teardown"},

            # FIXTURE-TEARDOWN: balderglob_fixture_variation
            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},

            # FIXTURE-TEARDOWN: ScenarioA.fixture_scenario
            {"cls": "ScenarioA", "meth": "fixture_scenario", "part": "teardown"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something", "category": "feature"},

            # FIXTURE-TEARDOWN: SetupI.fixture_scenario
            {"cls": setup_class_name, "meth": "fixture_scenario", "part": "teardown"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},

            # FIXTURE-TEARDOWN: balderglob_fixture_scenario
            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},

            # FIXTURE-TEARDOWN: ScenarioA.fixture_setup
            {"cls": "ScenarioA", "meth": "fixture_setup", "part": "teardown"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "ScenarioMethVarFeature", "meth": "do_something", "category": "feature"},

            # FIXTURE-TEARDOWN: SetupI.fixture_setup
            {"cls": setup_class_name, "meth": "fixture_setup", "part": "teardown"},
            {"cls": "FeatureVDeviceI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupMethVarFeature", "meth": "do_something", "category": "feature"},

            # FIXTURE-TEARDOWN: balderglob_fixture_setup
            {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "teardown"},
        )
