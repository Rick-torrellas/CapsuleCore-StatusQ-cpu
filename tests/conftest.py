from datetime import datetime
from unittest.mock import MagicMock

import pytest

# Importing core components from the statusq-cpu project
from cc.statusq.cpu.core import CPUEventBus, CPUProvider, CPUStatus


@pytest.fixture
def mock_cpu_status():
    """
    Provides a dummy CPUStatus object for testing.
    This avoids dependencies on real system metrics during assertions.
    """
    return CPUStatus(
        name="TestProcessor",
        architecture="x86_64",
        physical_cores=4,
        logical_cores=8,
        current_frequency=2500.0,
        min_frequency=800.0,
        max_frequency=4500.0,
        total_usage_percentage=15.5,
        usage_per_core=[10.0, 20.0, 15.0, 17.0],
        average_load=[0.5, 0.6, 0.7],
        user_time=1000.0,
        system_time=500.0,
        idle_time=5000.0,
        current_temperature=45.0,
        timestamp=datetime.now()
    )

@pytest.fixture
def event_bus():
    """
    Provides a clean instance of CPUEventBus for each test.
    Ensures that subscribers from one test don't interfere with another.
    """
    return CPUEventBus()

@pytest.fixture
def mock_provider(mock_cpu_status):
    """
    Creates a mock implementation of the CPUProvider Protocol.
    It returns the mock_cpu_status instead of querying the actual OS.
    """
    provider = MagicMock(spec=CPUProvider)
    provider.capture_once.return_value = mock_cpu_status
    provider.capture_continuous.return_value = [mock_cpu_status, mock_cpu_status]
    return provider

@pytest.fixture
def tracker_logs():
    """
    A simple list fixture to store events captured during a test run.
    Useful for verifying that the EventBus actually published the expected events.
    """
    return []