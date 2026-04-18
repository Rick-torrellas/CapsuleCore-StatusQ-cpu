from datetime import datetime
from unittest.mock import MagicMock

import pytest

from cc_statusq_cpu.core.CPUObserver import CPUObserver
from cc_statusq_cpu.core.CPUProvider import CPUProvider

# Importing the core components to define types and mocks
from cc_statusq_cpu.core.CPUStatus import CPUStatus
from cc_statusq_cpu.core.StatusqCPU import StatusqCPU


@pytest.fixture
def mock_cpu_status():
    """
    Provides a pre-populated CPUStatus Data Transfer Object (DTO).
    Used to verify that data flows correctly through the observers.
    """
    return CPUStatus(
        name="Test-Processor-v1",
        architecture="x86_64",
        physical_cores=4,
        logical_cores=8,
        current_frequency=3200.0,
        min_frequency=800.0,
        max_frequency=4500.0,
        total_usage_percentage=25.5,
        usage_per_core=[20.0, 30.0, 25.0, 27.0],
        average_load=[1.5, 1.2, 0.8],
        user_time=1200.5,
        system_time=400.2,
        idle_time=8000.0,
        current_temperature=55.0,
        timestamp=datetime(2026, 4, 18, 12, 0, 0)
    )

@pytest.fixture
def mock_provider(mock_cpu_status):
    """
    Creates a Mock object that adheres to the CPUProvider Protocol.
    Configured to return the mock_cpu_status when called.
    """
    # We use spec=CPUProvider to ensure the mock only has the methods defined in the Protocol
    provider = MagicMock(spec=CPUProvider)
    
    # Configure behavior for single capture
    provider.capture_once.return_value = mock_cpu_status
    
    # Configure behavior for continuous capture (returns a list of snapshots)
    provider.capture_continuous.return_value = [mock_cpu_status, mock_cpu_status]
    
    return provider

@pytest.fixture
def mock_observer():
    """
    Creates a Mock object based on the CPUObserver interface.
    Used to assert that notification methods (on_data_received, etc.) are called.
    """
    return MagicMock(spec=CPUObserver)

@pytest.fixture
def statusq_instance(mock_provider):
    """
    Provides an instance of the main StatusqCPU controller 
    injected with the mocked provider for isolated testing.
    """
    return StatusqCPU(provider=mock_provider)