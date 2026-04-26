"""
Generate physics model plots for MGPEB documentation.

Requirements (dev dependencies):
    pip install -e ".[dev]"

Usage (from any directory in the repo):
    python docs/generate_plots.py

Output: docs/plots/{altitude,drag_force,temperature,fuel_consumption}.png
"""

from __future__ import annotations

import sys
from pathlib import Path

# Anchor to repo root so `src` is importable regardless of CWD
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams.update({
    "figure.facecolor":  "#0a0f1e",
    "axes.facecolor":    "#0a0f1e",
    "axes.edgecolor":    "#2a3a5c",
    "axes.labelcolor":   "#c5d8f0",
    "xtick.color":       "#c5d8f0",
    "ytick.color":       "#c5d8f0",
    "text.color":        "#c5d8f0",
    "grid.color":        "#2a3a5c",
    "grid.alpha":        0.4,
    "axes.titlecolor":   "#c5d8f0",
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "figure.dpi":        150,
})

from src.constants import (
    DRAG_COEFFICIENT_K,
    ENTRY_PEAK_TEMP_C,
    FUEL_BURN_RATE_PCT_PER_S,
    FUEL_MIN_PCT,
    MARS_GRAVITY,
    MARS_SURFACE_TEMP_C,
    POWERED_DESCENT_INITIAL_FUEL_PCT,
    RETRO_IGNITION_ALTITUDE_M,
    THERMAL_DECAY_LAMBDA,
    THERMAL_MAX_C,
)
from src.physics import (
    compute_altitude,
    compute_drag_force,
    compute_fuel_consumed_linear,
    compute_fuselage_temperature,
)

LINE_COLOR   = "#7ab0e8"
THRESH_COLOR = "#e74c3c"
ALERT_COLOR  = "#f39c12"
LINE_WIDTH   = 2.0
THRESH_WIDTH = 1.5


def _save(fig: plt.Figure, output_dir: Path, name: str) -> None:
    path = output_dir / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved: {path}")


def plot_altitude(output_dir: Path) -> None:
    h0, v0 = 11_000.0, 470.0

    # Find when h(t) first reaches 0 — clip range there
    t_all = np.linspace(0, 30, 3000)
    h_all = np.array([compute_altitude(h0, v0, t) for t in t_all])
    touchdown_idx = np.argmax(h_all == 0.0)
    t_end = t_all[touchdown_idx] if touchdown_idx > 0 else 30.0

    t = np.linspace(0, t_end, 300)
    h = np.array([compute_altitude(h0, v0, ti) for ti in t])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t, h, color=LINE_COLOR, linewidth=LINE_WIDTH, label="h(t)")
    ax.axhline(
        RETRO_IGNITION_ALTITUDE_M,
        color=THRESH_COLOR, linestyle="--", linewidth=THRESH_WIDTH,
        label=f"ALTITUDE_OK = True  ({RETRO_IGNITION_ALTITUDE_M:.0f} m)",
    )
    ax.annotate(
        "solo marciano",
        xy=(t_end, 0), xytext=(t_end - 3, 600),
        arrowprops={"arrowstyle": "->", "color": "#c5d8f0"},
        color="#c5d8f0", fontsize=9,
    )
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Altitude (m)")
    ax.set_title("Altitude × Tempo de Descida — h(t) = h₀ - v₀·t - ½·g·t²")
    ax.legend(framealpha=0.15)
    ax.grid(True)
    _save(fig, output_dir, "altitude.png")


def plot_drag_force(output_dir: Path) -> None:
    v = np.linspace(100, 5900, 500)
    F = np.array([compute_drag_force(vi) for vi in v])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(v, F, color=LINE_COLOR, linewidth=LINE_WIDTH)
    ax.set_yscale("log")

    for v_mark in [5900, 2000, 500, 100]:
        f_mark = compute_drag_force(float(v_mark))
        ax.annotate(
            f"v={v_mark} m/s\nF={f_mark:,.0f} N",
            xy=(v_mark, f_mark),
            xytext=(v_mark - 700 if v_mark > 200 else v_mark + 200, f_mark * 1.8),
            arrowprops={"arrowstyle": "->", "color": "#c5d8f0"},
            color="#c5d8f0", fontsize=8,
        )

    ax.set_xlabel("Velocidade (m/s)")
    ax.set_ylabel("Força de Arrasto (N) — escala log")
    ax.set_title("Força de Arrasto × Velocidade — F(v) = k·v²")
    ax.grid(True, which="both")
    _save(fig, output_dir, "drag_force.png")


def plot_temperature(output_dir: Path) -> None:
    t = np.linspace(0, 600, 500)
    T = np.array([compute_fuselage_temperature(ti) for ti in t])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t, T, color=LINE_COLOR, linewidth=LINE_WIDTH, label="T(t)")
    ax.axhline(
        THERMAL_MAX_C,
        color=THRESH_COLOR, linestyle="--", linewidth=THRESH_WIDTH,
        label=f"THERMAL_OK = True  (≤ {THERMAL_MAX_C:.0f} °C)",
    )
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Temperatura (°C)")
    ax.set_title("Temperatura da Fuselagem × Tempo — T(t) = T_sup + (T_ent−T_sup)·e^(−λt)")
    ax.legend(framealpha=0.15)
    ax.grid(True)
    _save(fig, output_dir, "temperature.png")


def plot_fuel_consumption(output_dir: Path) -> None:
    t = np.linspace(0, 1000, 500)
    C = np.array([compute_fuel_consumed_linear(ti) for ti in t])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t, C, color=LINE_COLOR, linewidth=LINE_WIDTH, label="C(t)")
    ax.axhline(
        FUEL_MIN_PCT,
        color=THRESH_COLOR, linestyle="--", linewidth=THRESH_WIDTH,
        label=f"FUEL_OK = True  (≥ {FUEL_MIN_PCT:.0f}%)",
    )
    ax.axhline(
        55.0,
        color=ALERT_COLOR, linestyle="--", linewidth=THRESH_WIDTH,
        label="LOG-01 — nível inicial (55%) abaixo do limiar",
    )
    ax.axhline(
        48.0,
        color=ALERT_COLOR, linestyle=":", linewidth=THRESH_WIDTH,
        label="MIN-01 — nível inicial (48%) abaixo do limiar",
    )
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Combustível Restante (%)")
    ax.set_title("Consumo de Combustível × Tempo — C(t) = C₀ − r·t")
    ax.legend(framealpha=0.15)
    ax.grid(True)
    _save(fig, output_dir, "fuel_consumption.png")


def main() -> None:
    output_dir = Path(__file__).parent / "plots"
    output_dir.mkdir(exist_ok=True)
    print("Gerando gráficos em", output_dir)

    plot_altitude(output_dir)
    plot_drag_force(output_dir)
    plot_temperature(output_dir)
    plot_fuel_consumption(output_dir)

    print("Concluído.")


if __name__ == "__main__":
    main()
