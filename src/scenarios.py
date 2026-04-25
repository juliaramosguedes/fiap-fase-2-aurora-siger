from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from .enums import Criticality


@dataclass
class LandingModuleConfig:
    module_id: str
    name: str
    landing_priority: int
    fuel_pct: float
    mass_kg: float
    criticality: Criticality
    orbit_arrival_h: float   # cumulative window position — used for zone_clear spacing
    time_in_orbit_h: float   # radiation exposure time — used for sensor_error check


_MODULE_NAME_POOL = [
    "Life Support System",    "Power Generation",       "Inflatable Habitat",
    "Medical Support",        "Science Laboratory",     "Logistics and Supplies",
    "ISRU Mining",            "Communications Hub",     "Thermal Control",
    "Navigation Array",       "Water Extraction",       "Greenhouse Module",
    "Repair Workshop",        "Data Center",            "Emergency Shelter",
    "Fuel Production",        "Solar Array",            "Rover Depot",
    "Airlock System",         "Command Center",
]

_CRITICALITY_POOL = list(Criticality)


def default_scenario() -> List[LandingModuleConfig]:
    return [
        LandingModuleConfig("LSS-01", "Life Support System",    1, 78.0,  4_200.0, Criticality.VITAL,   0.5, 0.5),
        LandingModuleConfig("PWR-01", "Power Generation",       2, 85.0,  6_800.0, Criticality.VITAL,   1.0, 1.0),
        LandingModuleConfig("HAB-01", "Inflatable Habitat",     3, 62.0, 12_400.0, Criticality.HIGH,    2.0, 2.0),
        LandingModuleConfig("MED-01", "Medical Support",        4, 71.0,  3_100.0, Criticality.HIGH,    2.5, 2.5),
        LandingModuleConfig("SCI-01", "Science Laboratory",     5, 90.0,  5_600.0, Criticality.MEDIUM,  4.0, 4.0),
        LandingModuleConfig("LOG-01", "Logistics and Supplies", 6, 55.0, 18_200.0, Criticality.MEDIUM,  5.5, 5.5),  # SIMULATED — fuel + sensor anomaly
        LandingModuleConfig("MIN-01", "ISRU Mining",            7, 48.0,  9_900.0, Criticality.LOW,     7.0, 7.0),  # SIMULATED — fuel + sensor anomaly
    ]


def random_scenario(
    modules: int = 7,
    anomaly_pct: float = 0.0,
    seed: Optional[int] = None,
) -> List[LandingModuleConfig]:
    """Procedural generator — modules with item-level anomaly_pct probability of anomalies."""
    rng = random.Random(seed)
    configs: List[LandingModuleConfig] = []
    arrival_h = 0.5
    for i in range(modules):
        name = _MODULE_NAME_POOL[i % len(_MODULE_NAME_POOL)]
        criticality    = rng.choice(_CRITICALITY_POOL)
        fuel_anomaly   = rng.random() < anomaly_pct
        sensor_anomaly = rng.random() < anomaly_pct
        fuel_pct        = round(rng.uniform(30.0, 59.0), 1) if fuel_anomaly   else round(rng.uniform(60.0, 95.0), 1)
        time_in_orbit_h = round(rng.uniform(4.1, 8.0), 2)   if sensor_anomaly else round(rng.uniform(0.5, 3.5), 2)
        orbit_bump      = round(rng.uniform(0.5, 1.5), 2)
        mass_kg         = round(rng.uniform(2_000.0, 20_000.0), 0)
        configs.append(LandingModuleConfig(
            module_id=f"MOD-{i + 1:02d}",
            name=name,
            landing_priority=i + 1,
            fuel_pct=fuel_pct,
            mass_kg=mass_kg,
            criticality=criticality,
            orbit_arrival_h=round(arrival_h, 2),
            time_in_orbit_h=time_in_orbit_h,
        ))
        arrival_h += orbit_bump
    return configs
