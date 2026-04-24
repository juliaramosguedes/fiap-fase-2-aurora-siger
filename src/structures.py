from __future__ import annotations

from collections import deque
from typing import List, Optional, Tuple

from .constants import ALERT_SEVERITY_ORDER, CRITICALITY_TO_ALERT_SEVERITY
from .enums import EventType
from .models import Alert, AuditEntry, LandingEvent, LandingModule


def build_landing_queue(modules: List[LandingModule]) -> deque:
    from .algorithms import sort_by_priority
    return deque(sort_by_priority(modules))


def enqueue_alert(
    alert_queue: deque,
    module: LandingModule,
    reason: str,
) -> deque:
    alert = Alert(
        module_id=module.module_id,
        severity=CRITICALITY_TO_ALERT_SEVERITY[module.criticality],
        reason=reason,
    )
    new_queue = deque(alert_queue)
    new_queue.append(alert)
    return new_queue


def flush_alert_queue_to_list(alert_queue: deque) -> List[Alert]:
    return sorted(list(alert_queue), key=lambda a: ALERT_SEVERITY_ORDER[a.severity])


def push_event(
    event_stack: List[LandingEvent],
    event_type: EventType,
    module: LandingModule,
) -> List[LandingEvent]:
    event = LandingEvent(
        event_type=event_type,
        module_id=module.module_id,
        module_criticality=module.criticality,
    )
    return event_stack + [event]


def pop_event(
    event_stack: List[LandingEvent],
) -> Tuple[Optional[LandingEvent], List[LandingEvent]]:
    if not event_stack:
        return None, []
    return event_stack[-1], event_stack[:-1]


def append_audit(
    audit_log: List[AuditEntry],
    event_type: EventType,
    module_id: str,
    description: str,
) -> List[AuditEntry]:
    entry = AuditEntry(
        event_type=event_type,
        module_id=module_id,
        description=description,
    )
    return audit_log + [entry]
