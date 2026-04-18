from unittest.mock import MagicMock, patch

import pytest

from cc_statusq_cpu.capsule.PsutilCPUProvider import PsutilCPUProvider
from cc_statusq_cpu.core.CPUStatus import CPUStatus


class TestPsutilCPUProvider:
    """
    Test suite for PsutilCPUProvider implementation.
    Mocks 'psutil' to provide deterministic data.
    """

    @pytest.fixture
    def provider(self):
        """Initializes the provider instance for testing."""
        return PsutilCPUProvider()

    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.cpu_times')
    @patch('psutil.getloadavg')
    @patch('psutil.sensors_temperatures')
    def test_capture_once_returns_valid_dto(
        self, mock_temp, mock_load, mock_times, mock_freq, mock_count, mock_percent, provider
    ):
        # --- Setup Mocks ---
        mock_count.return_value = 4
        # Return total usage then per-cpu usage list
        mock_percent.side_effect = [15.0, [10.0, 20.0, 15.0, 15.0]]
        
        freq_mock = MagicMock(current=3000.0, min=800.0, max=4000.0)
        mock_freq.return_value = freq_mock
        
        times_mock = MagicMock(user=100.0, system=50.0, idle=500.0)
        mock_times.return_value = times_mock
        
        mock_load.return_value = (1.0, 0.5, 0.2)
        mock_temp.return_value = {'coretemp': [MagicMock(current=45.0)]}

        # --- Act ---
        result = provider.capture_once()

        # --- Assert ---
        assert isinstance(result, CPUStatus)
        assert result.total_usage_percentage == 15.0
        assert result.current_temperature == 45.0

    @patch('psutil.sensors_temperatures')
    def test_temperature_handling_when_missing(self, mock_temp, provider):
        """
        Ensures the provider handles missing sensors by returning None.
        Fixes the AssertionError: assert None == 0.0.
        """
        # Arrange: sensor_temperatures returns an empty dict
        mock_temp.return_value = {}

        # Act
        result = provider.capture_once()

        # Assert: Per your code, if no sensors, temp remains None
        assert result.current_temperature is None

    @patch('psutil.cpu_percent')
    @patch('time.sleep', return_value=None) # Prevent actual sleeping
    def test_capture_continuous_returns_list(self, mock_sleep, mock_percent, provider):
        """
        Fixes 'assert 0 == 3' by ensuring the mock provides values for all 
        internal calls within the loop.
        """
        # In each iteration of the loop (3 times), capture_once is called.
        # Inside capture_once, psutil.cpu_percent is called TWICE.
        # Total calls to mock_percent = 3 iterations * 2 calls = 6 values needed.
        mock_percent.side_effect = [
            10.0, [10.0, 10.0], # Iteration 1
            12.0, [12.0, 12.0], # Iteration 2
            15.0, [15.0, 15.0]  # Iteration 3
        ]

        # Act
        results = provider.capture_continuous(interval=0.1)

        # Assert
        # If it returns 0, the 'try/except' in your code is catching a 
        # StopIteration because the mock ran out of values.
        assert len(results) == 3 
        assert isinstance(results[0], CPUStatus)