import os
from datetime import datetime
from unittest.mock import patch

import pytest

# Importing the observers and the status DTO
from cc_statusq_cpu.capsule import ConsoleObserver, CSVObserver
from cc_statusq_cpu.core import CPUStatus


@pytest.fixture
def dummy_cpu_status():
    """
    Fixture that provides a valid CPUStatus snapshot for observer testing.
    """
    return CPUStatus(
        name="TestCPU",
        architecture="x86_64",
        physical_cores=2,
        logical_cores=4,
        current_frequency=2400.0,
        min_frequency=800.0,
        max_frequency=3500.0,
        total_usage_percentage=25.0,
        usage_per_core=[20.0, 30.0],
        average_load=[0.1, 0.2, 0.3],
        user_time=100.0,
        system_time=50.0,
        idle_time=500.0,
        current_temperature=55.0,
        timestamp=datetime(2026, 1, 1, 12, 0, 0)
    )

class TestConsoleObserver:
    """
    Suite to verify that ConsoleObserver correctly formats and prints 
    CPU information to the standard output.
    """

    def test_console_on_data_received_prints_correctly(self, dummy_cpu_status):
        observer = ConsoleObserver()
        
        # We patch 'builtins.print' to capture what the observer tries to output
        with patch('builtins.print') as mock_print:
            observer.on_data_received(dummy_cpu_status)
            
            # Verify that print was called
            mock_print.assert_called()
            
            # Check if the output contains key metrics
            args, _ = mock_print.call_args
            output_str = args[0]
            assert "Total Usage: 25.0%" in output_str
            assert "Temp: 55.0°C" in output_str

    def test_console_on_error_prints_message(self):
        observer = ConsoleObserver()
        with patch('builtins.print') as mock_print:
            observer.on_error("Connection lost", Exception("Hardware failure"))
            mock_print.assert_called_with("❌ ERROR: Connection lost -> Hardware failure")

class TestCSVObserver:
    """
    Suite to verify CSVObserver functionality, ensuring it creates files 
    and appends data correctly in CSV format.
    """

    @pytest.fixture
    def csv_path(self, tmp_path):
        """Creates a temporary path for the CSV file to avoid polluting the workspace."""
        return str(tmp_path / "test_cpu_log.csv")

    def test_csv_initialization_creates_header(self, csv_path, dummy_cpu_status):
        observer = CSVObserver(file_path=csv_path)
        
        # First call should initialize the file and write the header
        observer.on_data_received(dummy_cpu_status)
        
        assert os.path.exists(csv_path)
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            # Check that the first line is the header (keys of CPUStatus)
            assert "total_usage_percentage" in lines[0]
            # Check that the second line contains the data
            assert "25.0" in lines[1]

    def test_csv_appends_multiple_records(self, csv_path, dummy_cpu_status):
        observer = CSVObserver(file_path=csv_path)
        
        # Simulate two captures
        observer.on_data_received(dummy_cpu_status)
        observer.on_data_received(dummy_cpu_status)
        
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            # Header + 2 data rows = 3 lines total
            assert len(lines) == 3

    def test_csv_error_handling_does_not_crash(self, csv_path, dummy_cpu_status):
        """
        Ensures that if file writing fails (e.g. read-only filesystem), 
        the observer handles it gracefully via on_error.
        """
        observer = CSVObserver(file_path="/invalid/path/to/file.csv")
        
        with patch('builtins.print') as mock_print:
            # This should trigger the try-except block in CSVObserver
            observer.on_data_received(dummy_cpu_status)
            # Verify the error was logged to console instead of crashing the app
            mock_print.assert_called()
            assert "!!! FileLogger Error" in mock_print.call_args[0][0]