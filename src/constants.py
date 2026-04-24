from __future__ import annotations

from typing import Dict

from .enums import AlertSeverity, Criticality

# -- Landing authorization thresholds --
FUEL_MIN_PCT: float = 60.0                   # % — ESA Advanced Concepts Team (2021)
THERMAL_MAX_C: float = 800.0                 # °C — Edquist et al., AIAA 2009-4117
RETRO_IGNITION_ALTITUDE_M: float = 1_500.0   # m — NASA JPL MSL EDL Overview (2012)
LANDING_ZONE_CLEARANCE_MIN: float = 30.0     # min — Golombek et al., Space Sci. Rev. (2012)
SENSOR_ERROR_ORBIT_THRESHOLD_H: float = 4.0  # h — SIMULATED (NASA HRP radiation hazards)

# -- Mars physical constants --
MARS_GRAVITY: float = 3.72           # m/s² — NASA Mars Fact Sheet
MARS_SURFACE_TEMP_C: float = -60.0   # °C — NASA Mars Fact Sheet
ENTRY_PEAK_TEMP_C: float = 1_600.0   # °C — NASA JPL MEDLI (2012)
THERMAL_DECAY_LAMBDA: float = 0.008  # 1/s — SIMULATED (MSL thermal profile shape)

# -- Fuel consumption models --
DRAG_COEFFICIENT_K: float = 0.45            # SIMULATED — F(v)=k·v², NASA Mars Atmosphere Model (GRC)
FUEL_BURN_RATE_PCT_PER_S: float = 0.05      # %/s — SIMULATED (MSL powered descent ~30 s)
POWERED_DESCENT_INITIAL_FUEL_PCT: float = 100.0

HOURS_TO_MINUTES: float = 60.0

CRITICALITY_TO_ALERT_SEVERITY: Dict[Criticality, AlertSeverity] = {
    Criticality.VITAL:   AlertSeverity.CRITICAL,
    Criticality.HIGH:    AlertSeverity.HIGH,
    Criticality.MEDIUM:  AlertSeverity.MEDIUM,
    Criticality.LOW:     AlertSeverity.LOW,
}

ALERT_SEVERITY_ORDER: Dict[AlertSeverity, int] = {
    AlertSeverity.CRITICAL: 0,
    AlertSeverity.HIGH:     1,
    AlertSeverity.MEDIUM:   2,
    AlertSeverity.LOW:      3,
}

SEPARATOR: str = "=" * 62
