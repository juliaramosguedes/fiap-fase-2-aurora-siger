from __future__ import annotations

from dataclasses import dataclass

from .enums import AlertSeverity, Criticality, Decision, EventType


@dataclass(frozen=True)
class LandingModule:
    """Immutable snapshot of a module's state at orbit arrival."""
    module_id: str
    name: str
    landing_priority: int
    fuel_pct: float
    mass_kg: float
    criticality: Criticality
    orbit_arrival_h: float   # cumulative window position — used for zone_clear spacing
    time_in_orbit_h: float   # radiation exposure time — used for sensor_error check
    sensor_error: bool
    zone_clear: bool


@dataclass(frozen=True)
class DescentTelemetry:
    """Real-time telemetry snapshot during descent, computed via physics models."""
    module_id: str
    current_altitude_m: float
    current_velocity_ms: float
    fuselage_temperature_c: float
    elapsed_time_s: float


@dataclass(frozen=True)
class AuthorizationResult:
    """Outcome of a landing authorization check — each condition recorded independently."""
    module_id: str
    altitude_ok: bool
    fuel_ok: bool
    thermal_ok: bool
    sensor_ok: bool
    zone_ok: bool
    decision: Decision


@dataclass(frozen=True)
class LandingEvent:
    """Reversible landing control action for the Event Stack (LIFO)."""
    event_type: EventType
    module_id: str
    module_criticality: Criticality


@dataclass(frozen=True)
class AuditEntry:
    """Append-only record of any system event — never reversed or modified."""
    event_type: EventType
    module_id: str
    description: str


@dataclass(frozen=True)
class Alert:
    """Alert record entering via Alert Queue (FIFO) and sorted into Alert List."""
    module_id: str
    severity: AlertSeverity
    reason: str
