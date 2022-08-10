import balder


class ScenarioAdding(balder.Scenario):

    # NOTE: this scenario does not implement some devices

    def test_always_succeed(self):
        assert True, "should be never false"
