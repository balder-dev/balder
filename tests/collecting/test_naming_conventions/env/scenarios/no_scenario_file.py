import balder


class ScenarioNotMatching(balder.Scenario):
    """This scenario should not be collected"""

    class MyDevice(balder.Device):
        pass
    
    def test_do_something(self):
        assert True
