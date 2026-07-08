"""Data-driven realism radar charts. Requires matplotlib + numpy (conda env `ml`).

Absent (A) plots at 0; Unknown (U) becomes NaN so it renders as a gap, never as 0,
and is excluded from the filled area.
"""
import json
import math
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DIMS = [f"D{i}" for i in range(1, 12)]
LABELS = ["Topological", "Service\nfidelity", "OS\nfidelity", "Identity", "Temporal",
          "Defensive", "Benign\nactivity", "Telemetry\nfidelity", "Action",
          "Observation", "External\ninfo"]
_LEVEL = {"C": 100, "U": 50, "-": 0}
_CODE = {"F": 100, "P": 50, "A": 0}   # "U"/unknown handled separately -> NaN (a gap)


def level_value(v):
    return _LEVEL[v]


def code_value(v):
    return _CODE.get(v, float("nan"))   # "U" or unknown -> NaN


def _close(vals):
    return list(vals) + [vals[0]]


def _polar_ax():
    n = len(DIMS)
    angles = [i / n * 2 * math.pi for i in range(n)]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_xticks(angles)
    ax.set_xticklabels(LABELS, fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["", "50", "", "100"], fontsize=8, color="gray")
    return fig, ax, angles + [angles[0]]


def _plot(ax, ang, series, color, label, dashed=False):
    closed = _close(series)
    # Markers ensure isolated finite points (e.g. a lone Partial amid Unknown
    # gaps) remain visible even when no connecting line segment can be drawn.
    ax.plot(ang, closed, color=color, linewidth=2.2, marker="o", markersize=3.5,
            linestyle="--" if dashed else "-", label=label)
    # Fill only when there are no gaps; NaN (Unknown) points are left as gaps so
    # they are never rendered as 0/Absent.
    if not any(v != v for v in closed):   # v != v is True only for NaN
        ax.fill(ang, closed, color=color, alpha=0.12)


def _save(fig, out_dir, name):
    fig.savefig(os.path.join(out_dir, name), bbox_inches="tight", dpi=200)
    plt.close(fig)


def render_use_case(uc_id, uc, out_dir):
    fig, ax, ang = _polar_ax()
    req = [level_value(uc["profile"][d]) for d in DIMS]
    _plot(ax, ang, req, "#d7301f", "Requirement (C=100, U=50, —=0)", dashed=True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), frameon=False, fontsize=9)
    _save(fig, out_dir, f"uc_{uc_id.lower()}.png")


def render_environment(slug, env, out_dir):
    fig, ax, ang = _polar_ax()
    cov = [code_value(env["scores"][d]) for d in DIMS]
    _plot(ax, ang, cov, "#084594", "Coverage (F=100, P=50, A=0; U omitted)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), frameon=False, fontsize=9)
    _save(fig, out_dir, f"env_{slug}.png")


def render_overlay(env_slug, env, uc_id, uc, out_dir):
    fig, ax, ang = _polar_ax()
    _plot(ax, ang, [level_value(uc["profile"][d]) for d in DIMS], "#d7301f",
          "Requirement", dashed=True)
    _plot(ax, ang, [code_value(env["scores"][d]) for d in DIMS], "#084594",
          f"{env['name']} coverage")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), frameon=False, fontsize=9)
    _save(fig, out_dir, f"overlay_{env_slug}_{uc_id.lower()}.png")


def render_all(data_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ucs = json.load(open(os.path.join(data_dir, "use_cases.json")))["use_cases"]
    envs = json.load(open(os.path.join(data_dir, "environments.json")))["environments"]
    for uc_id, uc in ucs.items():
        render_use_case(uc_id, uc, out_dir)
    for slug, env in envs.items():
        render_environment(slug, env, out_dir)
    for uc_id in ("UC-A1", "UC-A5"):
        render_overlay("goad", envs["goad"], uc_id, ucs[uc_id], out_dir)


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    render_all(os.path.join(here, "data"), os.path.join(here, "figures"))
