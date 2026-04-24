from __future__ import annotations

from collections import deque
from typing import Dict, List

from .algorithms import (
    binary_search_by_priority,
    lookup_by_id,
    search_by_criticality,
    search_by_orbit_arrival_window,
    sort_by_fuel_ascending,
    sort_by_priority,
)
from .authorization import check_altitude, check_fuel, check_thermal
from .constants import (
    DRAG_COEFFICIENT_K,
    ENTRY_PEAK_TEMP_C,
    FUEL_BURN_RATE_PCT_PER_S,
    FUEL_MIN_PCT,
    MARS_GRAVITY,
    MARS_SURFACE_TEMP_C,
    POWERED_DESCENT_INITIAL_FUEL_PCT,
    RETRO_IGNITION_ALTITUDE_M,
    SEPARATOR,
    THERMAL_DECAY_LAMBDA,
)
from .enums import Criticality
from .models import Alert, AuditEntry, LandingEvent, LandingModule
from .physics import (
    compute_altitude,
    compute_drag_force,
    compute_fuel_consumed_linear,
    compute_fuselage_temperature,
)


def display_header() -> None:
    print(SEPARATOR)
    print("🛸 MGPEB — AURORA SIGER")
    print("   Módulo de Gerenciamento de Pouso e Estabilização de Base")
    print("   Sistema de bordo inicializado. Módulos em órbita. 🖖")
    print(SEPARATOR)


def display_module_queue(queue: deque) -> None:
    print(SEPARATOR)
    print("📋 FILA DE POUSO — MÓDULOS AGUARDANDO AUTORIZAÇÃO")
    print(SEPARATOR)
    for i, module in enumerate(queue):
        fuel_flag = " ⚠ COMBUSTÍVEL ABAIXO DO MÍNIMO" if module.fuel_pct < FUEL_MIN_PCT else ""
        sensor_flag = " ⚠ ERRO DE SENSOR" if module.sensor_error else ""
        print(
            f"  [{i + 1}] {module.module_id:<8} | {module.name:<28} | "
            f"Prior. {module.landing_priority} | "
            f"Comb. {module.fuel_pct:.0f}%"
            f"{fuel_flag}{sensor_flag}"
        )
    print(SEPARATOR)


def display_mathematical_models() -> None:
    print(SEPARATOR)
    print("📐 MODELOS MATEMÁTICOS — FENÔMENOS FÍSICOS DO POUSO")
    print(SEPARATOR)
    _display_model_altitude()
    _display_model_drag()
    _display_model_temperature()
    _display_model_fuel()
    print(SEPARATOR)


def _display_model_altitude() -> None:
    initial_altitude_m: float = 11_000.0
    initial_velocity_ms: float = 470.0
    print("\n  1. ALTITUDE × TEMPO — h(t) = h₀ - v₀·t - ½·g·t²  (quadrática)")
    print(f"     h₀={initial_altitude_m:.0f} m | v₀={initial_velocity_ms:.0f} m/s | g={MARS_GRAVITY} m/s²")
    print(f"     Limiar de ignição: {RETRO_IGNITION_ALTITUDE_M:.0f} m\n")
    print(f"  {'t (s)':<10} {'h(t) (m)':<15} ALTITUDE_OK")
    print(f"  {'-'*42}")
    for t in [0, 5, 10, 15, 20, 25]:
        h = compute_altitude(initial_altitude_m, initial_velocity_ms, float(t))
        ok = "✔ SIM" if check_altitude(h) else "✗ NÃO"
        print(f"  {t:<10} {h:<15.1f} {ok}")


def _display_model_drag() -> None:
    print("\n  2. FORÇA DE ARRASTO × VELOCIDADE — F(v) = k·v²  (quadrática)")
    print(f"     k={DRAG_COEFFICIENT_K} (SIMULATED) | NASA Mars Atmosphere Model\n")
    print(f"  {'v (m/s)':<12} {'F(v) (N)':<18} Fase")
    print(f"  {'-'*48}")
    for v, phase in [
        (5_900, "entrada hipersônica"),
        (2_000, "descida subsônica"),
        (100,   "aproximação final"),
    ]:
        print(f"  {v:<12} {compute_drag_force(float(v)):<18.1f} {phase}")


def _display_model_temperature() -> None:
    print("\n  3. TEMPERATURA DA FUSELAGEM × TEMPO — T(t) = T_sup + (T_ent-T_sup)·e^(-λt)  (exponencial)")
    print(f"     T_ent={ENTRY_PEAK_TEMP_C:.0f}°C | T_sup={MARS_SURFACE_TEMP_C:.0f}°C | λ={THERMAL_DECAY_LAMBDA} s⁻¹ (SIMULATED)\n")
    print(f"  {'t (s)':<10} {'T(t) (°C)':<15} THERMAL_OK")
    print(f"  {'-'*42}")
    for t in [0, 100, 200, 300, 400]:
        temp = compute_fuselage_temperature(float(t))
        ok = "✔ SIM" if check_thermal(temp) else "✗ NÃO"
        print(f"  {t:<10} {temp:<15.1f} {ok}")


def _display_model_fuel() -> None:
    print("\n  4. CONSUMO DE COMBUSTÍVEL × TEMPO — C(t) = C₀ - r·t  (linear)")
    print(f"     C₀={POWERED_DESCENT_INITIAL_FUEL_PCT:.0f}% | r={FUEL_BURN_RATE_PCT_PER_S} %/s (SIMULATED)")
    print(f"     Mínimo seguro: {FUEL_MIN_PCT:.0f}%\n")
    print(f"  {'t (s)':<10} {'C(t) (%)':<15} FUEL_OK")
    print(f"  {'-'*42}")
    for t in [0, 100, 200, 400, 600, 800]:
        remaining = compute_fuel_consumed_linear(float(t))
        ok = "✔ SIM" if check_fuel(remaining) else "✗ NÃO"
        print(f"  {t:<10} {remaining:<15.1f} {ok}")


def display_search_results(
    modules: List[LandingModule],
    criticality_index: Dict[Criticality, List[LandingModule]],
    module_index: Dict[str, LandingModule],
) -> None:
    print(SEPARATOR)
    print("🔍 BUSCA E ORDENAÇÃO — RESULTADOS")
    print(SEPARATOR)

    print("\n  Insertion Sort — por prioridade de pouso:")
    for m in sort_by_priority(modules):
        print(f"    [{m.landing_priority}] {m.module_id} — {m.name}")

    print("\n  Selection Sort — por combustível crescente:")
    for m in sort_by_fuel_ascending(modules):
        flag = " ⚠ ABAIXO DO MÍNIMO" if m.fuel_pct < FUEL_MIN_PCT else ""
        print(f"    {m.module_id} — {m.fuel_pct:.0f}%{flag}")

    print("\n  Busca O(1) — módulos VITAIS (índice por criticidade):")
    for m in search_by_criticality(criticality_index, Criticality.VITAL):
        print(f"    {m.module_id} — {m.name}")

    ref_module = modules[0]
    print(f"\n  Busca linear — módulos com chegada próxima a {ref_module.module_id} (±0.6 h):")
    for m in search_by_orbit_arrival_window(modules, ref_module.orbit_arrival_h, 0.6):
        print(f"    {m.module_id} — chegada em {m.orbit_arrival_h} h")

    mid_priority = sort_by_priority(modules)[len(modules) // 2].landing_priority
    print(f"\n  Busca binária — prioridade {mid_priority} (lista já ordenada):")
    result = binary_search_by_priority(sort_by_priority(modules), mid_priority)
    if result:
        print(f"    Encontrado: {result.module_id} — {result.name}")

    print(f"\n  Busca O(1) — lookup por ID ({ref_module.module_id}):")
    found = lookup_by_id(module_index, ref_module.module_id)
    if found:
        print(f"    Encontrado: {found.module_id} — {found.name} | Comb. {found.fuel_pct:.0f}%")
    print(SEPARATOR)


def display_alert_queue_and_list(
    alert_queue: deque,
    alert_list: List[Alert],
) -> None:
    print(SEPARATOR)
    print("🚨 ALERTAS — FILA DE ENTRADA E LISTA OPERACIONAL")
    print(SEPARATOR)
    print(f"\n  Fila de alertas (FIFO — ordem de chegada) — {len(alert_queue)} alertas:")
    for i, alert in enumerate(alert_queue):
        print(f"    [{i+1}] {alert.module_id} | {alert.severity} | {alert.reason}")
    print(f"\n  Lista de alertas (ordenada por criticidade) — visão do operador:")
    for i, alert in enumerate(alert_list):
        print(f"    [{i+1}] {alert.module_id} | {alert.severity} | {alert.reason}")
    print(SEPARATOR)


def display_event_stack(event_stack: List[LandingEvent]) -> None:
    print(SEPARATOR)
    print("📚 PILHA DE EVENTOS — AÇÕES REVERSÍVEIS")
    print(SEPARATOR)
    if not event_stack:
        print("  Pilha vazia.")
    else:
        for i, event in enumerate(reversed(event_stack)):
            print(f"  [{len(event_stack)-i}] {event.event_type} | {event.module_id} | {event.module_criticality}")
    print(SEPARATOR)


def display_audit_log(audit_log: List[AuditEntry]) -> None:
    print(SEPARATOR)
    print("📋 AUDIT LOG — HISTÓRICO COMPLETO")
    print(SEPARATOR)
    for i, entry in enumerate(audit_log):
        print(f"  [{i+1:02d}] {entry.event_type:<30} | {entry.module_id:<8} | {entry.description}")
    print(SEPARATOR)


def display_final_report(
    modules: List[LandingModule],
    landed: List[LandingModule],
    waiting: List[LandingModule],
    alert_list: List[Alert],
) -> None:
    print(SEPARATOR)
    print("🪐 AURORA SIGER — RELATÓRIO FINAL DE POUSO")
    print(SEPARATOR)

    print(f"\n  Módulos pousados ({len(landed)}):")
    for m in landed:
        print(f"    ✔  {m.module_id} — {m.name}")

    if waiting:
        print(f"\n  Módulos em espera ({len(waiting)}):")
        for m in waiting:
            print(f"    ⏸  {m.module_id} — {m.name}")

    if alert_list:
        print(f"\n  Módulos em alerta — aguardando autorização humana ({len(alert_list)}):")
        for alert in alert_list:
            print(f"    ⚠  {alert.module_id} | {alert.severity} | {alert.reason}")

    print()
    print(SEPARATOR)
    print(f"Módulos pousados: {len(landed)} | Em espera: {len(waiting)} | Alerta: {len(alert_list)}")

    if len(landed) == len(modules):
        print(">>> TODOS OS MÓDULOS POUSARAM COM SUCESSO <<<")
        print("Base Aurora Siger estabelecida. Vida longa e próspera. 🖖")
    else:
        print(">>> SEQUÊNCIA DE POUSO INCOMPLETA <<<")
        print("Anomalia detectada. Aguardando autorização para módulos em alerta. 💥")
    print(SEPARATOR)
