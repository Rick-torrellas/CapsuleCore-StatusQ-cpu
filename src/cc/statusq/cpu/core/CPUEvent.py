from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from cc.statusq.core.schema import CPUStatus


@dataclass(frozen=True, kw_only=True)
class CPUEvent:
    """Base class for all CPU related events."""
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True, kw_only=True)
class MonitoringStartedEvent(CPUEvent):
    """Fired when the monitoring process begins."""
    mode: str  # e.g., "single" or "continuous"

@dataclass(frozen=True, kw_only=True)
class DataReceivedEvent(CPUEvent):
    """Fired when new CPU metrics are successfully captured."""
    status: CPUStatus

@dataclass(frozen=True, kw_only=True)
class MonitoringErrorEvent(CPUEvent):
    """Fired when an error occurs during capture or processing."""
    message: str
    exception: Optional[Exception] = None

@dataclass(frozen=True, kw_only=True)
class MonitoringFinishedEvent(CPUEvent):
    """Fired when the monitoring session ends (successfully or not)."""
    pass