import pytest

from cc.statusq.cpu.core import CPUEventBus, CPUEventSubscriber, DataReceivedEvent, MonitoringStartedEvent


# 1. Create a concrete implementation of the ABC for testing purposes
class MockSubscriber(CPUEventSubscriber):
    """
    A concrete implementation of CPUEventSubscriber to test the interface contract.
    It simulates how a real UI or Logger would connect to the Bus.
    """
    def __init__(self):
        self.received_start = False
        self.received_data = False

    def subscribe_to(self, bus: CPUEventBus) -> None:
        # Implementation of the abstract method
        bus.subscribe(MonitoringStartedEvent, self._on_start)
        bus.subscribe(DataReceivedEvent, self._on_data)

    def _on_start(self, event: MonitoringStartedEvent):
        self.received_start = True

    def _on_data(self, event: DataReceivedEvent):
        self.received_data = True


## --- Tests ---

def test_subscriber_cannot_be_instantiated_directly():
    """
    Ensure that CPUEventSubscriber remains an abstract class and 
    cannot be used without implementation.
    """
    with pytest.raises(TypeError, match="Can't instantiate abstract class CPUEventSubscriber"):
        CPUEventSubscriber()


def test_concrete_subscriber_registers_to_bus(event_bus):
    """
    Verify that when subscribe_to is called, the subscriber correctly 
    registers its internal methods to the provided EventBus.
    """
    subscriber = MockSubscriber()
    
    # Action: Connect the subscriber to the bus
    subscriber.subscribe_to(event_bus)
    
    # Trigger events on the bus
    event_bus.publish(MonitoringStartedEvent(mode="test"))
    
    # Assert: The internal handler was called through the bus
    assert subscriber.received_start is True
    assert subscriber.received_data is False


def test_subscriber_responds_to_specific_data_events(event_bus, mock_cpu_status):
    """
    Verify that the subscriber reacts to data events once registered via subscribe_to.
    """
    subscriber = MockSubscriber()
    subscriber.subscribe_to(event_bus)
    
    # Action: Publish a data event
    event_bus.publish(DataReceivedEvent(status=mock_cpu_status))
    
    # Assert: Only the data handler was triggered
    assert subscriber.received_data is True


def test_interface_enforces_method_signature():
    """
    Safety check to ensure that any class inheriting from CPUEventSubscriber 
    must implement 'subscribe_to'.
    """
    class IncompleteSubscriber(CPUEventSubscriber):
        pass
        
    with pytest.raises(TypeError, match="Can't instantiate abstract class IncompleteSubscriber"):
        IncompleteSubscriber()