"""
Landing Manager — Aurora Siger Colony Mission
==============================================
MGPEB: Módulo de Gerenciamento de Pouso e Estabilização de Base

Entry point. All implementation lives in src/.

Authors: Julia Ramos RM568988 | Matheus Fuchelberguer RM569113 | Julio Joaquim RM571321
FIAP — Ciência da Computação | Fase 2 — Atividade Integradora | 2026

Usage:
    python landing_manager.py                          # default scenario (7 modules)
    python landing_manager.py --n 10                   # random scenario, 10 modules
    python landing_manager.py --n 10 --anomaly-pct 0.4 --seed 42
"""

import argparse

from src.scenarios import default_scenario, random_scenario
from src.simulation import main


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="landing_manager",
        description="MGPEB — Aurora Siger landing sequence manager",
    )
    parser.add_argument("--n", type=int, default=None, help="Number of modules (triggers random scenario)")
    parser.add_argument("--anomaly-pct", type=float, default=0.25, help="Anomaly probability per module (default: 0.25)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    scenario = random_scenario(n=args.n, anomaly_pct=args.anomaly_pct, seed=args.seed) if args.n is not None else default_scenario()
    main(scenario)
