"""
Landing Manager — Aurora Siger Colony Mission
==============================================
MGPEB: Módulo de Gerenciamento de Pouso e Estabilização de Base

Entry point. All implementation lives in src/.

Authors: Julia Ramos RM568988 | Matheus Fuchelberguer RM569113 | Julio Joaquim RM571321
FIAP — Ciência da Computação | Fase 2 — Atividade Integradora | 2026
"""

from src.simulation import main

if __name__ == "__main__":
    main()
    # To use a random scenario: main(random_scenario(n=10, anomaly_pct=0.4, seed=42))
    # from src.scenarios import random_scenario
