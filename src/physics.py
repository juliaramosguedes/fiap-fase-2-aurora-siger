from __future__ import annotations

import math

from .constants import (
    DRAG_COEFFICIENT_K,
    ENTRY_PEAK_TEMP_C,
    FUEL_BURN_RATE_PCT_PER_S,
    MARS_GRAVITY,
    MARS_SURFACE_TEMP_C,
    POWERED_DESCENT_INITIAL_FUEL_PCT,
    THERMAL_DECAY_LAMBDA,
)


def compute_altitude(
    initial_altitude_m: float,
    initial_velocity_ms: float,
    elapsed_time_s: float,
) -> float:
    """h(t) = h₀ - v₀·t - ½·g_mars·t²"""
    return max(0.0, (
        initial_altitude_m
        - initial_velocity_ms * elapsed_time_s
        - 0.5 * MARS_GRAVITY * elapsed_time_s ** 2
    ))


def compute_drag_force(velocity_ms: float) -> float:
    """F(v) = k · v²"""
    return DRAG_COEFFICIENT_K * velocity_ms ** 2


def compute_fuselage_temperature(
    elapsed_time_s: float,
    entry_temp_c: float = ENTRY_PEAK_TEMP_C,
    surface_temp_c: float = MARS_SURFACE_TEMP_C,
    decay_lambda: float = THERMAL_DECAY_LAMBDA,
) -> float:
    """T(t) = T_surface + (T_entry - T_surface) · e^(-λ·t)"""
    return surface_temp_c + (entry_temp_c - surface_temp_c) * math.exp(
        -decay_lambda * elapsed_time_s
    )


def compute_fuel_consumed_linear(elapsed_time_s: float) -> float:
    """C(t) = C₀ - r·t"""
    return POWERED_DESCENT_INITIAL_FUEL_PCT - FUEL_BURN_RATE_PCT_PER_S * elapsed_time_s
