from _balder.testresult import ResultState
from _balder.balder_session import BalderSession
from tests.test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0InnerScenarioFeatureRefWithUnmappedDev(Base0EnvtesterClass):
    """
    This testcase executes the basic example but uses inner-feature-references in the scenario feature. The features
    refer themselves like shown in the following:

    * scenario feature `FeatureII` references scenario feature `FeatureI`
    * setup feature `SetupFeatureIV` references scenario feature `FeatureIII`
    * scenario feature `FeatureVI` references scenario feature `FeatureV`
    * setup feature `SetupFeatureVIII` references scenario feature `FeatureVII`.

    It reduces the basic implementation to only one Scenario and one Setup, while the mapped devices are
    using `FeatureI`/`FeatureII` and `FeatureIII`/`FeatureIV`. In addition to that, the setup defines two unmapped
    devices that are using `SetupFeatureV`/`SetupFeatureVI` and `SetupFeatureVII`/`SetupFeatureVIII`. This test makes
    sure that the inner feature reference also works for these unmapped devices.
    """

    @property
    def expected_data(self):
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_session
            {"cls": "SetupA", "meth": "fixture_session", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
            # FIXTURE-CONSTRUCTION: ScenarioA.fixture_session
            {"cls": "ScenarioA", "meth": "fixture_session", "part": "construction"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
            # here we do not have `called_from_outer_feature`, because it is not declared on scenario scope

            # FIXTURE-CONSTRUCTION: balderglob_fixture_setup
            {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_setup
            {"cls": "SetupA", "meth": "fixture_setup", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
            # FIXTURE-CONSTRUCTION: ScenarioA.fixture_setup
            {"cls": "ScenarioA", "meth": "fixture_setup", "part": "construction"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
            # here we do not have `called_from_outer_feature`, because it is not declared on scenario scope

            # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_scenario
            {"cls": "SetupA", "meth": "fixture_scenario", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
            # FIXTURE-CONSTRUCTION: ScenarioA.fixture_scenario
            {"cls": "ScenarioA", "meth": "fixture_scenario", "part": "construction"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
            # here we do not have `called_from_outer_feature`, because it is not declared on scenario scope

            # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},
            # FIXTURE-CONSTRUCTION: SetupA.fixture_variation
            {"cls": "SetupA", "meth": "fixture_variation", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
            # FIXTURE-CONSTRUCTION: ScenarioA.fixture_variation
            {"cls": "ScenarioA", "meth": "fixture_variation", "part": "construction"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            [
                (
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_testcase
                    {"cls": "SetupA", "meth": "fixture_testcase", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioA.fixture_testcase
                    {"cls": "ScenarioA", "meth": "fixture_testcase", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    # TESTCASE: ScenarioA.test_a_1
                    {"cls": "ScenarioA", "meth": "test_a_1"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    # FIXTURE-TEARDOWN: ScenarioA.fixture_testcase
                    {"cls": "ScenarioA", "meth": "fixture_testcase", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupA.fixture_testcase
                    {"cls": "SetupA", "meth": "fixture_testcase", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "teardown"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_testcase
                    {"cls": "SetupA", "meth": "fixture_testcase", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioA.fixture_testcase
                    {"cls": "ScenarioA", "meth": "fixture_testcase", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    # TESTCASE: ScenarioA.test_a_2
                    {"cls": "ScenarioA", "meth": "test_a_2"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    # FIXTURE-TEARDOWN: ScenarioA.fixture_testcase
                    {"cls": "ScenarioA", "meth": "fixture_testcase", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupA.fixture_testcase
                    {"cls": "SetupA", "meth": "fixture_testcase", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
                    {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase", "part": "teardown"},
                ),
            ],
            # FIXTURE-TEARDOWN: ScenarioA.fixture_variation
            {"cls": "ScenarioA", "meth": "fixture_variation", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            # FIXTURE-TEARDOWN: SetupA.fixture_variation
            {"cls": "SetupA", "meth": "fixture_variation", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_variation
            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},

            # FIXTURE-TEARDOWN: ScenarioA.fixture_scenario
            {"cls": "ScenarioA", "meth": "fixture_scenario", "part": "teardown"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
            # here we do not have `called_from_outer_feature`, because it is not declared on scenario scope
            # FIXTURE-TEARDOWN: SetupA.fixture_scenario
            {"cls": "SetupA", "meth": "fixture_scenario", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_scenario
            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},

            # FIXTURE-TEARDOWN: ScenarioA.fixture_setup
            {"cls": "ScenarioA", "meth": "fixture_setup", "part": "teardown"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
            # here we do not have `called_from_outer_feature`, because it is not declared on scenario scope
            # FIXTURE-TEARDOWN: SetupA.fixture_setup
            {"cls": "SetupA", "meth": "fixture_setup", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_setup
            {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "teardown"},

            # FIXTURE-TEARDOWN: ScenarioA.fixture_session
            {"cls": "ScenarioA", "meth": "fixture_session", "part": "teardown"},
            {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
            # here we do not have `called_from_outer_feature`, because it is not declared on scenario scope
            # FIXTURE-TEARDOWN: SetupA.fixture_session
            {"cls": "SetupA", "meth": "fixture_session", "part": "teardown"},
            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureI", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureIII", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVI", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureV", "meth": "called_from_outer_feature", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVIII", "meth": "do_something", "category": "feature"},
            {"cls": "SetupFeatureVII", "meth": "called_from_outer_feature", "category": "feature"},
            # FIXTURE-TEARDOWN: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "teardown"},
        )

    @staticmethod
    def validate_finished_session(session: BalderSession):
        # check result states everywhere (have to be SUCCESS everywhere
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
