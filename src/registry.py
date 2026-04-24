from __future__ import annotations

from dataclasses import asdict
from typing import List

from .authorization import check_sensor_error, check_zone_clear
from .models import LandingModule
from .scenarios import LandingModuleConfig


def build_modules(configs: List[LandingModuleConfig]) -> List[LandingModule]:
    modules: List[LandingModule] = []
    for config in configs:
        sensor_error = check_sensor_error(config.orbit_arrival_h)
        temp = LandingModule(**asdict(config), sensor_error=sensor_error, zone_clear=True)
        zone_clear = check_zone_clear(temp, modules)
        modules.append(LandingModule(**asdict(config), sensor_error=sensor_error, zone_clear=zone_clear))
    return modules
