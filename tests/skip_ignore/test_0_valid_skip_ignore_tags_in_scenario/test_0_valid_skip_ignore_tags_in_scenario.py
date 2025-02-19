from _balder.testresult import ResultState
from _balder.balder_session import BalderSession
from ...test_utilities.base_0_envtester_class import Base0EnvtesterClass


class Test0ValidSkipIgnoreTagsInScenario(Base0EnvtesterClass):
    """
    This testcase is a modified version of the envtester environment. It defines parent scenario classes that defines
    own IGNORE/SKIP marker. The test ensures that balder recognize them correctly and only resolves variations with
    scenarios that are valid to run.
    """

    @property
    def expected_data(self):
        return (
            # FIXTURE-CONSTRUCTION: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "construction"},
            [
                (
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_session
                    {"cls": "SetupA", "meth": "fixture_session", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: SetupB.fixture_session
                    {"cls": "SetupB", "meth": "fixture_session", "part": "construction"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                )
            ],
            [
                (
                    # FIXTURE-CONSTRUCTION: ScenarioASub2.fixture_session
                    {"cls": "ScenarioAParent", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: ScenarioBSub1.fixture_session
                    {"cls": "ScenarioBParent", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-CONSTRUCTION: ScenarioBSub2.fixture_session
                    {"cls": "ScenarioBParent", "meth": "fixture_session", "part": "construction"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                )
            ],
            [
                (
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_setup
                    {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_setup
                    {"cls": "SetupA", "meth": "fixture_setup", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioASub2.fixture_setup
                    {"cls": "ScenarioAParent", "meth": "fixture_setup", "part": "construction"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
                    {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_scenario
                    {"cls": "SetupA", "meth": "fixture_scenario", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioASub2.fixture_scenario
                    {"cls": "ScenarioAParent", "meth": "fixture_scenario", "part": "construction"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
                    {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupA.fixture_variation
                    {"cls": "SetupA", "meth": "fixture_variation", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-CONSTRUCTION: ScenarioASub2.fixture_variation
                    {"cls": "ScenarioAParent", "meth": "fixture_variation", "part": "construction"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    [
                        (
                            # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                            {"file": "balderglob.py", "meth": "balderglob_fixture_testcase",
                             "part": "construction"},
                            # FIXTURE-CONSTRUCTION: SetupA.fixture_testcase
                            {"cls": "SetupA", "meth": "fixture_testcase", "part": "construction"},
                            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                            # FIXTURE-CONSTRUCTION: ScenarioASub2.fixture_testcase
                            {"cls": "ScenarioAParent", "meth": "fixture_testcase", "part": "construction"},
                            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                            # TESTCASE: ScenarioASub2.test_a_3
                            {"cls": "ScenarioAParent", "meth": "test_a_3"},
                            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: ScenarioASub2.fixture_testcase
                            {"cls": "ScenarioAParent", "meth": "fixture_testcase", "part": "teardown"},
                            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: SetupA.fixture_testcase
                            {"cls": "SetupA", "meth": "fixture_testcase", "part": "teardown"},
                            {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                            {"file": "balderglob.py", "meth": "balderglob_fixture_testcase",
                             "part": "teardown"},
                        ),
                    ],
                    # FIXTURE-TEARDOWN: ScenarioASub2.fixture_variation
                    {"cls": "ScenarioAParent", "meth": "fixture_variation", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupA.fixture_variation
                    {"cls": "SetupA", "meth": "fixture_variation", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_variation
                    {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},
                    # FIXTURE-TEARDOWN: ScenarioASub2.fixture_scenario
                    {"cls": "ScenarioAParent", "meth": "fixture_scenario", "part": "teardown"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupA.fixture_scenario
                    {"cls": "SetupA", "meth": "fixture_scenario", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_scenario
                    {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},
                    # FIXTURE-TEARDOWN: ScenarioASub2.fixture_setup
                    {"cls": "ScenarioAParent", "meth": "fixture_setup", "part": "teardown"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: SetupA.fixture_setup
                    {"cls": "SetupA", "meth": "fixture_setup", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_setup
                    {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "teardown"},
                ),
                #
                # ------------------------------------------- SETUP CHANGE ---------------------------------------------
                #
                (
                    # FIXTURE-CONSTRUCTION: balderglob_fixture_setup
                    {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "construction"},
                    # FIXTURE-CONSTRUCTION: SetupB.fixture_setup
                    {"cls": "SetupB", "meth": "fixture_setup", "part": "construction"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    [
                        (
                            # FIXTURE-CONSTRUCTION: ScenarioBSub1.fixture_setup
                            {"cls": "ScenarioBParent", "meth": "fixture_setup", "part": "construction"},
                            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                        ),
                        (
                            # FIXTURE-CONSTRUCTION: ScenarioBSub2.fixture_setup
                            {"cls": "ScenarioBParent", "meth": "fixture_setup", "part": "construction"},
                            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                        )
                    ],
                    [
                        (
                            # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
                            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
                            # FIXTURE-CONSTRUCTION: SetupB.fixture_scenario
                            {"cls": "SetupB", "meth": "fixture_scenario", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-CONSTRUCTION: ScenarioBSub1.fixture_scenario
                            {"cls": "ScenarioBParent", "meth": "fixture_scenario", "part": "construction"},
                            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
                            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},
                            # FIXTURE-CONSTRUCTION: SetupB.fixture_variation
                            {"cls": "SetupB", "meth": "fixture_variation", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-CONSTRUCTION: ScenarioBSub1.fixture_variation
                            {"cls": "ScenarioBParent", "meth": "fixture_variation", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            [
                                (
                                    # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase",
                                     "part": "construction"},
                                    # FIXTURE-CONSTRUCTION: SetupB.fixture_testcase
                                    {"cls": "SetupB", "meth": "fixture_testcase", "part": "construction"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-CONSTRUCTION: ScenarioBSub1.fixture_testcase
                                    {"cls": "ScenarioBParent", "meth": "fixture_testcase", "part": "construction"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # TESTCASE: ScenarioBSub1.test_b_1
                                    {"cls": "ScenarioBParent", "meth": "test_b_1"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-TEARDOWN: ScenarioBSub1.fixture_testcase
                                    {"cls": "ScenarioBParent", "meth": "fixture_testcase", "part": "teardown"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-TEARDOWN: SetupB.fixture_testcase
                                    {"cls": "SetupB", "meth": "fixture_testcase", "part": "teardown"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase",
                                     "part": "teardown"},
                                ),
                                (
                                    # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase",
                                     "part": "construction"},
                                    # FIXTURE-CONSTRUCTION: SetupB.fixture_testcase
                                    {"cls": "SetupB", "meth": "fixture_testcase", "part": "construction"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-CONSTRUCTION: ScenarioBSub1.fixture_testcase
                                    {"cls": "ScenarioBParent", "meth": "fixture_testcase", "part": "construction"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # TESTCASE: ScenarioBSub1.test_b_2
                                    {"cls": "ScenarioBParent", "meth": "test_b_2"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-TEARDOWN: ScenarioBSub1.fixture_testcase
                                    {"cls": "ScenarioBParent", "meth": "fixture_testcase", "part": "teardown"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-TEARDOWN: SetupB.fixture_testcase
                                    {"cls": "SetupB", "meth": "fixture_testcase", "part": "teardown"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase",
                                     "part": "teardown"},
                                ),
                            ],
                            # FIXTURE-TEARDOWN: ScenarioBSub1.fixture_variation
                            {"cls": "ScenarioBParent", "meth": "fixture_variation", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: SetupB.fixture_variation
                            {"cls": "SetupB", "meth": "fixture_variation", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: balderglob_fixture_variation
                            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},
                            # FIXTURE-TEARDOWN: ScenarioBSub1.fixture_scenario
                            {"cls": "ScenarioBParent", "meth": "fixture_scenario", "part": "teardown"},
                            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: SetupB.fixture_scenario
                            {"cls": "SetupB", "meth": "fixture_scenario", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: balderglob_fixture_scenario
                            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},
                        ),
                        (
                            # FIXTURE-CONSTRUCTION: balderglob_fixture_scenario
                            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "construction"},
                            # FIXTURE-CONSTRUCTION: SetupB.fixture_scenario
                            {"cls": "SetupB", "meth": "fixture_scenario", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-CONSTRUCTION: ScenarioBSub2.fixture_scenario
                            {"cls": "ScenarioBParent", "meth": "fixture_scenario", "part": "construction"},
                            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-CONSTRUCTION: balderglob_fixture_variation
                            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "construction"},
                            # FIXTURE-CONSTRUCTION: SetupB.fixture_variation
                            {"cls": "SetupB", "meth": "fixture_variation", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-CONSTRUCTION: ScenarioBSub2.fixture_variation
                            {"cls": "ScenarioBParent", "meth": "fixture_variation", "part": "construction"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            [
                                (
                                    # FIXTURE-CONSTRUCTION: balderglob_fixture_testcase
                                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase",
                                     "part": "construction"},
                                    # FIXTURE-CONSTRUCTION: SetupB.fixture_testcase
                                    {"cls": "SetupB", "meth": "fixture_testcase", "part": "construction"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-CONSTRUCTION: ScenarioBSub2.fixture_testcase
                                    {"cls": "ScenarioBParent", "meth": "fixture_testcase", "part": "construction"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # TESTCASE: ScenarioBSub2.test_b_3
                                    {"cls": "ScenarioBSub2", "meth": "test_b_3"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-TEARDOWN: ScenarioBSub2.fixture_testcase
                                    {"cls": "ScenarioBParent", "meth": "fixture_testcase", "part": "teardown"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-TEARDOWN: SetupB.fixture_testcase
                                    {"cls": "SetupB", "meth": "fixture_testcase", "part": "teardown"},
                                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                                    # FIXTURE-TEARDOWN: balderglob_fixture_testcase
                                    {"file": "balderglob.py", "meth": "balderglob_fixture_testcase",
                                     "part": "teardown"},
                                ),
                            ],
                            # FIXTURE-TEARDOWN: ScenarioBSub2.fixture_variation
                            {"cls": "ScenarioBParent", "meth": "fixture_variation", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: SetupB.fixture_variation
                            {"cls": "SetupB", "meth": "fixture_variation", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: balderglob_fixture_variation
                            {"file": "balderglob.py", "meth": "balderglob_fixture_variation", "part": "teardown"},
                            # FIXTURE-TEARDOWN: ScenarioBSub2.fixture_scenario
                            {"cls": "ScenarioBParent", "meth": "fixture_scenario", "part": "teardown"},
                            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: SetupB.fixture_scenario
                            {"cls": "SetupB", "meth": "fixture_scenario", "part": "teardown"},
                            {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                            # FIXTURE-TEARDOWN: balderglob_fixture_scenario
                            {"file": "balderglob.py", "meth": "balderglob_fixture_scenario", "part": "teardown"},
                        )
                    ],
                    [
                        (
                            # FIXTURE-TEARDOWN: ScenarioBSub1.fixture_setup
                            {"cls": "ScenarioBParent", "meth": "fixture_setup", "part": "teardown"},
                            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                        ),
                        (
                            # FIXTURE-TEARDOWN: ScenarioBSub2.fixture_setup
                            {"cls": "ScenarioBParent", "meth": "fixture_setup", "part": "teardown"},
                            {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                            {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                        )
                    ],
                    # FIXTURE-TEARDOWN: SetupB.fixture_setup
                    {"cls": "SetupB", "meth": "fixture_setup", "part": "teardown"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                    # FIXTURE-TEARDOWN: balderglob_fixture_setup
                    {"file": "balderglob.py", "meth": "balderglob_fixture_setup", "part": "teardown"},
                ),
            ],
            [
                (
                    # FIXTURE-TEARDOWN: ScenarioASub2.fixture_session
                    {"cls": "ScenarioAParent", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "FeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureII", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-TEARDOWN: ScenarioBSub1.fixture_session
                    {"cls": "ScenarioBParent", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-TEARDOWN: ScenarioBSub2.fixture_session
                    {"cls": "ScenarioBParent", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "FeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "FeatureIV", "meth": "do_something", "category": "feature"},
                )
            ],
            [
                (
                    # FIXTURE-TEARDOWN: SetupA.fixture_session
                    {"cls": "SetupA", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "SetupFeatureI", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureII", "meth": "do_something", "category": "feature"},
                ),
                (
                    # FIXTURE-TEARDOWN: SetupB.fixture_session
                    {"cls": "SetupB", "meth": "fixture_session", "part": "teardown"},
                    {"cls": "SetupFeatureIII", "meth": "do_something", "category": "feature"},
                    {"cls": "SetupFeatureIV", "meth": "do_something", "category": "feature"},
                )
            ],
            # FIXTURE-TEARDOWN: balderglob_fixture_session
            {"file": "balderglob.py", "meth": "balderglob_fixture_session", "part": "teardown"},
        )

    @staticmethod
    def validate_finished_session(session: BalderSession):

        expected_state = {
            'ScenarioASub1': {
                'test_a_1': ResultState.NOT_RUN,
                'test_a_2': ResultState.SKIP,
                'test_a_3': ResultState.SKIP,
            },
            'ScenarioASub2': {
                'test_a_1': ResultState.NOT_RUN,
                'test_a_2': ResultState.NOT_RUN,
                'test_a_3': ResultState.SUCCESS,
            },
            'ScenarioBSub1': {
                'test_b_1': ResultState.SUCCESS,
                'test_b_2': ResultState.SUCCESS,
                'test_b_3': ResultState.SKIP,
            },
            'ScenarioBSub2': {
                'test_b_1': ResultState.NOT_RUN,
                'test_b_2': ResultState.SKIP,
                'test_b_3': ResultState.SUCCESS,
            }
        }

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
                expected_for_tests = expected_state[cur_scenario_executor.base_scenario_class.__class__.__name__]
                expected_branch_result = ResultState.NOT_RUN
                if ResultState.SUCCESS in expected_for_tests.values():
                    expected_branch_result = ResultState.SUCCESS
                elif ResultState.SKIP in expected_for_tests.values():
                    # has no success but has at least one SKIP
                    expected_branch_result = ResultState.SKIP

                assert cur_scenario_executor.executor_result == expected_branch_result, \
                    f"the scenario executor does not have result {expected_branch_result}"

                assert cur_scenario_executor.construct_result.result == \
                       (ResultState.SUCCESS if expected_branch_result == ResultState.SUCCESS
                        else ResultState.NOT_RUN)
                assert cur_scenario_executor.body_result.result == expected_branch_result
                assert cur_scenario_executor.teardown_result.result == \
                       (ResultState.SUCCESS if expected_branch_result == ResultState.SUCCESS
                        else ResultState.NOT_RUN)

                # expect same branch result for variation-executor, because we only have one per scenario
                for cur_variation_executor in cur_scenario_executor.get_variation_executors():
                    assert cur_variation_executor.executor_result == expected_branch_result, \
                        f"the variation executor does not have result {expected_branch_result}"

                    assert cur_variation_executor.construct_result.result == \
                       (ResultState.SUCCESS if expected_branch_result == ResultState.SUCCESS
                        else ResultState.NOT_RUN)
                    assert cur_variation_executor.body_result.result == expected_branch_result
                    assert cur_variation_executor.teardown_result.result == \
                       (ResultState.SUCCESS if expected_branch_result == ResultState.SUCCESS
                        else ResultState.NOT_RUN)

                    for cur_testcase_executor in cur_variation_executor.get_testcase_executors():
                        expected_test_result = expected_for_tests[cur_testcase_executor.base_testcase_callable.__name__]
                        assert cur_testcase_executor.executor_result == expected_test_result, \
                            f"the testcase executor does not have result {expected_test_result}"

                        assert cur_testcase_executor.construct_result.result == \
                               (ResultState.SUCCESS if expected_test_result == ResultState.SUCCESS
                                else ResultState.NOT_RUN)
                        assert cur_testcase_executor.body_result.result == expected_test_result
                        assert cur_testcase_executor.teardown_result.result == \
                               (ResultState.SUCCESS if expected_test_result == ResultState.SUCCESS
                                else ResultState.NOT_RUN)
