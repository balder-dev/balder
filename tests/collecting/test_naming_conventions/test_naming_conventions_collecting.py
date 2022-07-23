from multiprocessing import Process
from _balder.balder_session import BalderSession


def test_collect_only_from_namespace(balder_working_dir):
    """
    This test checks if balder only collects the relevant classes from the correct naming convention files.
    """
    proc = Process(target=processed, args=(balder_working_dir, ))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):
    print("\n")
    session = BalderSession(cmd_args=["--collect-only"], working_dir=env_dir)
    session.run()
    print("\n")
    from .env.scenarios.scenario_file import ScenarioMatching
    from .env.scenarios.no_scenario_file import ScenarioNotMatching

    all_collected_scenario_names = [cur_scenario.__name__ for cur_scenario in session.all_collected_scenarios]
    all_collected_setup_names = [cur_setup.__name__ for cur_setup in session.all_collected_setups]

    assert ScenarioMatching.__name__ in all_collected_scenario_names, \
        f"can not find the scenario `{ScenarioMatching.__name__}` in collected data"
    assert ScenarioNotMatching.__name__ not in all_collected_scenario_names, \
        f"find the scenario `{ScenarioNotMatching.__name__}` in collected data, where the scenario file name doesn't " \
        f"match the requirements"

    from .env.setups.setup_file import SetupMatching
    from .env.setups.no_setup_file import SetupNoMatching

    assert SetupMatching.__name__ in all_collected_setup_names, \
        f"can not find the setup `{SetupMatching.__name__}` in collected data"
    assert SetupNoMatching.__name__ not in all_collected_setup_names, \
        f"find the setup `{SetupNoMatching.__name__}` in collected data, where the setup file name doesn't match the " \
        f"requirements"
