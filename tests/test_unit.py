from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from core_cpu_monitor import CPUStateCheck

TARGET_MODULE = "core_cpu_monitor.domain"


@pytest.fixture
def mock_psutil():
    with patch(f"{TARGET_MODULE}.psutil") as mocked:
        # Usamos PropertyMock o objetos simples para mayor claridad
        mocked.cpu_times.return_value = MagicMock(user=10.0, system=5.0, idle=100.0)
        mocked.cpu_freq.return_value = MagicMock(current=2500.0, min=800.0, max=3500.0)

        # Mejoramos la lógica de cpu_count
        mocked.cpu_count.side_effect = lambda logical: 4 if not logical else 8

        # Evitamos fragilidad en cpu_percent usando una función inteligente
        def cpu_percent_mock(interval=None, percpu=False):
            return [10.0, 30.0] if percpu else 20.5

        mocked.cpu_percent.side_effect = cpu_percent_mock

        mocked.getloadavg.return_value = (1.0, 0.5, 0.2)
        yield mocked


@pytest.fixture
def mock_platform():
    with patch(f"{TARGET_MODULE}.platform") as mocked:
        mocked.processor.return_value = "Intel"
        mocked.machine.return_value = "x86_64"
        yield mocked


# --- Tests Mejorados ---


def test_capture_complete_data(mock_psutil, mock_platform):
    """Verifica que todos los campos se mapeen correctamente."""
    fixed_now = datetime(2024, 1, 1)
    with patch(f"{TARGET_MODULE}.datetime") as mock_date:
        mock_date.now.return_value = fixed_now

        mock_logger = MagicMock()
        check = CPUStateCheck(logger=mock_logger)
        status = check.capture()

        assert status.total_usage_percentage == 20.5
        assert status.usage_per_core == [10.0, 30.0]
        assert status.user_time == 10.0
        assert status.average_load == [1.0, 0.5, 0.2]
        assert status.timestamp == fixed_now


def test_capture_temperature_exception_handling(mock_psutil, mock_platform):
    """Verifica la resiliencia: si los sensores fallan, la temperatura es None."""
    mock_psutil.sensors_temperatures.side_effect = Exception("Hardware error")

    mock_logger = MagicMock()
    check = CPUStateCheck(logger=mock_logger)
    status = check.capture()

    assert status.current_temperature is None
    # Verificamos que el resto del objeto se creó correctamente
    assert status.name == "Intel"


def test_capture_no_load_avg_support(mock_psutil, mock_platform):
    """Simula un sistema (como Windows antiguo) que no tiene getloadavg."""
    # Forzamos que la llamada lance AttributeError, simulando que no existe o falla
    mock_psutil.getloadavg.side_effect = AttributeError

    mock_logger = MagicMock()
    check = CPUStateCheck(logger=mock_logger)
    status = check.capture()

    assert status.average_load is None


def test_capture_freq_none(mock_psutil, mock_platform):
    """Verifica que si cpu_freq devuelve None, los valores sean 0.0."""
    mock_psutil.cpu_freq.return_value = None

    mock_logger = MagicMock()
    check = CPUStateCheck(logger=mock_logger)
    status = check.capture()

    assert status.current_frequency == 0.0
    assert status.min_frequency == 0.0
