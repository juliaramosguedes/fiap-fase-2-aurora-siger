from __future__ import annotations

from collections import deque
from typing import List, Optional, Tuple

from .algorithms import build_criticality_index, build_module_index, sort_by_priority
from .authorization import evaluate_authorization
from .constants import FUEL_MIN_PCT, SENSOR_ERROR_ORBIT_THRESHOLD_H, SEPARATOR
from .display import (
    display_alert_queue_and_list,
    display_audit_log,
    display_event_stack,
    display_final_report,
    display_header,
    display_mathematical_models,
    display_module_queue,
    display_search_results,
)
from .enums import Decision, EventType
from .models import Alert, AuditEntry, DescentTelemetry, LandingEvent, LandingModule
from .physics import compute_altitude, compute_fuselage_temperature
from .registry import build_modules
from .scenarios import LandingModuleConfig
from .structures import (
    append_audit,
    build_landing_queue,
    enqueue_alert,
    flush_alert_queue_to_list,
    push_event,
)


def simulate_landing_sequence(
    modules: List[LandingModule],
) -> Tuple[List[LandingModule], List[LandingModule], List[Alert], List[LandingEvent], List[AuditEntry]]:
    landing_queue = build_landing_queue(modules)
    landed:      List[LandingModule]  = []
    waiting:     List[LandingModule]  = []
    alert_queue: deque                = deque()
    event_stack: List[LandingEvent]   = []
    audit_log:   List[AuditEntry]     = []

    print(SEPARATOR)
    print("🚀 SEQUÊNCIA DE POUSO — PROCESSANDO FILA")
    print(SEPARATOR)

    while landing_queue:
        module = landing_queue.popleft()

        # SIMULATED: 210 s base + 5 s per orbit hour — places each module near
        # the 1,500 m retrorocket ignition threshold per MSL EDL timeline.
        descent_time_s: float = 210.0 + module.orbit_arrival_h * 5.0
        telemetry = DescentTelemetry(
            module_id=module.module_id,
            current_altitude_m=compute_altitude(11_000.0, 470.0, descent_time_s),
            current_velocity_ms=max(0.0, 470.0 - descent_time_s * 2.0),
            fuselage_temperature_c=compute_fuselage_temperature(descent_time_s),
            elapsed_time_s=descent_time_s,
        )

        result = evaluate_authorization(module, telemetry)

        check = lambda ok: "OK " if ok else "NOK"
        print(f"\n  {module.module_id} — {module.name}")
        print(f"  {check(result.altitude_ok)} Altitude  "
              f"| {check(result.fuel_ok)} Combustível  "
              f"| {check(result.thermal_ok)} Térmica  "
              f"| {check(result.sensor_ok)} Sensores  "
              f"| {check(result.zone_ok)} Zona")
        print(f"  >>> {result.decision} <<<")

        if result.decision == Decision.AUTHORIZED:
            event_stack = push_event(event_stack, EventType.AUTHORIZATION_GRANTED, module)
            event_stack = push_event(event_stack, EventType.LANDING_INITIATED, module)
            audit_log = append_audit(
                audit_log, EventType.LANDING_COMPLETED, module.module_id,
                f"Pousou com sucesso | comb. {module.fuel_pct:.0f}%"
            )
            landed.append(module)

        elif result.decision == Decision.ALERT:
            reason = []
            if not result.fuel_ok:
                reason.append(f"combustível {module.fuel_pct:.0f}% < {FUEL_MIN_PCT:.0f}%")
            if not result.sensor_ok:
                reason.append(f"erro de sensor (exposição {module.time_in_orbit_h}h > {SENSOR_ERROR_ORBIT_THRESHOLD_H}h)")
            alert_queue = enqueue_alert(alert_queue, module, " | ".join(reason))
            audit_log = append_audit(
                audit_log, EventType.ALERT_GENERATED, module.module_id,
                f"Alerta gerado — {' | '.join(reason)}"
            )

        else:
            audit_log = append_audit(
                audit_log, EventType.LANDING_DENIED, module.module_id,
                f"Pouso negado — zona={result.zone_ok} térmica={result.thermal_ok}"
            )
            waiting.append(module)

    alert_list = flush_alert_queue_to_list(alert_queue)
    return landed, waiting, alert_list, event_stack, audit_log


def main(scenario: Optional[List[LandingModuleConfig]] = None) -> None:
    from .scenarios import default_scenario
    modules = build_modules(scenario or default_scenario())
    module_index = build_module_index(modules)
    criticality_index = build_criticality_index(modules)

    display_header()
    display_module_queue(deque(sort_by_priority(modules)))
    display_mathematical_models()
    display_search_results(modules, criticality_index, module_index)

    landed, waiting, alert_list, event_stack, audit_log = simulate_landing_sequence(modules)

    display_alert_queue_and_list(deque(alert_list), alert_list)
    display_event_stack(event_stack)
    display_audit_log(audit_log)
    display_final_report(modules, landed, waiting, alert_list)
