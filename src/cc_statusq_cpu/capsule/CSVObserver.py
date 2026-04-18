import csv
import os

from ..core.CPUObserver import CPUObserver
from ..core.CPUStatus import CPUStatus


class CSVObserver(CPUObserver):
    """
    Observer that saves CPU monitoring logs to a CSV file in the background.
    This allows for persistent storage and later analysis of performance data.
    """

    def __init__(self, file_path: str = "cpu_monitoring_log.csv"):
        self.file_path = file_path
        self._initialized = False

    def _initialize_file(self, status: CPUStatus):
        """
        Creates the file and writes the header if it doesn't exist.
        Dynamically extracts headers from the CPUStatus dataclass fields.
        """
        # Check if file exists to avoid overwriting or redundant headers
        file_exists = os.path.isfile(self.file_path)
        
        if not file_exists:
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Use the keys from the dataclass as CSV headers
                writer.writerow(status.__dict__.keys())
        
        self._initialized = True

    def on_capture_start(self, mode: str):
        """Log the start of a monitoring session."""
        # Optional: You could log session breaks in the file here
        pass

    def on_data_received(self, status: CPUStatus):
        """
        Triggered every time new data is captured. 
        Appends the CPU status metrics as a new row in the CSV.
        """
        try:
            if not self._initialized:
                self._initialize_file(status)

            with open(self.file_path, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Extract values in the same order as the headers
                writer.writerow(status.__dict__.values())
        except Exception as e:
            # We don't want a file write error to crash the whole monitoring loop
            self.on_error(f"Failed to write to file {self.file_path}", e)

    def on_error(self, message: str, error: Exception = None):
        """Handles logging of internal errors to the console or a separate error log."""
        print(f"!!! FileLogger Error: {message} -> {error}")

    def on_finished(self):
        """Optional cleanup or finalization logic."""
        self._initialized = False # Reset state for potential new sessions