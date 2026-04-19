from datetime import datetime

from cc_statusq_cpu.core import CPUStatus

"""
Tests for the CPUStatus Data Transfer Object (DTO).
These tests ensure that the data structure correctly holds 
system metrics and maintains data integrity.
"""

def test_cpu_status_instantiation(mock_cpu_status):
    """
    Test that CPUStatus can be correctly instantiated with all required fields.
    It uses the 'mock_cpu_status' fixture defined in conftest.py.
    """
    status = mock_cpu_status
    
    # Verify core identity attributes
    assert status.name == "TestProcessor"
    assert status.architecture == "x86_64"
    assert status.physical_cores == 4
    assert status.logical_cores == 8
    
    # Verify frequency metrics
    assert isinstance(status.current_frequency, float)
    assert status.current_frequency == 2500.0
    
    # Verify usage metrics
    assert status.total_usage_percentage == 15.5
    assert len(status.usage_per_core) == 4
    assert status.usage_per_core[0] == 10.0
    
    # Verify time and date
    assert isinstance(status.timestamp, datetime)

def test_cpu_status_optional_fields():
    """
    Verify that CPUStatus handles Optional fields correctly, 
    such as temperature or average load which might not be available on all OS.
    """
    status = CPUStatus(
        name="MinimalCPU",
        architecture="ARM",
        physical_cores=None, # Optional
        logical_cores=None,  # Optional
        current_frequency=1000.0,
        min_frequency=400.0,
        max_frequency=2000.0,
        total_usage_percentage=5.0,
        usage_per_core=[5.0],
        average_load=None, # Optional
        user_time=100.0,
        system_time=50.0,
        idle_time=1000.0,
        current_temperature=None, # Optional
        timestamp=datetime.now()
    )
    
    assert status.physical_cores is None
    assert status.current_temperature is None
    assert status.average_load is None

def test_cpu_status_is_data_class():
    """
    Ensure CPUStatus behaves like a standard dataclass (supports equality checks).
    Two instances with the same values should be considered equal.
    """
    now = datetime.now()
    
    params = {
        "name": "Generic CPU",
        "architecture": "x86",
        "physical_cores": 2,
        "logical_cores": 2,
        "current_frequency": 3000.0,
        "min_frequency": 1000.0,
        "max_frequency": 4000.0,
        "total_usage_percentage": 0.0,
        "usage_per_core": [0.0, 0.0],
        "average_load": [0.1, 0.1, 0.1],
        "user_time": 0.0,
        "system_time": 0.0,
        "idle_time": 0.0,
        "current_temperature": 35.0,
        "timestamp": now
    }
    
    status1 = CPUStatus(**params)
    status2 = CPUStatus(**params)
    
    assert status1 == status2
    assert status1 is not status2 # They are different objects in memory

def test_cpu_status_type_integrity(mock_cpu_status):
    """
    Validate that specific fields maintain their expected types 
    to prevent logic errors in consumers (like UI or Loggers).
    """
    status = mock_cpu_status
    
    assert isinstance(status.usage_per_core, list)
    assert all(isinstance(usage, float) for usage in status.usage_per_core)
    assert isinstance(status.total_usage_percentage, float)