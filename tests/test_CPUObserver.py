from cc_statusq_cpu.core.CPUObserver import CPUObserver
from cc_statusq_cpu.core.CPUStatus import CPUStatus


class SpyObserver(CPUObserver):
    """A concrete implementation to verify method execution."""
    def __init__(self):
        self.start_called = False
        self.data_received = None
        self.error_message = None
        self.finished_called = False

    def on_capture_start(self, mode: str):
        self.start_called = True
        self.mode = mode

    def on_data_received(self, status: CPUStatus):
        self.data_received = status

    def on_error(self, message: str, error: Exception = None):
        self.error_message = message

    def on_finished(self):
        self.finished_called = True



def test_observer_on_capture_start():
    """Verify on_capture_start receives the correct mode string."""
    spy = SpyObserver()
    test_mode = "continuous"
    
    spy.on_capture_start(test_mode)
    
    assert spy.start_called is True
    assert spy.mode == test_mode

def test_observer_on_data_received(mock_cpu_status):
    """Verify on_data_received correctly handles a CPUStatus object."""
    # mock_cpu_status comes from your conftest.py
    spy = SpyObserver()
    
    spy.on_data_received(mock_cpu_status)
    
    assert spy.data_received == mock_cpu_status
    assert spy.data_received.name == "Test-Processor-v1"

def test_observer_on_error():
    """Verify on_error captures the error message and optional Exception."""
    spy = SpyObserver()
    error_msg = "Critical failure"
    exception = ValueError("Access denied")
    
    spy.on_error(error_msg, exception)
    
    assert spy.error_message == error_msg

def test_observer_on_finished():
    """Verify on_finished trigger."""
    spy = SpyObserver()
    
    spy.on_finished()
    
    assert spy.finished_called is True

def test_observer_interface_defaults():
    """
    Ensures that a class inheriting from CPUObserver 
    doesn't crash if it doesn't override optional methods.
    """
    class MinimalObserver(CPUObserver):
        pass
        
    minimal = MinimalObserver()
    # These should not raise NotImplementedError because base methods use 'pass'
    minimal.on_capture_start("single")
    minimal.on_finished()