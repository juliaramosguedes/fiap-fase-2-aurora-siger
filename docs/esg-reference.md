# ESG Reference — Aurora Siger Colony

> Environmental, Social and Governance principles applied to the Aurora Siger colony mission.
> This document grounds the ESG reflection section of the technical report
> in primary sources — the same standard applied to all reference documents in this project.

---

## Framework

The ESG analysis follows the **Triple Bottom Line** framework (Elkington, 1994):
- **People** — social responsibility, crew wellbeing, equitable governance
- **Planet** — environmental impact on Mars, resource stewardship
- **Profit** — long-term viability and sustainability of the colony

Applied to a Mars colony, "profit" translates to **colony viability** — the capacity to sustain itself over time without exhausting the resources it depends on.

**Reference:** Elkington, J. *Cannibals with Forks: The Triple Bottom Line of 21st Century Business*. Capstone, 1997.
**Reference:** Elkington, J. *The Triple Bottom Line: Does It All Add Up?* Pearson, 2018.

---

## E — Environmental

### Landing Site Selection
The choice of landing zone is not only an operational decision — it is an environmental one.

NASA's Office of Planetary Protection classifies Mars surface regions by biological potential:
- **Category IVa:** regions where liquid water cannot exist — standard EDL zones
- **Category IVb:** regions with subsurface liquid water potential — restricted access
- **Category IVc:** special regions with highest astrobiological interest — exclusion zones

The `LANDING_ZONE_CLEAR` boolean in MGPEB encodes `NOT IN_PROTECTED_ZONE` as a hard constraint — not a recommendation. Landing in a protected zone is treated as a sensor error: the system will not authorize it.

**Reference:** NASA Office of Planetary Protection. *Planetary Protection Policies and Practices*. 2020.
https://planetaryprotection.nasa.gov/
**Reference:** COSPAR. *Planetary Protection Policy*. Committee on Space Research, 2020.
https://cosparhq.cnes.fr/scientific-structure/panels/panel-on-planetary-protection-ppp/

### Resource Management
Mars resources are finite and non-replenishable on human timescales:
- **Water ice:** present at poles and mid-latitudes (NASA MRO, 2008) — critical for life support and fuel production
- **Solar energy:** 43% of Earth's solar irradiance at Mars (NASA Mars Fact Sheet) — primary power source
- **Regolith minerals:** iron oxide, perchlorates, basaltic rock — ISRU feedstock

The landing priority sequence encodes environmental stewardship:
MIN-01 (ISRU mining) lands **last** — priority 7 — because extraction without established infrastructure
leads to uncontrolled resource depletion. This is a deliberate ESG constraint in the module priority order.

**Reference:** NASA Mars Reconnaissance Orbiter. *Water Ice on Mars*. 2008.
https://www.nasa.gov/mission_pages/MRO/
**Reference:** NASA. *Mars Fact Sheet*. https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html

---

## S — Social

### Crew Wellbeing and Medical Priority
MED-01 (Medical Support) lands fourth — before science (SCI-01) and logistics (LOG-01).
This is not an arbitrary order: it encodes the value that **crew health takes precedence over mission productivity**.

NASA's Human Research Program identifies 5 hazards for long-duration spaceflight:
space and terrestrial weather, isolation and confinement, distance from Earth, gravity fields, and hostile environments.
All 5 are present in a Mars colony scenario. Medical infrastructure is not optional — it is survival infrastructure.

**Reference:** NASA Human Research Program. *Human Research Roadmap — The 5 Hazards*.
https://humanresearchroadmap.nasa.gov/

### Governance and Transparency
The MGPEB system makes autonomous decisions — but who defines the thresholds?

`FUEL_MIN_PCT = 60.0` is not a fact of nature. It is a value choice: a judgment that below 60% fuel,
the risk to the module and crew outweighs the operational benefit of attempting the landing.
This choice is documented, sourced, and revisable — which is precisely what the ESA ECSS standard requires
of safety-critical embedded systems.

ISO 26000 (ABNT, 2010) establishes **accountability** as a central principle of social responsibility.
In MGPEB, accountability is implemented as:
- All thresholds defined as named constants with inline source comments
- All SIMULATED values explicitly marked with justification
- Alert queue requires human authorization override — the system cannot bypass it autonomously
- Decision logic is pure and individually auditable per function

**Reference:** ABNT. *ISO 26000: Diretrizes sobre Responsabilidade Social*. ABNT, 2010.
**Reference:** ESA. *ECSS-E-ST-70-11C: Software Engineering*. ESA-ESTEC, 2009.

---

## G — Governance

### Algorithmic Decisions and Human Override
The MGPEB authorization logic is **advisory by design for alert cases**.

Nominal modules (fuel >= 60%, all sensors OK, zone clear) are authorized automatically.
Alert modules (fuel < 60% or sensor anomaly) require **explicit human override** before landing clearance.
This architecture reflects a deliberate governance principle:
automated systems reduce margin for error in routine operations,
but human judgment is mandatory when operating outside nominal parameters.

This is consistent with NASA's Autonomous Systems principles:
> "Autonomous systems should support human decision-making, not replace it in high-stakes contexts."
> — NASA Autonomous Systems, Armstrong Flight Research Center.

**Reference:** NASA. *Autonomous Systems*. Armstrong Flight Research Center.
https://www.nasa.gov/centers-and-facilities/armstrong/autonomous-systems/

### Long-Term Colony Governance
The ESG framework applied here anticipates questions the colony will face beyond the landing phase:

1. **Who decides threshold revisions?** — the colony needs a governance structure for updating safety parameters as knowledge of the Martian environment improves
2. **How are resources allocated?** — water, energy, and regolith access must be governed equitably among crew members and mission objectives
3. **What is the colony's relationship with Earth governance?** — jurisdiction, intellectual property of ISRU discoveries, and communication latency all create novel governance challenges with no established precedent

These questions are not resolved by MGPEB — but MGPEB is designed to make them answerable:
auditable constants, documented sources, and human override requirements are the governance infrastructure
that future colony decision-making will build on.

**Reference:** Zubrin, R. *The Case for Mars*. Simon & Schuster, 1996. — Chapter on colony governance
**Reference:** Elkington, J. *The Triple Bottom Line*. Pearson, 2018.

---

## ESG Tension: Efficiency vs. Sustainability

The MGPEB system optimizes for **landing efficiency** — fastest safe landing sequence for the highest-priority modules.
But efficiency and sustainability are not always aligned:

- Faster landings consume more fuel (higher velocity → higher drag → higher consumption per `F(v) = k·v²`)
- Denser landing schedules increase dust disturbance and zone contamination risk
- Prioritizing VITAL modules first means LSS-01 and PWR-01 consume the most favorable atmospheric windows

This tension is not resolved — it is declared. MGPEB documents it so future iterations of the system
can incorporate sustainability metrics into the priority algorithm, not just survival metrics.

---

## Summary Table

| ESG Dimension | MGPEB Implementation | Source |
|---|---|---|
| Environmental — zone protection | `NOT IN_PROTECTED_ZONE` as hard boolean constraint | NASA Planetary Protection, 2020 |
| Environmental — resource stewardship | MIN-01 priority 7 — ISRU last | NASA ISRU Roadmap, 2023 |
| Social — crew health | MED-01 priority 4 — before science and logistics | NASA HRP |
| Social — transparency | All thresholds sourced and documented | ISO 26000 / ECSS |
| Governance — human override | Alert queue requires manual authorization | NASA Autonomous Systems |
| Governance — auditability | Pure functions, named constants, SIMULATED markers | ESA ECSS-E-ST-70-11C |
