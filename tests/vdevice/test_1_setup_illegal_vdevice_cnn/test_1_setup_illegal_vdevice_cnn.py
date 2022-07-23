from multiprocessing import Process

from balder.exceptions import IllegalVDeviceMappingError
from _balder.balder_session import BalderSession


def test_1_setup_illegal_vdevice_cnn(balder_working_dir):
    """
    This testcase executes the basic CALCULATOR example. It maps a device to a vDevice, which requires a connection that
    does not exist in the setup class itself. The VDevice<->Device mapping is also done in the setup.

    The test expects the throwing of the ``IllegalVDeviceMappingError`` on COLLECTOR level.
    """
    proc = Process(target=processed, args=(balder_working_dir, ))
    proc.start()
    proc.join()
    assert proc.exitcode == 0, "the process terminates with an error"


def processed(env_dir):
    print("\n", flush=True)
    session = BalderSession(cmd_args=[], working_dir=env_dir)
    try:
        session.run()
        print("\n")
        assert False, "test session terminates without an error"
    except IllegalVDeviceMappingError as exc:
        assert exc.args[0] == "the @for_vdevice connection for vDevice `CalculatorDevice` of feature " \
                              "`PyAddProvideANumber` (used in `SetupPythonAdd.NumberProvider1`) uses a connection " \
                              "that does not fit with the connection defined in setup class `SetupPythonAdd` to " \
                              "related device `Calculator`"

    assert session.executor_tree is None, "test session does not terminates before collector work was done"
