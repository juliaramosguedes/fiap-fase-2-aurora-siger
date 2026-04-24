from __future__ import annotations

from typing import List

from .constants import (
    FUEL_MIN_PCT,
    HOURS_TO_MINUTES,
    LANDING_ZONE_CLEARANCE_MIN,
    RETRO_IGNITION_ALTITUDE_M,
    SENSOR_ERROR_ORBIT_THRESHOLD_H,
    THERMAL_MAX_C,
)
from .enums import Decision
from .models import AuthorizationResult, DescentTelemetry, LandingModule


def check_sensor_error(orbit_arrival_h: float) -> bool:
    return orbit_arrival_h > SENSOR_ERROR_ORBIT_THRESHOLD_H


def check_zone_clear(
    module: LandingModule,
    landed_modules: List[LandingModule],
) -> bool:
    if not landed_modules:
        return True
    return all(
        abs(module.orbit_arrival_h - landed.orbit_arrival_h) * HOURS_TO_MINUTES >= LANDING_ZONE_CLEARANCE_MIN
        for landed in landed_modules
    )


def check_altitude(current_altitude_m: float) -> bool:
    return current_altitude_m <= RETRO_IGNITION_ALTITUDE_M


def check_fuel(fuel_pct: float) -> bool:
    return fuel_pct >= FUEL_MIN_PCT


def check_thermal(fuselage_temperature_c: float) -> bool:
    return fuselage_temperature_c <= THERMAL_MAX_C


def check_sensor(sensor_error: bool) -> bool:
    return not sensor_error


def check_zone(zone_clear: bool) -> bool:
    return zone_clear


def evaluate_authorization(
    module: LandingModule,
    telemetry: DescentTelemetry,
) -> AuthorizationResult:
    altitude_ok = check_altitude(telemetry.current_altitude_m)
    fuel_ok      = check_fuel(module.fuel_pct)
    thermal_ok   = check_thermal(telemetry.fuselage_temperature_c)
    sensor_ok    = check_sensor(module.sensor_error)
    zone_ok      = check_zone(module.zone_clear)

    all_clear = all([altitude_ok, fuel_ok, thermal_ok, sensor_ok, zone_ok])
    requires_human_override = not fuel_ok or not sensor_ok

    decision_rules = [
        (all_clear,               Decision.AUTHORIZED),
        (requires_human_override, Decision.ALERT),
    ]
    decision = next(
        (d for condition, d in decision_rules if condition),
        Decision.DENIED,
    )

    return AuthorizationResult(
        module_id=module.module_id,
        altitude_ok=altitude_ok,
        fuel_ok=fuel_ok,
        thermal_ok=thermal_ok,
        sensor_ok=sensor_ok,
        zone_ok=zone_ok,
        decision=decision,
    )
