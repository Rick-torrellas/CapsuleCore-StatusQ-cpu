from unittest.mock import MagicMock

import pytest
from cc.statusq.core.schema import CPUStatus

# Importing core components
from cc.statusq.cpu.core import CPUEventBus, DataReceivedEvent, MonitoringFinishedEvent, MonitoringStartedEvent


class TestCPUEventBus:
    """
    Test suite for the CPUEventBus component.
    Ensures that the event-driven communication remains decoupled and reliable.
    """

    @pytest.fixture
    def bus(self):
        """Provides a fresh instance of CPUEventBus for every test."""
        return CPUEventBus()

    def test_subscribe_and_publish_event(self, bus):
        """
        GIVEN a subscriber registered for a specific event
        WHEN that event is published
        THEN the subscriber's callback should be executed with the correct data.
        """
        # Mock callback to track execution
        callback = MagicMock()
        
        # Subscribe to MonitoringStartedEvent
        bus.subscribe(MonitoringStartedEvent, callback)
        
        # Create and publish the event
        event = MonitoringStartedEvent(mode="single")
        bus.publish(event)
        
        # Assertions
        callback.assert_called_once_with(event)
        assert callback.call_args[0][0].mode == "single"

    def test_multiple_subscribers_for_same_event(self, bus):
        """
        GIVEN multiple subscribers for the same event type
        WHEN the event is published
        THEN all subscribers should receive the event.
        """
        callback_one = MagicMock()
        callback_two = MagicMock()
        
        bus.subscribe(DataReceivedEvent, callback_one)
        bus.subscribe(DataReceivedEvent, callback_two)
        
        # Dummy status object is required for DataReceivedEvent
        dummy_status = MagicMock(spec=CPUStatus)
        event = DataReceivedEvent(status=dummy_status)
        
        bus.publish(event)
        
        callback_one.assert_called_once_with(event)
        callback_two.assert_called_once_with(event)

    def test_event_isolation(self, bus):
        """
        GIVEN subscribers for different event types
        WHEN one type of event is published
        THEN only the relevant subscribers should be notified.
        """
        started_callback = MagicMock()
        finished_callback = MagicMock()
        
        bus.subscribe(MonitoringStartedEvent, started_callback)
        bus.subscribe(MonitoringFinishedEvent, finished_callback)
        
        # Publish only the "Finished" event
        bus.publish(MonitoringFinishedEvent())
        
        # Assertions
        started_callback.assert_not_called()
        finished_callback.assert_called_once()

    def test_publish_without_subscribers(self, bus):
        """
        GIVEN no subscribers for an event type
        WHEN an event is published
        THEN the system should not raise any errors.
        """
        try:
            bus.publish(MonitoringStartedEvent(mode="test"))
        except Exception as e:
            pytest.fail(f"Publishing without subscribers raised an exception: {e}")

    def test_subscriber_receives_correct_payload(self, bus):
        """
        Ensures that the complex DataReceivedEvent carries the CPUStatus 
        payload correctly through the bus.
        """
        received_data = []

        def store_event(event: DataReceivedEvent):
            received_data.append(event.status)

        bus.subscribe(DataReceivedEvent, store_event)

        # Creating a realistic mock status
        mock_status = MagicMock(spec=CPUStatus)
        mock_status.total_usage_percentage = 45.5
        
        event = DataReceivedEvent(status=mock_status)
        bus.publish(event)

        assert len(received_data) == 1
        assert received_data[0].total_usage_percentage == 45.5