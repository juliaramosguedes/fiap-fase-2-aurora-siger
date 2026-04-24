# Landing Modules Reference — Aurora Siger

> Attributes and priorities for the 7 landing modules of the Aurora Siger colony mission.
> All values are grounded in real mission data from NASA, ESA, and SpaceX documentation.
> Values marked as SIMULATED are order-of-magnitude estimates with declared justification.

---

## Module Definitions

### LSS-01 — Life Support System
| Attribute | Value | Source |
|---|---|---|
| Priority | 1 (VITAL) | NASA Human Research Program — life support is prerequisite for all crew operations |
| Fuel | 78% | SIMULATED — margin based on EDL propellant budget (NASA JPL, 2012) |
| Mass | 4,200 kg | SIMULATED — based on ISS Environmental Control and Life Support System (ECLSS) segment mass |
| Criticality | VITAL | NASA HRP — without life support, no other module can be operated by crew |
| Orbit arrival | 0.5 h | First module released from mothership — immediate priority |

**Reference:** NASA Human Research Program. *Life Support Systems*. https://www.nasa.gov/hrp

---

### PWR-01 — Power Generation
| Attribute | Value | Source |
|---|---|---|
| Priority | 2 (VITAL) | NASA/DoE Kilopower Project — surface power is prerequisite for all systems |
| Fuel | 85% | SIMULATED — higher reserve justified by critical role in base startup |
| Mass | 6,800 kg | SIMULATED — based on Kilopower 10kWe reactor system mass estimate |
| Criticality | VITAL | Kilopower (2018) — 10 kWe fission system designed for Mars surface operations |
| Orbit arrival | 1.0 h | Second module released — must land before habitat inflation |

**Reference:** Gibson, M. et al. *NASA's Kilopower Reactor Development and the Path to Higher Power Missions*. NASA/DoE, 2018. https://www.nasa.gov/kilopower

---

### HAB-01 — Inflatable Habitat
| Attribute | Value | Source |
|---|---|---|
| Priority | 3 (HIGH) | Lockheed Martin Mars Base Camp (2016) — crew shelter third priority after life support and power |
| Fuel | 62% | SIMULATED — heavier module requires more propellant; near FUEL_MIN_PCT threshold |
| Mass | 12,400 kg | SIMULATED — based on Bigelow BEAM module (1,400 kg) scaled for Mars surface habitat |
| Criticality | HIGH | Mars Base Camp concept — primary crew shelter |
| Orbit arrival | 2.0 h | Third release — power must be active before habitat systems can initialize |

**Reference:** Lockheed Martin. *Mars Base Camp*. 2016. https://www.lockheedmartin.com/mars
**Reference:** Bigelow Aerospace / NASA. *BEAM (Bigelow Expandable Activity Module)*. ISS Module, 2016.

---

### MED-01 — Medical Support
| Attribute | Value | Source |
|---|---|---|
| Priority | 4 (HIGH) | NASA HRP — medical emergencies have critical time window; ranked above science |
| Fuel | 71% | SIMULATED — standard EDL margin |
| Mass | 3,100 kg | SIMULATED — based on ISS medical equipment manifest and surgical suite mass |
| Criticality | HIGH | NASA Human Research Program — medical capability required before extended surface ops |
| Orbit arrival | 2.5 h | Fourth release — crew may need medical support during habitat setup |

**Reference:** NASA Human Research Program. *Human Research Roadmap*. https://humanresearchroadmap.nasa.gov

---

### SCI-01 — Science Laboratory
| Attribute | Value | Source |
|---|---|---|
| Priority | 5 (MEDIUM) | Zubrin, R. *The Case for Mars* (1996) — science module lands after survival infrastructure |
| Fuel | 90% | SIMULATED — lighter module, full fuel reserve |
| Mass | 5,600 kg | SIMULATED — based on Mars Direct ERV science payload mass (Zubrin, 1996) |
| Criticality | MEDIUM | Science operations begin only after colony is stabilized |
| Orbit arrival | 4.0 h | Fifth release |

**Reference:** Zubrin, R.; Wagner, R. *The Case for Mars*. Simon & Schuster, 1996.

---

### LOG-01 — Logistics and Supplies
| Attribute | Value | Source |
|---|---|---|
| Priority | 6 (MEDIUM) | SpaceX Starship cargo configuration — logistics lands after crew survival modules |
| Fuel | 55% | SIMULATED — **below FUEL_MIN_PCT (60%) — triggers ALERT status** |
| Mass | 18,200 kg | SIMULATED — based on SpaceX Starship payload capacity to Mars surface (~100t scaled) |
| Criticality | MEDIUM | SpaceX Mars architecture — cargo delivery for colony sustenance |
| Orbit arrival | 5.5 h | Sixth release — heaviest module, last high-priority landing |

**Reference:** SpaceX. *Starship*. https://www.spacex.com/vehicles/starship/
**Note:** LOG-01 fuel at 55% is intentionally below threshold to demonstrate alert queue behavior in MGPEB.

---

### MIN-01 — ISRU Mining
| Attribute | Value | Source |
|---|---|---|
| Priority | 7 (LOW) | NASA ISRU Roadmap (2023) — in-situ resource utilization begins only after base is established |
| Fuel | 48% | SIMULATED — **below FUEL_MIN_PCT (60%) — triggers ALERT status** |
| Mass | 9,900 kg | SIMULATED — based on MOXIE scaling for full ISRU plant (NASA, 2021) |
| Criticality | LOW | MOXIE demonstrated oxygen production on Mars (Perseverance, 2021) — future expansion |
| Orbit arrival | 7.0 h | Last release — mining operations are long-term colony capability |

**Reference:** NASA. *MOXIE (Mars Oxygen In-Situ Resource Utilization Experiment)*. Perseverance Rover, 2021. https://mars.nasa.gov/mars2020/spacecraft/instruments/moxie/
**Reference:** NASA. *In-Situ Resource Utilization*. NASA ISRU Roadmap, 2023. https://www.nasa.gov/isru
**Note:** MIN-01 fuel at 48% is intentionally below threshold to demonstrate alert queue behavior in MGPEB.

---

## Priority Rationale Summary

The landing sequence follows the **survival-first principle** established by NASA's Human Research Program and the Mars Direct architecture (Zubrin, 1996):

1. **VITAL modules first** — without life support (LSS-01) and power (PWR-01), no other module can operate
2. **Crew safety second** — habitat (HAB-01) and medical (MED-01) before any science or logistics
3. **Science and logistics third** — colony must be stable before research begins
4. **ISRU last** — long-term capability, not immediate survival

This priority order is encoded as the `landing_priority` attribute and drives the sorting algorithm in `landing_manager.py`.

---

## Alert Modules

LOG-01 (55%) and MIN-01 (48%) land with fuel below `FUEL_MIN_PCT = 60.0%`.
These modules are routed to the **alert queue** and require manual authorization override before landing clearance is granted.

This behavior is intentional — it demonstrates the MGPEB alert handling logic and the fuel threshold enforcement defined in `thresholds-reference.md`.
