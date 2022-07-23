import balder


class ScenarioMatching(balder.Scenario):
    """This scenario should be collected"""

    class MyDevice(balder.Device):
        pass
    
    def test_do_something(self):
        assert True
