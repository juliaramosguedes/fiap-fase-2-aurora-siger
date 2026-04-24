# Thresholds Reference — Aurora Siger MGPEB

> Safety thresholds for landing authorization logic.
> All constants defined here are the single source of truth —
> referenced in `landing_manager.py` and in the boolean logic diagrams.
> Values marked as SIMULATED are order-of-magnitude estimates with declared justification.

---

## Boolean Authorization Rule

```
LANDING_AUTHORIZED =
    ALTITUDE_OK
    AND FUEL_OK
    AND THERMAL_OK
    AND NOT SENSOR_ERROR
    AND LANDING_ZONE_CLEAR
```

Each variable is derived from a threshold defined below.

---

## ALTITUDE_OK

**Condition:** `current_altitude_m <= RETRO_IGNITION_ALTITUDE_M`
**Threshold:** `RETRO_IGNITION_ALTITUDE_M = 1_500` m

**Source:** NASA JPL — Mars Science Laboratory EDL (Entry, Descent and Landing).
Curiosity powered descent initiation occurred at approximately 1.6 km altitude.
Perseverance used a similar threshold in its EDL sequence.

> "Powered descent initiation occurred at approximately 1,600 meters above the Martian surface."
> — NASA JPL, MSL EDL Overview, 2012.

**Justification:** Below 1,500 m, the Martian atmosphere provides enough aerodynamic resistance for retrorockets to operate efficiently without excessive propellant expenditure. Above this altitude, aeroshell and parachute are the primary deceleration mechanism.

**Reference:** NASA JPL. *Mars Science Laboratory: EDL Overview*. 2012.
https://mars.nasa.gov/msl/mission/timeline/edl/

---

## FUEL_OK

**Condition:** `fuel_pct >= FUEL_MIN_PCT`
**Threshold:** `FUEL_MIN_PCT = 60.0` %

**Source:** ESA Advanced Concepts Team — propellant margin for EDL on Mars.
Analogous to the energy threshold applied in Aurora Siger Phase 1 (`ENERGY_MIN_PCT = 60.0%`, ESA Advanced Concepts Team).

**Justification:** Below 60% fuel, there is insufficient margin for trajectory correction in case of obstacle detection during final approach. Modules LOG-01 (55%) and MIN-01 (48%) fall below this threshold and are routed to the alert queue.

**Reference:** ESA Advanced Concepts Team. *Mars EDL Propellant Margins*. ESA, 2021.

---

## THERMAL_OK

**Condition:** `fuselage_temperature_c <= THERMAL_MAX_C`
**Threshold:** `THERMAL_MAX_C = 800` °C

**Source:** NASA JPL — Mars Science Laboratory EDL thermal analysis.
Peak heating during Curiosity EDL estimated between 600°C and 1,000°C depending on entry angle.
800°C is the conservative structural integrity limit for the thermal protection system.

> "Peak heating rates during entry reached approximately 215 W/cm², with peak temperatures exceeding 1,600°C on the heatshield outer surface — but structural limits constrained acceptable entry corridors."
> — Edquist, K. et al., *Aerothermodynamics for the Mars Science Laboratory Entry Capsule*, AIAA, 2009.

**Justification:** 800°C is applied as the structural limit for the module airframe (not the heatshield outer surface). Beyond this temperature, aluminum alloy structural members begin to lose load-bearing capacity (NASA materials standards).

**Reference:** Edquist, K. et al. *Aerothermodynamics for the Mars Science Laboratory Entry Capsule*. AIAA 2009-4117.
**Reference:** NASA JPL. *MSL Entry, Descent and Landing Instrumentation (MEDLI)*. 2012.

---

## SENSOR_ERROR

**Condition:** `NOT SENSOR_ERROR` — any navigation, altitude, or temperature sensor returning out-of-range value or null triggers this flag

**Source:** ESA Software Engineering Standard — fault detection in embedded systems.

**Justification:** A landing authorization issued on faulty sensor data is more dangerous than an aborted landing. Fail-fast on sensor error is a safety invariant — consistent with the Phase 1 architecture principle.

**Reference:** ESA. *ECSS-E-ST-70-11C: Space Engineering — Software Engineering*. ESA-ESTEC, 2009.
https://ecss.nl/standard/ecss-e-st-70-11c-space-engineering-software-engineering/

---

## LANDING_ZONE_CLEAR

**Condition:** landing zone unoccupied for at least `LANDING_ZONE_CLEARANCE_MINUTES = 30` minutes AND no dust storm detected

**Source:** NASA Mars landing site selection criteria — applied across MER, MSL, and Mars 2020 missions.

**Justification (operational):** 30-minute clearance window accounts for dust settling after a previous landing and safe distance verification between modules. Derived from Mars 2020 landing site proximity analysis (Golombek et al., 2012).

**Justification (ESG):** Landing zone selection also incorporates NASA Planetary Protection Office criteria — zones near potential subsurface water ice or geological features of astrobiological interest are flagged as restricted. This is an ESG constraint encoded as a boolean: `NOT IN_PROTECTED_ZONE`.

**Reference:** Golombek, M. et al. *Selection of the Mars Science Laboratory Landing Site*. Space Science Reviews, 2012.
https://doi.org/10.1007/s11214-012-9916-y
**Reference:** NASA Office of Planetary Protection. *Planetary Protection Policies*. 2020.
https://planetaryprotection.nasa.gov/

---

## Mathematical Models — Threshold Derivation

Four physical phenomena modeled in `landing_manager.py` produce real-time values
compared against the thresholds above.

### Model 1 — Altitude as a function of descent time (quadratic)

```
h(t) = h₀ - v₀·t - ½·g_mars·t²
```

- `h₀` = initial altitude at parachute deploy (~11,000 m — NASA JPL MSL)
- `v₀` = velocity at parachute deploy (~470 m/s — NASA JPL MSL)
- `g_mars = 3.72` m/s² — Martian surface gravity (NASA Mars Fact Sheet)
- Comparison: `h(t) <= RETRO_IGNITION_ALTITUDE_M` → `ALTITUDE_OK = True`

**Source:** NASA. *Mars Fact Sheet*. https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html
**Source:** NASA JPL. *MSL EDL Overview*. 2012.

---

### Model 2 — Fuel consumption as a function of velocity (quadratic)

```
F(v) = k · v²
```

- Aerodynamic drag force proportional to v² (standard fluid dynamics)
- `k = 0.45` — drag coefficient (SIMULATED — NASA Mars Atmosphere Model)
- Comparison: `remaining_fuel_pct >= FUEL_MIN_PCT` → `FUEL_OK = True`

**Source:** Anderson, J. *Introduction to Flight*. McGraw-Hill, 2016.
**Source:** NASA GRC. *Mars Atmosphere Model*. https://www.grc.nasa.gov/www/k-12/airplane/atmosmrm.html

---

### Model 3 — Fuselage temperature as a function of descent time (exponential)

```
T(t) = T_surface + (T_entry - T_surface) · e^(-λ·t)
```

- `T_entry = 1,600°C` — peak entry temperature (NASA JPL MEDLI, 2012)
- `T_surface = -60°C` — Martian mean surface temperature (NASA Mars Fact Sheet)
- `λ = 0.008 s⁻¹` — thermal decay constant (SIMULATED — MSL thermal profile)
- Comparison: `T(t) <= THERMAL_MAX_C` → `THERMAL_OK = True`

**Source:** Edquist, K. et al. *Aerothermodynamics for the MSL Entry Capsule*. AIAA 2009-4117.
**Source:** NASA JPL. *MEDLI*. 2012.

---

### Model 4 — Cumulative fuel consumed during powered descent (linear)

```
C(t) = C₀ - r·t
```

- `C₀ = 100%` — fuel level at powered descent initiation
- `r = 0.05 %/s` — constant burn rate (SIMULATED — MSL powered descent ~30 s)
- Models the constant-thrust phase where deceleration is controlled and
  velocity is approximately constant → fuel consumption is linear
- Comparison: `C(t) >= FUEL_MIN_PCT` → `FUEL_OK = True`

**Engineering connection:** Modules arriving with `fuel_pct < 60%` have already consumed
beyond their safety margin before powered descent begins. The linear model shows that even
a module starting at exactly 60% has a finite safe descent window before dropping below
the safety threshold.

**Source:** NASA JPL. *MSL EDL Overview (2012)* — powered descent duration and thrust profile.
**Source:** `FUEL_BURN_RATE_PCT_PER_S = 0.05 %/s` (SIMULATED)

---

## Dynamic Flag Computation

### sensor_error

Previously hardcoded `False` — now computed dynamically.

```
sensor_error = orbit_arrival_h > SENSOR_ERROR_ORBIT_THRESHOLD_H
```

- `SENSOR_ERROR_ORBIT_THRESHOLD_H = 4.0 h` (SIMULATED)
- Modules in orbit longer than 4 hours have elevated sensor failure probability
  due to cumulative cosmic ray dose during Mars transit.
- This is a simplified binary model. Real missions use probabilistic dose models.

**Source:** NASA Human Research Program — space radiation hazards.

---

### zone_clear

Previously hardcoded `True` — now computed dynamically.

```
zone_clear = all(
    |module.orbit_arrival_h - landed.orbit_arrival_h| * 60 >= LANDING_ZONE_CLEARANCE_MIN
    for landed in previously_landed_modules
)
```

- `LANDING_ZONE_CLEARANCE_MIN = 30 min`
- A zone is occupied if another module landed within the last 30 minutes.
- In the sequential landing architecture, each module checks against all
  previously landed modules before receiving zone clearance.

**Source:** Golombek, M. et al. *Selection of the MSL Landing Site*. Space Science Reviews, 2012.
