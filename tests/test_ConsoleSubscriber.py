from unittest.mock import MagicMock

from cc.statusq.cpu.capsule.ConsoleSubscriber import ConsoleSubscriber
from cc.statusq.cpu.core import DataReceivedEvent, MonitoringStartedEvent


def test_subscriber_registration(event_bus):
    """
    Ensures that ConsoleSubscriber registers its handlers when 
    the subscribe_to method is explicitly called.
    """
    event_bus.subscribe = MagicMock(side_effect=event_bus.subscribe)
    
    # New flow: Instantiate without arguments
    subscriber = ConsoleSubscriber()
    # Explicitly call the contract method
    subscriber.subscribe_to(event_bus)
    
    # Check captured calls
    args_passed = [call[0][0] for call in event_bus.subscribe.call_args_list]
    assert MonitoringStartedEvent in args_passed
    assert DataReceivedEvent in args_passed

def test_handle_start_output(event_bus, capsys):
    """
    Verifies output after proper contract fulfillment.
    """
    subscriber = ConsoleSubscriber()
    subscriber.subscribe_to(event_bus) # Essential step
    
    event = MonitoringStartedEvent(mode="continuous")
    event_bus.publish(event)
    
    captured = capsys.readouterr()
    assert "🚀 Started: continuous" in captured.out

def test_handle_data_output(event_bus, mock_cpu_status, capsys):
    """
    Verifies usage output after proper contract fulfillment.
    """
    subscriber = ConsoleSubscriber()
    subscriber.subscribe_to(event_bus)
    
    event = DataReceivedEvent(status=mock_cpu_status)
    event_bus.publish(event)
    
    captured = capsys.readouterr()
    expected_usage = f"Usage: {mock_cpu_status.total_usage_percentage}%"
    assert expected_usage in captured.out

def test_subscriber_ignores_unrelated_events(event_bus, capsys):
    """
    Ensures no output for unsubscribed events.
    """
    from cc.statusq.cpu.core import MonitoringFinishedEvent
    
    subscriber = ConsoleSubscriber()
    subscriber.subscribe_to(event_bus)
    
    event_bus.publish(MonitoringFinishedEvent())
    
    captured = capsys.readouterr()
    assert captured.out == ""