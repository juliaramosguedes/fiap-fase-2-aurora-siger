"""
Landing Manager — Aurora Siger Colony Mission
==============================================
MGPEB: Módulo de Gerenciamento de Pouso e Estabilização de Base

Entry point. All implementation lives in src/.

Authors: Julia Ramos RM568988 | Matheus Fuchelberguer RM569113 | Julio Joaquim RM571321
FIAP — Ciência da Computação | Fase 2 — Atividade Integradora | 2026

Usage:
    python landing_manager.py                                    # default scenario (7 fixed modules, 2 anomalies)
    python landing_manager.py --random                           # random scenario, 7 modules, no anomalies
    python landing_manager.py --random --modules 10             # random scenario, 10 modules
    python landing_manager.py --random --anomaly 0.4            # with anomaly probability
    python landing_manager.py --random --modules 10 --anomaly 0.4
"""

import argparse

from src.scenarios import default_scenario, random_scenario
from src.simulation import main


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="landing_manager",
        description="MGPEB — Aurora Siger landing sequence manager",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Use procedural random scenario instead of default",
    )
    parser.add_argument(
        "--modules",
        type=int,
        default=7,
        help="Number of modules for random scenario (default: 7)",
    )
    parser.add_argument(
        "--anomaly",
        type=float,
        default=0.0,
        help="Anomaly probability per module (default: 0.0)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    scenario = (
        random_scenario(modules=args.modules, anomaly_pct=args.anomaly)
        if args.random
        else default_scenario()
    )
    main(scenario)
