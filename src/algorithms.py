from __future__ import annotations

from typing import Dict, List, Optional

from .enums import Criticality
from .models import LandingModule


def sort_by_priority(modules: List[LandingModule]) -> List[LandingModule]:
    """Insertion Sort — stable, zero auxiliary memory. O(n²), n=7."""
    result = list(modules)
    for i in range(1, len(result)):
        current = result[i]
        j = i - 1
        while j >= 0 and result[j].landing_priority > current.landing_priority:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result


def sort_by_fuel_ascending(modules: List[LandingModule]) -> List[LandingModule]:
    """Selection Sort — minimal swaps. O(n²), O(n) swaps."""
    result = list(modules)
    n = len(result)
    for i in range(n):
        min_index = i
        for j in range(i + 1, n):
            if result[j].fuel_pct < result[min_index].fuel_pct:
                min_index = j
        result[i], result[min_index] = result[min_index], result[i]
    return result


def search_by_criticality(
    criticality_index: Dict[Criticality, List[LandingModule]],
    criticality: Criticality,
) -> List[LandingModule]:
    """O(1) — pre-built hash index lookup by criticality group."""
    return criticality_index.get(criticality, [])


def search_by_orbit_arrival_window(
    modules: List[LandingModule],
    reference_arrival_h: float,
    window_h: float,
) -> List[LandingModule]:
    """Linear search for zone conflict detection. O(n)."""
    return [m for m in modules if abs(m.orbit_arrival_h - reference_arrival_h) <= window_h]


def binary_search_by_priority(
    sorted_modules: List[LandingModule],
    target_priority: int,
) -> Optional[LandingModule]:
    """Binary Search — requires list sorted by priority. O(log n)."""
    low, high = 0, len(sorted_modules) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_priority = sorted_modules[mid].landing_priority
        if mid_priority == target_priority:
            return sorted_modules[mid]
        elif mid_priority < target_priority:
            low = mid + 1
        else:
            high = mid - 1
    return None


def build_module_index(modules: List[LandingModule]) -> Dict[str, LandingModule]:
    """O(n) build → O(1) lookups. Hash map keyed by module_id."""
    return {m.module_id: m for m in modules}


def lookup_by_id(
    module_index: Dict[str, LandingModule],
    module_id: str,
) -> Optional[LandingModule]:
    """O(1) — pre-built hash index lookup by module_id."""
    return module_index.get(module_id)


def build_criticality_index(modules: List[LandingModule]) -> Dict[Criticality, List[LandingModule]]:
    """O(n) build → O(1) group lookups. Hash map keyed by Criticality."""
    index: Dict[Criticality, List[LandingModule]] = {}
    for m in modules:
        index.setdefault(m.criticality, []).append(m)
    return index
