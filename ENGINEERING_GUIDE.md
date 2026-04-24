# Guia de Engenharia — Aurora Siger MGPEB

> Walkthrough do pacote `src/` — do panorama geral até as linhas individuais de código.
> Destinado a engenheiros lendo esta base de código pela primeira vez. Leia o README antes.

---

## Índice

1. [Panorama Geral](#1-panorama-geral)
2. [Arquitetura em Camadas](#2-arquitetura-em-camadas)
3. [Modelo de Execução](#3-modelo-de-execução)
4. [src/enums.py — Tipos de domínio](#4-srcenumspy--tipos-de-domínio)
5. [src/constants.py — Fonte única da verdade numérica](#5-srcconstantspy--fonte-única-da-verdade-numérica)
6. [src/models.py — Dataclasses imutáveis](#6-srcmodelspy--dataclasses-imutáveis)
7. [src/scenarios.py — Configuração de missão](#7-srcscenariopspy--configuração-de-missão)
8. [src/physics.py — Modelos matemáticos do EDL](#8-srcphysicspy--modelos-matemáticos-do-edl)
9. [src/authorization.py — Lógica de autorização e flags dinâmicos](#9-srcauthorizationpy--lógica-de-autorização-e-flags-dinâmicos)
10. [src/structures.py — Operações sobre estruturas de dados](#10-srcstructurespy--operações-sobre-estruturas-de-dados)
11. [src/algorithms.py — Busca e ordenação](#11-srcalgorithmspy--busca-e-ordenação)
12. [src/display.py — Funções de exibição](#12-srcdisplaypy--funções-de-exibição)
13. [src/registry.py — Construção de módulos](#13-srcregistrypy--construção-de-módulos)
14. [src/simulation.py — Orquestração](#14-srcsimulationpy--orquestração)
15. [Padrões recorrentes](#15-padrões-recorrentes)
16. [Fluxo de dados completo](#16-fluxo-de-dados-completo)
17. [Glossário](#17-glossário)

---

## 1. Panorama Geral

**Em uma frase:** Este sistema simula a sequência de pouso dos módulos da colônia Aurora Siger em Marte — decidindo quem pousa, quando, e quem aguarda autorização humana.

```
Cenário de missão (default ou aleatório)
        ↓
7 módulos com flags dinâmicos computados (sensor_error, zone_clear)
        ↓
Fila de pouso (Insertion Sort por prioridade)
        ↓
Para cada módulo — telemetria calculada via modelos físicos:
  h(t) = h₀ - v₀·t - ½·g·t²               → ALTITUDE_OK
  T(t) = T_sup + (T_ent-T_sup)·e^(-λt)    → THERMAL_OK
        ↓
Regra booleana de autorização:
  ALTITUDE_OK AND FUEL_OK AND THERMAL_OK AND NOT SENSOR_ERROR AND ZONE_CLEAR
        ↓
  AUTORIZADO → Lista de pousados + Event Stack + Audit Log
  ALERTA     → Alert Queue (FIFO) → Alert List (por criticidade) + Audit Log
  NEGADO     → Lista de espera + Audit Log
        ↓
Relatório final
```

---

## 2. Arquitetura em Camadas

O pacote `src/` segue uma arquitetura em camadas. Cada camada depende apenas das camadas abaixo — nunca do contrário.

```
Camada 6 — Orquestração    simulation.py → main(), simulate_landing_sequence()
                                  │
Camada 5 — Exibição        display.py → display_*()
                                  │
Camada 4 — Computação      physics.py, authorization.py, structures.py, algorithms.py
                                  │
Camada 3 — Configuração    scenarios.py → LandingModuleConfig, default_scenario(), random_scenario()
                                  │
Camada 2 — Tipos de dado   models.py → dataclasses frozen
                                  │
Camada 1 — Fundação        enums.py → tipos de domínio | constants.py → limiares numéricos
```

Nenhum ciclo. `enums.py` e `physics.py` ficam na base — sem dependências internas entre módulos `src/`.

**Por que isso importa:** `constants.py` é a única fonte de verdade numérica. `FUEL_MIN_PCT = 60.0` é definido uma vez e reutilizado em `authorization.py`, `display.py` e `simulation.py`. Mudar o threshold em um lugar propaga para o sistema inteiro.

---

## 3. Modelo de Execução

```
landing_manager.py
    └── from src.simulation import main
              │
              ▼
         build_modules(scenario)       ← registry.py + authorization.py
              │
         build_module_index()          ← O(n) build, O(1) lookups
         build_criticality_index()     ← O(n) build, O(1) group lookups
              │
         display_header()
         display_module_queue()
         display_mathematical_models()
         display_search_results()
              │
         simulate_landing_sequence()   ← o loop principal
              │
         display_alert_queue_and_list()
         display_event_stack()
         display_audit_log()
         display_final_report()
```

O ponto de entrada é `landing_manager.py` — menos de 10 linhas, só importa e chama `main()`. Toda a lógica vive em `src/`.

---

## 4. src/enums.py — Tipos de domínio

Quatro enums com mixin `str`: `Criticality`, `AlertSeverity`, `Decision`, `EventType`.

O mixin `str` garante que cada valor IS uma string — `Criticality.VITAL == "VITAL"` é `True`. Isso preserva compatibilidade com dicts, JSON e f-strings sem conversão explícita. `__str__` é sobrescrito em cada classe para garantir que `f"{Criticality.VITAL}"` produza `"VITAL"` no Python 3.9+ (sem o override, Python < 3.11 retorna `"Criticality.VITAL"`).

```python
class Criticality(str, Enum):
    VITAL  = "VITAL"
    HIGH   = "ALTA"
    MEDIUM = "MÉDIA"
    LOW    = "BAIXA"

    def __str__(self) -> str:
        return self.value
```

`EventType` concentra todos os 5 tipos de evento. Os dois primeiros são ações reversíveis (Event Stack); os três últimos são fatos irreversíveis (Audit Log):

```python
class EventType(str, Enum):
    # Reversible control actions → Event Stack
    AUTHORIZATION_GRANTED = "AUTHORIZATION_GRANTED"
    LANDING_INITIATED     = "LANDING_INITIATED"
    # Irreversible facts → Audit Log
    LANDING_COMPLETED = "LANDING_COMPLETED"
    LANDING_DENIED    = "LANDING_DENIED"
    ALERT_GENERATED   = "ALERT_GENERATED"
```

A distinção `LANDING_COMPLETED` → Audit Log (não Event Stack) é intencional: pouso concluído é um fato físico. O módulo está no solo — colocá-lo na pilha implicaria que pode ser desfeito, o que é falso.

---

## 5. src/constants.py — Fonte única da verdade numérica

Apenas limiares numéricos e constantes físicas. Strings de decisão e tipos de evento foram migrados para `enums.py`. Os dois dicionários de mapeamento usam chaves e valores tipados com enums — erros de typo viram erros de tipo em análise estática.

| Constante | Valor | Fonte |
|---|---|---|
| `FUEL_MIN_PCT` | 60.0 % | ESA Advanced Concepts Team (2021) |
| `THERMAL_MAX_C` | 800.0 °C | Edquist et al., AIAA 2009-4117 |
| `RETRO_IGNITION_ALTITUDE_M` | 1 500 m | NASA JPL MSL EDL Overview (2012) |
| `LANDING_ZONE_CLEARANCE_MIN` | 30 min | Golombek et al., Space Sci. Rev. (2012) |
| `SENSOR_ERROR_ORBIT_THRESHOLD_H` | 4.0 h | SIMULATED — NASA HRP |
| `MARS_GRAVITY` | 3.72 m/s² | NASA Mars Fact Sheet |
| `MARS_SURFACE_TEMP_C` | -60.0 °C | NASA Mars Fact Sheet |
| `ENTRY_PEAK_TEMP_C` | 1 600.0 °C | NASA JPL MEDLI (2012) |
| `THERMAL_DECAY_LAMBDA` | 0.008 s⁻¹ | SIMULATED — MSL thermal profile |
| `DRAG_COEFFICIENT_K` | 0.45 | SIMULATED — NASA Mars Atmosphere Model (GRC) |

Consulte `docs/thresholds-reference.md` para justificativas completas.

---

## 6. src/models.py — Dataclasses imutáveis

Seis `@dataclass(frozen=True)`. `frozen=True` gera `__hash__` automaticamente e proíbe atribuição após criação — cada instância é um snapshot de estado que não pode ser mutado. Campos tipados com os enums correspondentes.

| Classe | Papel | Campos chave |
|---|---|---|
| `LandingModule` | Estado do módulo na chegada em órbita | `criticality: Criticality`, `sensor_error`, `zone_clear` |
| `DescentTelemetry` | Snapshot de telemetria durante descida | `current_altitude_m`, `fuselage_temperature_c` |
| `AuthorizationResult` | Resultado das 5 verificações booleanas | `decision: Decision` |
| `LandingEvent` | Ação reversível de controle | `event_type: EventType`, `module_criticality: Criticality` |
| `AuditEntry` | Fato físico ou evento irreversível | `event_type: EventType` |
| `Alert` | Alerta que requer override humano | `severity: AlertSeverity` |

`LandingModule` tem dois campos computados — `sensor_error` e `zone_clear` — que não são hardcoded. São calculados por `check_sensor_error()` e `check_zone_clear()` em `authorization.py` antes de construir o objeto.

---

## 7. src/scenarios.py — Configuração de missão

`LandingModuleConfig` é um `@dataclass` mutável (não frozen) — é input de configuração, não snapshot de estado. Essa distinção é intencional: configuração pode ser alterada antes de ser processada; estado computado não.

### `default_scenario()`

Retorna os 7 módulos canônicos da missão. `LOG-01` (55%) e `MIN-01` (48%) têm `fuel_pct < FUEL_MIN_PCT` por design (`# SIMULATED`) — exercitam o caminho de alerta e o override humano obrigatório.

| Módulo | Combustível | Órbita | sensor_error esperado | Resultado |
|---|---|---|---|---|
| LSS-01 | 78% | 0.5 h | False | ✔ Autorizado |
| PWR-01 | 85% | 1.0 h | False | ✔ Autorizado |
| HAB-01 | 62% | 2.0 h | False | ✔ Autorizado |
| MED-01 | 71% | 2.5 h | False | ✔ Autorizado |
| SCI-01 | 90% | 4.0 h | False | ✔ Autorizado |
| LOG-01 | **55%** | 5.5 h | **True** | ⚠ Alerta |
| MIN-01 | **48%** | 7.0 h | **True** | ⚠ Alerta |

### `random_scenario(n, anomaly_pct, seed)`

Gera `n` módulos proceduralmente. Cada módulo tem duas probabilidades independentes de anomalia, ambas controladas por `anomaly_pct`:

- **`fuel_anomaly`** — `fuel_pct` cai para 30–59% (abaixo do mínimo)
- **`sensor_anomaly`** — o incremento de `orbit_arrival_h` pula para 4.1–8.0h (acima do threshold de 4h), forçando `sensor_error=True`

O `orbit_bump` do módulo anômalo também serve de espaçamento para o próximo — acumula `orbit_arrival_h` naturalmente. IDs gerados como `MOD-01`..`MOD-n`; nomes ciclam por `_MODULE_NAME_POOL` (20 entradas) quando `n > 20`.

```python
from src.scenarios import random_scenario
from src.simulation import main

main(random_scenario(n=10, anomaly_pct=0.4, seed=42))
```

---

## 8. src/physics.py — Modelos matemáticos do EDL

Quatro funções puras modelando fenômenos físicos reais do EDL (Entry, Descent and Landing). Cada função tem uma fórmula, documentada na docstring de uma linha.

### `compute_altitude(initial_altitude_m, initial_velocity_ms, elapsed_time_s)`

```
h(t) = h₀ - v₀·t - ½·g_mars·t²
```

Modelo quadrático após abertura do paraquedas. `max(0.0, ...)` impede altitude negativa — o modelo não simula o pouso em si, apenas a descida. Com os parâmetros da simulação (t ≈ 210–245s), a altitude já é 0 m para todos os módulos — todos passam em `ALTITUDE_OK`.

### `compute_drag_force(velocity_ms)`

```
F(v) = k · v²
```

Força de arrasto proporcional ao quadrado da velocidade. Demonstra como velocidades hipersônicas (5 900 m/s) geram forças ordens de grandeza maiores que a fase final (100 m/s).

### `compute_fuselage_temperature(elapsed_time_s)`

```
T(t) = T_surface + (T_entry - T_surface) · e^(-λ·t)
```

Resfriamento exponencial desde o pico na entrada (`T_entry = 1 600°C`) até a superfície marciana (`T_surface = -60°C`). `λ = 0.008 s⁻¹` é SIMULATED com base no perfil térmico do MSL. Após ~210s, a temperatura está abaixo de 250°C — todos os módulos passam em `THERMAL_OK`.

### `compute_fuel_consumed_linear(elapsed_time_s)`

```
C(t) = C₀ - r·t
```

Consumo linear durante powered descent (thrust constante). Demonstra que módulos com `fuel_pct < 60%` já consumiram além da margem **antes** do powered descent — o problema é pré-existente, não causado pela descida em si.

---

## 9. src/authorization.py — Lógica de autorização e flags dinâmicos

Centraliza toda a lógica de decisão de pouso. Absorveu o antigo `flags.py` — os flags dinâmicos e as verificações de autorização vivem no mesmo módulo porque são dois lados da mesma moeda: computar o estado e verificar o estado.

### Flags dinâmicos

**`check_sensor_error(orbit_arrival_h)`**

```python
return orbit_arrival_h > SENSOR_ERROR_ORBIT_THRESHOLD_H  # 4.0 h
```

Modelo binário de exposição à radiação cósmica. Módulos em órbita por mais de 4h têm probabilidade elevada de falha de sensor por dose acumulada. Limiar SIMULATED — NASA Human Research Program.

**`check_zone_clear(module, landed_modules)`**

```python
if not landed_modules:
    return True
return all(
    abs(module.orbit_arrival_h - landed.orbit_arrival_h) * HOURS_TO_MINUTES >= LANDING_ZONE_CLEARANCE_MIN
    for landed in landed_modules
)
```

`all()` com generator expression curto-circuita na primeira colisão — sem loop explícito. Janela de 30 min por módulo já pousado.

### Cinco funções `check_*` de autorização

Cada condição é uma função pura de uma linha — testável individualmente (mandatório em sistemas de segurança crítica):

```python
def check_altitude(current_altitude_m):     return current_altitude_m <= RETRO_IGNITION_ALTITUDE_M
def check_fuel(fuel_pct):                   return fuel_pct >= FUEL_MIN_PCT
def check_thermal(fuselage_temperature_c):  return fuselage_temperature_c <= THERMAL_MAX_C
def check_sensor(sensor_error):             return not sensor_error
def check_zone(zone_clear):                 return zone_clear
```

### `evaluate_authorization(module, telemetry)`

```python
all_clear = all([altitude_ok, fuel_ok, thermal_ok, sensor_ok, zone_ok])
requires_human_override = not fuel_ok or not sensor_ok

decision_rules = [
    (all_clear,               Decision.AUTHORIZED),
    (requires_human_override, Decision.ALERT),
]
decision = next((d for condition, d in decision_rules if condition), Decision.DENIED)
```

**Strategy table em vez de `if/elif/else`** — adicionar um novo branch é inserir uma linha na lista. `Decision.DENIED` é o fallback explícito: fail-safe por design.

**Roteamento de alertas:**
- `NOT FUEL_OK` ou `sensor_error` → `ALERT` (override humano obrigatório — problema irrecuperável sem intervenção)
- `NOT THERMAL_OK` ou `NOT ZONE_CLEAR` → `DENIED` (tentar novamente — pode se resolver com o tempo)

---

## 10. src/structures.py — Operações sobre estruturas de dados

Implementa as sete estruturas lineares. Todas as operações são **puras** — retornam novas estruturas em vez de mutar as existentes.

### `build_landing_queue(modules)`

Chama `sort_by_priority()` e retorna um `deque`. O `deque` é FIFO: `popleft()` sempre consome o módulo de maior prioridade.

### `enqueue_alert(alert_queue, module, reason)`

```python
new_queue = deque(alert_queue)  # copia — não muta o original
new_queue.append(alert)
return new_queue
```

Copia antes de appendar. Todos os alertas entram por aqui; nenhum é perdido ou pulado.

### `flush_alert_queue_to_list(alert_queue)`

```python
return sorted(list(alert_queue), key=lambda a: ALERT_SEVERITY_ORDER[a.severity])
```

Drena a fila FIFO para uma lista ordenada por severidade. Alertas `CRÍTICO` aparecem primeiro independente da ordem de chegada. A fila é o canal de intake; a lista é a visão de trabalho do operador.

### `push_event(event_stack, event_type, module)`

```python
return event_stack + [event]
```

Retorna nova lista com o evento appended — imutável por design. O topo é sempre `[-1]`. Aceitável para n ≤ 14 eventos (2 por módulo × 7 módulos).

### `pop_event(event_stack)`

```python
return event_stack[-1], event_stack[:-1]
```

Retorna `(topo, pilha_sem_o_topo)`. Permite desfazer ações reversíveis de controle sem mutar a pilha original.

### `append_audit(audit_log, event_type, module_id, description)`

```python
return audit_log + [entry]
```

O Audit Log nunca é revertido. `LANDING_COMPLETED` vai aqui — não na Event Stack — porque pouso concluído é um fato físico irreversível.

---

## 11. src/algorithms.py — Busca e ordenação

| Função | Complexidade | Contexto |
|---|---|---|
| `sort_by_priority` | O(n²) | Insertion Sort — estável, zero memória auxiliar (RAD750) |
| `sort_by_fuel_ascending` | O(n²) | Selection Sort — mínimo de trocas para identificar módulos em risco |
| `build_module_index` | O(n) build | Dict `{module_id → LandingModule}` — construído uma vez em `main()` |
| `build_criticality_index` | O(n) build | Dict `{Criticality → [modules]}` — construído uma vez em `main()` |
| `lookup_by_id` | O(1) | Hash lookup por `module_id` — requer index pré-construído |
| `search_by_criticality` | O(1) | Hash lookup por grupo de criticidade — requer index pré-construído |
| `binary_search_by_priority` | O(log n) | Requer lista já ordenada pelo Insertion Sort |
| `search_by_orbit_arrival_window` | O(n) | Lista não ordenada por `orbit_arrival_h` — scan completo necessário |

Os índices `build_module_index` e `build_criticality_index` seguem o padrão "build once, query many" — análogo a índices de banco de dados. São construídos uma vez em `main()` e passados para baixo às funções de display.

**Por que Insertion Sort e não hash para a fila de pouso?** Sorting e indexação são operações distintas. Um hash dá O(1) para lookup por chave individual; não produz uma sequência ordenada. O `deque` FIFO precisa de uma lista completa em ordem de prioridade — o Insertion Sort é a ferramenta certa. Com n=7, O(n²) executa em microssegundos.

**Por que Selection Sort para combustível?** Minimiza trocas — O(n) trocas no pior caso vs. O(n²) do Insertion Sort. Útil quando identificar módulos críticos com menor movimentação de dados importa.

---

## 12. src/display.py — Funções de exibição

Funções de saída puras — nenhuma altera dados ou retorna valores. A separação calcular / exibir é absoluta: a lógica de computação vive em outros módulos; `display_*` recebe o resultado pronto e formata.

### `display_search_results(modules, criticality_index, module_index)`

Recebe os índices pré-construídos como parâmetro — não sabe como construí-los. Isso mantém a separação de responsabilidades: `main()` conhece o ciclo de vida dos índices; `display.py` apenas consome.

As referências de busca são derivadas dinamicamente:
- `ref_module = modules[0]` — primeiro módulo do cenário (qualquer cenário)
- `mid_priority = sorted[len // 2].landing_priority` — prioridade central, não hardcoded

Funciona corretamente com `default_scenario()` e `random_scenario()`.

---

## 13. src/registry.py — Construção de módulos

`build_modules(configs)` aceita `List[LandingModuleConfig]` — cenário injetado por `main()`. Retorna `List[LandingModule]` com flags dinâmicos computados.

```python
for config in configs:
    sensor_error = check_sensor_error(config.orbit_arrival_h)
    temp = LandingModule(**asdict(config), sensor_error=sensor_error, zone_clear=True)
    zone_clear = check_zone_clear(temp, modules)
    modules.append(LandingModule(**asdict(config), sensor_error=sensor_error, zone_clear=zone_clear))
```

**Por que construção sequencial?** `zone_clear` de cada módulo depende dos módulos já construídos. A iteração reflete a arquitetura de pousos sequenciais.

**O placeholder `zone_clear=True`:** `check_zone_clear` recebe um `LandingModule` para acessar `orbit_arrival_h`. O campo `zone_clear` do objeto temporário é irrelevante — apenas `orbit_arrival_h` é usado na comparação. `LandingModule` é frozen, então o campo precisa ser preenchido com algum valor.

---

## 14. src/simulation.py — Orquestração

### `main(scenario=None)`

```python
def main(scenario: Optional[List[LandingModuleConfig]] = None) -> None:
    from .scenarios import default_scenario
    modules = build_modules(scenario or default_scenario())
    module_index = build_module_index(modules)
    criticality_index = build_criticality_index(modules)
    ...
```

Os índices são construídos aqui, uma vez, e passados para baixo. Se `scenario` não for fornecido, usa `default_scenario()`. O import local de `default_scenario` evita importação circular.

### `simulate_landing_sequence(modules)`

O loop principal — um módulo por vez, em ordem de prioridade:

```python
while landing_queue:
    module = landing_queue.popleft()

    descent_time_s = 210.0 + module.orbit_arrival_h * 5.0  # SIMULATED — MSL EDL timeline
    telemetry = DescentTelemetry(
        current_altitude_m=compute_altitude(11_000.0, 470.0, descent_time_s),
        fuselage_temperature_c=compute_fuselage_temperature(descent_time_s),
        ...
    )

    result = evaluate_authorization(module, telemetry)

    if result.decision == Decision.AUTHORIZED:
        event_stack = push_event(event_stack, EventType.AUTHORIZATION_GRANTED, module)
        event_stack = push_event(event_stack, EventType.LANDING_INITIATED, module)
        audit_log   = append_audit(audit_log, EventType.LANDING_COMPLETED, ...)
        landed.append(module)

    elif result.decision == Decision.ALERT:
        alert_queue = enqueue_alert(alert_queue, module, reason)
        audit_log   = append_audit(audit_log, EventType.ALERT_GENERATED, ...)

    else:
        audit_log = append_audit(audit_log, EventType.LANDING_DENIED, ...)
        waiting.append(module)
```

**Por que dois eventos por módulo autorizado?** `AUTHORIZATION_GRANTED` e `LANDING_INITIATED` são ações distintas e reversíveis. Se um módulo falhar após a autorização mas antes de iniciar a descida, apenas `LANDING_INITIATED` precisa ser desfeito. A granularidade permite reverter em cascata com precisão.

**`descent_time_s = 210.0 + orbit_arrival_h * 5.0`** — SIMULATED: 210 s de base mais 5 s por hora de órbita coloca cada módulo próximo ao limiar de 1 500 m de ignição de retrofoguetes, conforme o timeline de EDL do MSL.

---

## 15. Padrões recorrentes

**Strategy table** — `[(condition, result), ...]` + `next(... if condition)` substitui `if/elif/else`. Cada regra é uma linha; a ordem importa; o default é o fallback seguro.

**Functional pipeline** — nenhuma função modifica estado externo. `event_stack = push_event(event_stack, ...)` reatribui a variável local, não muta a lista original.

**Fail-safe** — `Decision.DENIED` é o default. Para receber `AUTHORIZED`, todas as 5 condições devem ser `True` — `AND` lógico puro, sem exceções.

**`@dataclass(frozen=True)`** — snapshots de telemetria, resultados de autorização e eventos de auditoria não podem ser alterados após a criação. É um invariante de segurança, não apenas um conveniente.

**Build once, query many** — índices construídos uma vez em `main()`, passados por parâmetro. Sem reconstrução em cada chamada de display.

**`# SIMULATED`** — todo valor estimado declara sua origem. Qualquer leitor distingue constantes físicas documentadas de aproximações de engenharia.

---

## 16. Fluxo de dados completo

```
landing_manager.py
    main(scenario?)
        ↓
    build_modules(default_scenario() | random_scenario(n, anomaly_pct, seed))
        check_sensor_error(orbit_arrival_h) → bool
        check_zone_clear(module, prev_modules) → bool
        LandingModule(frozen) ← cada config + flags
        ↓
    build_module_index(modules)       → Dict[str, LandingModule]         O(n)
    build_criticality_index(modules)  → Dict[Criticality, List[Module]]  O(n)
        ↓
    display_header()
    display_module_queue(deque(sort_by_priority(modules)))
    display_mathematical_models()
        └── compute_altitude / compute_drag_force / compute_fuselage_temperature / compute_fuel_consumed_linear
            check_altitude / check_fuel / check_thermal
    display_search_results(modules, criticality_index, module_index)
        └── sort_by_priority (Insertion Sort)
            sort_by_fuel_ascending (Selection Sort)
            search_by_criticality(criticality_index, Criticality.VITAL)  O(1)
            search_by_orbit_arrival_window(modules, ref_h, 0.6)          O(n)
            binary_search_by_priority(sorted_modules, mid_priority)      O(log n)
            lookup_by_id(module_index, ref_module_id)                    O(1)
        ↓
    simulate_landing_sequence(modules)
        build_landing_queue → deque ordenada por priority (Insertion Sort)
        while queue:
            module = popleft()
            descent_time_s = 210.0 + orbit_arrival_h * 5.0  # SIMULATED
            compute_altitude(11_000, 470, t) → float
            compute_fuselage_temperature(t)  → float
            DescentTelemetry(module_id, altitude, velocity, temp, t)
            evaluate_authorization(module, telemetry) → AuthorizationResult

            Decision.AUTHORIZED:
                push_event(stack, EventType.AUTHORIZATION_GRANTED) → stack
                push_event(stack, EventType.LANDING_INITIATED)     → stack
                append_audit(log, EventType.LANDING_COMPLETED)     → log
                landed.append(module)

            Decision.ALERT:
                enqueue_alert(queue, module, reason) → queue
                append_audit(log, EventType.ALERT_GENERATED) → log

            Decision.DENIED:
                append_audit(log, EventType.LANDING_DENIED) → log
                waiting.append(module)

        flush_alert_queue_to_list(alert_queue) → alert_list (sorted by AlertSeverity)
        ↓
    display_alert_queue_and_list(deque(alert_list), alert_list)
    display_event_stack(event_stack)
    display_audit_log(audit_log)
    display_final_report(modules, landed, waiting, alert_list)
```

---

## 17. Glossário

| Termo | Significado |
|---|---|
| `@dataclass(frozen=True)` | Classe Python com campos imutáveis após criação — `FrozenInstanceError` em qualquer atribuição |
| Função pura | Sem efeitos colaterais — mesmo input sempre produz mesmo output |
| EDL | Entry, Descent and Landing — sequência de entrada na atmosfera, descida e pouso |
| Fail-safe | Qualquer falha impede autorização automática — o sistema falha em modo seguro |
| FIFO | First In, First Out — fila: primeiro a entrar, primeiro a sair |
| LIFO | Last In, First Out — pilha: último a entrar, primeiro a sair |
| Append-only | Estrutura que só cresce — nunca reverte ou modifica entradas anteriores |
| Override humano | Autorização manual obrigatória — o sistema não decide sozinho em casos de alerta |
| `# SIMULATED` | Valor estimado por ordem de grandeza com justificativa declarada — não derivado de dataset |
| Strategy table | Lista de tuplas `(condition, result)` avaliada em ordem — substitui `if/elif/else` |
| Build once, query many | Índice construído uma vez (O(n)), consultado múltiplas vezes (O(1)) |
| RAD750 | Processador de voo real do Curiosity e Perseverance — 256 MB RAM, 200 MHz — contexto do Insertion Sort |
| Insertion Sort | O(n²), estável, zero memória auxiliar — escolha para n=7 em ambiente de voo |
| Selection Sort | O(n) trocas no pior caso — identificação de módulos em risco com mínima movimentação |
| Busca binária | O(log n) — requer lista ordenada; eficiente para manifests maiores em fases futuras |
| Alert Queue | `deque` FIFO — canal de intake; nenhum alerta é perdido ou reordenado na entrada |
| Alert List | Lista ordenada por `AlertSeverity` — visão de trabalho do operador |
| Event Stack | Lista LIFO — registra ações reversíveis de controle de pouso |
| Audit Log | Lista append-only — registra fatos físicos e eventos irreversíveis |

---

*Missão Aurora Siger · FIAP — Ciência da Computação, Fase 2 · 2026*

🧑‍🚀 [Julia Ramos | RM568988](https://www.linkedin.com/in/juliaramosguedes) · [Matheus Fuchelberguer | RM569113](https://www.linkedin.com/in/matheus-fuchelberguer-neves/) · [Julio Joaquim | RM571321](https://github.com/jojigoats)
