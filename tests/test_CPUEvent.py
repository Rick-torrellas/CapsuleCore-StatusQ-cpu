from datetime import datetime

import pytest

from cc_statusq_cpu.core import (
    CPUEvent,
    CPUStatus,
    DataReceivedEvent,
    MonitoringErrorEvent,
    MonitoringFinishedEvent,
    MonitoringStartedEvent,
)


@pytest.fixture
def sample_cpu_status():
    """Provides a valid CPUStatus instance for event testing."""
    return CPUStatus(
        name="Test CPU",
        architecture="x64",
        physical_cores=2,
        logical_cores=4,
        current_frequency=3000.0,
        min_frequency=800.0,
        max_frequency=4000.0,
        total_usage_percentage=25.0,
        usage_per_core=[20.0, 30.0],
        average_load=[0.1, 0.2, 0.3],
        user_time=100.0,
        system_time=50.0,
        idle_time=500.0,
        current_temperature=55.0,
        timestamp=datetime.now()
    )

def test_base_event_timestamp():
    """Verify that a base CPUEvent generates a default timestamp if not provided."""
    before = datetime.now()
    event = CPUEvent()
    after = datetime.now()
    
    assert isinstance(event.timestamp, datetime)
    assert before <= event.timestamp <= after

def test_monitoring_started_event_initialization():
    """Ensure MonitoringStartedEvent correctly stores the operation mode."""
    mode = "continuous"
    event = MonitoringStartedEvent(mode=mode)
    
    assert event.mode == mode
    assert isinstance(event.timestamp, datetime)

def test_data_received_event_payload(sample_cpu_status):
    """Verify that DataReceivedEvent carries the CPUStatus payload correctly."""
    event = DataReceivedEvent(status=sample_cpu_status)
    
    assert event.status == sample_cpu_status
    assert event.status.name == "Test CPU"

def test_monitoring_error_event_with_exception():
    """Verify MonitoringErrorEvent stores messages and optional exception objects."""
    error_msg = "Connection lost"
    exc = RuntimeError("Hardware failure")
    
    event = MonitoringErrorEvent(message=error_msg, exception=exc)
    
    assert event.message == error_msg
    assert event.exception == exc

def test_monitoring_finished_event():
    """Ensure MonitoringFinishedEvent can be instantiated without arguments."""
    event = MonitoringFinishedEvent()
    assert isinstance(event.timestamp, datetime)

def test_event_immutability():
    """
    Since events are defined as frozen=True, they should be immutable.
    This test ensures that trying to modify an event raises a FrozenInstanceError.
    """
    event = MonitoringStartedEvent(mode="single")
    
    with pytest.raises(AttributeError):
        # Data classes with frozen=True raise AttributeError (or FrozenInstanceError) on set
        event.mode = "new_mode"

def test_event_equality(sample_cpu_status):
    """Verify that two events with the same data and timestamp are considered equal."""
    ts = datetime.now()
    event1 = DataReceivedEvent(timestamp=ts, status=sample_cpu_status)
    event2 = DataReceivedEvent(timestamp=ts, status=sample_cpu_status)
    
    assert event1 == event2