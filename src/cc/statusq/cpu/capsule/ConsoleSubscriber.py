from ..core import CPUEventBus, CPUEventSubscriber, DataReceivedEvent, MonitoringStartedEvent


class ConsoleSubscriber(CPUEventSubscriber):
    """
    Infrastructure implementation of a CPU event subscriber.
    It fulfills the CPUEventSubscriber contract by implementing subscribe_to.
    """

    def __init__(self):
        """
        Initialize the subscriber. 
        Note: We no longer require the bus in the constructor to keep it decoupled.
        """
        pass

    def subscribe_to(self, bus: CPUEventBus) -> None:
        """
        Implementation of the mandatory contract method.
        Maps specific events to internal handler methods.
        """
        bus.subscribe(MonitoringStartedEvent, self._handle_start)
        bus.subscribe(DataReceivedEvent, self._handle_data)

    def _handle_start(self, event: MonitoringStartedEvent) -> None:
        """Prints a rocket icon and the monitoring mode when started."""
        print(f"🚀 Started: {event.mode}")

    def _handle_data(self, event: DataReceivedEvent) -> None:
        """Prints the CPU usage percentage from the received status snapshot."""
        print(f"Usage: {event.status.total_usage_percentage}%")