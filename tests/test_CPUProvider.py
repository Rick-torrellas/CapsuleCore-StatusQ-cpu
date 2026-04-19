from unittest.mock import MagicMock, patch

import pytest

from cc_statusq_cpu.capsule import PsutilCPUProvider
from cc_statusq_cpu.core import CPUStatus


class TestPsutilCPUProvider:
    """
    Unit tests for the PsutilCPUProvider implementation.
    We mock the 'psutil' library to ensure tests are environment-independent.
    """

    @pytest.fixture
    def provider(self):
        """Fixture to initialize the provider before each test."""
        return PsutilCPUProvider()

    @patch("psutil.cpu_freq")
    @patch("psutil.cpu_times")
    @patch("psutil.cpu_percent")
    @patch("psutil.getloadavg")
    def test_capture_once_returns_valid_cpu_status(
        self, mock_load, mock_percent, mock_times, mock_freq, provider
    ):
        """
        GIVEN a functional PsutilCPUProvider
        WHEN capture_once() is called
        THEN it should return a CPUStatus object with correct mapped values.
        """
        # Mocking cpu_freq
        mock_freq.return_value = MagicMock(current=2400.0, min=800.0, max=4000.0)
        
        # Mocking cpu_times
        mock_times.return_value = MagicMock(user=100.0, system=50.0, idle=500.0)
        
        # Mocking cpu_percent (total and per-core)
        mock_percent.side_effect = [25.0, [20.0, 30.0]] 
        
        # Mocking load average
        mock_load.return_value = (1.5, 1.2, 1.0)

        # Execute
        result = provider.capture_once()

        # Assertions
        assert isinstance(result, CPUStatus)
        assert result.current_frequency == 2400.0
        assert result.total_usage_percentage == 25.0
        assert len(result.usage_per_core) == 2
        assert result.average_load == [1.5, 1.2, 1.0]
        assert result.idle_time == 500.0

    @patch("psutil.sensors_temperatures")
    def test_capture_once_handles_missing_temperature(self, mock_temps, provider):
        """
        GIVEN a system where temperature sensors are not accessible
        WHEN capture_once() is called
        THEN the current_temperature field should be None (no crash).
        """
        # Simulate exception or empty dict often returned by psutil on some OS
        mock_temps.side_effect = Exception("Access Denied")

        result = provider.capture_once()

        assert result.current_temperature is None

    def test_capture_continuous_returns_list_of_status(self, provider):
        """
        GIVEN a PsutilCPUProvider
        WHEN capture_continuous is called with an interval
        THEN it should return a list containing multiple CPUStatus measurements.
        """
        # We use a small interval for the test to be fast
        with patch.object(PsutilCPUProvider, 'capture_once') as mock_capture:
            mock_capture.return_value = MagicMock(spec=CPUStatus)
            
            interval = 0.01
            results = provider.capture_continuous(interval=interval)

            # Based on the implementation, it collects 3 samples
            assert isinstance(results, list)
            assert len(results) == 3
            assert mock_capture.call_count == 3

    @patch("psutil.cpu_freq")
    def test_capture_once_handles_null_frequency(self, mock_freq, provider):
        """
        GIVEN a virtualized system where frequency might return None
        WHEN capture_once() is called
        THEN it should default frequencies to 0.0 instead of crashing.
        """
        mock_freq.return_value = None

        result = provider.capture_once()

        assert result.current_frequency == 0.0
        assert result.min_frequency == 0.0
        assert result.max_frequency == 0.0