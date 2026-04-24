from __future__ import annotations

from enum import Enum


class Criticality(str, Enum):
    VITAL  = "VITAL"
    HIGH   = "ALTA"
    MEDIUM = "MÉDIA"
    LOW    = "BAIXA"

    def __str__(self) -> str:
        return self.value


class AlertSeverity(str, Enum):
    CRITICAL = "CRÍTICO"
    HIGH     = "ALTO"
    MEDIUM   = "MÉDIO"
    LOW      = "BAIXO"

    def __str__(self) -> str:
        return self.value


class Decision(str, Enum):
    AUTHORIZED = "POUSO AUTORIZADO"
    DENIED     = "POUSO NEGADO"
    ALERT      = "AGUARDANDO AUTORIZAÇÃO MANUAL"

    def __str__(self) -> str:
        return self.value


class EventType(str, Enum):
    # Reversible control actions → Event Stack
    AUTHORIZATION_GRANTED = "AUTHORIZATION_GRANTED"
    LANDING_INITIATED     = "LANDING_INITIATED"
    # Irreversible facts → Audit Log
    LANDING_COMPLETED = "LANDING_COMPLETED"
    LANDING_DENIED    = "LANDING_DENIED"
    ALERT_GENERATED   = "ALERT_GENERATED"

    def __str__(self) -> str:
        return self.value
